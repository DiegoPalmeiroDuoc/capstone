# 🔐 Configuración de Credenciales - Intexta

Este documento explica cómo están configuradas las credenciales del proyecto para que funcionen localmente pero NO se suban a Git.

---

## ✅ Estado Actual de Credenciales

### 1. **DeepSeek API Key** 
- **Ubicación**: `.env` (línea: `DEEPSEEK_API_KEY`)
- **Valor actual**: `sk-5d84c8f184c14de89a58c5c4da59889a`
- **Usado en**: `intexta_chatbot.py`
- **Estado Git**: ✅ Ignorado (`.env` en `.gitignore`)

### 2. **Firebase Admin SDK**
- **Ubicación**: `cliente_web/admin-doc-ia-firebase-adminsdk-fbsvc-82d2fcac61.json`
- **Usado en**: `cliente_web/firebase_config.py`
- **Estado Git**: ✅ Ignorado (`*firebase*.json` en `.gitignore`)

### 3. **Firebase Client Config**
- **Ubicación**: Hardcodeado en templates HTML (`login.html`, `dashboard.html`, `perfil.html`)
- **Estado**: ✅ OK (config público del cliente, no sensible)

### 4. **Twilio Credentials** (Opcional)
- **Ubicación**: `.env` 
- **Variables**: 
  - `TWILIO_ACCOUNT_SID`
  - `TWILIO_AUTH_TOKEN`
  - `TWILIO_WHATSAPP_NUMBER`
- **Estado**: ⚠️ Pendiente de configurar (actualmente usa valores de ejemplo)

---

## 📝 Archivos de Credenciales

### ✅ Ignorados por Git (Locales)

```
.env                                          ← Variables de entorno
cliente_web/*firebase-adminsdk*.json          ← Credenciales Firebase Admin
*.log                                         ← Logs
__pycache__/                                  ← Caché Python
venv/                                         ← Entorno virtual
```

### ✅ Incluidos en Git (Configuración pública)

```
.env.example                                  ← Plantilla de .env
firebase.json                                 ← Config pública Firebase
firestore.rules                               ← Reglas de seguridad
firestore.indexes.json                        ← Índices de Firestore
```

---

## 🔧 Cómo Funciona

### 1. `.gitignore` - Protección

```ignore
# Variables de entorno (NUNCA subir)
.env
.env.local

# Credenciales Firebase (NUNCA subir)
*firebase*.json              ← Ignora TODOS los JSON de Firebase
!firebase.json               ← EXCEPTO firebase.json (config pública)
!firestore.rules             ← EXCEPTO reglas
!firestore.indexes.json      ← EXCEPTO índices
```

### 2. `.env.example` - Plantilla

El archivo `.env.example` es una **plantilla** que SÍ se sube a Git y muestra qué variables se necesitan, pero con valores de ejemplo:

```env
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. `.env` - Credenciales Reales

El archivo `.env` contiene tus credenciales REALES y NO se sube a Git:

```env
DEEPSEEK_API_KEY=sk-5d84c8f184c14de89a58c5c4da59889a  ← TU KEY REAL
```

---

## ✅ Verificación de Seguridad

### Comando 1: Ver archivos ignorados

```bash
git status --ignored
```

**Debe mostrar**:
```
Ignored files:
  .env
  venv/
  __pycache__/
  cliente_web/admin-doc-ia-firebase-adminsdk-*.json
```

### Comando 2: Ver qué archivos están en Git

```bash
git ls-files | grep -E "(\.env|firebase-adminsdk)"
```

**Debe mostrar**: NADA (vacío) - ninguna credencial en Git

### Comando 3: Ver archivos que se subirían

```bash
git add . --dry-run
```

**NO debe incluir**: `.env` ni `*firebase-adminsdk*.json`

---

## 🚀 Setup para Nuevos Desarrolladores

Si alguien más clona el repositorio, debe:

### 1. Copiar `.env.example` a `.env`

```bash
cp .env.example .env
```

### 2. Editar `.env` con sus credenciales reales

```bash
# Abrir con editor de texto
notepad .env

# Llenar con valores reales:
DEEPSEEK_API_KEY=sk-TU_KEY_AQUI
TWILIO_ACCOUNT_SID=AC_TU_SID_AQUI
```

### 3. Obtener credenciales de Firebase

- Ir a Firebase Console → Project Settings → Service Accounts
- Generar nueva clave privada
- Guardar como `cliente_web/admin-doc-ia-firebase-adminsdk-*.json`

---

## ⚠️ IMPORTANTE: Nunca Hacer

❌ **NO** hagas `git add .env`
❌ **NO** hagas `git add *firebase-adminsdk*.json`
❌ **NO** pongas credenciales en archivos de documentación
❌ **NO** hagas commit de archivos con credenciales hardcodeadas

---

## ✅ Estado Actual del Proyecto

```
✅ .env creado localmente con DeepSeek API Key
✅ Firebase credentials en cliente_web/
✅ .gitignore configurado correctamente
✅ Credenciales NO están en Git
✅ .env.example disponible para otros desarrolladores
✅ Sistema funcional para pruebas locales
```

---

## 🔄 Actualizar Credenciales

### Si cambias tu API Key de DeepSeek:

1. Edita `.env`:
   ```env
   DEEPSEEK_API_KEY=sk-NUEVA_KEY_AQUI
   ```

2. Reinicia el chatbot:
   ```bash
   # En terminal del chatbot, presiona Ctrl+C
   # Luego vuelve a ejecutar:
   python intexta_chatbot.py
   ```

### Si cambias credenciales de Firebase:

1. Descarga el nuevo JSON desde Firebase Console
2. Reemplaza el archivo en `cliente_web/`
3. **NO** hagas commit del nuevo archivo

---

## 📞 Soporte

Si tienes problemas con credenciales:
1. Verifica que `.env` existe: `ls .env`
2. Verifica que está ignorado: `git status --ignored`
3. Verifica que las variables se cargan: agrega `print(os.getenv("DEEPSEEK_API_KEY"))` en el código

---

**Última actualización**: 3 de Noviembre, 2025
