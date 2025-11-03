# 📄 Document Processor - Guía de Uso

## 🎯 ¿Qué hace?

El `document_processor.py` es el **procesador automático de documentos** que:

1. **Escucha** cambios en Firestore
2. **Detecta** documentos con estado `pendiente`
3. **Descarga** archivos desde Firebase Storage
4. **Extrae** texto usando el ETL
5. **Actualiza** Firestore con el contenido procesado

---

## 🚀 Inicio Rápido

### Modo 1: Listener Continuo (RECOMENDADO)
Escucha continuamente nuevos documentos:

```bash
python document_processor.py --mode listen --interval 10
```

- `--interval 10`: Verifica cada 10 segundos (ajustable)
- Presiona `Ctrl+C` para detener

### Modo 2: Procesamiento Único
Procesa todos los pendientes una sola vez:

```bash
python document_processor.py --mode process-pending
```

### Modo 3: Reprocesar Documento Específico
Fuerza el reprocesamiento de un documento:

```bash
python document_processor.py --mode reprocess --doc-id ABC123
```

---

## 📊 Estados de Documentos

### Flujo de Estados

```
┌─────────────┐
│  PENDIENTE  │  ← Usuario sube documento
└──────┬──────┘
       │
       ↓ Processor detecta
┌─────────────┐
│ PROCESANDO  │  ← Extrayendo texto
└──────┬──────┘
       │
       ↓ Éxito / Error
┌─────────────┐     ┌─────────────┐
│  PROCESADO  │     │    ERROR    │
└─────────────┘     └─────────────┘
```

### Estados en Firestore

#### `pendiente`
- Documento recién subido
- Esperando procesamiento
- **Acción**: El processor lo detectará

#### `procesando`
- Actualmente en proceso
- Descargando y extrayendo texto
- **Acción**: Esperar finalización

#### `procesado`
- ✅ Texto extraído exitosamente
- Contenido guardado en Firestore
- Listo para usar en chatbot
- **Campos adicionales**:
  - `contenidoProcesado`: Texto completo
  - `caracteresTotales`: Longitud del texto
  - `fechaProcesado`: Timestamp

#### `error`
- ❌ Falló el procesamiento
- Ver `errorMensaje` para detalles
- **Campos adicionales**:
  - `errorMensaje`: Descripción del error
  - `fechaError`: Timestamp

---

## 🔧 Opciones de Línea de Comandos

```bash
python document_processor.py [opciones]
```

### Opciones disponibles

| Opción | Descripción | Ejemplo |
|--------|-------------|---------|
| `--mode listen` | Modo escucha continua | `--mode listen` |
| `--mode process-pending` | Procesar pendientes una vez | `--mode process-pending` |
| `--mode reprocess` | Reprocesar documento | `--mode reprocess` |
| `--interval N` | Intervalo en segundos (listen) | `--interval 30` |
| `--doc-id ID` | ID del documento (reprocess) | `--doc-id abc123` |
| `--help` | Mostrar ayuda | `--help` |

---

## 📝 Ejemplos de Uso

### Ejemplo 1: Desarrollo Local
Escucha rápida para testing:

```bash
python document_processor.py --mode listen --interval 5
```

### Ejemplo 2: Producción
Escucha con intervalo moderado:

```bash
python document_processor.py --mode listen --interval 30
```

### Ejemplo 3: Procesamiento Masivo
Procesar documentos acumulados:

```bash
python document_processor.py --mode process-pending
```

### Ejemplo 4: Fix de Error
Reprocesar un documento que falló:

```bash
python document_processor.py --mode reprocess --doc-id documento123
```

---

## 🔍 Logs y Monitoreo

### Niveles de Log

#### INFO (normal)
```
2025-11-02 22:34:57 [INFO] Firebase inicializado correctamente
2025-11-02 22:34:57 [INFO] 🔄 Iniciando listener de documentos (intervalo: 10s)
2025-11-02 22:35:10 [INFO] Procesando documento: archivo.pdf (ID: abc123)
2025-11-02 22:35:15 [INFO] ✅ Documento procesado exitosamente: archivo.pdf (15234 caracteres)
```

#### ERROR
```
2025-11-02 22:35:20 [ERROR] ❌ Error procesando documento abc123: No se pudo descargar
```

### Interpretar los Logs

- ✅ `Documento procesado exitosamente` = Todo OK
- 🔄 `Iniciando listener` = Procesador activo
- ❌ `Error procesando documento` = Ver detalles en Firestore

---

## ⚙️ Configuración

### Variables de Entorno (opcional)

```bash
# Suprimir warnings de gRPC
export GRPC_VERBOSITY=ERROR
export GLOG_minloglevel=2
```

### Archivo de Credenciales

El procesador busca credenciales en:
```
cliente_web/admin-doc-ia-firebase-adminsdk-fbsvc-82d2fcac61.json
```

Si está en otra ubicación:
```python
processor = DocumentProcessor(
    firebase_config_path="/ruta/al/archivo.json"
)
```

---

## 🐛 Solución de Problemas

### Error: "No se encontró archivo de credenciales Firebase"

**Causa**: Archivo de credenciales no encontrado

**Solución**:
```bash
# Verificar que existe
ls cliente_web/*.json

# O especificar ruta manualmente
python document_processor.py --config /ruta/credenciales.json
```

---

### Warning: "Detected filter using positional arguments"

**Causa**: Uso antiguo de `.where()` en Firestore

**Solución**: Ya corregido en versión actual usando `FieldFilter`

---

### Warning: "ALTS creds ignored"

**Causa**: Google Cloud detecta que no estás en GCP

**Solución**: Es solo un aviso, no afecta el funcionamiento. Ya está suprimido.

---

### Error: "Permission denied"

**Causa**: Credenciales sin permisos suficientes

**Solución**:
1. Verificar que el archivo JSON es el correcto
2. Verificar permisos en Firebase Console
3. Regenerar credenciales si es necesario

---

### Documentos no se procesan

**Diagnóstico**:
```bash
# Ver documentos pendientes en Firestore
# Firebase Console → Firestore → Colección "documentos"
# Filtrar por: estado == "pendiente"
```

**Posibles causas**:
1. No hay documentos pendientes
2. Error en ETL (ver logs)
3. Archivo no descargable desde Storage

---

## 🚀 Deployment

### Ejecutar en Servidor

#### Opción 1: Screen (Linux)
```bash
screen -S document-processor
python document_processor.py --mode listen --interval 30
# Ctrl+A, D para detach
```

#### Opción 2: systemd (Linux)
Crear `/etc/systemd/system/document-processor.service`:

```ini
[Unit]
Description=Intexta Document Processor
After=network.target

[Service]
Type=simple
User=usuario
WorkingDirectory=/path/to/capstone
ExecStart=/usr/bin/python3 document_processor.py --mode listen --interval 30
Restart=always

[Install]
WantedBy=multi-user.target
```

Activar:
```bash
sudo systemctl enable document-processor
sudo systemctl start document-processor
sudo systemctl status document-processor
```

#### Opción 3: PM2 (Node.js)
```bash
pm2 start document_processor.py --name doc-processor --interpreter python3 -- --mode listen --interval 30
pm2 save
pm2 startup
```

#### Opción 4: Windows Service (NSSM)
```powershell
# Descargar NSSM
# https://nssm.cc/download

nssm install DocumentProcessor "C:\Python\python.exe" "C:\path\to\document_processor.py --mode listen --interval 30"
nssm start DocumentProcessor
```

---

## 📊 Monitoreo en Producción

### Verificar que está corriendo

```bash
# Linux
ps aux | grep document_processor

# Windows
tasklist | findstr python
```

### Ver logs en tiempo real

```bash
# Si usas systemd
journalctl -u document-processor -f

# Si usas PM2
pm2 logs doc-processor

# Si usas screen
screen -r document-processor
```

### Estadísticas

Puedes agregar logging personalizado para métricas:

```python
# En el código
logging.info(f"📊 Estadísticas: {processed_count} procesados en {elapsed_time}s")
```

---

## 🔄 Integración con el Sistema

### Flujo Completo

```
Usuario → Django → Firebase Storage → Firestore (pendiente)
                                           ↓
                              Document Processor detecta
                                           ↓
                              Descarga y procesa (ETL)
                                           ↓
                         Firestore (procesado + contenido)
                                           ↓
                              Chatbot lee contenido
                                           ↓
                            Responde en WhatsApp
```

### Conexión con otros componentes

- **ETL** (`etl.py`): Extrae texto de archivos
- **Dashboard** (`dashboard.html`): Sube documentos
- **Chatbot** (`intexta_chatbot.py`): Lee documentos procesados
- **Firestore**: Base de datos compartida

---

## 📈 Optimizaciones

### Para gran volumen de documentos

```python
# Aumentar intervalo para ahorrar recursos
python document_processor.py --mode listen --interval 60
```

### Procesamiento por lotes

```python
# Procesar máximo N documentos por ciclo
# (modificar en el código)
for doc in docs[:10]:  # Limitar a 10 por ciclo
    process_document(doc)
```

### Multiprocessing

```python
# Para procesamiento paralelo (avanzado)
from multiprocessing import Pool

with Pool(4) as pool:
    pool.map(process_document, pending_docs)
```

---

## 🧪 Testing

### Test manual

1. Subir documento desde dashboard
2. Ver logs del processor
3. Verificar estado en Firestore
4. Confirmar contenido procesado

### Test automático

```python
# test_processor.py
from document_processor import DocumentProcessor

processor = DocumentProcessor()

# Test con documento de prueba
test_doc = {
    'nombre': 'test.pdf',
    'url': 'gs://bucket/test.pdf',
    'estado': 'pendiente'
}

result = processor.process_document('test_id', test_doc)
assert result == True
```

---

## 📚 Recursos

- [ETL Documentation](../etl.py)
- [Chatbot Integration](../intexta_chatbot.py)
- [Firebase Setup](../cliente_web/firebase_config.py)
- [Architecture](./ARCHITECTURE.md)

---

## 🔐 Seguridad

### Credenciales
- ✅ Nunca commitear archivo JSON de credenciales
- ✅ Usar `.gitignore` para excluir `*.json`
- ✅ Rotar credenciales periódicamente

### Firestore Rules
Asegurar que solo el service account pueda escribir estados:

```javascript
// firestore.rules
match /documentos/{docId} {
  allow read: if request.auth.uid == resource.data.usuarioId;
  allow write: if request.auth.uid == resource.data.usuarioId 
              || request.auth.token.admin == true;
}
```

---

## ✨ Características Implementadas

- ✅ Detección automática de documentos pendientes
- ✅ Descarga desde Firebase Storage
- ✅ Procesamiento con ETL multi-formato
- ✅ Actualización de estados en Firestore
- ✅ Manejo de errores robusto
- ✅ Logging detallado
- ✅ Múltiples modos de operación
- ✅ Supresión de warnings innecesarios

---

**Última actualización**: Noviembre 2025  
**Versión**: 2.0  
**Autor**: Equipo Intexta
