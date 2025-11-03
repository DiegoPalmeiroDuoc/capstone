# 📄 Intexta - Sistema de Gestión Documental con IA

**Intexta** es una plataforma web integral para la gestión, procesamiento y consulta inteligente de documentos mediante inteligencia artificial. Permite a los usuarios subir documentos, procesarlos automáticamente con ETL, y consultarlos a través de un chatbot de WhatsApp.

---

## 🚀 Características Principales

### ✨ Gestión de Documentos
- **Subida de archivos**: PDF, DOCX, XLSX, PPTX, TXT, CSV
- **Procesamiento automático**: Extracción de texto con ETL
- **Almacenamiento seguro**: Firebase Storage + Firestore
- **Estados de procesamiento**: Pendiente → Procesando → Procesado/Error

### 🤖 Chatbot WhatsApp (Twilio)
- **Consulta por WhatsApp**: Accede a tus documentos desde cualquier lugar
- **IA conversacional**: Powered by DeepSeek API
- **Búsqueda contextual**: Respuestas basadas en el contenido de tus documentos
- **Autenticación por teléfono**: Sistema seguro de vinculación

### 🔐 Sistema de Autenticación
- **Firebase Authentication**: Login/registro seguro
- **Verificación de email**: Protección de cuentas
- **Gestión de perfiles**: Vinculación de WhatsApp

### 📊 Dashboard Moderno
- **UI/UX profesional**: Diseño responsivo y moderno
- **Gestión visual**: Ver, descargar y eliminar documentos
- **Métricas en tiempo real**: Estado de procesamiento

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.13**
- **Django 5.2.7**: Framework web principal
- **Flask 3.0.0**: Servidor del chatbot
- **Firebase Admin SDK**: Backend de Firebase

### Frontend
- **HTML5 + CSS3 + JavaScript (ES6+)**
- **Firebase SDK 9.22.2**: Autenticación y Firestore client-side

### Servicios Cloud
- **Firebase Authentication**: Gestión de usuarios
- **Cloud Firestore**: Base de datos NoSQL
- **Firebase Storage**: Almacenamiento de archivos
- **Twilio WhatsApp API**: Mensajería

### Librerías de Procesamiento
- **pdfplumber**: Extracción de PDF
- **python-docx**: Procesamiento de Word
- **openpyxl**: Lectura de Excel
- **python-pptx**: Procesamiento de PowerPoint
- **pandas**: Manipulación de datos

### IA
- **DeepSeek API**: Modelo de lenguaje para chatbot

---

## 📁 Estructura del Proyecto

```
capstone/
├── cliente_web/                    # Aplicación Django principal
│   ├── core/                       # App principal
│   │   ├── templates/              # Templates HTML
│   │   │   ├── login.html          # Autenticación
│   │   │   ├── dashboard.html      # Panel principal
│   │   │   ├── perfil.html         # Gestión de perfil
│   │   │   └── debug_logs.html     # Herramienta de debugging
│   │   ├── static/                 # CSS, JS, imágenes
│   │   └── views.py                # Vistas de Django
│   ├── intexta_web/                # Configuración del proyecto
│   │   ├── settings.py
│   │   └── urls.py
│   ├── firebase_config.py          # Configuración Firebase Admin
│   ├── manage.py                   # CLI de Django
│   └── admin-doc-ia-firebase-adminsdk-*.json  # Credenciales Firebase
├── intexta_chatbot.py              # Servidor del chatbot WhatsApp
├── etl.py                          # Sistema de procesamiento ETL
├── document_processor.py           # Procesador automático de documentos
├── requirements.txt                # Dependencias Python
├── scripts_utilidad/               # Scripts de mantenimiento
│   ├── diagnostico_whatsapp.py     # Diagnóstico del sistema
│   ├── sincronizar_usuarios.py     # Sync Firebase Auth → Firestore
│   ├── ver_documentos_usuarios.py  # Ver relación docs-usuarios
│   └── transferir_documentos.py    # Transferir docs entre usuarios
└── README.md                       # Este archivo
```

---

## ⚙️ Instalación y Configuración

### 1️⃣ Requisitos Previos

- **Python 3.13+**
- **Node.js + npm** (para Firebase CLI)
- **Cuenta de Firebase**
- **Cuenta de Twilio** (para WhatsApp)
- **API Key de DeepSeek**

### 2️⃣ Clonar el Repositorio

```bash
git clone https://github.com/DiegoPalmeiroDuoc/capstone.git
cd capstone
```

### 3️⃣ Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar Firebase

1. **Crear proyecto en Firebase Console**
2. **Habilitar servicios**:
   - Authentication (Email/Password)
   - Firestore Database
   - Storage
3. **Descargar credenciales**:
   - Ir a Project Settings → Service Accounts
   - Generar nueva clave privada
   - Guardar como `cliente_web/admin-doc-ia-firebase-adminsdk-*.json`

4. **Configurar Firebase en el frontend**:
   - Copiar tu `firebaseConfig` en los templates HTML

5. **Desplegar reglas de Firestore**:
```bash
cd cliente_web
firebase login
firebase use --add
firebase deploy --only firestore:rules
```

### 5️⃣ Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# DeepSeek API
DEEPSEEK_API_KEY=tu_api_key_aqui

# Twilio (opcional para producción)
TWILIO_ACCOUNT_SID=tu_account_sid
TWILIO_AUTH_TOKEN=tu_auth_token
TWILIO_WHATSAPP_NUMBER=+14155238886
```

### 6️⃣ Configurar Twilio WhatsApp

1. **Crear cuenta en Twilio**
2. **Activar WhatsApp Sandbox**:
   - Ir a Messaging → Try it out → Send a WhatsApp message
   - Enviar mensaje de activación desde tu WhatsApp
3. **Configurar Webhook**:
   - Iniciar ngrok: `ngrok http 5000`
   - Copiar URL de ngrok
   - Pegar en Twilio Sandbox Settings → "When a message comes in"
   - Agregar `/webhook` al final de la URL

---

## 🚀 Iniciar el Sistema

### Opción 1: Inicio Manual (Desarrollo)

Necesitas **3 terminales** abiertas:

#### Terminal 1: Servidor Django
```bash
cd cliente_web
python manage.py runserver
```
Acceder a: `http://localhost:8000`

#### Terminal 2: Chatbot WhatsApp
```bash
python intexta_chatbot.py
```
Servidor en: `http://localhost:5000`

#### Terminal 3: Túnel ngrok (para WhatsApp)
```bash
ngrok http 5000
```
Copiar URL pública y configurar en Twilio.

### Opción 2: Procesamiento Automático de Documentos

Para procesar documentos automáticamente cada cierto tiempo:

```bash
python document_processor.py --mode listen --interval 30
```

Esto procesará documentos pendientes cada 30 segundos.

---

## 📱 Uso del Sistema

### 1. Registro y Login
1. Ir a `http://localhost:8000/login`
2. Registrarse con email y contraseña
3. Verificar email (revisar bandeja de entrada)
4. Iniciar sesión

### 2. Subir Documentos
1. En el dashboard, hacer clic en "Subir archivo"
2. Seleccionar documento (PDF, DOCX, XLSX, PPTX, etc.)
3. Esperar procesamiento automático
4. Ver estado: Pendiente → Procesado

### 3. Vincular WhatsApp
1. Ir a "Perfil"
2. Ingresar número de teléfono (ej: `930104972`)
3. Guardar vinculación

### 4. Consultar por WhatsApp
1. Enviar mensaje al número de Twilio sandbox
2. Ejemplos de consultas:
   - "¿Cuántos documentos tengo?"
   - "Busca información sobre contratos"
   - "¿Qué dice mi último documento?"
   - "Muéstrame un resumen"

---

## 🔧 Scripts de Utilidad

### Diagnóstico del Sistema
```bash
cd scripts_utilidad
python diagnostico_whatsapp.py
```
Verifica: Firebase, usuarios, documentos, vinculación WhatsApp

### Ver Documentos y Usuarios
```bash
python ver_documentos_usuarios.py
```
Muestra la relación completa entre usuarios y sus documentos

### Sincronizar Usuarios
```bash
python sincronizar_usuarios.py
```
Sincroniza Firebase Auth → Firestore (útil si faltan usuarios en Firestore)

### Transferir Documentos
```bash
python transferir_documentos.py
```
Transfiere documentos de un usuario a otro

---

## 🐛 Debugging

### Ver Logs de Autenticación
Ir a: `http://localhost:8000/debug-logs/`

Esta página muestra logs en tiempo real del flujo de autenticación entre páginas.

### Verificar Procesamiento de Documentos
```bash
python check_documents.py
```

### Resetear Documentos con Error
```bash
python reset_errors.py
```

---

## 📊 Reglas de Firestore

Las reglas de seguridad están configuradas para:
- ✅ Usuarios solo pueden leer/escribir sus propios datos
- ✅ Documentos solo accesibles por su dueño
- ✅ Autenticación requerida para todas las operaciones

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /usuarios/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    match /documentos/{docId} {
      allow read: if request.auth != null && resource.data.usuarioId == request.auth.uid;
      allow write: if request.auth != null && request.resource.data.usuarioId == request.auth.uid;
    }
  }
}
```

---

## 🔐 Seguridad

- ✅ Autenticación Firebase con verificación de email
- ✅ Reglas de Firestore restrictivas
- ✅ Tokens de autenticación en cada request
- ✅ Validación de permisos en backend
- ✅ HTTPS obligatorio en producción

---

## 🤝 Contribuir

1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

---

## 📝 Licencia

Este proyecto es parte del Proyecto Capstone de DuocUC.

---

## 👥 Autores

- **Giovanna Narayana Espinosa** - Desarrollo principal
- **DiegoPalmeiroDuoc** - Repositorio

---

## 📞 Soporte

Para problemas o preguntas:
- 📧 Email: gi.espinosa@duocuc.cl
- 🐛 Issues: [GitHub Issues](https://github.com/DiegoPalmeiroDuoc/capstone/issues)

---

## 🎯 Roadmap

- [ ] Modo producción con Gunicorn/uWSGI
- [ ] Panel de administración
- [ ] Soporte para más formatos de archivo
- [ ] Análisis de sentimientos
- [ ] Exportación de conversaciones
- [ ] App móvil nativa

---

**¡Gracias por usar Intexta! 🚀**
