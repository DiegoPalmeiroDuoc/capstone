# Intexta Web Client - Cliente Web

Sistema web para gestión de documentos con procesamiento automático y chatbot de WhatsApp.

## 🚀 Inicio Rápido

### 1. Instalar dependencias
```bash
cd cliente_web
pip install -r ../requirements.txt
```

### 2. Configurar Firebase
El archivo `firebase_config.py` ya está configurado con las credenciales del proyecto.

### 3. Ejecutar servidor de desarrollo
```bash
python manage.py runserver
```

### 4. Acceder a la aplicación
- **Inicio**: http://localhost:8000/
- **Login**: http://localhost:8000/login
- **Dashboard**: http://localhost:8000/dashboard (requiere autenticación)

---

## 📁 Estructura del Proyecto

```
cliente_web/
├── manage.py                 # Django management script
├── db.sqlite3               # Base de datos local (desarrollo)
├── firebase_config.py       # Configuración de Firebase
├── intexta_web/            # Configuración principal Django
│   ├── settings.py         # Settings del proyecto
│   ├── urls.py            # URLs principales
│   └── wsgi.py            # WSGI config
└── core/                   # App principal
    ├── models.py          # Modelos (no usa ORM de Django)
    ├── views.py           # Vistas y API endpoints
    ├── urls.py            # URLs de la app
    ├── static/            # Archivos estáticos
    │   ├── css/
    │   │   ├── estilos.css      # CSS principal (mejorado)
    │   │   └── estilos.old.css  # Backup del CSS anterior
    │   ├── img/
    │   │   └── logo.png         # Logo de Intexta
    │   └── js/
    │       └── main.js          # JavaScript general
    └── templates/         # Plantillas HTML
        ├── index.html     # Landing page (mejorada)
        ├── login.html     # Login/Registro (mejorado)
        ├── dashboard.html # Panel principal (mejorado)
        ├── perfil.html    # Perfil de usuario
        └── home.html      # Home alternativo
```

---

## 🎨 UI/UX - Mejoras Recientes

### CSS Moderno (estilos.css)
- ✅ **Design System completo** con variables CSS
- ✅ **Paleta de colores** profesional (Indigo + Amber)
- ✅ **Componentes reutilizables** (cards, botones, forms)
- ✅ **Animaciones suaves** (slideIn, fadeIn, pulse)
- ✅ **Responsive design** (móvil/tablet/desktop)
- ✅ **Dark mode ready** (fácil implementación)

### Dashboard Mejorado
- ✅ **Estadísticas en tiempo real** (4 widgets)
- ✅ **Sistema de filtros** (Todos, Procesados, Pendientes, Errores)
- ✅ **Toast notifications** elegantes
- ✅ **Progress bar** en subida de archivos
- ✅ **Auto-refresh** cada 30 segundos
- ✅ **Validación de archivos** (tipo y tamaño)
- ✅ **Cards interactivas** con estados visuales

### Landing Page Completa
- ✅ **Hero section** impactante
- ✅ **6 features cards** detalladas
- ✅ **4 casos de uso** explicados
- ✅ **Sección de contacto** completa
- ✅ **Animaciones AOS** (scroll animations)
- ✅ **Footer profesional**

### Login/Registro Mejorado
- ✅ **Validación completa** de formularios
- ✅ **Loading states** durante procesos
- ✅ **Toggle password** (mostrar/ocultar)
- ✅ **Toast notifications** personalizadas
- ✅ **Enter key** para enviar
- ✅ **Mensajes de error** específicos

---

## 🔥 Firebase - Configuración

### Servicios utilizados
- **Authentication**: Login con email/password
- **Firestore**: Base de datos NoSQL para documentos y usuarios
- **Storage**: Almacenamiento de archivos PDF, DOCX, XLSX, PPTX

### Colecciones Firestore

#### `documentos`
```javascript
{
  nombre: string,           // Nombre del archivo
  url: string,              // URL de Storage
  tipo: string,             // MIME type
  tamaño: number,           // Tamaño en bytes
  fechaSubida: string,      // ISO timestamp
  usuarioId: string,        // UID del usuario
  descripcion: string,      // Descripción opcional
  estado: string,           // pendiente | procesando | procesado | error
  caracteresTotales: number // Total caracteres extraídos (opcional)
}
```

#### `usuarios`
```javascript
{
  nombre: string,
  email: string,
  rol: string,              // cliente | admin
  fechaRegistro: string,
  emailVerificado: boolean,
  telefono: string          // Opcional, para WhatsApp
}
```

---

## 🛠️ API Endpoints (Django)

### Endpoints disponibles en `core/views.py`

#### `GET /api/document-status/<doc_id>/`
Obtiene el estado de procesamiento de un documento.

**Response**:
```json
{
  "estado": "procesado",
  "caracteresTotales": 15234,
  "fechaProcesamiento": "2024-12-10T10:30:00Z"
}
```

#### `POST /api/process-document/`
Fuerza el procesamiento de un documento específico.

**Request**:
```json
{
  "doc_id": "abc123"
}
```

#### `GET /api/search-documents/`
Busca documentos por query string.

**Query params**: `?q=busqueda`

#### `POST /api/trigger-processor/`
Inicia el procesador de documentos en segundo plano.

#### `POST /api/update-phone/`
Actualiza el número de WhatsApp del usuario.

**Request**:
```json
{
  "phone": "+56912345678"
}
```

#### `GET /api/user-documents/`
Lista todos los documentos del usuario autenticado.

---

## 📱 Integración con componentes

### Conexión con ETL (`etl.py`)
El ETL procesa documentos desde 3 fuentes:
1. **Firebase Storage** - `gs://bucket/path/file.pdf`
2. **HTTP URLs** - `https://example.com/file.pdf`
3. **Archivos locales** - `/path/to/file.pdf`

### Conexión con Chatbot (`intexta_chatbot.py`)
El chatbot lee documentos procesados desde Firestore:
- Autentica usuarios por WhatsApp
- Busca documentos del usuario
- Construye contexto para DeepSeek AI
- Responde preguntas basadas en los documentos

### Conexión con Procesador (`document_processor.py`)
El procesador escucha cambios en Firestore:
- Detecta documentos con estado `pendiente`
- Ejecuta ETL para extraer texto
- Actualiza estado a `procesado` o `error`
- Registra caracteres totales extraídos

---

## 🎯 Flujo Completo del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│  USUARIO                                                        │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────────────┐
│  1. LOGIN / REGISTRO                                            │
│     - Email + Password                                          │
│     - Verificación de email                                     │
│     - Creación perfil Firestore                                 │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────────────┐
│  2. DASHBOARD                                                   │
│     - Ver estadísticas                                          │
│     - Subir documento (PDF/DOCX/XLSX/PPTX)                     │
│     - Archivo → Firebase Storage                                │
│     - Registro → Firestore (estado: pendiente)                  │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────────────┐
│  3. PROCESAMIENTO AUTOMÁTICO                                    │
│     - document_processor.py detecta documento pendiente         │
│     - Descarga desde Storage                                    │
│     - etl.py extrae texto                                       │
│     - Actualiza Firestore (estado: procesado)                   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────────────┐
│  4. CHATBOT WHATSAPP                                            │
│     - Usuario envía mensaje a WhatsApp                          │
│     - intexta_chatbot.py recibe vía Twilio                      │
│     - Busca documentos procesados del usuario                   │
│     - Construye contexto con documentos                         │
│     - DeepSeek AI genera respuesta                              │
│     - Responde por WhatsApp                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔐 Seguridad

### Autenticación
- Firebase Authentication (email/password)
- Verificación de email obligatoria
- Protección de rutas sensibles

### Autorización
- Documentos solo accesibles por su propietario
- Storage rules configuradas en `storage.rules`
- Firestore rules en `firestore.rules`

### Validación
- Frontend: Tipo y tamaño de archivos
- Backend: Verificación de permisos
- Firebase: Security rules

---

## 🐛 Debugging

### Ver logs de Django
```bash
python manage.py runserver --verbosity 2
```

### Verificar conexión Firebase
```python
from firebase_config import db
print(db.collection('documentos').limit(1).get())
```

### Probar ETL manualmente
```python
from etl import procesar_archivo
resultado = procesar_archivo('ruta/al/archivo.pdf')
print(resultado)
```

---

## 📊 Monitoreo

### Estadísticas en Dashboard
- **Total documentos**: Cuenta de todos los docs del usuario
- **Procesados**: Documentos con estado `procesado`
- **Pendientes**: Documentos con estado `pendiente`
- **Errores**: Documentos con estado `error`

### Auto-refresh
El dashboard se actualiza automáticamente cada 30 segundos para mostrar:
- Cambios de estado
- Nuevos documentos procesados
- Errores de procesamiento

---

## 🚀 Deployment

### Variables de entorno necesarias
```bash
# Firebase (ya configuradas en firebase_config.py)
FIREBASE_API_KEY=...
FIREBASE_AUTH_DOMAIN=...
FIREBASE_PROJECT_ID=...
FIREBASE_STORAGE_BUCKET=...

# Django
DJANGO_SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=tudominio.com
```

### Collectstatic
```bash
python manage.py collectstatic --noinput
```

### Migración (si usas SQLite para algo)
```bash
python manage.py migrate
```

---

## 📚 Recursos Adicionales

### Documentación relacionada
- [README principal](../README.md)
- [Arquitectura del sistema](../docs/ARCHITECTURE.md)
- [Mejoras de UI](../docs/UI_IMPROVEMENTS.md)
- [Comandos útiles](../docs/COMMANDS.md)
- [Guía rápida](../docs/QUICKSTART.md)

### Librerías utilizadas
- **Django**: 5.2.7
- **Firebase Admin**: 6.6.0
- **Font Awesome**: 6.4.0 (icons)
- **AOS**: 2.3.4 (animations)

---

## 🤝 Contribuir

### Para agregar una nueva página
1. Crear template en `core/templates/`
2. Agregar vista en `core/views.py`
3. Registrar URL en `core/urls.py`
4. Usar estilos de `estilos.css`

### Para agregar un nuevo componente CSS
1. Usar variables CSS existentes
2. Seguir naming convention BEM
3. Agregar responsive breakpoints
4. Documentar en `UI_IMPROVEMENTS.md`

---

## 📝 Notas Importantes

### Archivos estáticos
Los archivos en `static/` son servidos por Django en desarrollo.  
En producción, usar servidor web (Nginx/Apache) o CDN.

### Base de datos
Django usa SQLite solo para sesiones.  
Los datos principales están en Firebase Firestore.

### Procesamiento de archivos
El procesamiento es **asíncrono** y **automático**.  
No bloquea la interfaz de usuario.

---

## 🎓 Ejemplos de Código

### Subir archivo desde JavaScript
```javascript
const file = document.getElementById('fileInput').files[0];
const fileRef = ref(storage, `clientes/${uid}/${file.name}`);

await uploadBytes(fileRef, file);
const url = await getDownloadURL(fileRef);

await addDoc(collection(db, "documentos"), {
  nombre: file.name,
  url: url,
  usuarioId: uid,
  estado: 'pendiente'
});
```

### Leer documentos del usuario
```javascript
const q = query(
  collection(db, "documentos"), 
  where("usuarioId", "==", uid)
);
const snapshot = await getDocs(q);

snapshot.forEach(doc => {
  console.log(doc.id, doc.data());
});
```

### Mostrar toast notification
```javascript
showToast("Operación exitosa", "success");
showToast("Ha ocurrido un error", "error");
showToast("Atención", "warning");
showToast("Información", "info");
```

---

## 🔧 Solución de Problemas

### "No module named 'firebase_admin'"
```bash
pip install firebase-admin
```

### "Static files not found"
```bash
python manage.py collectstatic
```

### "CSRF verification failed"
Agregar en `settings.py`:
```python
CSRF_TRUSTED_ORIGINS = ['https://tudominio.com']
```

### "Firebase permission denied"
Verificar `firestore.rules` y `storage.rules`

---

## 📞 Soporte

Para dudas o problemas:
- **Email**: contacto@intexta.com
- **Documentación**: Ver carpeta `docs/`
- **Issues**: Crear issue en el repositorio

---

**Última actualización**: Diciembre 2024  
**Versión**: 2.0  
**Mantenido por**: Equipo Intexta
