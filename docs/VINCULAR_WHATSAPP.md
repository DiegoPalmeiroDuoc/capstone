# 📱 Guía: Vincular WhatsApp al Perfil de Usuario

## 🎯 Objetivo

Conectar el número de WhatsApp del cliente con su cuenta en la plataforma web para que el chatbot pueda acceder a sus documentos personales.

---

## 🔄 Flujo Completo

```
┌─────────────────────┐
│ 1. Usuario crea     │
│    cuenta en web    │
│    (Firebase Auth)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 2. Usuario agrega   │
│    su número de     │
│    WhatsApp en      │
│    perfil           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 3. Se guarda en     │
│    Firestore:       │
│    usuarios/        │
│    {uid}/telefono   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 4. Usuario sube     │
│    documentos con   │
│    su UID           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 5. Chatbot recibe   │
│    mensaje de       │
│    WhatsApp         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 6. Busca UID por    │
│    número de        │
│    teléfono         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 7. Obtiene          │
│    documentos del   │
│    usuario con UID  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 8. Genera respuesta │
│    con DeepSeek AI  │
│    usando docs      │
└─────────────────────┘
```

---

## 📊 Estructura de Firestore

### Colección: `usuarios`

```javascript
usuarios/
  {uid}/  // UID de Firebase Auth
    {
      "uid": "ABC123XYZ",
      "telefono": "+56912345678",  // Formato internacional
      "email": "usuario@ejemplo.com",
      "nombre": "Juan Pérez",
      "fechaActualizacion": Timestamp,
      "fechaRegistro": Timestamp
    }
```

### Colección: `documentos`

```javascript
documentos/
  {doc_id}/
    {
      "usuarioId": "ABC123XYZ",  // UID del dueño
      "nombre": "contrato.pdf",
      "url": "https://storage.../archivo.pdf",
      "estado": "procesado",
      "contenidoProcesado": "texto extraído...",
      "descripcion": "Contrato de arriendo",
      "fechaSubida": "2025-11-02T20:30:00Z"
    }
```

---

## 🛠️ Implementación

### Paso 1: Agregar Campo de Teléfono al Perfil

#### En `perfil.html` (crear/modificar):

```html
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mi Perfil - Intexta</title>
    <link rel="stylesheet" href="{% static 'css/estilos.css' %}">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>

<header>
    <div class="logo-container">
        <img src="{% static 'img/logo.png' %}" alt="Logo Intexta" class="logo-img">
        <div>
            <div class="logo-text">Intexta</div>
            <div class="subtitle">Tu asistente virtual</div>
        </div>
    </div>
    <nav>
        <a href="/dashboard"><i class="fas fa-home"></i> Dashboard</a>
        <button onclick="logoutUser()"><i class="fas fa-sign-out-alt"></i> Cerrar sesión</button>
    </nav>
</header>

<section class="dashboard-section">
    <h2><i class="fas fa-user-circle"></i> Mi Perfil</h2>
    
    <!-- Información del usuario -->
    <div class="card" style="max-width: 600px; margin: 0 auto;">
        <h3><i class="fas fa-info-circle"></i> Información Personal</h3>
        
        <div class="form-group">
            <label><i class="fas fa-envelope"></i> Email</label>
            <input type="text" id="userEmail" readonly style="background: var(--bg-color); cursor: not-allowed;">
        </div>
        
        <div class="form-group">
            <label><i class="fas fa-id-card"></i> ID de Usuario</label>
            <input type="text" id="userId" readonly style="background: var(--bg-color); cursor: not-allowed; font-family: monospace;">
        </div>
    </div>
    
    <!-- WhatsApp Configuration -->
    <div class="card" style="max-width: 600px; margin: 2rem auto;">
        <h3><i class="fab fa-whatsapp"></i> Configuración de WhatsApp</h3>
        <p style="color: var(--text-light); margin-bottom: 1.5rem;">
            Vincula tu número de WhatsApp para recibir notificaciones y consultar tus documentos desde el chatbot.
        </p>
        
        <div class="form-group">
            <label for="telefono">
                <i class="fas fa-phone"></i> Número de WhatsApp
            </label>
            <div style="display: flex; gap: 0.5rem;">
                <select id="countryCode" style="max-width: 100px;">
                    <option value="+56">🇨🇱 +56</option>
                    <option value="+1">🇺🇸 +1</option>
                    <option value="+54">🇦🇷 +54</option>
                    <option value="+55">🇧🇷 +55</option>
                    <option value="+57">🇨🇴 +57</option>
                    <option value="+52">🇲🇽 +52</option>
                    <option value="+51">🇵🇪 +51</option>
                    <option value="+34">🇪🇸 +34</option>
                </select>
                <input 
                    type="tel" 
                    id="telefono" 
                    placeholder="912345678"
                    pattern="[0-9]{9,15}"
                >
            </div>
            <small style="color: var(--text-light); display: block; margin-top: 0.5rem;">
                Formato: Solo números, sin espacios ni guiones
            </small>
        </div>
        
        <button onclick="updatePhone()" class="primary">
            <i class="fas fa-save"></i> Guardar Número
        </button>
        
        <div id="phoneStatus" style="margin-top: 1rem;"></div>
    </div>
    
    <!-- Instrucciones WhatsApp -->
    <div class="card" style="max-width: 600px; margin: 2rem auto; background: linear-gradient(135deg, #25D366, #128C7E);">
        <h3 style="color: white;"><i class="fas fa-question-circle"></i> ¿Cómo usar el chatbot?</h3>
        <div style="color: white;">
            <ol style="padding-left: 1.5rem;">
                <li>Guarda tu número de WhatsApp arriba</li>
                <li>Agrega este número a tus contactos: <strong>+1 415 523 8886</strong></li>
                <li>Envía el mensaje: <code style="background: rgba(0,0,0,0.2); padding: 0.2rem 0.5rem; border-radius: 4px;">join yellow-tiger</code></li>
                <li>¡Listo! Ahora puedes consultar tus documentos por WhatsApp</li>
            </ol>
            
            <div style="background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                <strong>Ejemplos de preguntas:</strong>
                <ul style="list-style: none; padding-left: 0; margin-top: 0.5rem;">
                    <li>💬 "Muéstrame mis documentos"</li>
                    <li>💬 "¿Cuántos archivos tengo?"</li>
                    <li>💬 "Busca información sobre contratos"</li>
                    <li>💬 "¿Qué dice mi último documento?"</li>
                </ul>
            </div>
        </div>
    </div>
</section>

<!-- Toast Container -->
<div id="toastContainer"></div>

<!-- Firebase SDK -->
<script type="module">
    import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js";
    import { getAuth, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-auth.js";
    import { getFirestore, doc, getDoc, setDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-firestore.js";

    const firebaseConfig = {
        apiKey: "AIzaSyC6iYpvQNRh9_E2UoHcqABzvqzGRNa2YPY",
        authDomain: "admin-doc-ia.firebaseapp.com",
        projectId: "admin-doc-ia",
        storageBucket: "admin-doc-ia.firebasestorage.app",
        messagingSenderId: "425806071651",
        appId: "1:425806071651:web:2f2f0d6e8eec8fa5e6a1fb"
    };

    const app = initializeApp(firebaseConfig);
    const auth = getAuth(app);
    const db = getFirestore(app);

    let currentUser = null;

    // Verificar autenticación
    onAuthStateChanged(auth, async (user) => {
        if (user) {
            currentUser = user;
            document.getElementById('userEmail').value = user.email;
            document.getElementById('userId').value = user.uid;
            
            // Cargar número de teléfono guardado
            await loadUserPhone(user.uid);
        } else {
            window.location.href = '/login';
        }
    });

    // Cargar número de teléfono guardado
    async function loadUserPhone(uid) {
        try {
            const userDoc = await getDoc(doc(db, 'usuarios', uid));
            
            if (userDoc.exists()) {
                const data = userDoc.data();
                if (data.telefono) {
                    // Separar código de país y número
                    const phone = data.telefono;
                    const match = phone.match(/^(\+\d{1,3})(\d+)$/);
                    
                    if (match) {
                        document.getElementById('countryCode').value = match[1];
                        document.getElementById('telefono').value = match[2];
                    } else {
                        document.getElementById('telefono').value = phone;
                    }
                    
                    document.getElementById('phoneStatus').innerHTML = `
                        <div style="padding: 1rem; background: var(--success-color); color: white; border-radius: 8px;">
                            <i class="fas fa-check-circle"></i> Número verificado: ${data.telefono}
                        </div>
                    `;
                }
            }
        } catch (error) {
            console.error("Error cargando teléfono:", error);
        }
    }

    // Actualizar número de teléfono
    window.updatePhone = async function() {
        const countryCode = document.getElementById('countryCode').value;
        const telefono = document.getElementById('telefono').value.trim();
        
        if (!telefono) {
            showToast("Por favor ingresa tu número de WhatsApp", "warning");
            return;
        }
        
        // Validar formato
        if (!/^\d{9,15}$/.test(telefono)) {
            showToast("Número inválido. Solo usa dígitos sin espacios", "error");
            return;
        }
        
        const fullPhone = countryCode + telefono;
        
        try {
            // Guardar en Firestore
            await setDoc(doc(db, 'usuarios', currentUser.uid), {
                uid: currentUser.uid,
                email: currentUser.email,
                telefono: fullPhone,
                fechaActualizacion: serverTimestamp()
            }, { merge: true });
            
            showToast("✅ Número de WhatsApp guardado correctamente", "success");
            
            document.getElementById('phoneStatus').innerHTML = `
                <div style="padding: 1rem; background: var(--success-color); color: white; border-radius: 8px;">
                    <i class="fas fa-check-circle"></i> Número verificado: ${fullPhone}
                    <br><small>Ahora puedes usar el chatbot de WhatsApp</small>
                </div>
            `;
            
        } catch (error) {
            console.error("Error guardando teléfono:", error);
            showToast("Error al guardar el número: " + error.message, "error");
        }
    };

    // Cerrar sesión
    window.logoutUser = async function() {
        try {
            await signOut(auth);
            window.location.href = '/login';
        } catch (error) {
            console.error("Error al cerrar sesión:", error);
        }
    };

    // Toast notifications
    function showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        
        toast.innerHTML = `
            <i class="fas ${icons[type]}"></i>
            <span>${message}</span>
        `;
        
        container.appendChild(toast);
        
        setTimeout(() => toast.classList.add('show'), 10);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => container.removeChild(toast), 300);
        }, 3000);
    }
</script>

</body>
</html>
```

---

### Paso 2: Actualizar el Dashboard para enlazar al Perfil

En `dashboard.html`, agregar enlace en el header:

```html
<nav>
    <a href="/perfil"><i class="fas fa-user"></i> Mi Perfil</a>
    <button onclick="logoutUser()"><i class="fas fa-sign-out-alt"></i> Cerrar sesión</button>
</nav>
```

---

### Paso 3: Agregar Ruta en Django

En `cliente_web/intexta_web/urls.py`:

```python
from django.urls import path
from core import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('perfil/', views.perfil_view, name='perfil'),  # ← AGREGAR ESTO
    
    # APIs
    path('api/list-docs/', views.api_list_docs, name='api_list_docs'),
    path('api/update-phone/', views.api_update_phone, name='api_update_phone'),
]
```

---

## 🔍 Cómo Funciona el Chatbot

### Flujo de Autenticación por WhatsApp

1. **Usuario envía mensaje desde WhatsApp:**
   ```
   Número: +56912345678
   Mensaje: "Hola"
   ```

2. **Chatbot busca el UID:**
   ```python
   # En intexta_chatbot.py
   phone = "+56912345678"
   uid = chatbot.get_user_by_phone(phone)
   # Retorna: "ABC123XYZ"
   ```

3. **Obtiene documentos del usuario:**
   ```python
   documentos = chatbot.get_user_documents(uid)
   # Retorna lista de documentos procesados
   ```

4. **Genera respuesta con DeepSeek:**
   ```python
   context = chatbot.build_context_from_documents(documentos)
   respuesta = chatbot.call_deepseek_api(messages)
   ```

---

## 📱 Formato de Números de Teléfono

### ✅ Formato Correcto:

```
+56912345678   (Chile)
+14155238886   (USA)
+5491123456789 (Argentina)
```

### ❌ Formato Incorrecto:

```
912345678       (sin código de país)
+56 9 1234 5678 (con espacios)
+56-9-1234-5678 (con guiones)
(56) 912345678  (con paréntesis)
```

### Función de Normalización:

```python
def normalize_phone(phone):
    """Normaliza número de teléfono al formato internacional"""
    # Eliminar espacios, guiones, paréntesis
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Asegurar que empiece con +
    if not phone.startswith('+'):
        # Asumir Chile si no hay código
        phone = '+56' + phone
    
    return phone
```

---

## 🧪 Pruebas

### Test 1: Guardar Número

1. Login en la web
2. Ir a Perfil
3. Ingresar número: `912345678`
4. Seleccionar país: `+56`
5. Guardar
6. Verificar en Firestore: `usuarios/{uid}/telefono` = `+56912345678`

### Test 2: Chatbot Reconoce Usuario

1. Enviar mensaje desde WhatsApp al número de Twilio
2. Verificar logs del chatbot:
   ```
   [INFO] 📥 Mensaje recibido de +56912345678: Hola
   [INFO] Usuario ABC123XYZ: 3 documentos encontrados
   [INFO] 🤖 Respuesta enviada
   ```

### Test 3: Consulta de Documentos

Desde WhatsApp:
```
Usuario: "Muéstrame mis documentos"
Bot: "Tienes 3 documentos procesados:
     1. contrato.pdf - Contrato de arriendo
     2. factura.xlsx - Factura del mes
     3. informe.docx - Informe anual"
```

---

## 🐛 Solución de Problemas

### Problema: Chatbot no encuentra al usuario

**Causa:** Número de teléfono no coincide

**Solución:**
1. Verifica formato en Firestore
2. Verifica número que llega desde Twilio
3. Usa función de normalización

```python
# En intexta_chatbot.py
phone_from_twilio = request.form.get('From', '').replace('whatsapp:', '')
phone_normalized = normalize_phone(phone_from_twilio)
```

### Problema: Usuario no tiene documentos

**Causa:** `usuarioId` en documentos no coincide con UID

**Solución:**
1. Verificar que al subir documentos se guarde el UID correcto
2. Revisar en Firestore: `documentos/{doc}/usuarioId`

### Problema: Cambio de número

**Solución:**
El usuario puede actualizar su número en cualquier momento desde el perfil. El sistema actualiza automáticamente la vinculación.

---

## 📊 Monitoreo

### Ver vinculaciones activas:

En Firebase Console:
```
Firestore → usuarios → [ver todos]
```

Verás lista de usuarios con sus números.

### Ver documentos por usuario:

```
Firestore → documentos → [filtrar por usuarioId]
```

---

## 🎯 Resumen

**Para vincular WhatsApp:**

1. ✅ Usuario crea cuenta en la web
2. ✅ Va a "Mi Perfil"
3. ✅ Ingresa su número de WhatsApp
4. ✅ Guarda
5. ✅ Se une al sandbox de Twilio
6. ✅ Envía mensaje desde WhatsApp
7. ✅ El chatbot lo reconoce por su número
8. ✅ Accede a sus documentos personales

**¡Listo!** El sistema está completamente integrado. 🎉
