# 🛠️ Scripts de Utilidad - Intexta

Esta carpeta contiene scripts de diagnóstico, mantenimiento y utilidad para el sistema Intexta.

---

## 📋 Scripts Disponibles

### 🔍 diagnostico_whatsapp.py
**Propósito**: Diagnóstico completo del sistema WhatsApp

**Verifica**:
- ✅ Conexión a Firebase
- ✅ Usuarios registrados
- ✅ Documentos procesados
- ✅ Vinculación WhatsApp-Usuario
- ✅ Configuración de Twilio

**Uso**:
```bash
python diagnostico_whatsapp.py
```

**Salida**:
- Estado de Firebase
- Lista de usuarios con WhatsApp
- Documentos por usuario
- Recomendaciones

---

### 👥 sincronizar_usuarios.py
**Propósito**: Sincronizar Firebase Authentication → Firestore

**Cuándo usar**:
- Después de registrar usuarios manualmente
- Si la colección `usuarios` está vacía
- Para migrar usuarios existentes

**Uso**:
```bash
python sincronizar_usuarios.py
```

**Acción**:
- Lee todos los usuarios de Firebase Auth
- Crea/actualiza documentos en Firestore `usuarios/`
- Preserva datos existentes (teléfono, etc.)

---

### 📄 ver_documentos_usuarios.py
**Propósito**: Ver relación completa entre usuarios y documentos

**Muestra**:
- Todos los usuarios registrados
- Documentos de cada usuario
- Estado de procesamiento
- Vinculación WhatsApp
- Estadísticas

**Uso**:
```bash
python ver_documentos_usuarios.py
```

**Salida**:
```
USUARIOS REGISTRADOS (1):
  • gi.espinosa@duocuc.cl
    UID: 99IIKbpCqYRVRxCKMjCGitUJ8j32
    WhatsApp: 930104972

DOCUMENTOS EN FIRESTORE:
📄 Documento: ejemplo.docx
   Estado: procesado
   Usuario: gi.espinosa@duocuc.cl
   ...
```

---

### 🔄 transferir_documentos.py
**Propósito**: Transferir documentos entre usuarios

**Cuándo usar**:
- Migrar documentos a otro usuario
- Corregir asignaciones incorrectas
- Consolidar cuentas

**Uso**:
```bash
python transferir_documentos.py
```

**Interactivo**:
1. Muestra lista de usuarios
2. Selecciona usuario origen
3. Selecciona usuario destino
4. Confirma transferencia

**⚠️ Precaución**: Esta operación es irreversible

---

### ✅ check_documents.py
**Propósito**: Verificar estado de procesamiento de documentos

**Muestra**:
- Documentos pendientes
- Documentos procesados
- Documentos con error
- Estadísticas de procesamiento

**Uso**:
```bash
python check_documents.py
```

---

### 🔄 migrate_documents.py
**Propósito**: Agregar campo `estado` a documentos antiguos

**Cuándo usar**:
- Migración de documentos antiguos
- Actualizar estructura de datos

**Uso**:
```bash
python migrate_documents.py
```

---

### 🔁 reset_errors.py
**Propósito**: Resetear documentos con error a estado pendiente

**Cuándo usar**:
- Reprocesar documentos que fallaron
- Después de corregir bugs en ETL

**Uso**:
```bash
python reset_errors.py
```

**Acción**:
- Encuentra documentos con `estado: error`
- Cambia a `estado: pendiente`
- Limpia mensaje de error
- Permite reprocesamiento

---

## 🗂️ Archivos Antiguos/Demo

### consultaInventario.py
Script de prueba antiguo para consultas de inventario

### convivencia_escolar.py
Ejemplo de análisis de datos

### manualPython.py
Ejemplos básicos de Python

### presentacion.py
Script para presentaciones

### static/ y templates/
Archivos HTML/CSS antiguos (antes de Django)

---

## 📝 Notas

- Todos los scripts requieren acceso a Firebase
- Asegúrate de tener configurado `firebase_config.py`
- Los scripts son seguros de ejecutar múltiples veces
- Algunos scripts son interactivos (piden confirmación)

---

## ⚠️ Advertencias

- **transferir_documentos.py**: Operación irreversible
- **reset_errors.py**: Solo usar si sabes que quieres reprocesar
- Siempre haz backup antes de operaciones masivas

---

## 🔗 Ver También

- [README principal](../README.md)
- [Documentación de Firebase](https://firebase.google.com/docs)
- [Documentación de Twilio](https://www.twilio.com/docs)
