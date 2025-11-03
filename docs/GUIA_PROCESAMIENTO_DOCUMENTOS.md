# 📚 Guía: Procesamiento Automático de Documentos

## 🔄 Flujo Completo

```
┌─────────────────┐
│  1. Cliente Web │
│  Sube documento │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  2. Firebase Storage    │
│  Almacena archivo       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  3. Firestore Database  │
│  Registro:              │
│  - estado: "pendiente"  │
│  - url, nombre, etc.    │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  4. Document Processor  │
│  Detecta pendientes     │
│  (cada 30 segundos)     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  5. ETL Pipeline        │
│  Extrae texto del PDF   │
│  Procesa con IA         │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  6. Actualiza Firestore │
│  - estado: "procesado"  │
│  - contenido extraído   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  7. Dashboard actualiza │
│  Muestra en tiempo real │
└─────────────────────────┘
```

## 🚀 Pasos para Activar el Procesamiento

### **Paso 1: Iniciar el Servidor Web Django**

```powershell
# Terminal 1
cd "c:\Users\GiovannaNarayanaEspi\OneDrive - IBM\Escritorio\Proyecto_Capstone\capstone\cliente_web"
python manage.py runserver
```

**Resultado esperado:**
```
Starting development server at http://127.0.0.1:8000/
```

---

### **Paso 2: Iniciar el Document Processor (Modo Escucha)**

**Opción A - Con el Script (Recomendado):**
```powershell
# Terminal 2
cd "c:\Users\GiovannaNarayanaEspi\OneDrive - IBM\Escritorio\Proyecto_Capstone\capstone"
.\run_processor.bat
# Selecciona opción 1: Modo Escucha
```

**Opción B - Manual:**
```powershell
# Terminal 2
cd "c:\Users\GiovannaNarayanaEspi\OneDrive - IBM\Escritorio\Proyecto_Capstone\capstone"
python document_processor.py --mode listen --interval 30
```

**Resultado esperado:**
```
2025-11-02 23:00:00 [INFO] Firebase inicializado correctamente
2025-11-02 23:00:00 [INFO] Modo: listen - Intervalo: 30 segundos
2025-11-02 23:00:00 [INFO] Iniciando monitoreo de documentos pendientes...
2025-11-02 23:00:00 [INFO] Presiona Ctrl+C para detener
2025-11-02 23:00:01 [INFO] Buscando documentos pendientes...
2025-11-02 23:00:01 [INFO] Procesamiento completado: 0 documentos
```

---

### **Paso 3: Probar la Subida**

1. **Abre el navegador**: http://localhost:8000/login
2. **Inicia sesión** con tu cuenta Firebase
3. **Sube un documento**:
   - Formatos aceptados: PDF, DOCX, XLSX, PPTX, TXT
   - Tamaño máximo: 10MB
   - Agrega una descripción (opcional)
4. **Haz clic en "Subir documento"**

**Verás:**
- ✅ Barra de progreso
- ✅ Toast de confirmación
- ✅ Documento en la lista con estado "Pendiente"

---

### **Paso 4: Observar el Procesamiento**

**En el Terminal 2 (document_processor):**
```
2025-11-02 23:01:32 [INFO] Buscando documentos pendientes...
2025-11-02 23:01:32 [INFO] Documentos pendientes encontrados: 1
2025-11-02 23:01:32 [INFO] Procesando documento: mi_documento.pdf (doc123abc)
2025-11-02 23:01:33 [INFO] Descargando archivo desde Firebase Storage...
2025-11-02 23:01:34 [INFO] Extrayendo texto del PDF...
2025-11-02 23:01:35 [INFO] Documento procesado exitosamente
2025-11-02 23:01:35 [INFO] Estado actualizado a: procesado
2025-11-02 23:01:35 [INFO] Procesamiento completado: 1 documentos
```

**En el Dashboard (refresca automáticamente cada 30 segundos):**
- ✅ El contador "Pendientes" disminuye
- ✅ El contador "Procesados" aumenta
- ✅ El estado del documento cambia a "Procesado" ✔️
- ✅ Aparece el icono verde de éxito

---

## 🔧 Configuración del Intervalo

El processor revisa cada **30 segundos** por defecto. Puedes cambiar esto:

```powershell
# Revisar cada 10 segundos (más rápido)
python document_processor.py --mode listen --interval 10

# Revisar cada 60 segundos (más lento, menos recursos)
python document_processor.py --mode listen --interval 60
```

---

## 🐛 Solución de Problemas

### **1. El documento no se procesa**

**Verifica:**
```powershell
# ¿Está el processor corriendo?
# Deberías ver logs cada X segundos

# ¿Tiene estado "pendiente"?
# Revisa en Firebase Console
```

**Procesar manualmente:**
```powershell
python document_processor.py --mode process-pending
```

---

### **2. Error al subir archivo**

**Causas comunes:**
- ❌ Archivo muy grande (>10MB)
- ❌ Formato no soportado
- ❌ Usuario no autenticado
- ❌ Credenciales Firebase incorrectas

**Solución:**
1. Revisa la consola del navegador (F12)
2. Verifica el tamaño y formato del archivo
3. Recarga la página e inicia sesión nuevamente

---

### **3. Document Processor no encuentra archivos**

**Causas:**
- ❌ Firestore rules bloquean lectura
- ❌ Credenciales Firebase incorrectas
- ❌ El documento no tiene `estado: 'pendiente'`

**Verifica:**
```powershell
# Revisar credenciales
ls cliente_web/admin-doc-ia-firebase-adminsdk-fbsvc-82d2fcac61.json

# Probar consulta manual
python -c "from firebase_config import db; print(list(db.collection('documentos').where('estado', '==', 'pendiente').stream()))"
```

---

### **4. Error de permisos en Firebase**

**Firestore Rules mínimas necesarias:**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /documentos/{document} {
      // Usuarios autenticados pueden leer/escribir sus documentos
      allow read, write: if request.auth != null && 
                         request.auth.uid == resource.data.usuarioId;
      
      // El backend puede leer/escribir cualquier documento
      allow read, write: if request.auth.token.admin == true;
    }
  }
}
```

**Storage Rules:**
```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /clientes/{userId}/{allPaths=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

---

## 📊 Monitoreo en Tiempo Real

### **Ver logs del processor:**
```powershell
# Modo verbose (más detalles)
python document_processor.py --mode listen --interval 30 --verbose
```

### **Ver estadísticas en dashboard:**
- 📈 Total documentos
- ✅ Procesados
- ⏳ Pendientes
- ❌ Con errores

### **Actualización automática:**
El dashboard se refresca automáticamente cada **30 segundos**

---

## 🎯 Mejores Prácticas

### **Para Desarrollo:**
```powershell
# Intervalo corto para pruebas rápidas
python document_processor.py --mode listen --interval 5
```

### **Para Producción:**
```powershell
# Intervalo moderado para balance recursos/velocidad
python document_processor.py --mode listen --interval 30
```

### **Para Servidor Linux:**
```bash
# Crear servicio systemd
sudo nano /etc/systemd/system/intexta-processor.service
```

```ini
[Unit]
Description=Intexta Document Processor
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/capstone
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 document_processor.py --mode listen --interval 30
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Activar servicio
sudo systemctl enable intexta-processor
sudo systemctl start intexta-processor
sudo systemctl status intexta-processor
```

---

## 🔄 Reprocesar Documentos

Si un documento falló o necesitas reprocesarlo:

```powershell
# Opción 1: Con el script
.\run_processor.bat
# Selecciona opción 3: Reprocesar Documento
# Ingresa el ID del documento

# Opción 2: Manual
python document_processor.py --mode reprocess --doc-id ABC123XYZ
```

---

## 📝 Checklist de Inicio

Antes de usar el sistema en producción:

- [ ] ✅ Django server corriendo (puerto 8000)
- [ ] ✅ Document processor en modo listen
- [ ] ✅ Firebase credentials configuradas
- [ ] ✅ Firestore rules configuradas
- [ ] ✅ Storage rules configuradas
- [ ] ✅ Probado con documento de prueba
- [ ] ✅ Verificado estado cambia a "procesado"
- [ ] ✅ Logs sin errores

---

## 🎉 ¡Listo!

Ahora tu sistema procesará documentos automáticamente:

1. Cliente sube → Estado: "pendiente"
2. Processor detecta (cada 30s)
3. ETL procesa el archivo
4. Estado cambia a: "procesado"
5. Dashboard actualiza automáticamente

**¡El sistema está completamente automatizado!** 🚀
