# Procfile para Railway, Render, Heroku
# Especifica cómo iniciar cada servicio

# Web Django (servicio principal)
web: cd cliente_web && gunicorn intexta_web.wsgi:application --bind 0.0.0.0:$PORT --workers 3

# Procesador de documentos (worker)
worker: python document_processor.py --mode listen --interval 30

# Chatbot WhatsApp (servicio separado)
chatbot: python intexta_chatbot.py
