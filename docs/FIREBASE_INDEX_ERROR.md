# 🔥 Solución: Error de Índice Firebase Firestore

## ❌ Error Recibido

```
FirebaseError: The query requires an index. 
You can create it here: https://console.firebase.google.com/...
```

## 🔍 Causa del Error

Firestore requiere **índices compuestos** cuando haces consultas que combinan:
- `where()` + `orderBy()` en diferentes campos
- Múltiples `where()` con diferentes campos
- `orderBy()` en múltiples campos

En nuestro caso:
```javascript
// Esta consulta requiere un índice
query(
    collection(db, "documentos"), 
    where("usuarioId", "==", uid),     // ← Campo 1
    orderBy("fechaSubida", "desc")     // ← Campo 2 diferente
)
```

---

## ✅ Solución Implementada (TEMPORAL)

He modificado el código para ordenar en el **cliente** en lugar de en Firestore:

```javascript
// Consulta simple (sin índice)
const q = query(
    collection(db, "documentos"), 
    where("usuarioId", "==", uid)
);
const snapshot = await getDocs(q);

// Ordenar en JavaScript
allDocuments.sort((a, b) => {
    const dateA = new Date(a.fechaSubida);
    const dateB = new Date(b.fechaSubida);
    return dateB - dateA; // Más reciente primero
});
```

**Ventaja**: Funciona inmediatamente sin configurar Firebase  
**Desventaja**: Menos eficiente con muchos documentos (>1000)

---

## 🎯 Solución Permanente (RECOMENDADA)

### Opción 1: Crear el índice desde la consola (MÁS RÁPIDO)

1. **Abre el enlace del error** en tu navegador:
   ```
   https://console.firebase.google.com/v1/r/project/admin-doc-ia/firestore/indexes?create_composite=...
   ```

2. **Click en "Crear índice"** (botón azul)

3. **Espera 1-2 minutos** mientras Firebase construye el índice

4. **¡Listo!** Ya puedes usar `orderBy()` en tus consultas

---

### Opción 2: Desplegar índices con Firebase CLI

Si tienes Firebase CLI instalado:

```bash
# 1. Navega al directorio
cd cliente_web

# 2. Despliega los índices
firebase deploy --only firestore:indexes
```

El archivo `firestore.indexes.json` ya está configurado con los índices necesarios.

---

### Opción 3: Crear manualmente desde Firebase Console

1. Ve a [Firebase Console](https://console.firebase.google.com/)

2. Selecciona tu proyecto: **admin-doc-ia**

3. Ve a **Firestore Database** → **Índices**

4. Click en **"Crear índice"**

5. Configura el índice:
   ```
   Colección: documentos
   Campo 1: usuarioId (Ascending)
   Campo 2: fechaSubida (Descending)
   ```

6. Click en **"Crear"**

---

## 📋 Índices Necesarios para Intexta

### Índice 1: Listar documentos por fecha
```json
{
  "collectionGroup": "documentos",
  "queryScope": "COLLECTION",
  "fields": [
    { "fieldPath": "usuarioId", "order": "ASCENDING" },
    { "fieldPath": "fechaSubida", "order": "DESCENDING" }
  ]
}
```

**Uso**: Mostrar documentos del usuario ordenados por fecha

---

### Índice 2: Filtrar por estado y fecha
```json
{
  "collectionGroup": "documentos",
  "queryScope": "COLLECTION",
  "fields": [
    { "fieldPath": "usuarioId", "order": "ASCENDING" },
    { "fieldPath": "estado", "order": "ASCENDING" },
    { "fieldPath": "fechaSubida", "order": "DESCENDING" }
  ]
}
```

**Uso**: Consultas futuras para filtrar documentos procesados/pendientes

---

## 🔄 Revertir a Consulta Optimizada (Después de crear índice)

Una vez que hayas creado el índice, puedes volver a usar la consulta optimizada:

```javascript
// En dashboard.html, cambiar:

// De:
const q = query(
    collection(db, "documentos"), 
    where("usuarioId", "==", uid)
);
// ... ordenar en JavaScript

// A:
import { orderBy } from "firebase/firestore"; // Agregar import

const q = query(
    collection(db, "documentos"), 
    where("usuarioId", "==", uid),
    orderBy("fechaSubida", "desc")  // Ordenar en Firestore
);
// ... eliminar sort() de JavaScript
```

---

## 🚀 Ventajas de Usar Índices

1. **Performance**: Consultas más rápidas
2. **Escalabilidad**: Funciona con miles de documentos
3. **Ahorro de datos**: Menos transferencia desde Firestore
4. **Paginación**: Permite usar `limit()` y `startAfter()` eficientemente

---

## 📊 Comparación de Métodos

| Característica | Ordenar en Cliente | Ordenar en Firestore |
|----------------|-------------------|---------------------|
| **Configuración** | ✅ Ninguna | ⚠️ Requiere índice |
| **Performance** | ⚠️ Lento con >100 docs | ✅ Siempre rápido |
| **Uso de datos** | ⚠️ Descarga todo | ✅ Solo lo necesario |
| **Paginación** | ❌ Difícil | ✅ Fácil |
| **Complejidad** | ✅ Simple | ⚠️ Requiere config |

---

## 🐛 Solución de Problemas

### Error persiste después de crear el índice
- Espera 2-5 minutos (construcción del índice)
- Refresca la página
- Limpia caché del navegador

### No puedo acceder a Firebase Console
- Verifica que tienes permisos en el proyecto
- Contacta al administrador del proyecto

### Firebase CLI no funciona
```bash
# Instalar
npm install -g firebase-tools

# Login
firebase login

# Inicializar (si no está)
firebase init firestore
```

---

## 📝 Estado Actual

✅ **Código modificado** para funcionar sin índice  
⏳ **Pendiente**: Crear índice en Firebase Console  
🎯 **Objetivo**: Restaurar `orderBy()` después de crear índice

---

## 🔗 Enlaces Útiles

- [Firebase Indexes Documentation](https://firebase.google.com/docs/firestore/query-data/indexing)
- [Crear Índices Compuestos](https://firebase.google.com/docs/firestore/query-data/index-overview#composite_indexes)
- [Firebase Console - Índices](https://console.firebase.google.com/project/admin-doc-ia/firestore/indexes)

---

**Última actualización**: Noviembre 2025  
**Autor**: Equipo Intexta
