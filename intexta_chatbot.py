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
    
    def build_context_from_documents(self, documentos, max_chars=8000):
        """
        Construye contexto para la IA a partir de los documentos del usuario.
        
        Args:
            documentos: Lista de documentos
            max_chars: Máximo de caracteres a incluir
        
        Returns:
            String con el contexto formateado
        """
        if not documentos:
            return "No hay documentos disponibles para consultar."
        
        context_parts = ["=== DOCUMENTOS DEL USUARIO ===\n"]
        total_chars = 0
        
        for doc in documentos:
            doc_header = f"\n--- {doc['nombre']} ---\n"
            doc_content = doc['contenido']
            
            # Calcular cuánto espacio queda
            available = max_chars - total_chars - len(doc_header)
            
            if available <= 0:
                break
            
            # Truncar contenido si es necesario
            if len(doc_content) > available:
                doc_content = doc_content[:available] + "\n[...contenido truncado...]"
            
            context_parts.append(doc_header)
            context_parts.append(doc_content)
            total_chars += len(doc_header) + len(doc_content)
        
        return "".join(context_parts)
    
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
            "max_tokens": 500
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
        
        # Construir contexto
        context = self.build_context_from_documents(documentos)
        
        # Construir mensajes para la IA
        system_prompt = {
            "role": "system",
            "content": (
                "Eres Intexta, un asistente virtual experto. "
                "Tu trabajo es responder preguntas basándote ÚNICAMENTE en los documentos del usuario. "
                "Responde de forma clara, concisa y profesional. "
                "Si la información no está en los documentos, indica que no tienes esa información. "
                "Mantén las respuestas en máximo 3-4 frases para WhatsApp."
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
