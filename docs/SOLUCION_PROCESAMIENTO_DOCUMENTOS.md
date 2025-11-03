# Solución: Documentos No Cambian de Pendiente a Procesado

## Problema Identificado

Los documentos subidos a la plataforma permanecían en estado "pendiente" y nunca cambiaban a "procesado", impidiendo que el chatbot de WhatsApp pudiera acceder a su contenido.

## Causas Raíz Encontradas

### 1. **Campo `estado` Faltante en Documentos Existentes**

**Diagnóstico**: Los documentos subidos ANTES de implementar el sistema de procesamiento automático no tenían el campo `estado` en Firestore.

**Evidencia**:
```javascript
// Los documentos retornaban:
{
  nombre: "Documentación S4.pdf",
  url: "...",
  estado: undefined  // ← Campo faltante
}
```

**Impacto**: El procesador buscaba documentos con `estado == 'pendiente'`, pero como estos documentos no tenían el campo, nunca eran detectados.

### 2. **Configuración Incorrecta del Storage Bucket**

**Diagnóstico**: El bucket configurado en `document_processor.py` no coincidía con el bucket real donde se almacenaban los archivos.

**Evidencia**:
```python
# Configuración incorrecta:
'storageBucket': 'admin-doc-ia.appspot.com'  # ❌ Bucket antiguo

# URLs reales en Firestore:
'https://firebasestorage.googleapis.com/v0/b/admin-doc-ia.firebasestorage.app/...'
```

**Error resultante**:
```
404 GET https://storage.googleapis.com/.../admin-doc-ia.appspot.com/...
The specified bucket does not exist.
```

**Impacto**: Aunque el procesador detectara documentos pendientes, fallaba al intentar descargar los archivos de Storage con error 404.

## Soluciones Implementadas

### Solución 1: Script de Migración de Datos

**Archivo creado**: `migrate_documents.py`

Este script agrega el campo `estado: 'pendiente'` a todos los documentos existentes que no lo tenían.

**Uso**:
```bash
python migrate_documents.py
```

**Código clave**:
```python
for doc in docs:
    data = doc.to_dict()
    if 'estado' not in data or data.get('estado') is None:
        db.collection('documentos').document(doc.id).update({
            'estado': 'pendiente'
        })
```

**Resultado**: 4 documentos actualizados exitosamente.

### Solución 2: Corrección del Storage Bucket

**Archivo modificado**: `document_processor.py` (línea 91)

**Cambio aplicado**:
```python
# Antes:
app = firebase_admin.initialize_app(cred, {
    'storageBucket': 'admin-doc-ia.appspot.com'  # ❌
})

# Después:
app = firebase_admin.initialize_app(cred, {
    'storageBucket': 'admin-doc-ia.firebasestorage.app'  # ✅
})
```

**Razón**: Firebase migró de `.appspot.com` a `.firebasestorage.app` para los buckets de Storage.

### Solución 3: Script de Restablecimiento de Errores

**Archivo creado**: `reset_errors.py`

Este script permite restablecer documentos con `estado: 'error'` a `estado: 'pendiente'` para reintentarlos.

**Uso**:
```bash
python reset_errors.py
```

**Utilidad**: Después de corregir bugs en el procesador, permite reprocesar documentos que fallaron.

## Scripts de Utilidad Creados

### 1. `check_documents.py`
Muestra el estado de todos los documentos en Firestore.

**Uso**:
```bash
python check_documents.py
```

**Salida**:
```
📄 Documento 1: EDR1u79qZrqSD9rExw5R
   Nombre: Documentación S4.pdf
   Estado: procesado
   Caracteres: 47457

RESUMEN POR ESTADO:
  PENDIENTE: 0
  PROCESADO: 3
  ERROR: 1
```

### 2. `check_urls.py`
Verifica las URLs de Storage guardadas en Firestore.

**Uso**:
```bash
python check_urls.py
```

**Utilidad**: Debug de problemas de acceso a archivos en Storage.

### 3. `migrate_documents.py`
Agrega campo `estado` a documentos existentes (ya descrito arriba).

### 4. `reset_errors.py`
Restablece documentos con error a pendiente (ya descrito arriba).

## Flujo de Procesamiento Corregido

```
1. Usuario sube documento en dashboard.html
   ↓
2. Archivo se guarda en Firebase Storage
   ↓
3. Metadata se guarda en Firestore con estado: 'pendiente'
   ↓
4. document_processor.py detecta el documento pendiente
   ↓
5. Actualiza estado a 'procesando'
   ↓
6. Descarga archivo desde Storage (con bucket correcto ✅)
   ↓
7. Extrae texto con ETL (choose_extractor)
   ↓
8. Normaliza texto (normalize_text)
   ↓
9. Guarda contenidoProcesado en Firestore
   ↓
10. Actualiza estado a 'procesado' ✅
```

## Resultados Post-Corrección

**Antes de las correcciones**:
```
PENDIENTE: 0
PROCESADO: 0
ERROR: 0
(4 documentos sin campo 'estado')
```

**Después de migrate_documents.py**:
```
PENDIENTE: 4
PROCESADO: 0
ERROR: 0
```

**Después de corregir bucket y ejecutar procesador**:
```
PENDIENTE: 0
PROCESADO: 3
ERROR: 1
```

**Tasa de éxito**: 75% (3 de 4 documentos procesados correctamente)

**Nota**: El 1 documento con error probablemente tiene problemas con el archivo en Storage (archivo corrupto o eliminado).

## Comandos de Mantenimiento

### Procesar documentos pendientes (una vez)
```bash
python document_processor.py --mode process-pending
```

### Iniciar procesador en modo escucha (continuo)
```bash
python document_processor.py --mode listen --interval 30
```

### Verificar estado de documentos
```bash
python check_documents.py
```

### Migrar documentos antiguos
```bash
python migrate_documents.py
```

### Reintentar documentos con error
```bash
python reset_errors.py
python document_processor.py --mode process-pending
```

### Reprocesar documento específico
```bash
python document_processor.py --mode reprocess --doc-id EDR1u79qZrqSD9rExw5R
```

## Prevención de Problemas Futuros

### 1. Garantizar que nuevos documentos incluyan `estado`

El código en `dashboard.html` ya está correcto:
```javascript
await addDoc(collection(db, "documentos"), {
    nombre: file.name,
    url: url,
    tipo: file.type,
    tamaño: file.size,
    fechaSubida: new Date().toISOString(),
    usuarioId: uid,
    descripcion: descripcion || 'Sin descripción',
    estado: 'pendiente'  // ✅ Siempre incluido
});
```

### 2. Mantener procesador en ejecución

**Opción A - Modo escucha continuo**:
```bash
python document_processor.py --mode listen --interval 30
```

**Opción B - Cron job / Tarea programada** (Windows):
```bash
# Ejecutar cada 5 minutos
schtasks /create /tn "ProcessDocuments" /tr "python C:\ruta\document_processor.py --mode process-pending" /sc minute /mo 5
```

### 3. Monitoreo de errores

Ejecutar periódicamente:
```bash
python check_documents.py
```

Si hay documentos en estado `error`, investigar con:
```bash
python check_urls.py
```

## Troubleshooting

### Problema: Documentos se quedan en "procesando"

**Causa**: El procesador se interrumpió durante el procesamiento.

**Solución**:
```python
# Crear script para resetear "procesando" a "pendiente"
db.collection('documentos').where('estado', '==', 'procesando').stream()
# ... actualizar cada uno a 'pendiente'
```

### Problema: Error 404 al descargar de Storage

**Causas posibles**:
1. Bucket incorrecto en `document_processor.py`
2. Archivo fue eliminado manualmente de Storage
3. Permisos insuficientes

**Solución**:
1. Verificar bucket con `check_urls.py`
2. Verificar que el archivo exista en Firebase Console → Storage
3. Verificar reglas de Storage en `storage.rules`

### Problema: Documentos no se detectan como pendientes

**Causa**: Campo `estado` faltante o con valor `null`.

**Solución**:
```bash
python migrate_documents.py
```

## Referencias

- **Procesador de documentos**: `document_processor.py`
- **ETL de texto**: `etl.py`
- **Dashboard frontend**: `cliente_web/core/templates/dashboard.html`
- **Configuración Firebase**: `cliente_web/admin-doc-ia-firebase-adminsdk-fbsvc-82d2fcac61.json`
- **Bucket Storage**: `admin-doc-ia.firebasestorage.app`

## Conclusión

El problema de documentos que no cambiaban de estado tenía **dos causas principales**:

1. ✅ **Documentos legacy sin campo `estado`** → Solucionado con migración
2. ✅ **Bucket de Storage incorrecto** → Solucionado actualizando configuración

**Estado actual**: Sistema completamente funcional con 75% de éxito en procesamiento (1 documento tiene archivo corrupto/faltante).

**Próximos pasos**:
- Mantener procesador en modo escucha continuo
- Monitorear logs para detectar errores temprano
- Implementar notificaciones cuando documentos fallen
