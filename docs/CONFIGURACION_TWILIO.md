# 📱 Guía Completa de Configuración de Twilio para WhatsApp

## 🎯 Resumen Rápido

Twilio permite conectar tu chatbot a WhatsApp para que los clientes puedan consultar sus documentos procesados directamente desde WhatsApp.

---

## 📋 Requisitos Previos

- ✅ Cuenta de Twilio (gratuita para desarrollo)
- ✅ Número de teléfono (para recibir mensajes de prueba)
- ✅ Chatbot funcionando (`intexta_chatbot.py`)
- ✅ ngrok instalado (para desarrollo local)

---

## 🚀 Paso 1: Crear Cuenta en Twilio

### 1.1 Registro

1. Ve a: **https://www.twilio.com/try-twilio**
2. Completa el formulario:
   - Nombre
   - Email
   - Contraseña
3. Verifica tu email
4. Verifica tu número de teléfono

### 1.2 Obtener Credenciales

Una vez dentro del dashboard de Twilio:

1. Ve a: **Console Dashboard** (https://console.twilio.com/)
2. Verás tu información:
   ```
   Account SID: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   Auth Token: [Click para revelar]
   ```
3. **¡IMPORTANTE!** Guarda estas credenciales de forma segura

**Ejemplo:**
```
Account SID: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Auth Token: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 🔧 Paso 2: Configurar WhatsApp Sandbox

Para desarrollo, Twilio ofrece un "Sandbox" de WhatsApp gratuito.

### 2.1 Activar WhatsApp Sandbox

1. En el dashboard de Twilio, ve a:
   ```
   Messaging → Try it out → Send a WhatsApp message
   ```
   
   O directo: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn

2. Verás instrucciones como:
   ```
   Join your sandbox by sending:
   join <código-único>
   
   To: +1 415 523 8886
   ```

3. **Desde tu WhatsApp personal:**
   - Agrega el número: **+1 415 523 8886**
   - Envía el mensaje: **join codigo-unico** (ejemplo: `join yellow-tiger`)

4. Recibirás confirmación:
   ```
   Twilio Sandbox: You are all set! 🎉
   ```

---

## 🌐 Paso 3: Configurar ngrok (Desarrollo Local)

### 3.1 Instalar ngrok

**Windows:**
```powershell
# Opción 1: Descargar desde
https://ngrok.com/download

# Opción 2: Con Chocolatey
choco install ngrok
```

**Verificar instalación:**
```powershell
ngrok version
```

### 3.2 Autenticar ngrok

1. Regístrate en: https://dashboard.ngrok.com/signup
2. Copia tu token de autenticación
3. Ejecuta:
   ```powershell
   ngrok config add-authtoken TU_TOKEN_AQUI
   ```

### 3.3 Iniciar túnel ngrok

1. **Primero, inicia el chatbot:**
   ```powershell
   cd capstone
   python intexta_chatbot.py
   ```
   
   Verás:
   ```
   * Running on http://127.0.0.1:5000
   ```

2. **En otra terminal, inicia ngrok:**
   ```powershell
   ngrok http 5000
   ```

3. **Copia la URL pública:**
   ```
   Forwarding: https://abc123.ngrok.io -> http://localhost:5000
   ```
   
   **URL importante:** `https://abc123.ngrok.io`

---

## 🔗 Paso 4: Configurar Webhook en Twilio

### 4.1 Configurar el Webhook

1. Ve a: **Messaging → Settings → WhatsApp Sandbox Settings**
   
   URL: https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox

2. En **"WHEN A MESSAGE COMES IN":**
   ```
   URL: https://abc123.ngrok.io/webhook
   Method: HTTP POST
   ```

3. Click **Save**

### 4.2 Verificar Configuración

El webhook correcto debe apuntar a:
```
https://tu-dominio-ngrok.ngrok.io/webhook
```

**NO olvides el `/webhook` al final!**

---

## 💻 Paso 5: Configurar Variables de Entorno (Opcional)

Aunque el chatbot actual no las requiere explícitamente, es buena práctica guardarlas.

### 5.1 Crear archivo `.env`

Crea un archivo `.env` en la carpeta `capstone`:

```bash
# Twilio WhatsApp
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# DeepSeek API
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Firebase
FIREBASE_CREDENTIALS_PATH=cliente_web/admin-doc-ia-firebase-adminsdk-fbsvc-82d2fcac61.json
```

### 5.2 Cargar variables en Python

Modifica `intexta_chatbot.py` para cargar el `.env`:

```python
# Al inicio del archivo
from dotenv import load_dotenv
load_dotenv()

# Luego usar:
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
```

---

## 🧪 Paso 6: Probar el Chatbot

### 6.1 Verificar que todo esté corriendo

**Terminal 1 - Django:**
```powershell
cd capstone\cliente_web
python manage.py runserver
```

**Terminal 2 - Document Processor:**
```powershell
cd capstone
python document_processor.py --mode listen --interval 30
```

**Terminal 3 - Chatbot:**
```powershell
cd capstone
python intexta_chatbot.py
```

**Terminal 4 - ngrok:**
```powershell
ngrok http 5000
```

### 6.2 Enviar mensaje de prueba

Desde tu WhatsApp, envía al número de Twilio:

```
Hola
```

**Respuesta esperada:**
```
¡Hola! 👋 Soy Intexta, tu asistente virtual.

¿En qué puedo ayudarte hoy?
- Consultar documentos
- Ver estado de procesamiento
- Ayuda

Escribe tu consulta o 'ayuda' para más opciones.
```

---

## 🔍 Paso 7: Debugging y Logs

### 7.1 Ver logs del chatbot

En la terminal donde corre `intexta_chatbot.py` verás:

```
23:45:12 [INFO] ✅ Firebase conectado correctamente
 * Running on http://127.0.0.1:5000
23:45:30 [INFO] 📥 Mensaje recibido de +56912345678: Hola
23:45:31 [INFO] 🤖 Respuesta enviada (120 caracteres)
```

### 7.2 Ver logs en Twilio Console

1. Ve a: **Monitor → Logs → Messaging**
   
   URL: https://console.twilio.com/us1/monitor/logs/sms

2. Verás todos los mensajes entrantes y salientes

### 7.3 Ver logs en ngrok

Abre en tu navegador:
```
http://localhost:4040
```

Verás todas las peticiones HTTP que pasan por ngrok.

---

## ⚙️ Configuración Avanzada

### Enviar mensajes desde Python (opcional)

Si quieres enviar mensajes proactivamente:

```python
from twilio.rest import Client

account_sid = 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
auth_token = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
client = Client(account_sid, auth_token)

message = client.messages.create(
    from_='whatsapp:+14155238886',
    body='Tu documento ha sido procesado! 📄✅',
    to='whatsapp:+56912345678'
)

print(f"Mensaje enviado: {message.sid}")
```

---

## 🚀 Paso 8: Despliegue en Producción

### 8.1 Para producción (servidor real)

En lugar de ngrok, necesitas:

1. **Servidor con IP pública o dominio:**
   - AWS, Google Cloud, Heroku, DigitalOcean, etc.

2. **Certificado SSL (HTTPS):**
   - Let's Encrypt (gratuito)
   - Cloudflare (gratuito)

3. **Webhook en Twilio apunta a:**
   ```
   https://tu-dominio.com/webhook
   ```

### 8.2 Actualizar cuenta de Twilio a producción

Para usar WhatsApp en producción (no sandbox):

1. Solicita aprobación de WhatsApp Business API
2. Configura un número de WhatsApp dedicado
3. Paga la tarifa de Twilio (varía por país)

---

## 📊 Diagrama de Flujo

```
┌─────────────────┐
│  Usuario envía  │
│  mensaje por    │
│  WhatsApp       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  WhatsApp →     │
│  Twilio         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Twilio envía   │
│  POST a webhook │
│  (ngrok)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ngrok túnel    │
│  → localhost    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Flask recibe   │
│  en /webhook    │
│  (chatbot.py)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Procesa msg    │
│  + consulta     │
│  Firebase       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  DeepSeek API   │
│  genera         │
│  respuesta      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Respuesta →    │
│  Twilio →       │
│  WhatsApp       │
└─────────────────┘
```

---

## 🐛 Solución de Problemas

### Problema 1: No recibo mensajes

**Verificar:**
```powershell
# ¿Está el chatbot corriendo?
# Deberías ver:
# * Running on http://127.0.0.1:5000

# ¿Está ngrok corriendo?
# Deberías ver:
# Forwarding https://abc123.ngrok.io -> http://localhost:5000

# ¿El webhook está configurado?
# Debe apuntar a: https://abc123.ngrok.io/webhook
```

### Problema 2: Error 404 en webhook

**Causa:** URL incorrecta en Twilio

**Solución:**
```
Correcto:   https://abc123.ngrok.io/webhook
Incorrecto: https://abc123.ngrok.io
Incorrecto: https://abc123.ngrok.io/
```

### Problema 3: Error 500 en chatbot

**Verificar logs:**
```powershell
# Ver terminal del chatbot
# Busca mensajes de error en rojo
```

**Causas comunes:**
- Firebase no conectado
- DeepSeek API key inválida
- Error en el código

### Problema 4: ngrok se desconecta

**Causa:** La sesión gratuita de ngrok expira cada 2 horas

**Solución:**
1. Reinicia ngrok
2. Copia la nueva URL
3. Actualiza el webhook en Twilio

---

## 📝 Checklist de Configuración

Antes de empezar a usar el chatbot:

- [ ] ✅ Cuenta de Twilio creada
- [ ] ✅ Account SID y Auth Token guardados
- [ ] ✅ WhatsApp Sandbox activado
- [ ] ✅ Número de WhatsApp unido al sandbox (mensaje "join codigo")
- [ ] ✅ ngrok instalado y autenticado
- [ ] ✅ Chatbot corriendo (puerto 5000)
- [ ] ✅ ngrok corriendo (túnel a puerto 5000)
- [ ] ✅ Webhook configurado en Twilio con URL de ngrok
- [ ] ✅ Firebase conectado correctamente
- [ ] ✅ Mensaje de prueba enviado y recibido

---

## 🎯 Resumen de URLs Importantes

| Servicio | URL |
|----------|-----|
| Twilio Console | https://console.twilio.com |
| WhatsApp Sandbox | https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn |
| Webhook Settings | https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox |
| Logs de Mensajes | https://console.twilio.com/us1/monitor/logs/sms |
| ngrok Dashboard | https://dashboard.ngrok.com |
| ngrok Inspector | http://localhost:4040 |

---

## 💡 Consejos Útiles

1. **Guarda la URL de ngrok:** Cada vez que reinicias ngrok, cambia la URL
2. **Actualiza el webhook:** Si cambias la URL de ngrok, actualiza en Twilio
3. **Logs son tu amigo:** Revisa logs en chatbot, Twilio y ngrok
4. **Prueba primero localmente:** Usa el endpoint `/test` antes del webhook real
5. **Respaldo de credenciales:** Guarda Account SID y Auth Token en lugar seguro

---

## 🎉 ¡Listo!

Con estos pasos, tu chatbot de WhatsApp debería estar funcionando perfectamente.

**Comandos rápidos para iniciar todo:**

```powershell
# Terminal 1
cd capstone\cliente_web
python manage.py runserver

# Terminal 2
cd capstone
python document_processor.py --mode listen --interval 30

# Terminal 3
cd capstone
python intexta_chatbot.py

# Terminal 4
ngrok http 5000
```

**Luego:**
1. Copia URL de ngrok
2. Pégala en Twilio webhook settings (agrega `/webhook` al final)
3. Envía "Hola" desde WhatsApp

**¡Disfruta tu chatbot!** 🚀📱
