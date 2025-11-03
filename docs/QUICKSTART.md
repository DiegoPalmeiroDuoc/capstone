# 🚀 Guía Rápida de Inicio - Intexta

## ⚡ Inicio Rápido (5 minutos)

### 1️⃣ Instalación

```powershell
# Clonar repositorio
git clone https://github.com/DiegoPalmeiroDuoc/capstone.git
cd capstone/capstone

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

### 2️⃣ Configurar Firebase

1. **Descargar credenciales**: 
   - Ve a Firebase Console → Project Settings → Service Accounts
   - Click "Generate new private key"
   - Guarda el archivo en `cliente_web/` con el nombre exacto:
     `admin-doc-ia-firebase-adminsdk-fbsvc-82d2fcac61.json`

2. **Verificar conexión**:
```powershell
python start.py
# Selecciona opción 6 para verificar Firebase
```

### 3️⃣ Iniciar Sistema

#### Opción A: Usar el script de inicio
```powershell
python start.py
# Selecciona opción 5 para iniciar todo
```

#### Opción B: Iniciar manualmente

**Terminal 1 - Web Django:**
```powershell
cd cliente_web
python manage.py runserver
```

**Terminal 2 - Procesador:**
```powershell
python document_processor.py --mode listen
```

**Terminal 3 - Chatbot WhatsApp:**
```powershell
python intexta_chatbot.py
```

### 4️⃣ Probar el Sistema

1. **Accede a la web**: http://localhost:8000
2. **Regístrate** con tu email
3. **Verifica tu email** (revisa spam)
4. **Sube un documento** (PDF, DOCX, etc.)
5. **Espera** ~10 segundos (el procesador lo detecta automáticamente)
6. **Refresca** la página para ver el estado "Procesado"

---

## 📱 Configurar WhatsApp (Opcional)

### Para Desarrollo Local

1. **Instalar ngrok**:
```powershell
# Descargar de https://ngrok.com/download
ngrok http 5000
```

2. **Configurar Twilio**:
   - Ve a Twilio Console → WhatsApp Sandbox
   - Webhook URL: `https://TU-URL-NGROK.ngrok.io/webhook`
   - Método: POST

3. **Vincular número**:
   - Envía el código de activación al sandbox de Twilio
   - Ve a http://localhost:8000/perfil
   - Agrega tu número de WhatsApp

4. **Probar**:
   - Envía un mensaje por WhatsApp
   - El bot responderá con información de tus documentos

---

## 🔧 Comandos Útiles

### Procesador de Documentos

```powershell
# Procesar documentos pendientes (una vez)
python document_processor.py --mode process-pending

# Escuchar cambios continuamente
python document_processor.py --mode listen --interval 10

# Reprocesar un documento específico
python document_processor.py --mode reprocess --doc-id DOCUMENTO_ID
```

### ETL (Extracción de Texto)

```powershell
# Desde Google Drive
python etl.py --url "https://docs.google.com/document/d/..."

# Desde Firebase Storage
python etl.py --firebase-url "gs://bucket/path/archivo.pdf"

# Archivo local
python etl.py --local-file "ruta/archivo.pdf"
```

### Django

```powershell
cd cliente_web

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Shell interactiva
python manage.py shell
```

---

## 🎯 Flujo de Trabajo Típico

```
Usuario → Sube PDF → Firebase Storage (estado: pendiente)
                              ↓
                     Procesador detecta nuevo archivo
                              ↓
                      Descarga y extrae texto
                              ↓
                   Guarda en Firestore (estado: procesado)
                              ↓
          Usuario consulta por WhatsApp → Chatbot busca en Firestore
                              ↓
                    DeepSeek genera respuesta contextual
                              ↓
                      Usuario recibe respuesta por WhatsApp
```

---

## ❓ Solución Rápida de Problemas

### "No se puede conectar a Firebase"
```powershell
# Verificar que el archivo de credenciales existe
dir cliente_web\admin-doc-ia-firebase-adminsdk-fbsvc-82d2fcac61.json

# Si no existe, descargarlo de Firebase Console
```

### "Documento no se procesa"
```powershell
# Verificar que el procesador está corriendo
# Terminal debe mostrar: "🔄 Iniciando listener de documentos"

# Procesar manualmente
python document_processor.py --mode process-pending
```

### "Chatbot no responde"
```powershell
# Verificar que Flask está corriendo
# Debe mostrar: "🚀 Iniciando Intexta Chatbot en puerto 5000"

# Verificar webhook de Twilio
curl http://localhost:5000/health
```

### "Error al subir archivo"
- Verifica que el tamaño sea menor a 50MB
- Verifica que el formato sea soportado (PDF, DOCX, XLSX, PPTX)
- Revisa las reglas de Storage en Firebase Console

---

## 📊 Monitoreo

### Ver estado de documentos
```powershell
# En navegador
http://localhost:8000/dashboard

# Via API
curl "http://localhost:8000/api/docs/status/?uid=USER_ID"
```

### Ver logs

**Django:**
```powershell
# En la terminal donde corre manage.py
```

**Procesador:**
```powershell
# Muestra logs en tiempo real
python document_processor.py --mode listen
```

**Chatbot:**
```powershell
# Ver health check
curl http://localhost:5000/health
```

---

## 🌐 URLs Importantes

| Servicio | URL Local | Descripción |
|----------|-----------|-------------|
| Web Django | http://localhost:8000 | Aplicación principal |
| Admin Django | http://localhost:8000/admin | Panel de administración |
| Dashboard | http://localhost:8000/dashboard | Gestión de documentos |
| Chatbot Health | http://localhost:5000/health | Estado del chatbot |
| Chatbot Webhook | http://localhost:5000/webhook | Endpoint para Twilio |

---

## 📞 Soporte

¿Problemas? Revisa:
1. El README.md completo
2. Los logs en cada terminal
3. Firebase Console para errores
4. GitHub Issues: https://github.com/DiegoPalmeiroDuoc/capstone/issues

---

**¡Listo para empezar!** 🎉
