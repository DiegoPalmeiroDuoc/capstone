# 🛠️ Comandos Útiles - Intexta

Referencia rápida de comandos para el desarrollo y operación de Intexta.

---

## 🚀 Inicio del Sistema

### Inicio Completo (Recomendado)
```powershell
python start.py
# Seleccionar opción 5
```

### Inicio Individual

**Web Django:**
```powershell
cd cliente_web
python manage.py runserver

# Con puerto específico
python manage.py runserver 0.0.0.0:8080
```

**Procesador:**
```powershell
# Modo automático (escucha continua)
python document_processor.py --mode listen --interval 10

# Procesar solo pendientes (una vez)
python document_processor.py --mode process-pending

# Reprocesar documento específico
python document_processor.py --mode reprocess --doc-id abc123xyz
```

**Chatbot:**
```powershell
python intexta_chatbot.py

# Con puerto específico
PORT=5001 python intexta_chatbot.py
```

---

## 📦 Gestión de Dependencias

### Instalación
```powershell
# Todas las dependencias
pip install -r requirements.txt

# Actualizar pip primero
python -m pip install --upgrade pip

# Instalar en modo desarrollo
pip install -r requirements.txt --upgrade
```

### Generar requirements.txt
```powershell
pip freeze > requirements.txt
```

### Verificar instalación
```powershell
pip list
```

---

## 🗄️ Django - Comandos

### Migraciones
```powershell
cd cliente_web

# Crear migraciones
python manage.py makemigrations

# Ver SQL de migraciones
python manage.py sqlmigrate core 0001

# Aplicar migraciones
python manage.py migrate

# Ver estado de migraciones
python manage.py showmigrations
```

### Base de Datos
```powershell
# Shell de Django
python manage.py shell

# Ejemplo en shell:
# >>> from firebase_config import db
# >>> docs = list(db.collection('documentos').stream())
# >>> len(docs)

# Crear superusuario
python manage.py createsuperuser
```

### Archivos Estáticos
```powershell
# Recolectar archivos estáticos
python manage.py collectstatic

# Limpiar archivos estáticos
python manage.py collectstatic --clear --noinput
```

### Testing
```powershell
# Ejecutar tests
python manage.py test

# Con verbosidad
python manage.py test --verbosity=2

# Test específico
python manage.py test core.tests.TestViews
```

---

## 📄 ETL - Extracción de Documentos

### Google Drive
```powershell
# Google Docs
python etl.py --url "https://docs.google.com/document/d/ABC123/edit"

# Google Sheets
python etl.py --url "https://docs.google.com/spreadsheets/d/XYZ789/edit"

# Google Slides
python etl.py --url "https://docs.google.com/presentation/d/DEF456/edit"

# Archivo de Drive
python etl.py --url "https://drive.google.com/file/d/GHI789/view"
```

### Firebase Storage
```powershell
# URL gs://
python etl.py --firebase-url "gs://admin-doc-ia.appspot.com/clientes/user123/archivo.pdf"

# URL HTTP pública
python etl.py --url "https://firebasestorage.googleapis.com/v0/b/admin-doc-ia.appspot.com/o/..."
```

### Archivos Locales
```powershell
# PDF
python etl.py --local-file "documentos/catalogo.pdf"

# Word
python etl.py --local-file "documentos/manual.docx"

# Excel
python etl.py --local-file "documentos/inventario.xlsx"

# PowerPoint
python etl.py --local-file "documentos/presentacion.pptx"

# Con salida específica
python etl.py --local-file "doc.pdf" --out "salida.txt"

# Modo silencioso
python etl.py --local-file "doc.pdf" --quiet
```

---

## 🔄 Procesador de Documentos

### Modos de Operación

**Escucha continua (Producción):**
```powershell
# Intervalo por defecto (10 segundos)
python document_processor.py --mode listen

# Intervalo personalizado (30 segundos)
python document_processor.py --mode listen --interval 30

# Intervalo largo (5 minutos = 300 segundos)
python document_processor.py --mode listen --interval 300
```

**Procesamiento único:**
```powershell
# Procesar todos los pendientes
python document_processor.py --mode process-pending

# Reprocesar documento específico
python document_processor.py --mode reprocess --doc-id abc123xyz
```

**Con configuración personalizada:**
```powershell
# Especificar archivo de credenciales
python document_processor.py --mode listen --firebase-config "path/to/creds.json"
```

---

## 💬 Chatbot WhatsApp

### Inicio
```powershell
# Puerto por defecto (5000)
python intexta_chatbot.py

# Puerto personalizado
$env:PORT=5001; python intexta_chatbot.py
```

### Testing Local con ngrok
```powershell
# Terminal 1: Iniciar chatbot
python intexta_chatbot.py

# Terminal 2: Iniciar ngrok
ngrok http 5000

# Copiar URL de ngrok y configurar en Twilio:
# https://abc123.ngrok.io/webhook
```

### Health Check
```powershell
# PowerShell
Invoke-WebRequest http://localhost:5000/health

# o con curl (si está instalado)
curl http://localhost:5000/health

# Respuesta esperada:
# {
#   "status": "ok",
#   "timestamp": "2025-11-02T...",
#   "firebase_connected": true,
#   "active_conversations": 5
# }
```

---

## 🔍 Testing y Debug

### Verificar Firebase
```powershell
python start.py
# Seleccionar opción 6

# O manualmente en Python:
python
>>> import sys
>>> sys.path.insert(0, 'cliente_web')
>>> from firebase_config import db, bucket
>>> list(db.collection('documentos').limit(5).stream())
```

### Ver Logs

**Django:**
```powershell
# Los logs aparecen en la consola donde corre manage.py
# Para guardar en archivo:
python manage.py runserver 2>&1 | Tee-Object -FilePath django.log
```

**Procesador:**
```powershell
# Logs en consola por defecto
python document_processor.py --mode listen 2>&1 | Tee-Object -FilePath processor.log
```

**Chatbot:**
```powershell
# Logs en consola por defecto
python intexta_chatbot.py 2>&1 | Tee-Object -FilePath chatbot.log
```

---

## 🌐 API Testing

### Con PowerShell (Invoke-WebRequest)

```powershell
# GET - Listar documentos
Invoke-WebRequest -Uri "http://localhost:8000/api/docs/?uid=USER_ID" -Method GET

# GET - Estado de documentos
Invoke-WebRequest -Uri "http://localhost:8000/api/docs/status/?uid=USER_ID" -Method GET

# POST - Procesar documento
$body = @{doc_id="abc123"} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/api/docs/process/" -Method POST -Body $body -ContentType "application/json"

# POST - Actualizar teléfono
$body = @{uid="USER_ID"; telefono="+56912345678"} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/api/user/update-phone/" -Method POST -Body $body -ContentType "application/json"

# POST - Disparar procesador
Invoke-WebRequest -Uri "http://localhost:8000/api/processor/trigger/" -Method POST

# GET - Buscar en documentos
Invoke-WebRequest -Uri "http://localhost:8000/api/docs/search/?uid=USER_ID&query=precio" -Method GET
```

### Con curl (si está instalado)

```bash
# Listar documentos
curl "http://localhost:8000/api/docs/?uid=USER_ID"

# Estado de documentos
curl "http://localhost:8000/api/docs/status/?uid=USER_ID"

# Procesar documento
curl -X POST http://localhost:8000/api/docs/process/ \
  -H "Content-Type: application/json" \
  -d '{"doc_id":"abc123"}'

# Buscar
curl "http://localhost:8000/api/docs/search/?uid=USER_ID&query=precio"
```

---

## 🧹 Limpieza y Mantenimiento

### Limpiar archivos temporales
```powershell
# Eliminar __pycache__
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# Eliminar .pyc
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force

# Limpiar todo
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
Get-ChildItem -Recurse -Filter "*.pyo" | Remove-Item -Force
```

### Reset de base de datos (desarrollo)
```powershell
cd cliente_web
Remove-Item db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

---

## 🔒 Seguridad

### Generar SECRET_KEY nueva (Django)
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Verificar variables de entorno
```powershell
# Ver todas
Get-ChildItem Env:

# Ver específica
$env:DEEPSEEK_API_KEY
```

---

## 🐛 Debugging

### Python Debugger (pdb)
```python
# Agregar en el código donde quieres parar:
import pdb; pdb.set_trace()

# Comandos útiles en pdb:
# n - siguiente línea
# s - step into
# c - continuar
# p variable - imprimir variable
# l - listar código alrededor
# q - quit
```

### Django Debug Toolbar (opcional)
```powershell
pip install django-debug-toolbar

# Agregar en settings.py INSTALLED_APPS:
# 'debug_toolbar',

# Agregar en urls.py:
# import debug_toolbar
# path('__debug__/', include(debug_toolbar.urls)),
```

---

## 📊 Monitoreo

### Ver procesos Python corriendo
```powershell
Get-Process | Where-Object {$_.ProcessName -eq "python"}
```

### Matar proceso específico
```powershell
Stop-Process -Name python -Force

# O por PID
Stop-Process -Id 1234
```

### Ver puertos en uso
```powershell
# Puerto 8000 (Django)
netstat -ano | findstr :8000

# Puerto 5000 (Chatbot)
netstat -ano | findstr :5000
```

---

## 🎓 Python Virtual Environment

### Crear
```powershell
python -m venv venv
```

### Activar
```powershell
# PowerShell
.\venv\Scripts\Activate.ps1

# CMD
.\venv\Scripts\activate.bat
```

### Desactivar
```powershell
deactivate
```

### Eliminar
```powershell
Remove-Item -Recurse -Force venv
```

---

## 📝 Git Commands (útiles)

```powershell
# Estado
git status

# Agregar archivos
git add .

# Commit
git commit -m "mensaje"

# Push
git push origin web_test

# Pull
git pull origin web_test

# Ver diferencias
git diff

# Ver historial
git log --oneline

# Crear rama
git checkout -b nueva-rama

# Cambiar rama
git checkout web_test

# Ver ramas
git branch -a
```

---

## 🔄 Actualización de Dependencias

```powershell
# Ver paquetes desactualizados
pip list --outdated

# Actualizar paquete específico
pip install --upgrade paquete

# Actualizar todo (cuidado!)
pip install --upgrade -r requirements.txt
```

---

## 💾 Backup

### Backup de Firestore (Firebase Console)
1. Ir a Firebase Console
2. Firestore Database
3. Import/Export
4. Export

### Backup local
```powershell
# Crear carpeta de backup
New-Item -ItemType Directory -Path "backup_$(Get-Date -Format 'yyyy-MM-dd')"

# Copiar archivos importantes
Copy-Item -Recurse cliente_web backup_*
Copy-Item *.py backup_*
Copy-Item requirements.txt backup_*
```

---

**Última actualización**: 2 de noviembre, 2025
