<div align="center">

# 📄 Intexta - Asistente Documental Inteligente

### *Tu biblioteca personal con IA en WhatsApp*

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://www.djangoproject.com/)
[![Firebase](https://img.shields.io/badge/Firebase-Admin_SDK-orange.svg)](https://firebase.google.com/)
[![DeepSeek](https://img.shields.io/badge/DeepSeek-AI-purple.svg)](https://www.deepseek.com/)
[![License](https://img.shields.io/badge/License-Capstone-red.svg)](LICENSE)

[Características](#-características-principales) • [Instalación](#-instalación-rápida) • [Uso](#-cómo-usar) • [Arquitectura](#-arquitectura-del-sistema) • [Contribuir](#-contribuir)

</div>

---

## 📖 Descripción

**Intexta** es una plataforma web completa para la gestión inteligente de documentos con consulta por WhatsApp. Sube tus archivos (PDF, Word, Excel, PowerPoint), déjalos procesar automáticamente, y luego consúltalos desde WhatsApp usando inteligencia artificial.

### ✨ ¿Qué hace especial a Intexta?

- 🤖 **Chatbot WhatsApp inteligente** con 7+ comandos interactivos
- 📚 **Procesamiento ETL automático** de múltiples formatos
- 🔍 **Búsqueda inteligente** con scoring por palabras clave (hasta 860k caracteres)
- 🔐 **Sistema de autenticación seguro** con Firebase
- 🎨 **UI/UX moderna** con diseño responsivo
- ⚡ **Respuestas optimizadas** directas, concisas y amigables

---

## 🚀 Características Principales

### 📁 Gestión de Documentos
- ✅ Formatos soportados: **PDF, DOCX, XLSX, PPTX, TXT, CSV**
- ✅ Procesamiento automático con **pipeline ETL**
- ✅ Almacenamiento en **Firebase Storage**
- ✅ Metadata en **Cloud Firestore**
- ✅ Estados: Pendiente → Procesando → Procesado/Error

### 🤖 Chatbot WhatsApp Inteligente
- ✅ **7+ comandos interactivos**: `/documentos`, `/resumen`, `/buscar`, `/ayuda`, `/reset`
- ✅ **IA conversacional** powered by DeepSeek API
- ✅ **Búsqueda contextual** con scoring de relevancia
- ✅ **Respuestas optimizadas**: directas (3-5 líneas), con emojis, estructuradas
- ✅ **Autenticación por teléfono** vinculado a Firebase
- ✅ **Contexto de 100k caracteres** (12.5x más que versiones anteriores)
- ✅ **Mensajes amigables** con sugerencias automáticas

### 🔐 Sistema de Autenticación
- ✅ Firebase Authentication (Email/Password)
- ✅ Verificación de email obligatoria
- ✅ Gestión de perfil con vinculación WhatsApp
- ✅ Reglas de seguridad Firestore/Storage

### 📊 Dashboard Web
- ✅ UI moderna con gradientes y animaciones
- ✅ Subida drag-and-drop de archivos
- ✅ Vista de documentos con estado en tiempo real
- ✅ Descarga y eliminación de documentos
- ✅ QR code para WhatsApp

---

## 🛠️ Stack Tecnológico

### Backend
```
Python 3.13
├── Django 5.2.7         # Framework web
├── Flask 3.0.0          # Servidor chatbot
├── Firebase Admin SDK   # Backend Firebase
├── python-dotenv 1.1.1  # Variables de entorno
└── Twilio SDK           # WhatsApp API
```

### Procesamiento de Documentos
```
ETL Pipeline
├── pdfplumber          # Extracción PDF
├── python-docx         # Procesamiento Word
├── openpyxl            # Lectura Excel
├── python-pptx         # Procesamiento PowerPoint
└── pandas              # Manipulación de datos
```

### Frontend
```
Modern Web Stack
├── HTML5 + CSS3 + JavaScript (ES6+)
├── Firebase SDK 9.22.2  # Auth + Firestore client
└── Font Awesome 6.4.0   # Iconos
```

### Servicios Cloud
```
Firebase + Twilio
├── Firebase Authentication
├── Cloud Firestore (NoSQL)
├── Firebase Storage
├── Twilio WhatsApp API
└── DeepSeek AI API
```

---

## 📁 Estructura del Proyecto

```
capstone/
│
├── 📱 cliente_web/                # Aplicación Django
│   ├── core/
│   │   ├── templates/
│   │   │   ├── index.html         # Landing page
│   │   │   ├── login.html         # Autenticación
│   │   │   ├── dashboard.html     # Panel principal
│   │   │   ├── perfil.html        # Gestión perfil + WhatsApp
│   │   │   └── home.html          # Página post-login
│   │   ├── static/
│   │   │   ├── css/
│   │   │   │   └── estilos.css    # Estilos principales
│   │   │   ├── js/
│   │   │   │   └── main.js        # Scripts frontend
│   │   │   └── img/               # Logos, QR WhatsApp
│   │   └── views.py               # Vistas Django
│   ├── intexta_web/
│   │   ├── settings.py            # Configuración Django
│   │   └── urls.py                # Rutas
│   ├── firebase_config.py         # Config Firebase Admin
│   ├── firestore.rules            # Reglas seguridad Firestore
│   ├── storage.rules              # Reglas seguridad Storage
│   └── manage.py                  # CLI Django
│
├── 🤖 intexta_chatbot.py          # Servidor chatbot WhatsApp (Flask)
├── ⚙️  etl.py                     # Pipeline ETL procesamiento
├── 📑 document_processor.py       # Procesador automático
│
├── 🔧 verificar_credenciales.py   # Verificar .env y credenciales
├── 🔧 analizar_limites_documentos.py  # Analizar tamaños documentos
│
├── 📂 scripts_utilidad/
│   ├── check_documents.py         # Verificar estado documentos
│   └── README.md
│
├── 📄 requirements.txt            # Dependencias Python
├── 📄 Procfile                    # Deploy Heroku
├── 📄 runtime.txt                 # Python version
├── 📄 .env.example                # Template variables
├── 📄 .gitignore
└── 📄 README.md                   # Este archivo
```

---

## ⚙️ Instalación Rápida

### 1️⃣ Prerrequisitos

- **Python 3.13+**
- **Firebase CLI** (opcional para deploy de reglas)
- **Cuenta Firebase** (gratuita)
- **Cuenta Twilio** (sandbox gratuito)
- **API Key DeepSeek** (gratuita con límites)

### 2️⃣ Clonar e Instalar

```bash
git clone https://github.com/DiegoPalmeiroDuoc/capstone.git
cd capstone

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3️⃣ Configurar Firebase

1. **Crear proyecto en [Firebase Console](https://console.firebase.google.com/)**

2. **Habilitar servicios**:
   - Authentication → Email/Password
   - Firestore Database → Modo producción
   - Storage → Configurar

3. **Descargar credenciales**:
   - Project Settings → Service Accounts → Generate new private key
   - Guardar como: `cliente_web/admin-doc-ia-firebase-adminsdk-*.json`

4. **Configurar frontend**:
   - Copiar `firebaseConfig` de Firebase Console
   - Pegar en templates: `login.html`, `dashboard.html`, `perfil.html`

5. **Desplegar reglas** (opcional):
   ```bash
   cd cliente_web
   firebase login
   firebase deploy --only firestore:rules,storage
   ```

### 4️⃣ Variables de Entorno

Crear archivo `.env` en la raíz:

```env
# DeepSeek API (REQUERIDO)
DEEPSEEK_API_KEY=sk-tu-api-key-aqui

# Twilio (opcional - usar sandbox)
TWILIO_ACCOUNT_SID=tu_account_sid
TWILIO_AUTH_TOKEN=tu_auth_token
TWILIO_WHATSAPP_NUMBER=+14155238886
```

**Verificar configuración**:
```bash
python verificar_credenciales.py
```

### 5️⃣ Configurar Twilio WhatsApp (Sandbox)

1. Ir a [Twilio Console](https://www.twilio.com/console)
2. Messaging → Try it out → Send a WhatsApp message
3. Desde tu WhatsApp, enviar: `join fence-wolf` al `+1 415 523 8886`
4. Configurar webhook:
   ```bash
   # Terminal 1: Iniciar chatbot
   python intexta_chatbot.py
   
   # Terminal 2: Iniciar ngrok
   ngrok http 5000
   ```
5. Copiar URL de ngrok (ej: `https://abc123.ngrok-free.app`)
6. En Twilio Sandbox Settings → When a message comes in:
   ```
   https://abc123.ngrok-free.app/webhook
   ```

---

## 🚀 Cómo Usar

### Iniciar el Sistema (3 terminales)

**Terminal 1 - Servidor Django**:
```bash
cd cliente_web
python manage.py runserver
# Abrir: http://localhost:8000
```

**Terminal 2 - Chatbot WhatsApp**:
```bash
python intexta_chatbot.py
# Servidor: http://localhost:5000
```

**Terminal 3 - Túnel ngrok**:
```bash
ngrok http 5000
# Copiar URL pública → Configurar en Twilio
```

### Flujo de Uso Completo

#### 1. Registro y Login
1. Ir a `http://localhost:8000/login`
2. Crear cuenta con email/contraseña
3. Verificar email (revisar bandeja)
4. Iniciar sesión

#### 2. Subir Documentos
1. Dashboard → "Subir archivo"
2. Seleccionar PDF, Word, Excel, etc.
3. Esperar procesamiento (aparece en lista)

4. Estado cambia: Pendiente → Procesado

#### 3. Vincular WhatsApp
1. Perfil → Ingresar número (ej: `930104972`)
2. Seleccionar código país (ej: `+56` para Chile)
3. Guardar número
4. **Activar sandbox Twilio**: Enviar `join fence-wolf` al `+1 415 523 8886`

#### 4. Consultar por WhatsApp

**Comandos disponibles**:
```
/ayuda, ayuda, help, menu, ?
  → Ver menú interactivo con todos los comandos

/documentos, documentos, lista
  → Ver lista formateada de documentos con emojis y tamaños

/resumen
  → Resumen inteligente de documentos

/buscar [tema]
  → Buscar información sobre un tema específico
  Ejemplo: /buscar matrimonio

/reset, reset, reiniciar, limpiar
  → Reiniciar conversación
```

**Ejemplos de preguntas**:
```
� "¿Qué dice sobre el matrimonio?"
💬 "¿Cuántos documentos tengo?"
💬 "Busca información sobre contratos"
💬 "Dame un resumen de mis archivos"
💬 "¿Qué temas cubre mi PDF?"
```

**Características del chatbot**:
- ✅ Respuestas directas sin introducciones innecesarias
- ✅ Formato conciso (3-5 líneas) ideal para WhatsApp
- ✅ Emojis relevantes para mejor legibilidad
- ✅ Sugerencias automáticas cuando no encuentra información
- ✅ Búsqueda inteligente con scoring por palabras clave
- ✅ Contexto de hasta 100,000 caracteres
- ✅ Soporte para documentos grandes (860k+ caracteres)

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                         USUARIO                              │
└───────────────┬─────────────────────────────┬────────────────┘
                │                             │
        ┌───────▼───────┐            ┌────────▼────────┐
        │  Navegador    │            │   WhatsApp      │
        │  Web Client   │            │   (Twilio)      │
        └───────┬───────┘            └────────┬────────┘
                │                             │
        ┌───────▼───────────────────┐ ┌───────▼────────┐
        │   Django Server           │ │ Flask Chatbot  │
        │   (puerto 8000)           │ │ (puerto 5000)  │
        │   • Autenticación         │ │ • Webhook      │
        │   • Subida archivos       │ │ • IA (DeepSeek)│
        │   • Dashboard             │ │ • Comandos     │
        └───────┬───────────────────┘ └───────┬────────┘
                │                             │
        ┌───────▼─────────────────────────────▼────────┐
        │            Firebase Services                  │
        │  • Authentication (Email/Password)            │
        │  • Firestore (usuarios, documentos)           │
        │  • Storage (archivos originales)              │
        └───────────────────────┬──────────────────────┘
                                │
                        ┌───────▼───────┐
                        │   ETL Pipeline│
                        │   • Extracción│
                        │   • Limpieza  │
                        │   • Metadata  │
                        └───────────────┘
```

### Flujo de Procesamiento de Documentos

```
Usuario sube archivo
         ↓
Firebase Storage (archivo original)
         ↓
Firestore (metadata: estado="pendiente")
         ↓
ETL Pipeline detecta documento pendiente
         ↓
Descarga archivo de Storage
         ↓
Procesa según tipo (PDF/DOCX/XLSX/PPTX)
         ↓
Extrae texto limpio
         ↓
Guarda en Firestore (contenidoProcesado, estado="procesado")
         ↓
Usuario consulta por WhatsApp
         ↓
Chatbot busca en contenidoProcesado
         ↓
IA genera respuesta contextual
         ↓
Respuesta enviada por WhatsApp
```

---

## 🔧 Herramientas de Diagnóstico

### Verificar Credenciales
```bash
python verificar_credenciales.py
```
Muestra:
- ✅/❌ DEEPSEEK_API_KEY
- ✅/❌ Firebase credenciales
- ⚠️ Twilio (opcional)

### Analizar Límites de Documentos
```bash
python analizar_limites_documentos.py
```
Muestra:
- Tamaño de cada documento procesado
- Comparación con límites del sistema
- Recomendaciones de optimización
- Estimación de tokens para IA

### Verificar Estado de Documentos
```bash
cd scripts_utilidad
python check_documents.py
```
Lista todos los documentos con:
- Estado (pendiente/procesando/procesado/error)
- Tamaño del contenido
- Usuario propietario

---

## 🔐 Seguridad y Reglas

### Firestore Rules (`firestore.rules`)
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Usuarios: solo acceso propio
    match /usuarios/{userId} {
      allow read, write: if request.auth != null && 
                            request.auth.uid == userId;
    }
    
    // Documentos: solo lectura/escritura propietario
    match /documentos/{docId} {
      allow read: if request.auth != null && 
                     resource.data.usuarioId == request.auth.uid;
      
      allow create, update: if request.auth != null && 
                              request.resource.data.usuarioId == request.auth.uid;
      
      allow delete: if request.auth != null && 
                       resource.data.usuarioId == request.auth.uid;
    }
  }
}
```

### Storage Rules (`storage.rules`)
```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /clientes/{userId}/{allPaths=**} {
      allow read, write, delete: if request.auth != null && 
                                     request.auth.uid == userId;
    }
  }
}
```

**Desplegar reglas**:
```bash
cd cliente_web
firebase deploy --only firestore:rules,storage
```

---

## 🐛 Troubleshooting

### Problema: Chatbot no responde por WhatsApp
**Solución**:
1. Verificar que `intexta_chatbot.py` esté corriendo
2. Verificar que ngrok esté activo y URL configurada en Twilio
3. Verificar logs del chatbot: buscar errores HTTP 502/404
4. Revisar que el número esté vinculado en Firestore

### Problema: Documentos no se procesan
**Solución**:
1. Verificar estado en Firestore (debe ser "pendiente")
2. Ejecutar manualmente:
   ```bash
   python document_processor.py --mode once
   ```
3. Revisar logs de ETL para errores de procesamiento
4. Verificar formato del archivo soportado

### Problema: Error al subir archivos
**Solución**:
1. Verificar reglas de Storage desplegadas
2. Verificar autenticación Firebase en frontend
3. Revisar consola del navegador (F12) para errores JS
4. Verificar tamaño del archivo (límite: 10MB)

### Problema: "No encuentro información" en chatbot
**Solución**:
1. Verificar que el documento esté procesado (estado="procesado")
2. Reformular pregunta con otras palabras
3. Usar comando `/buscar [tema]` para búsqueda dirigida
4. Verificar que `contenidoProcesado` no esté vacío en Firestore

### Problema: DeepSeek API timeout
**Solución**:
1. Hacer preguntas más específicas (reduce contexto)
2. Verificar API key válida en `.env`
3. Aumentar timeout en `intexta_chatbot.py` si es necesario
4. Usar búsqueda inteligente automática (ya implementada)

---

## 📊 Métricas y Límites

| Componente | Límite | Valor Actual |
|------------|--------|--------------|
| Contexto IA | 256k chars (DeepSeek) | 100k chars |
| Tokens respuesta | Variable | 1,000 tokens |
| Búsqueda inteligente | N/A | Top 50 párrafos |
| Documento máximo procesado | N/A | 860k chars (La Familia y el Matrimonio.pdf) |
| Formatos soportados | N/A | PDF, DOCX, XLSX, PPTX, TXT, CSV |
| Usuarios simultáneos | Firebase free | Unlimited |

---

## � Deploy a Producción

### Heroku

1. **Preparar app**:
   ```bash
   heroku login
   heroku create intexta-app
   ```

2. **Configurar variables**:
   ```bash
   heroku config:set DEEPSEEK_API_KEY=tu_key
   heroku config:set TWILIO_ACCOUNT_SID=tu_sid
   # etc...
   ```

3. **Desplegar**:
   ```bash
   git push heroku main
   ```

4. **Configurar webhook Twilio**:
   - URL: `https://intexta-app.herokuapp.com/webhook`

### Consideraciones de Producción

- ✅ Usar **Gunicorn** o **uWSGI** en lugar de Django dev server
- ✅ Configurar **ALLOWED_HOSTS** en `settings.py`
- ✅ Habilitar **DEBUG=False**
- ✅ Usar **PostgreSQL** en lugar de SQLite (si usas base de datos local)
- ✅ Configurar **HTTPS** obligatorio
- ✅ Implementar **rate limiting** para API
- ✅ Monitoreo con **Sentry** o **New Relic**
- ✅ Backups automáticos de Firestore

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Sigue estos pasos:

1. **Fork** el repositorio
2. **Crea rama** feature:
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
3. **Commit** cambios:
   ```bash
   git commit -m 'feat: Agrega nueva funcionalidad'
   ```
4. **Push** a la rama:
   ```bash
   git push origin feature/nueva-funcionalidad
   ```
5. **Abre Pull Request** en GitHub

### Convenciones de Código

- **Python**: PEP 8
- **JavaScript**: ES6+
- **Commits**: Conventional Commits
- **Documentación**: Docstrings en funciones

---

## 📝 Changelog

### v2.0.0 (2025-11-07) - Limpieza y Optimización
- 🗑️ Eliminados 47 archivos obsoletos (12,721 líneas)
- ✨ UX del chatbot completamente optimizada
- 🎨 Mejoras visuales en perfil.html (QR WhatsApp centrado)
- 📚 README actualizado con documentación completa
- 🔧 Fix: Comando `/resumen` error 502 corregido

### v1.5.0 (2025-11-06) - UX Chatbot
- ✨ 7+ comandos interactivos (antes: 2)
- 🤖 Prompt IA optimizado para respuestas directas
- 💬 Mensajes amigables con emojis
- 🔍 Auto-enriquecimiento de respuestas
- 📋 Comando `/documentos` con lista formateada

### v1.4.0 (2025-11-05) - Búsqueda Inteligente
- 🔍 Algoritmo de scoring por palabras clave
- 📈 Contexto aumentado a 100k caracteres
- 🎯 Soporte para documentos grandes (860k+ chars)
- ⚡ Top 50 párrafos más relevantes

### v1.3.0 (2025-11-04) - Correcciones Permisos
- 🔐 Fix: Reglas Firestore delete separadas
- 🔐 Fix: Storage rules con delete explícito
- ✅ Deploy exitoso de reglas

### v1.0.0 (2025-11-01) - Lanzamiento Inicial
- 🎉 Sistema completo funcional
- 🤖 Chatbot WhatsApp con IA
- 📄 Procesamiento ETL de documentos
- 🔐 Autenticación Firebase

---

## � Licencia

Este proyecto es parte del **Proyecto Capstone** de **DuocUC**.  
Todos los derechos reservados © 2025

---

## 👥 Autores

<div align="center">

### Giovanna Narayana Espinosa
**Desarrolladora Principal**

📧 [gi.espinosa@duocuc.cl](mailto:gi.espinosa@duocuc.cl)

---

### Diego Palmeiro
**Repositorio y Colaboración**

🔗 [GitHub: @DiegoPalmeiroDuoc](https://github.com/DiegoPalmeiroDuoc)

</div>

---

## 📞 Soporte

¿Necesitas ayuda? Contáctanos:

- 📧 **Email**: gi.espinosa@duocuc.cl
- 🐛 **Issues**: [GitHub Issues](https://github.com/DiegoPalmeiroDuoc/capstone/issues)
- 📚 **Documentación**: Este README
- 💬 **WhatsApp**: Prueba el chatbot en acción!

---

## 🎯 Roadmap Futuro

### v3.0 - En Planificación
- [ ] Panel de administración completo
- [ ] Estadísticas de uso y analytics
- [ ] Soporte para más formatos (audio, video)
- [ ] OCR para imágenes y PDFs escaneados
- [ ] Exportación de conversaciones
- [ ] Modo offline con sincronización

### v3.5 - Ideas
- [ ] App móvil nativa (React Native)
- [ ] Integración con Google Drive/Dropbox
- [ ] Análisis de sentimientos
- [ ] Resúmenes automáticos periódicos
- [ ] Chatbot en Telegram/Discord
- [ ] API pública para desarrolladores

---

<div align="center">

### ⭐ Si te gusta Intexta, ¡dale una estrella en GitHub! ⭐

**Hecho con ❤️ en Chile 🇨🇱**

[Inicio](#-intexta---asistente-documental-inteligente) • [Instalación](#-instalación-rápida) • [Uso](#-cómo-usar) • [Contribuir](#-contribuir)

---

**© 2025 Intexta - Proyecto Capstone DuocUC**

</div>
