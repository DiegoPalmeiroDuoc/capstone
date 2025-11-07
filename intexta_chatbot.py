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
            "max_tokens": 1000  # Aumentado para respuestas más completas
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
            return "⏱️ La consulta está tardando más de lo esperado. Por favor, intenta de nuevo."
        except requests.exceptions.RequestException as e:
            logging.error(f"Error en API DeepSeek: {e}")
            return "❌ Lo siento, hubo un problema al procesar tu consulta. Intenta de nuevo más tarde."
        except (KeyError, IndexError) as e:
            logging.error(f"Error parseando respuesta de DeepSeek: {e}")
            return "❌ Hubo un error al procesar la respuesta. Por favor, intenta de nuevo."
    
    def process_message(self, phone_number, incoming_msg):
        """
        Procesa un mensaje entrante de WhatsApp.
        
        Args:
            phone_number: Número de teléfono del usuario
            incoming_msg: Mensaje del usuario
        
        Returns:
            Respuesta para enviar al usuario
        """
        # Inicializar conversación si no existe
        if phone_number not in conversaciones:
            conversaciones[phone_number] = []
        
        # Comandos especiales
        if incoming_msg.lower() in ['/ayuda', 'ayuda', 'help']:
            return self.get_help_message()
        
        if incoming_msg.lower() in ['/reset', 'reset', 'reiniciar']:
            conversaciones[phone_number] = []
            return "🔄 Conversación reiniciada. ¿En qué puedo ayudarte?"
        
        # Verificar si el usuario está autenticado
        if phone_number not in usuarios_autenticados:
            user_id = self.get_user_by_phone(phone_number)
            
            if not user_id:
                return self.get_authentication_message()
            
            usuarios_autenticados[phone_number] = user_id
            logging.info(f"Usuario autenticado: {phone_number} -> {user_id}")
        
        # Obtener documentos del usuario
        user_id = usuarios_autenticados[phone_number]
        documentos = self.get_user_documents(user_id)
        
        if not documentos:
            return (
                "📄 No tienes documentos procesados disponibles.\n\n"
                "Por favor, sube tus documentos desde la web de Intexta:\n"
                "https://tu-dominio.com/dashboard"
            )
        
        # Construir contexto con búsqueda inteligente basada en la pregunta
        context = self.build_context_from_documents(documentos, user_query=incoming_msg)
        
        # Construir mensajes para la IA
        system_prompt = {
            "role": "system",
            "content": (
                "Eres Intexta, un asistente virtual experto en análisis de documentos. "
                "Tu trabajo es responder preguntas basándote ÚNICAMENTE en los documentos proporcionados. "
                "\n\nINSTRUCCIONES:"
                "\n- Lee cuidadosamente todo el contexto antes de responder"
                "\n- Si la información está en los documentos, responde directamente"
                "\n- Si NO está en los documentos, indica claramente 'No encuentro esa información en tus documentos'"
                "\n- Para documentos grandes, se te proporciona contenido relevante basado en la pregunta"
                "\n- Responde de forma clara y estructurada"
                "\n- Usa párrafos cortos para WhatsApp (máximo 5-6 líneas)"
                "\n- Si es necesario, usa viñetas con emojis (• ✓ →)"
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
        
        # Guardar respuesta en historial
        conversaciones[phone_number].append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def get_help_message(self):
        """Mensaje de ayuda"""
        return (
            "🤖 *Intexta - Asistente Virtual*\n\n"
            "Puedo ayudarte a consultar información de tus documentos.\n\n"
            "*Comandos:*\n"
            "• /ayuda - Ver este mensaje\n"
            "• /reset - Reiniciar conversación\n\n"
            "Simplemente escribe tu pregunta y te responderé basándome en tus documentos."
        )
    
    def get_authentication_message(self):
        """Mensaje cuando el usuario no está autenticado"""
        return (
            "👋 ¡Hola! Bienvenido a Intexta.\n\n"
            "Para usar este servicio, necesitas:\n\n"
            "1️⃣ Registrarte en https://tu-dominio.com\n"
            "2️⃣ Vincular tu número de WhatsApp en tu perfil\n"
            "3️⃣ Subir tus documentos\n\n"
            "Una vez completado, podrás consultar tus documentos por WhatsApp. 📱"
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
