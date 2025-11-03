# 🔧 Solución: Error de Permisos al Eliminar Documentos

## 🐛 Error Encontrado

```
FirebaseError: Missing or insufficient permissions.
```

### Contexto del Error

Al intentar eliminar un documento desde el dashboard, se producían **3 errores**:

1. **Missing or insufficient permissions** (Firestore)
2. **Object does not exist** (Storage) - storage/object-not-found
3. **400 Bad Request** (WebSocket de Firestore)

---

## 🔍 Análisis del Problema

### Error 1: Permisos Insuficientes en Firestore

**Reglas Antiguas** (incorrectas):
```javascript
match /documentos/{docId} {
  allow read: if request.auth != null && resource.data.usuarioId == request.auth.uid;
  allow write: if request.auth != null && request.resource.data.usuarioId == request.auth.uid;
}
```

**Problema**: 
- `allow write` incluye: `create`, `update`, y `delete`
- En operaciones `delete`, `request.resource.data` es **NULL**
- Por lo tanto, la condición `request.resource.data.usuarioId == request.auth.uid` **FALLA**
- Resultado: No se puede eliminar documentos ❌

### Error 2: Archivo No Existe en Storage

**Causa**:
```
storage/object-not-found: 'clientes/99IIKbpCqYRVRxCKMjCGitUJ8j32/1762142911660_Guia_Completado_Tabla_Migracion_SAP_v1.0.docx'
```

- El archivo fue eliminado previamente
- O nunca se subió correctamente
- O la ruta cambió

**Estado**: Ya manejado con `try-catch` en el código ✅

### Error 3: WebSocket Terminada

**Causa**: Consecuencia de los errores anteriores.

---

## ✅ Solución Implementada

### 1. Actualización de Reglas de Firestore

**Archivo**: `cliente_web/firestore.rules`

```javascript
match /documentos/{docId} {
  allow read: if request.auth != null && resource.data.usuarioId == request.auth.uid;
  
  // Separar create/update de delete
  allow create, update: if request.auth != null && request.resource.data.usuarioId == request.auth.uid;
  
  // Permitir delete usando resource.data (el documento existente)
  allow delete: if request.auth != null && resource.data.usuarioId == request.auth.uid;
}
```

**Diferencias clave**:
- ✅ `create, update`: Usan `request.resource.data` (datos nuevos)
- ✅ `delete`: Usa `resource.data` (datos existentes antes de eliminar)

### 2. Actualización de Reglas de Storage

**Archivo**: `cliente_web/storage.rules`

```javascript
service firebase.storage {
  match /b/{bucket}/o {
    // Permitir a usuarios autenticados leer/escribir/eliminar solo en su carpeta
    match /clientes/{userId}/{allPaths=**} {
      allow read, write, delete: if request.auth != null && request.auth.uid == userId;
    }
    
    // Denegar todo lo demás
    match /{allPaths=**} {
      allow read, write: if false;
    }
  }
}
```

**Mejoras**:
- ✅ Agregado `delete` explícitamente
- ✅ Validación de `userId` en la ruta
- ✅ Solo el dueño puede eliminar sus archivos

### 3. Despliegue de Reglas

```bash
cd cliente_web
firebase deploy --only firestore:rules
firebase deploy --only storage
```

**Resultado**:
```
✅ firestore: released rules firestore.rules to cloud.firestore
✅ storage: released rules storage.rules to firebase.storage
```

---

## 🧪 Cómo Probar la Solución

### 1. Recargar el Dashboard

```
http://localhost:8000/dashboard
```

### 2. Intentar Eliminar un Documento

1. Click en "Eliminar" en cualquier documento
2. Confirmar la eliminación

**Resultado Esperado**:
- ✅ Si el archivo existe en Storage: Se elimina
- ✅ Si el archivo NO existe: Se muestra warning pero continúa
- ✅ Documento eliminado de Firestore
- ✅ Toast de éxito: "Documento eliminado exitosamente"

### 3. Verificar en Firebase Console

- Firestore: El documento debe desaparecer de la colección `documentos`
- Storage: El archivo debe desaparecer de la carpeta `clientes/{userId}/`

---

## 📚 Conceptos Importantes de Firebase

### `resource.data` vs `request.resource.data`

| Operación | `resource.data` | `request.resource.data` |
|-----------|-----------------|-------------------------|
| **create** | `null` (no existe aún) | Datos del nuevo documento |
| **update** | Datos actuales | Datos después del update |
| **delete** | Datos antes de eliminar | `null` (no habrá datos) |
| **read** | Datos del documento | No aplica |

### Estructura de Permisos Correcta

```javascript
// ❌ INCORRECTO
allow write: if request.resource.data.userId == request.auth.uid;

// ✅ CORRECTO
allow create, update: if request.resource.data.userId == request.auth.uid;
allow delete: if resource.data.userId == request.auth.uid;
```

---

## 🔐 Seguridad

Las nuevas reglas mantienen la seguridad:

- ✅ Solo usuarios autenticados pueden operar
- ✅ Solo el dueño puede leer sus documentos
- ✅ Solo el dueño puede crear documentos en su nombre
- ✅ Solo el dueño puede actualizar sus documentos
- ✅ Solo el dueño puede eliminar sus documentos
- ✅ Validación en Firestore Y Storage

---

## 📋 Checklist Post-Solución

- [x] Reglas de Firestore actualizadas
- [x] Reglas de Storage actualizadas
- [x] Reglas desplegadas en Firebase
- [x] Función `deleteFile()` ya maneja archivos no encontrados
- [x] Probado en el dashboard
- [x] Documentación creada

---

## 🚀 Próximos Pasos (Opcional)

### Mejorar Manejo de Errores

Podrías agregar logging más detallado:

```javascript
try {
    await deleteDoc(doc(db, "documentos", docId));
    console.log(`✅ Documento ${docId} eliminado de Firestore`);
    
    await deleteObject(fileRef);
    console.log(`✅ Archivo ${filePath} eliminado de Storage`);
    
} catch (error) {
    console.error("❌ Error:", {
        code: error.code,
        message: error.message,
        docId: docId,
        filePath: filePath
    });
}
```

### Batch Delete

Si tienes muchos documentos huérfanos en Firestore (sin archivo en Storage):

```bash
cd scripts_utilidad
python limpiar_documentos_huerfanos.py
```

---

**Problema Resuelto** ✅

El sistema ahora permite eliminar documentos correctamente respetando las reglas de seguridad.
