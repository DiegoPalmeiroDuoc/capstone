# Solución: Acceso a Página de Perfil

## Problema Identificado

Los usuarios autenticados no podían acceder a `/perfil` debido a un ciclo de redirecciones:

```
/perfil → /login → /dashboard (loop infinito)
```

### Causa Raíz

1. **Race Condition en perfil.html**: `onAuthStateChanged()` podía dispararse con `user = null` antes de que Firebase cargara el estado de autenticación desde localStorage
2. **Redirección Agresiva en login.html**: Cualquier usuario autenticado era redirigido automáticamente al dashboard, incluso si habían llegado desde otra página

## Soluciones Implementadas

### 1. Protección contra Múltiples Redirecciones en perfil.html

**Archivo**: `cliente_web/core/templates/perfil.html`

```javascript
let hasRedirected = false;  // Evitar redirecciones múltiples

onAuthStateChanged(auth, async (user) => {
    if (user && !hasRedirected) {
        currentUser = user;
        document.getElementById('userEmail').value = user.email;
        document.getElementById('userId').value = user.uid;
        
        // Cargar número de teléfono guardado
        await loadUserPhone(user.uid);
    } else if (!user && !hasRedirected) {
        hasRedirected = true;
        window.location.href = '/login';
    }
});
```

**Beneficio**: Previene múltiples llamadas a `onAuthStateChanged` que causen redirecciones no deseadas.

### 2. Eliminación de Redirección Automática en login.html

**Archivo**: `cliente_web/core/templates/login.html`

**Antes**:
```javascript
onAuthStateChanged(auth, (user) => {
    if (user && user.emailVerified && !hasRedirected) {
        const urlParams = new URLSearchParams(window.location.search);
        const fromLogout = urlParams.get('logout');
        
        if (!fromLogout) {
            hasRedirected = true;
            window.location.href = "/dashboard";
        }
    }
});
```

**Después**:
```javascript
// No redirigir automáticamente - solo mostrar dashboard si ya están autenticados
// Esto permite que los usuarios accedan al login intencionalmente
onAuthStateChanged(auth, (user) => {
    if (user && user.emailVerified) {
        // Usuario ya autenticado - mostrar mensaje opcional
        console.log("Usuario ya autenticado:", user.email);
        // No redirigir automáticamente para evitar loops
    }
});
```

**Beneficio**: Permite que usuarios autenticados permanezcan en la página de login si llegan ahí por error o intención, rompiendo el ciclo de redirecciones.

### 3. Mejora en Funciones de Logout

**Archivos**: 
- `cliente_web/core/templates/dashboard.html`
- `cliente_web/core/templates/perfil.html`

```javascript
window.logoutUser = async function() {
    try {
        await signOut(auth);
        window.location.href = '/login?logout=true';
    } catch (error) {
        console.error("Error al cerrar sesión:", error);
    }
};
```

**Beneficio**: Añade parámetro `?logout=true` para distinguir entre logout intencional y navegación accidental.

## Flujo de Navegación Corregido

### Escenario 1: Usuario Autenticado Accede a /perfil

```
1. Usuario escribe localhost:8000/perfil
2. perfil.html carga
3. onAuthStateChanged detecta usuario autenticado
4. Página de perfil se muestra correctamente ✅
```

### Escenario 2: Usuario No Autenticado Accede a /perfil

```
1. Usuario escribe localhost:8000/perfil
2. perfil.html carga
3. onAuthStateChanged detecta user = null
4. Redirige a /login una sola vez (hasRedirected = true)
5. Usuario debe iniciar sesión ✅
```

### Escenario 3: Usuario Hace Logout desde Dashboard

```
1. Usuario hace clic en "Cerrar Sesión" en dashboard
2. signOut() cierra sesión en Firebase
3. Redirige a /login?logout=true
4. Usuario permanece en página de login ✅
```

### Escenario 4: Usuario Hace Logout desde Perfil

```
1. Usuario hace clic en "Cerrar Sesión" en perfil
2. signOut() cierra sesión en Firebase
3. Redirige a /login?logout=true
4. Usuario permanece en página de login ✅
```

### Escenario 5: Navegación Dashboard ↔ Perfil

```
Dashboard:
1. Clic en "Mi Perfil" → /perfil
2. onAuthStateChanged detecta usuario
3. Perfil se muestra correctamente ✅

Perfil:
1. Clic en "Volver al Dashboard"
2. Navega a /dashboard
3. Dashboard se muestra correctamente ✅
```

## Testing Checklist

Realiza las siguientes pruebas para validar la solución:

- [ ] **Test 1**: Login → Dashboard → Clic "Mi Perfil" → Se muestra perfil
- [ ] **Test 2**: URL directa `localhost:8000/perfil` estando autenticado → Se muestra perfil
- [ ] **Test 3**: URL directa `localhost:8000/perfil` sin autenticación → Redirige a /login
- [ ] **Test 4**: Logout desde dashboard → Redirige a /login y permanece ahí
- [ ] **Test 5**: Logout desde perfil → Redirige a /login y permanece ahí
- [ ] **Test 6**: Navegación dashboard → perfil → dashboard (múltiples veces) → Sin problemas
- [ ] **Test 7**: Modo incógnito, login, acceso a /perfil → Funciona correctamente

## Archivos Modificados

1. `cliente_web/core/templates/perfil.html`
   - Añadido flag `hasRedirected`
   - Protección contra race condition en `onAuthStateChanged`
   - Logout redirige a `/login?logout=true`

2. `cliente_web/core/templates/login.html`
   - Eliminada redirección automática al dashboard
   - Solo log de usuario autenticado en consola

3. `cliente_web/core/templates/dashboard.html`
   - Logout redirige a `/login?logout=true`

## Notas Técnicas

### ¿Por qué onAuthStateChanged se dispara múltiples veces?

Firebase Auth dispara `onAuthStateChanged` en varios momentos:
1. Inmediatamente al registrar el listener (puede ser `null` inicialmente)
2. Cuando completa la carga del estado desde localStorage
3. Cuando el estado de autenticación cambia (login/logout)
4. Cuando el token se refresca

### ¿Por qué usar hasRedirected?

Sin esta bandera, si `onAuthStateChanged` se dispara múltiples veces con `user = null`, causaría múltiples redirecciones. El flag asegura que solo redirigimos una vez.

### Alternativas Consideradas

1. **Usar sessionStorage para rastrear navegación**: Más complejo, innecesario
2. **Parámetros URL para rastrear origen**: Útil solo para debugging
3. **Delay en la redirección**: Mala UX, no resuelve el problema raíz

## Troubleshooting

### Problema: Todavía se redirige a /login desde /perfil

**Solución**: 
1. Limpia el caché del navegador (Ctrl + Shift + Delete)
2. Cierra todas las pestañas del sitio
3. Abre en modo incógnito para probar
4. Verifica que los archivos se guardaron correctamente

### Problema: Login no redirige al dashboard después de autenticación

**Solución**: 
Esto es esperado ahora. Después de hacer login exitoso, la función `loginUser()` maneja la redirección. Verifica que esta función incluya:

```javascript
await signInWithEmailAndPassword(auth, email, password);
// ... verificación de email ...
window.location.href = "/dashboard";
```

### Problema: Logout redirige pero vuelve al dashboard

**Solución**: 
Verifica que ambos archivos (dashboard.html y perfil.html) tengan el logout actualizado con `?logout=true`.

## Referencias

- Firebase Auth Documentation: https://firebase.google.com/docs/auth/web/start
- Firebase onAuthStateChanged: https://firebase.google.com/docs/auth/web/manage-users#get_the_currently_signed-in_user
