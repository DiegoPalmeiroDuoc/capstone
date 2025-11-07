#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Intexta Chatbot - Asistente Virtual por WhatsApp
Integrado con Firebase para consultar documentos del cliente

Funcionalidades:
- Autenticación de usuarios por WhatsApp
- Consulta de documentos procesados en Firestore
- Respuestas contextualizadas usando DeepSeek API
- Gestión de conversaciones persistentes
"""

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import sys
import logging
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

app = Flask(__name__)

# Configuración
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    logging.warning("⚠️  DEEPSEEK_API_KEY no configurada. El chatbot funcionará con limitaciones.")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Base de datos en memoria para conversaciones
conversaciones = {}  # {phone_number: [{role, content}, ...]}
usuarios_autenticados = {}  # {phone_number: user_id}
usuarios_contexto = {}  # {phone_number: {'last_doc': doc_id, 'waiting_for': command}}

# Inicializar Firebase
db = None
try:
    # Importar configuración de Firebase desde cliente_web
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cliente_web'))
    from firebase_config import db as firestore_db
    db = firestore_db
    logging.info("✅ Firebase conectado correctamente")
except Exception as e:
    logging.error(f"❌ Error conectando Firebase: {e}")
    logging.error("El chatbot funcionará en modo limitado sin acceso a documentos")


class IntextaChatbot:
    """Chatbot inteligente integrado con Firebase"""
    
    def __init__(self, db):
        self.db = db
    
    def get_user_documents(self, user_id):
        """
        Obtiene todos los documentos procesados de un usuario.
        
        Args:
            user_id: UID del usuario en Firebase
        
        Returns:
            Lista de documentos con su contenido procesado
        """
        try:
            if not self.db:
                return []
            
            docs_ref = self.db.collection('documentos').where('usuarioId', '==', user_id)
            docs = docs_ref.stream()
            
            documentos = []
            for doc in docs:
                data = doc.to_dict()
                # Solo incluir documentos procesados exitosamente
                if data.get('estado') == 'procesado' and data.get('contenidoProcesado'):
                    documentos.append({
                        'id': doc.id,
                        'nombre': data.get('nombre', 'Sin nombre'),
                        'contenido': data.get('contenidoProcesado', ''),
                        'descripcion': data.get('descripcion', ''),
                        'fecha': data.get('fechaSubida', '')
                    })
            
            logging.info(f"Usuario {user_id}: {len(documentos)} documentos encontrados")
            return documentos
            
        except Exception as e:
            logging.error(f"Error obteniendo documentos del usuario {user_id}: {e}")
            return []
    
    def get_user_by_phone(self, phone_number):
        """
        Busca un usuario por su número de teléfono.
        Normaliza el formato del número para buscar correctamente.
        
        Args:
            phone_number: Número de WhatsApp (puede incluir +56 o no)
        
        Returns:
            UID del usuario o None
        """
        try:
            if not self.db:
                return None
            
            # Normalizar número: quitar +, espacios, guiones
            normalized = phone_number.replace('+', '').replace(' ', '').replace('-', '')
            
            # Si empieza con 56 (código Chile), quitarlo
            if normalized.startswith('56'):
                normalized_local = normalized[2:]  # Sin +56
            else:
                normalized_local = normalized
            
            logging.info(f"🔍 Buscando usuario con teléfono: {phone_number}")
            logging.info(f"   Formatos a buscar: {phone_number}, {normalized}, {normalized_local}")
            
            # Buscar con múltiples formatos
            formats_to_try = [
                phone_number,           # Formato original
                normalized,             # Sin +
                normalized_local,       # Sin +56
                f"+{normalized}",       # Con +
                f"+56{normalized_local}" # Formato internacional completo
            ]
            
            # Eliminar duplicados
            formats_to_try = list(set(formats_to_try))
            
            # Buscar en colección de usuarios con cada formato
            for phone_format in formats_to_try:
                users_ref = self.db.collection('usuarios').where('telefono', '==', phone_format)
                users = list(users_ref.stream())
                
                if users:
                    logging.info(f"✅ Usuario encontrado con formato: {phone_format}")
                    return users[0].id
            
            logging.warning(f"❌ No se encontró usuario con teléfono: {phone_number}")
            return None
            
        except Exception as e:
            logging.error(f"Error buscando usuario por teléfono {phone_number}: {e}")
            return None
    
    def search_relevant_content(self, text, query, max_chars=100000):
        """
        Busca secciones relevantes del texto basándose en la consulta del usuario.
        Usa búsqueda por palabras clave para encontrar fragmentos relevantes.
        
        Args:
            text: Texto completo del documento
            query: Pregunta del usuario
            max_chars: Máximo de caracteres a retornar
        
        Returns:
            String con las secciones más relevantes
        """
        # Palabras clave de la consulta (sin palabras comunes)
        stop_words = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se', 'no', 'hay', 'por', 'con', 'su', 'para', 'como', 'está', 'lo', 'pero', 'sus', 'le', 'ya', 'o', 'fue', 'este', 'ha', 'sí', 'porque', 'esta', 'son', 'entre', 'cuando', 'muy', 'sin', 'sobre', 'también', 'me', 'hasta', 'donde', 'quien', 'desde', 'todo', 'nos', 'durante', 'todos', 'uno', 'les', 'ni', 'contra', 'otros', 'ese', 'eso', 'ante', 'ellos', 'e', 'esto', 'mí', 'antes', 'algunos', 'qué', 'unos', 'yo', 'del', 'mucho', 'te', 'más', 'cual', 'poco', 'ella', 'estar', 'estas', 'algunas', 'algo', 'nosotros', 'cuántos', 'cuánto', 'cuánta', 'cuántas', 'cuál', 'cuáles', 'dice', 'dices', 'tengo', 'tienes', 'tiene'}
        
        query_words = [w.lower() for w in query.split() if len(w) > 2 and w.lower() not in stop_words]
        
        logging.info(f"🔍 Búsqueda inteligente - Palabras clave: {query_words}")
        
        if not query_words:
            # Si no hay palabras clave, retornar inicio del documento
            logging.info(f"⚠️  Sin palabras clave, retornando inicio del documento")
            return text[:max_chars]
        
        # Dividir texto en párrafos (bloques más grandes para mejor contexto)
        # Intentar dividir por doble salto de línea primero
        paragraphs = text.split('\n\n')
        
        # Si hay muy pocos párrafos, dividir por salto de línea simple
        if len(paragraphs) < 10:
            paragraphs = text.split('\n')
        
        # Calcular score de relevancia para cada párrafo
        scored_paragraphs = []
        for i, para in enumerate(paragraphs):
            para_stripped = para.strip()
            if len(para_stripped) < 30:  # Ignorar párrafos muy cortos
                continue
            
            para_lower = para_stripped.lower()
            score = 0
            
            # Contar coincidencias de palabras clave (con mayor peso)
            for word in query_words:
                count = para_lower.count(word)
                if count > 0:
                    # Bonus por coincidencias múltiples
                    score += count * 20
                    
                    # Bonus extra si la palabra aparece al inicio del párrafo
                    if para_lower.startswith(word) or para_lower.startswith(' ' + word):
                        score += 10
            
            # Bonus por posición (primeros párrafos pueden tener introducción relevante)
            if i < 50:  # Primeros 50 párrafos
                position_bonus = 15
            elif i < 100:  # Párrafos 51-100
                position_bonus = 10
            elif i < 200:  # Párrafos 101-200
                position_bonus = 5
            else:
                position_bonus = 0
            
            score += position_bonus
            
            # Bonus por longitud (párrafos con contenido sustancial)
            if 100 < len(para_stripped) < 500:
                score += 5
            
            scored_paragraphs.append((score, i, para_stripped))
        
        # Ordenar por score descendente
        scored_paragraphs.sort(reverse=True, key=lambda x: x[0])
        
        logging.info(f"📊 Analizados {len(scored_paragraphs)} párrafos, top score: {scored_paragraphs[0][0] if scored_paragraphs else 0}")
        
        # Tomar los párrafos más relevantes hasta alcanzar max_chars
        selected_parts = []
        total_chars = 0
        
        # Aumentar a top 50 para documentos grandes
        for score, idx, para in scored_paragraphs[:50]:
            if score == 0:
                break
            
            if total_chars + len(para) + 2 > max_chars:  # +2 por \n\n
                # Si queda espacio razonable, agregar truncado
                remaining = max_chars - total_chars
                if remaining > 300:
                    selected_parts.append((idx, para[:remaining] + "..."))
                break
            
            selected_parts.append((idx, para))
            total_chars += len(para) + 2  # +2 por \n\n
        
        # Ordenar por índice original para mantener coherencia
        selected_parts.sort(key=lambda x: x[0])
        
        if not selected_parts:
            logging.warning(f"⚠️  No se encontraron secciones relevantes, retornando inicio")
            return text[:max_chars]
        
        # Unir párrafos seleccionados
        result = "\n\n".join([para for _, para in selected_parts])
        
        logging.info(f"✅ Contexto relevante: {len(result)} caracteres de {len(text)} totales ({len(selected_parts)} secciones)")
        
        return result
    
    def build_context_from_documents(self, documentos, user_query="", max_chars=100000):
        """
        Construye contexto para la IA a partir de los documentos del usuario.
        Con búsqueda inteligente de contenido relevante.
        
        Args:
            documentos: Lista de documentos
            user_query: Pregunta del usuario (para búsqueda relevante)
            max_chars: Máximo de caracteres a incluir (DeepSeek límite ~256k chars, usamos 100k para seguridad)
        
        Returns:
            String con el contexto formateado
        """
        if not documentos:
            return "No hay documentos disponibles para consultar."
        
        context_parts = ["=== DOCUMENTOS DEL USUARIO ===\n"]
        total_chars = 0
        
        for doc in documentos:
            doc_header = f"\n--- {doc['nombre']} ({len(doc['contenido'])} caracteres) ---\n"
            doc_content = doc['contenido']
            
            # Calcular cuánto espacio queda
            available = max_chars - total_chars - len(doc_header)
            
            if available <= 500:  # Mínimo 500 chars por documento
                context_parts.append(f"\n[...más documentos disponibles pero omitidos por límite de contexto...]")
                break
            
            # Si el documento es muy grande y hay una consulta, buscar contenido relevante
            if len(doc_content) > available and user_query:
                doc_content = self.search_relevant_content(doc_content, user_query, available)
                doc_header = f"\n--- {doc['nombre']} (extracto relevante de {len(doc['contenido'])} caracteres totales) ---\n"
            elif len(doc_content) > available:
                # Sin consulta, tomar inicio y fin
                half = available // 2 - 100
                doc_content = (
                    doc_content[:half] + 
                    f"\n\n[...{len(doc_content) - available} caracteres omitidos...]\n\n" +
                    doc_content[-half:]
                )
            
            context_parts.append(doc_header)
            context_parts.append(doc_content)
            total_chars += len(doc_header) + len(doc_content)
        
        final_context = "".join(context_parts)
        logging.info(f"📊 Contexto construido: {total_chars} caracteres, {len(documentos)} documentos")
        
        return final_context
    
    def call_deepseek_api(self, messages):
        """
        Llama a la API de DeepSeek para generar respuestas.
        
        Args:
            messages: Lista de mensajes [{role, content}, ...]
        
        Returns:
            Respuesta de la IA
        """
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500  # Aumentado para respuestas más completas
        }
        
        try:
            r = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=30)
            logging.info(f"DeepSeek status: {r.status_code}")
            r.raise_for_status()
            
            response_data = r.json()
            
            # Log de uso de tokens
            usage = response_data.get("usage", {})
            logging.info(
                f"Tokens - prompt: {usage.get('prompt_tokens', '?')}, "
                f"completion: {usage.get('completion_tokens', '?')}, "
                f"total: {usage.get('total_tokens', '?')}"
            )
            
            return response_data["choices"][0]["message"]["content"]
            
        except requests.exceptions.Timeout:
            return (
                "⏱️ *Ups, tomó demasiado tiempo...*\n\n"
                "Tu consulta está tardando más de lo esperado.\n\n"
                "💡 *Intenta:*\n"
                "• Hacer una pregunta más específica\n"
                "• Esperar unos segundos y volver a intentar\n\n"
                "Estoy aquí cuando estés listo 😊"
            )
        except requests.exceptions.RequestException as e:
            logging.error(f"Error en API DeepSeek: {e}")
            return (
                "❌ *Algo salió mal...*\n\n"
                "Hubo un problema técnico procesando tu consulta.\n\n"
                "💡 Por favor:\n"
                "• Intenta nuevamente en unos momentos\n"
                "• Si persiste, escribe `/ayuda`\n\n"
                "¡Disculpa las molestias! 🙏"
            )
        except (KeyError, IndexError) as e:
            logging.error(f"Error parseando respuesta de DeepSeek: {e}")
            return (
                "🔧 *Error procesando respuesta*\n\n"
                "Hubo un problema interpretando la respuesta.\n\n"
                "Por favor, intenta reformular tu pregunta. 💬"
            )
    
    def process_message(self, phone_number, incoming_msg):
        """
        Procesa un mensaje entrante de WhatsApp con comandos mejorados.
        
        Args:
            phone_number: Número de teléfono del usuario
            incoming_msg: Mensaje del usuario
        
        Returns:
            Respuesta para enviar al usuario
        """
        # Inicializar conversación si no existe
        if phone_number not in conversaciones:
            conversaciones[phone_number] = []
        
        # Normalizar mensaje
        msg_lower = incoming_msg.lower().strip()
        
        # Comandos de ayuda
        if msg_lower in ['/ayuda', 'ayuda', 'help', 'menu', '/menu', '?']:
            return self.get_help_message()
        
        # Comando de reset
        if msg_lower in ['/reset', 'reset', 'reiniciar', 'limpiar', 'borrar']:
            conversaciones[phone_number] = []
            if phone_number in usuarios_contexto:
                del usuarios_contexto[phone_number]
            return (
                "🔄 *Conversación reiniciada*\n\n"
                "Historial borrado y listo para comenzar de nuevo.\n\n"
                "¿En qué puedo ayudarte? 😊"
            )
        
        # Verificar si el usuario está autenticado
        if phone_number not in usuarios_autenticados:
            user_id = self.get_user_by_phone(phone_number)
            
            if not user_id:
                return self.get_authentication_message()
            
            usuarios_autenticados[phone_number] = user_id
            logging.info(f"Usuario autenticado: {phone_number} -> {user_id}")
            
            # Mensaje de bienvenida en primera conexión
            return self.get_welcome_message()
        
        # Obtener documentos del usuario
        user_id = usuarios_autenticados[phone_number]
        documentos = self.get_user_documents(user_id)
        
        # Comando: Ver lista de documentos
        if msg_lower in ['/documentos', 'documentos', 'mis documentos', 'lista', '/lista']:
            return self.get_documents_list(documentos)
        
        # Comando: Resumen de documento
        if msg_lower.startswith('/resumen') or msg_lower.startswith('resumen de'):
            if not documentos:
                return (
                    "📄 No tienes documentos para resumir.\n\n"
                    "Sube documentos en tu dashboard web primero. 📤"
                )
            
            # Si solo tiene un documento, resumirlo directamente
            if len(documentos) == 1:
                doc = documentos[0]
                resumen_prompt = f"Resume brevemente el documento '{doc['nombre']}' en 3-4 puntos clave. maximo 3 lineas "
                # Procesar como pregunta normal
                incoming_msg = resumen_prompt
                # Continuar con el flujo normal (no hacer return aquí)
            else:
                # Retornar mensaje de ayuda si tiene múltiples documentos
                return (
                    "📚 Tienes varios documentos.\n\n"
                    "Por favor especifica cuál quieres resumir:\n"
                    f"Ejemplo: 'Resumen de {documentos[0]['nombre'][:30]}...'\n\n"
                    "O usa `/documentos` para ver la lista completa."
                )
        
        # Comando: Buscar por tema
        if msg_lower.startswith('/buscar '):
            tema = incoming_msg[8:].strip()  # Quitar '/buscar '
            if not tema:
                return (
                    "🔍 *Búsqueda por tema*\n\n"
                    "Uso: `/buscar [tema]`\n\n"
                    "Ejemplos:\n"
                    "• /buscar matrimonio\n"
                    "• /buscar contratos\n"
                    "• /buscar familia\n\n"
                    "¿Qué tema quieres buscar?"
                )
            
            incoming_msg = f"Busca información sobre: {tema} dame una respuesta concisa en 3-4 lineas"
        
        # Si no tiene documentos, informar amigablemente
        if not documentos:
            return (
                "📄 *Aún no tienes documentos*\n\n"
                "Para comenzar a usar Intexta:\n\n"
                "1️⃣ Ve a tu dashboard web\n"
                "2️⃣ Sube documentos (PDF, Word, Excel...)\n"
                "3️⃣ Espera el procesamiento\n"
                "4️⃣ ¡Vuelve aquí para consultarlos!\n\n"
                "✨ Estaré esperando tus documentos."
            )
        
        # Construir contexto con búsqueda inteligente basada en la pregunta
        context = self.build_context_from_documents(documentos, user_query=incoming_msg)
        
        # Construir mensajes para la IA con prompt optimizado
        system_prompt = {
            "role": "system",
            "content": (
                "Eres *Intexta* 🤖, un asistente virtual experto y amigable.\n\n"
                
                "📋 TU MISIÓN:\n"
                "Responder preguntas basándote ÚNICAMENTE en los documentos del usuario.\n\n"
                
                "✅ RESPUESTAS IDEALES:\n"
                "• DIRECTO AL GRANO: Sin introducciones innecesarias\n"
                "• ESPECÍFICO: Cita información exacta del documento\n"
                "• ESTRUCTURADO: Usa viñetas (•) o números cuando sea apropiado\n"
                "• CONCISO: 3-5 líneas máximo por WhatsApp\n"
                "• AMIGABLE: Tono conversacional y emojis relevantes ✨\n\n"
                
                "❌ EVITA:\n"
                "• Frases como 'Según el documento...', 'Basándome en...'\n"
                "• Repetir la pregunta del usuario\n"
                "• Información que NO esté en los documentos\n"
                "• Respuestas ambiguas o vagas\n\n"
                
                "🎯 SI NO ENCUENTRAS LA INFO:\n"
                "Di claramente: '❌ No encuentro esa información en tus documentos'\n\n"
                
                "💡 FORMATO PREFERIDO:\n"
                "→ Respuesta directa primero\n"
                "→ Detalles o ejemplos después\n"
                "→ Usa emojis relevantes (📌 ✓ → • 📊 💡)"
            )
        }
                
        context_message = {
            "role": "system",
            "content": context
        }
        
        # Agregar mensaje del usuario
        conversaciones[phone_number].append({
            "role": "user",
            "content": incoming_msg
        })
        
        # Construir lista completa de mensajes
        messages = [system_prompt, context_message] + conversaciones[phone_number][-5:]  # Últimos 5 mensajes
        
        # Llamar a la IA
        response = self.call_deepseek_api(messages)
        
        # Mejorar respuesta si es muy corta o vaga
        if response and len(response.strip()) < 20:
            response += "\n\n💡 ¿Necesitas más detalles? ¡Pregúntame!"
        
        # Agregar sugerencia de comandos si la respuesta indica no encontrar información
        if "no encuentro" in response.lower() or "no tengo" in response.lower():
            response += (
                "\n\n💡 *Sugerencias:*\n"
                "• Usa `/documentos` para ver qué documentos tienes\n"
                "• Reformula tu pregunta con otras palabras\n"
                "• Verifica que la info esté en tus documentos"
            )
        
        # Guardar respuesta en historial
        conversaciones[phone_number].append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def get_help_message(self):
        """Mensaje de ayuda mejorado con formato amigable"""
        return (
            "🤖 *¡Hola! Soy Intexta* 👋\n\n"
            "Tu asistente personal para consultar documentos.\n\n"
            "📋 *Comandos disponibles:*\n"
            "• `/documentos` - Ver mis documentos\n"
            "• `/resumen` - Resumen de un documento\n"
            "• `/buscar [tema]` - Buscar por tema\n"
            "• `/ayuda` - Ver este menú\n"
            "• `/reset` - Nueva conversación\n\n"
            "💬 *O simplemente pregúntame:*\n"
            "→ '¿Qué dice sobre el matrimonio?'\n"
            "→ '¿Cuántos documentos tengo?'\n"
            "→ '¿Qué temas cubre mi PDF?'\n\n"
            "✨ ¡Estoy listo para ayudarte!"
        )
    
    def get_welcome_message(self, nombre_usuario=""):
        """Mensaje de bienvenida personalizado"""
        saludo = f"¡Hola{', ' + nombre_usuario if nombre_usuario else ''}! 👋\n\n" if nombre_usuario else "👋 ¡Bienvenido de nuevo!\n\n"
        return (
            f"{saludo}"
            "🤖 Soy *Intexta*, tu asistente de documentos.\n\n"
            "📚 Puedo ayudarte a:\n"
            "✓ Consultar información de tus documentos\n"
            "✓ Hacer búsquedas específicas\n"
            "✓ Obtener resúmenes\n\n"
            "💡 *Tip:* Escribe `/ayuda` para ver todos los comandos disponibles.\n\n"
            "¿En qué puedo ayudarte hoy? 😊"
        )
    
    def get_documents_list(self, documentos):
        """Lista formateada de documentos del usuario"""
        if not documentos:
            return (
                "📄 *Tus documentos*\n\n"
                "No tienes documentos procesados aún.\n\n"
                "💡 Para subir documentos:\n"
                "1. Ve a tu dashboard web\n"
                "2. Haz clic en 'Subir archivo'\n"
                "3. ¡Espera el procesamiento!\n\n"
                "✨ Luego podrás consultarlos aquí por WhatsApp."
            )
        
        msg = "📚 *Tus documentos procesados:*\n\n"
        for i, doc in enumerate(documentos[:10], 1):  # Máximo 10
            nombre = doc['nombre']
            tamaño = len(doc['contenido'])
            
            # Emoji según tipo de archivo
            emoji = "📄"
            if '.pdf' in nombre.lower():
                emoji = "📕"
            elif '.docx' in nombre.lower() or '.doc' in nombre.lower():
                emoji = "📘"
            elif '.xlsx' in nombre.lower() or '.xls' in nombre.lower():
                emoji = "📊"
            elif '.pptx' in nombre.lower() or '.ppt' in nombre.lower():
                emoji = "📙"
            
            # Tamaño en formato legible
            if tamaño > 1000000:
                tamaño_str = f"{tamaño // 1000000}MB"
            elif tamaño > 1000:
                tamaño_str = f"{tamaño // 1000}KB"
            else:
                tamaño_str = f"{tamaño}B"
            
            msg += f"{i}. {emoji} *{nombre[:40]}{'...' if len(nombre) > 40 else ''}*\n"
            msg += f"   └ {tamaño_str} • {len(doc['contenido'].split())} palabras\n\n"
        
        if len(documentos) > 10:
            msg += f"\n_...y {len(documentos) - 10} documentos más_\n\n"
        
        msg += "💬 *Pregúntame sobre cualquiera de ellos*"
        
        return msg
    
    def get_authentication_message(self):
        """Mensaje cuando el usuario no está autenticado - más amigable"""
        return (
            "👋 *¡Hola! Bienvenido a Intexta*\n\n"
            "Para comenzar a usar este servicio necesitas:\n\n"
            "1️⃣ *Registrarte* en la plataforma web\n"
            "   → Crea tu cuenta con email\n\n"
            "2️⃣ *Vincular WhatsApp*\n"
            "   → En tu perfil, agrega este número\n\n"
            "3️⃣ *Subir documentos*\n"
            "   → PDF, Word, Excel, PowerPoint...\n\n"
            "✨ Una vez completado, ¡podré ayudarte aquí en WhatsApp!\n\n"
            "� ¿Necesitas ayuda? Contáctanos:\n"
            "→ gi.espinosa@duocuc.cl"
        )


# Crear instancia del chatbot
chatbot = IntextaChatbot(db)


@app.route("/webhook", methods=["GET"])
def webhook_verify():
    """Verificación del webhook de Twilio"""
    return "Webhook activo", 200


@app.route("/webhook", methods=["POST"])
def webhook_reply():
    """Endpoint principal para recibir mensajes de WhatsApp"""
    try:
        incoming_msg = request.form.get('Body', '').strip()
        phone_number = request.form.get('From', '').replace('whatsapp:', '')
        
        logging.info(f"📩 Mensaje de {phone_number}: {incoming_msg}")
        
        # Procesar mensaje
        response_text = chatbot.process_message(phone_number, incoming_msg)
        
        # Crear respuesta de Twilio
        resp = MessagingResponse()
        msg = resp.message()
        msg.body(response_text)
        
        logging.info(f"📤 Respuesta a {phone_number}: {response_text[:100]}...")
        
        return str(resp)
        
    except Exception as e:
        logging.error(f"❌ Error procesando mensaje: {e}", exc_info=True)
        
        # Respuesta de error genérica
        resp = MessagingResponse()
        msg = resp.message()
        msg.body("❌ Lo siento, hubo un error procesando tu mensaje. Por favor, intenta de nuevo.")
        
        return str(resp)


@app.route("/health", methods=["GET"])
def health_check():
    """Endpoint de health check"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "firebase_connected": db is not None,
        "active_conversations": len(conversaciones)
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logging.info(f"🚀 Iniciando Intexta Chatbot en puerto {port}")
    logging.info(f"🔗 Webhook: http://localhost:{port}/webhook")
    logging.info(f"❤️  Health check: http://localhost:{port}/health")
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )
