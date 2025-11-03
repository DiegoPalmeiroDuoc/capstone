# 📝 Resumen: Vinculación WhatsApp con Usuarios

## 🎯 ¿Qué se implementó?

Se agregó la funcionalidad completa para vincular números de WhatsApp a las cuentas de usuario, permitiendo que el chatbot reconozca a cada cliente y acceda a sus documentos personales.

---

## ✅ Cambios Realizados

### 1. Página de Perfil Actualizada (`perfil.html`)

**Nueva funcionalidad:**
- ✅ Campo para agregar número de WhatsApp
- ✅ Selector de código de país (Chile, USA, Argentina, etc.)
- ✅ Validación de formato de teléfono
- ✅ Guardado en Firestore
- ✅ Instrucciones de uso del chatbot
- ✅ Ejemplos de preguntas para WhatsApp

**Vista previa:**
```
┌────────────────────────────────────┐
│  Mi Perfil                          │
├────────────────────────────────────┤
│                                     │
│  Email: usuario@ejemplo.com        │
│  ID: ABC123XYZ                     │
│                                     │
│  ┌─ WhatsApp ─────────────┐        │
│  │ Código: [+56 ▼]        │        │
│  │ Número: [912345678 ]   │        │
│  │ [Guardar Número]       │        │
│  └────────────────────────┘        │
│                                     │
│  📱 Cómo usar el chatbot:          │
│  1. Guarda tu número arriba        │
│  2. Agrega +1 415 523 8886         │
│  3. Envía "join yellow-tiger"      │
│  4. ¡Listo!                        │
└────────────────────────────────────┘
```

### 2. Dashboard Actualizado (`dashboard.html`)

**Nuevo enlace:**
```html
<nav>
    <a href="/perfil">Mi Perfil</a>
    <button>Cerrar sesión</button>
</nav>
```

### 3. Documentación Completa

**Creados:**
- `docs/VINCULAR_WHATSAPP.md` - Guía completa de vinculación
- `docs/CONFIGURACION_TWILIO.md` - Configuración de Twilio
- `configurar_twilio.bat` - Asistente de configuración

---

## 🔄 Flujo Completo de Uso

```
PASO 1: Usuario Web
──────────────────────────────────────
1. Usuario crea cuenta → Firebase Auth
2. Inicia sesión
3. Va a "Mi Perfil"
4. Ingresa número: +56912345678
5. Click "Guardar Número"
   ↓
   Se guarda en Firestore:
   usuarios/ABC123XYZ/telefono = "+56912345678"


PASO 2: Usuario WhatsApp
──────────────────────────────────────
1. Abre WhatsApp
2. Agrega contacto: +1 415 523 8886
3. Envía: "join yellow-tiger"
4. Recibe confirmación de Twilio


PASO 3: Vinculación Automática
──────────────────────────────────────
Usuario envía: "Hola"
   ↓
Twilio → Webhook → Chatbot
   ↓
Chatbot busca:
   Firestore.usuarios
   .where('telefono', '==', '+56912345678')
   .get()
   ↓
Encuentra: UID = "ABC123XYZ"
   ↓
Busca documentos:
   Firestore.documentos
   .where('usuarioId', '==', 'ABC123XYZ')
   .where('estado', '==', 'procesado')
   .get()
   ↓
Encuentra: 3 documentos
   ↓
DeepSeek API genera respuesta usando docs
   ↓
Envía respuesta a WhatsApp
```

---

## 📊 Estructura de Datos

### Firestore: Colección `usuarios`

```javascript
usuarios/
  ABC123XYZ/  // ← UID de Firebase Auth
    {
      "uid": "ABC123XYZ",
      "email": "usuario@ejemplo.com",
      "telefono": "+56912345678",  // ← CLAVE
      "fechaActualizacion": Timestamp
    }
```

### Firestore: Colección `documentos`

```javascript
documentos/
  DOC001/
    {
      "usuarioId": "ABC123XYZ",  // ← Vincula con usuario
      "nombre": "contrato.pdf",
      "estado": "procesado",
      "contenidoProcesado": "texto...",
      "url": "https://storage...",
      "fechaSubida": "2025-11-02T20:00:00Z"
    }
```

---

## 💻 Código Clave

### En `perfil.html` - Guardar Teléfono

```javascript
async function updatePhone() {
    const countryCode = "+56";  // De select
    const telefono = "912345678";  // Del input
    const fullPhone = "+56912345678";  // Combinado
    
    // Guardar en Firestore
    await setDoc(doc(db, 'usuarios', currentUser.uid), {
        uid: currentUser.uid,
        email: currentUser.email,
        telefono: fullPhone,
        fechaActualizacion: serverTimestamp()
    }, { merge: true });
}
```

### En `intexta_chatbot.py` - Buscar Usuario

```python
def get_user_by_phone(self, phone_number):
    """Busca UID por número de teléfono"""
    users_ref = self.db.collection('usuarios')\
        .where('telefono', '==', phone_number)
    
    users = list(users_ref.stream())
    
    if users:
        return users[0].id  # Retorna UID
    return None
```

### En `intexta_chatbot.py` - Obtener Documentos

```python
def get_user_documents(self, user_id):
    """Obtiene docs procesados del usuario"""
    docs_ref = self.db.collection('documentos')\
        .where('usuarioId', '==', user_id)\
        .where('estado', '==', 'procesado')
    
    documentos = []
    for doc in docs_ref.stream():
        data = doc.to_dict()
        documentos.append({
            'nombre': data['nombre'],
            'contenido': data['contenidoProcesado']
        })
    
    return documentos
```

---

## 🧪 Prueba Completa

### Test 1: Guardar Número en la Web

```bash
1. Abre: http://localhost:8000/login
2. Inicia sesión
3. Click "Mi Perfil"
4. Ingresa: +56912345678
5. Click "Guardar Número"
6. Ver toast: "✅ Número guardado"
```

**Verificar en Firestore:**
```
usuarios/ABC123XYZ/telefono = "+56912345678"
```

### Test 2: Chatbot Reconoce Usuario

```bash
# Terminal con chatbot
python intexta_chatbot.py

# Desde WhatsApp
Enviar: "Hola"

# Logs esperados:
[INFO] 📥 Mensaje recibido de +56912345678: Hola
[INFO] Usuario ABC123XYZ: 3 documentos encontrados
[INFO] 🤖 Respuesta enviada
```

### Test 3: Consultar Documentos

**Desde WhatsApp:**
```
Usuario: "¿Qué documentos tengo?"

Bot: "Tienes 3 documentos procesados:

1. contrato.pdf
   - Contrato de arriendo
   
2. factura.xlsx
   - Factura del mes
   
3. informe.docx
   - Informe anual

¿Quieres que busque algo específico en ellos?"
```

---

## 🔐 Seguridad

### Firestore Rules (Recomendado)

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Usuarios
    match /usuarios/{userId} {
      // Solo el dueño puede leer/escribir su perfil
      allow read, write: if request.auth != null && 
                         request.auth.uid == userId;
    }
    
    // Documentos
    match /documentos/{docId} {
      // Solo el dueño puede acceder
      allow read, write: if request.auth != null && 
                         request.auth.uid == resource.data.usuarioId;
      
      // Backend puede leer todo (chatbot)
      allow read: if request.auth.token.admin == true;
    }
  }
}
```

---

## 📱 Formatos de Teléfono

### ✅ Válidos:
```
+56912345678    (Chile)
+14155238886    (USA)
+5491123456789  (Argentina)
```

### ❌ Inválidos:
```
912345678       (sin código)
+56 9 1234 5678 (con espacios)
56-9-1234-5678  (sin +, con guiones)
```

---

## 🚀 ¿Qué Sigue?

### Mejoras Opcionales:

1. **Verificación de número:**
   - Enviar código de verificación por WhatsApp
   - Usuario confirma código en la web

2. **Notificaciones proactivas:**
   - Avisar cuando documento es procesado
   - Resumen diario de actividad

3. **Múltiples números:**
   - Permitir agregar varios números
   - WhatsApp personal + trabajo

4. **Dashboard de conversaciones:**
   - Ver historial de chats
   - Estadísticas de uso

---

## ✅ Checklist Final

- [x] Página de perfil con campo de teléfono
- [x] Validación de formato
- [x] Guardado en Firestore
- [x] Chatbot busca usuario por teléfono
- [x] Chatbot obtiene documentos del usuario
- [x] Respuestas personalizadas con docs
- [x] Instrucciones para el usuario
- [x] Documentación completa
- [x] Enlace desde dashboard

---

## 🎉 ¡Todo Listo!

El sistema está completamente funcional. Los usuarios pueden:

1. ✅ Registrarse en la web
2. ✅ Vincular su WhatsApp
3. ✅ Subir documentos
4. ✅ Consultar desde WhatsApp
5. ✅ Recibir respuestas personalizadas

**El chatbot ahora reconoce a cada usuario y accede solo a sus documentos.** 🚀
