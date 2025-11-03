# 🚀 Guía de Configuración - Intexta

Esta guía te ayudará a configurar el proyecto Intexta después de clonarlo desde GitHub.

---

## ⚡ Inicio Rápido

```bash
# 1. Clonar repositorio
git clone https://github.com/DiegoPalmeiroDuoc/capstone.git
cd capstone

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar credenciales (ver abajo)
# 4. Iniciar sistema
iniciar_sistema.bat  # Windows
```

---

## 📋 Requisitos Previos

- **Python 3.13+**
- **Git**
- **Node.js + npm** (para Firebase CLI)
- **ngrok** (para túnel público de WhatsApp)

---

## 🔐 Configuración de Credenciales

### Paso 1: Crear archivo `.env`

```bash
# Copiar plantilla
cp .env.example .env

# O en Windows PowerShell:
copy .env.example .env
```

### Paso 2: Obtener DeepSeek API Key

1. Ve a https://platform.deepseek.com/api_keys
2. Crea una cuenta o inicia sesión
3. Genera una nueva API key
4. Copia la key

### Paso 3: Editar `.env`

Abre `.env` y llena con tus credenciales:

```env
# DeepSeek API
DEEPSEEK_API_KEY=sk-TU_API_KEY_AQUI

# Twilio (opcional para desarrollo)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### Paso 4: Obtener Credenciales de Firebase

#### Opción A: Proyecto Existente (Trabajo en Equipo)

Si trabajas con el equipo existente:

1. **Solicita al administrador del proyecto**:
   - Archivo: `admin-doc-ia-firebase-adminsdk-*.json`
   
2. **Guárdalo en**: `cliente_web/admin-doc-ia-firebase-adminsdk-*.json`

#### Opción B: Crear Tu Propio Proyecto Firebase

Si quieres tu propio proyecto para desarrollo:

1. **Ve a** https://console.firebase.google.com/
2. **Crear nuevo proyecto** → Nombrar (ej: "intexta-dev")
3. **Habilitar servicios**:
   - Authentication → Email/Password
   - Firestore Database → Modo producción
   - Storage → Modo producción

4. **Descargar credenciales**:
   - Project Settings → Service Accounts
   - Generate new private key
   - Guardar como: `cliente_web/admin-doc-ia-firebase-adminsdk-*.json`

5. **Configurar reglas de Firestore**:
   ```bash
   cd cliente_web
   firebase login
   firebase use --add  # Selecciona tu proyecto
   firebase deploy --only firestore:rules
   ```

6. **Actualizar config en templates** (si usas proyecto propio):
   - Editar `cliente_web/core/templates/login.html`
   - Editar `cliente_web/core/templates/dashboard.html`
   - Editar `cliente_web/core/templates/perfil.html`
   - Reemplazar `firebaseConfig` con tu configuración

---

## ✅ Verificar Configuración

### 1. Verificar que `.env` está ignorado

```bash
git status --ignored | grep .env
```

**Debe mostrar**: `.env` en la lista de ignorados

### 2. Verificar credenciales de Firebase

```bash
# Windows PowerShell
ls cliente_web/*firebase-adminsdk*.json

# Linux/Mac
ls cliente_web/*firebase-adminsdk*.json
```

**Debe mostrar**: El archivo JSON

### 3. Probar conexión

```bash
cd scripts_utilidad
python diagnostico_whatsapp.py
```

**Debe mostrar**: ✅ Firebase conectado correctamente

---

## 🚀 Iniciar el Sistema

### Opción 1: Script Automático (Recomendado - Windows)

```bash
iniciar_sistema.bat
```

Esto iniciará automáticamente:
- Django server (puerto 8000)
- Chatbot WhatsApp (puerto 5000)
- ngrok tunnel

### Opción 2: Inicio Manual

**Terminal 1 - Django**:
```bash
cd cliente_web
python manage.py runserver
```

**Terminal 2 - Chatbot**:
```bash
python intexta_chatbot.py
```

**Terminal 3 - ngrok** (solo para WhatsApp):
```bash
ngrok http 5000
```

---

## 📱 Configurar WhatsApp (Opcional)

### 1. Crear cuenta Twilio

1. Ve a https://www.twilio.com/try-twilio
2. Regístrate y verifica tu número

### 2. Activar WhatsApp Sandbox

1. En Twilio Console → Messaging → Try it out → Send a WhatsApp message
2. Envía el mensaje de activación desde tu WhatsApp al número sandbox

### 3. Configurar Webhook

1. Inicia ngrok: `ngrok http 5000`
2. Copia la URL (ej: `https://xxxxx.ngrok-free.app`)
3. En Twilio Console → WhatsApp Sandbox Settings
4. Pega: `https://xxxxx.ngrok-free.app/webhook`
5. Guarda

### 4. Agregar credenciales a `.env`

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxx  # Desde Twilio Console
TWILIO_AUTH_TOKEN=xxxxxxxxxx   # Desde Twilio Console
```

---

## 🧪 Probar el Sistema

### 1. Acceder a la web

```
http://localhost:8000/login
```

### 2. Registrar usuario

1. Haz clic en "Registrarse"
2. Ingresa email y contraseña
3. Verifica email (revisa bandeja de entrada)
4. Inicia sesión

### 3. Subir documento

1. En el dashboard, sube un archivo (PDF, DOCX, etc.)
2. Espera el procesamiento automático
3. Verifica que aparezca como "Procesado"

### 4. Vincular WhatsApp (opcional)

1. Ve a "Perfil"
2. Ingresa tu número de teléfono
3. Guarda

### 5. Probar chatbot (opcional)

1. Envía mensaje por WhatsApp al número sandbox
2. Consulta tus documentos

---

## 🔧 Solución de Problemas

### Error: "Firebase not connected"

**Causa**: Archivo de credenciales no encontrado

**Solución**:
```bash
# Verificar que existe
ls cliente_web/*firebase-adminsdk*.json

# Si no existe, descárgalo de Firebase Console
```

### Error: "DEEPSEEK_API_KEY no configurada"

**Causa**: API key no está en `.env`

**Solución**:
```bash
# Editar .env
notepad .env

# Agregar:
DEEPSEEK_API_KEY=sk-TU_KEY_AQUI
```

### Error: "Module not found"

**Causa**: Dependencias no instaladas

**Solución**:
```bash
pip install -r requirements.txt
```

### Error: "Port already in use"

**Causa**: Otro proceso usando el puerto

**Solución**:
```bash
# Windows - Matar proceso en puerto 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# O cambia el puerto
python manage.py runserver 8001
```

---

## 📚 Recursos Adicionales

- **README.md**: Documentación completa del proyecto
- **CREDENCIALES.md**: Guía detallada de credenciales
- **scripts_utilidad/README.md**: Documentación de scripts de diagnóstico
- **docs/**: Documentación técnica completa

---

## 🤝 Trabajo en Equipo

### Compartir Credenciales de Forma Segura

**NO hagas**:
- ❌ Enviar credenciales por email sin encriptar
- ❌ Compartir en chat público
- ❌ Hacer commit de archivos con credenciales

**SÍ haz**:
- ✅ Usar 1Password, LastPass o similar
- ✅ Enviar por email encriptado
- ✅ Compartir en persona
- ✅ Usar canales seguros del equipo

### Archivo a Compartir

Si trabajas en el mismo proyecto Firebase:

```
cliente_web/admin-doc-ia-firebase-adminsdk-fbsvc-82d2fcac61.json
```

El receptor debe guardarlo en la misma ubicación.

---

## ✅ Checklist de Configuración Completa

- [ ] Repositorio clonado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Archivo `.env` creado y configurado
- [ ] DeepSeek API Key agregada
- [ ] Credenciales Firebase descargadas y guardadas
- [ ] Conexión Firebase verificada (`python diagnostico_whatsapp.py`)
- [ ] Django server funciona (`python manage.py runserver`)
- [ ] Usuario registrado y verificado
- [ ] Documento subido y procesado
- [ ] (Opcional) Twilio configurado
- [ ] (Opcional) WhatsApp vinculado
- [ ] (Opcional) Chatbot probado

---

## 📞 Soporte

Si tienes problemas:

1. Revisa **CREDENCIALES.md** para más detalles
2. Ejecuta `python scripts_utilidad/diagnostico_whatsapp.py`
3. Revisa los logs del servidor
4. Contacta al equipo: gi.espinosa@duocuc.cl

---

**¡Listo! Ya puedes empezar a desarrollar con Intexta** 🚀
