# 🔧 Solución: Ciclo de Redirección Login

## 🐛 Problema Identificado

**Síntoma:** Al intentar acceder al login, la página cierra sesión y vuelve a redireccionar al login infinitamente.

**Causa raíz:** Conflicto en los listeners `onAuthStateChanged` entre las páginas de login, dashboard y perfil.

---

## ✅ Correcciones Aplicadas

### 1. **login.html** - Agregar Redirección Automática

**Problema:** Si un usuario ya autenticado intentaba acceder a `/login`, no era redirigido al dashboard.

**Solución aplicada:**
```javascript
// Verificar si ya hay sesión activa
onAuthStateChanged(auth, (user) => {
    if (user && user.emailVerified) {
        // Usuario ya autenticado, redirigir al dashboard
        window.location.href = "/dashboard";
    }
});
```

**Resultado:** Ahora si un usuario con sesión activa intenta ir a `/login`, es redirigido automáticamente al dashboard.

---

### 2. **dashboard.html** - Mejorar Verificación de Usuario

**Problema:** El `user.reload()` se ejecutaba sin `await`, causando condiciones de carrera.

**Antes:**
```javascript
onAuthStateChanged(auth, user => {
    if (!user) {
        window.location.href = "/login";
    } else {
        user.reload().then(() => {  // ← Sin await
            if (!user.emailVerified) {
                signOut(auth);  // ← Sin await
                setTimeout(() => window.location.href = "/login", 2000);
            }
        });
    }
});
```

**Después:**
```javascript
onAuthStateChanged(auth, async (user) => {
    if (!user) {
        window.location.href = "/login";
        return;  // ← Early return
    }
    
    try {
        await user.reload();  // ← Con await
        
        if (!user.emailVerified) {
            showToast("Debes verificar tu correo", "error");
            await signOut(auth);  // ← Con await
            setTimeout(() => window.location.href = "/login", 2000);
            return;  // ← Early return
        }
        
        // Usuario OK
        loadFiles();
        
    } catch (error) {
        console.error("Error verificando usuario:", error);
        await signOut(auth);
        window.location.href = "/login";
    }
});
```

**Mejoras:**
- ✅ Función ahora es `async`
- ✅ `user.reload()` usa `await`
- ✅ `signOut()` usa `await`
- ✅ Early returns para evitar ejecución posterior
- ✅ Try-catch para manejar errores

---

## 🧪 Cómo Probar la Corrección

### Test 1: Login Normal

```bash
1. Abre: http://localhost:8000/login
2. Ingresa credenciales válidas
3. Click "Ingresar"
4. Deberías ser redirigido a /dashboard
5. Dashboard carga correctamente
```

**Resultado esperado:** Login exitoso sin loops.

---

### Test 2: Usuario Ya Autenticado

```bash
1. Inicia sesión en /login
2. Ve al dashboard
3. En la barra de URL, escribe: /login
4. Presiona Enter
5. Deberías ser redirigido AUTOMÁTICAMENTE a /dashboard
```

**Resultado esperado:** No puedes acceder a `/login` si ya tienes sesión activa.

---

### Test 3: Cuenta No Verificada

```bash
1. Crea una cuenta nueva
2. NO verifiques el email
3. Intenta hacer login
4. Deberías ver mensaje: "Tu cuenta no está verificada"
5. Sesión se cierra automáticamente
6. Vuelves al login
```

**Resultado esperado:** Mensaje claro, sin loops infinitos.

---

### Test 4: Cerrar Sesión

```bash
1. Inicia sesión normalmente
2. En dashboard, click "Cerrar sesión"
3. Deberías ser redirigido a /login
4. Página de login carga correctamente
```

**Resultado esperado:** Logout limpio.

---

## 🔍 Diagnóstico de Problemas

### Si Aún Tienes Loops de Redirección:

#### Paso 1: Limpiar Caché y Cookies

**En Chrome:**
```
1. F12 (DevTools)
2. Pestaña "Application"
3. Storage → Clear site data
4. Recargar página (Ctrl + F5)
```

**En Firefox:**
```
1. F12 (DevTools)
2. Pestaña "Storage"
3. Cookies → Eliminar todos
4. Local Storage → Eliminar
5. Recargar página (Ctrl + F5)
```

---

#### Paso 2: Verificar Estado de Firebase Auth

**Abre la consola del navegador (F12) y ejecuta:**

```javascript
// Ver estado actual de autenticación
import { getAuth } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-auth.js";
const auth = getAuth();
console.log("Usuario actual:", auth.currentUser);
console.log("Email verificado:", auth.currentUser?.emailVerified);
```

**O más simple:**
```javascript
// En la consola
console.log(firebase.auth().currentUser);
```

---

#### Paso 3: Verificar Logs de Red

**En DevTools (F12):**
```
1. Pestaña "Network"
2. Recarga la página
3. Busca peticiones a /login o /dashboard
4. Si ves muchas peticiones rápidas = loop detectado
```

---

## 🛠️ Soluciones Adicionales

### Problema: Loop Persiste Después de las Correcciones

**Solución 1: Cerrar Sesión Manualmente**

```javascript
// Abre consola del navegador (F12)
// Ejecuta:
import { getAuth, signOut } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-auth.js";
const auth = getAuth();
await signOut(auth);
console.log("Sesión cerrada");
```

Luego recarga la página.

---

**Solución 2: Limpiar IndexedDB de Firebase**

```javascript
// En consola del navegador
indexedDB.deleteDatabase('firebaseLocalStorageDb');
location.reload();
```

---

**Solución 3: Modo Incógnito**

1. Abre ventana de incógnito (Ctrl + Shift + N)
2. Ve a http://localhost:8000/login
3. Prueba el login desde cero

Si funciona en incógnito, el problema es caché/cookies.

---

## 📊 Flujo Correcto Después de las Correcciones

```
ESCENARIO 1: Usuario NO Autenticado
─────────────────────────────────────
/login
  │
  ├─ onAuthStateChanged detecta: user = null
  │  └─ Muestra formulario de login
  │
  └─ Usuario hace login
      └─ Redirige a /dashboard


ESCENARIO 2: Usuario YA Autenticado
─────────────────────────────────────
/login
  │
  ├─ onAuthStateChanged detecta: user existe
  │  └─ user.emailVerified = true
  │      └─ Redirige INMEDIATAMENTE a /dashboard
  │
/dashboard
  │
  ├─ onAuthStateChanged detecta: user existe
  │  └─ await user.reload()
  │      └─ user.emailVerified = true
  │          └─ Carga archivos
  │          └─ Muestra dashboard


ESCENARIO 3: Usuario Sin Verificar
─────────────────────────────────────
/login
  │
  ├─ Usuario hace login
  │  └─ Detecta: emailVerified = false
  │      └─ Muestra error
  │      └─ signOut()
  │      └─ Permanece en /login

/dashboard
  │
  ├─ onAuthStateChanged detecta: user existe
  │  └─ await user.reload()
  │      └─ user.emailVerified = false
  │          └─ Muestra error
  │          └─ await signOut()
  │          └─ Redirige a /login (2 segundos)
```

---

## ✅ Checklist de Verificación

Después de aplicar las correcciones:

- [ ] Limpiar caché del navegador
- [ ] Limpiar cookies de localhost:8000
- [ ] Cerrar todas las pestañas de localhost:8000
- [ ] Abrir nueva pestaña
- [ ] Ir a http://localhost:8000/login
- [ ] Hacer login con cuenta verificada
- [ ] Confirmar redirección a dashboard
- [ ] Dashboard carga correctamente
- [ ] Click "Cerrar sesión"
- [ ] Confirmar vuelta a login
- [ ] No hay loops de redirección

---

## 🆘 Si Nada Funciona

### Opción 1: Reiniciar Servidor Django

```bash
# Detener servidor (Ctrl+C)
# Reiniciar
cd cliente_web
python manage.py runserver
```

### Opción 2: Verificar Archivos

```bash
# Verificar que los cambios se guardaron
cd cliente_web/core/templates

# Ver fecha de modificación
dir login.html
dir dashboard.html
```

### Opción 3: Hard Refresh

En el navegador:
- **Windows:** Ctrl + Shift + R
- **Mac:** Cmd + Shift + R

Esto fuerza la recarga sin caché.

---

## 📝 Resumen

**Cambios aplicados:**

1. ✅ `login.html` - Agregado `onAuthStateChanged` para redirigir usuarios autenticados
2. ✅ `dashboard.html` - Mejorado manejo asíncrono con async/await
3. ✅ Ambos archivos - Agregados early returns para evitar ejecución posterior
4. ✅ Mejor manejo de errores con try-catch

**Resultado esperado:**

- ✅ No más loops de redirección
- ✅ Login fluido
- ✅ Dashboard carga correctamente
- ✅ Mensajes de error claros
- ✅ Logout limpio

---

## 🔗 Archivos Modificados

- `cliente_web/core/templates/login.html` - Líneas 115-125
- `cliente_web/core/templates/dashboard.html` - Líneas 178-200

---

**¿Sigues teniendo problemas?** Prueba esto en la consola del navegador:

```javascript
// Ver estado actual
console.log("Current URL:", window.location.href);
console.log("Current User:", firebase?.auth()?.currentUser);

// Forzar limpieza
localStorage.clear();
sessionStorage.clear();
location.reload();
```

¡Esto debería resolver el problema! 🎉
