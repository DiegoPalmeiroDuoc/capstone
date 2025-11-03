# 🏗️ Arquitectura Técnica de Intexta

## Diagrama General del Sistema

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INTEXTA - ARQUITECTURA                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         CAPA DE PRESENTACIÓN                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │   Landing    │  │  Dashboard   │  │    Perfil    │                 │
│  │     Page     │  │   (Gestión   │  │   Usuario    │                 │
│  │              │  │  Documentos) │  │              │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
│         │                  │                  │                         │
│         └──────────────────┴──────────────────┘                         │
│                            │                                            │
│                  Django Templates + HTML/CSS/JS                         │
│                            │                                            │
└────────────────────────────┼────────────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────────────┐
│                    CAPA DE APLICACIÓN (Django)                          │
├────────────────────────────┼────────────────────────────────────────────┤
│                            ▼                                            │
│   ┌─────────────────────────────────────────────────────────┐          │
│   │              Django Views & API Endpoints               │          │
│   ├─────────────────────────────────────────────────────────┤          │
│   │  • index()           • api_list_docs()                  │          │
│   │  • login_view()      • api_document_status()            │          │
│   │  • dashboard_view()  • api_process_document()           │          │
│   │  • perfil_view()     • api_search_documents()           │          │
│   │                      • api_trigger_processor()          │          │
│   └─────────────────────────────────────────────────────────┘          │
│                            │                                            │
└────────────────────────────┼────────────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────────────┐
│                   CAPA DE SERVICIOS                                     │
├────────────────────────────┴────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │  ETL (etl.py)    │  │  Procesador      │  │  Chatbot         │     │
│  │                  │  │  (document_      │  │  (intexta_       │     │
│  │ • Descarga docs  │  │   processor.py)  │  │   chatbot.py)    │     │
│  │ • Extrae texto   │  │                  │  │                  │     │
│  │ • Normaliza      │  │ • Detecta nuevos │  │ • Recibe msg     │     │
│  │ • Soporta:       │  │ • Llama a ETL    │  │ • Consulta docs  │     │
│  │   - PDF          │  │ • Actualiza BD   │  │ • Llama AI       │     │
│  │   - DOCX         │  │ • Gestiona       │  │ • Responde       │     │
│  │   - XLSX         │  │   errores        │  │                  │     │
│  │   - PPTX         │  │                  │  │                  │     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
│         │                      │                      │                │
└─────────┼──────────────────────┼──────────────────────┼────────────────┘
          │                      │                      │
┌─────────┼──────────────────────┼──────────────────────┼────────────────┐
│         │           CAPA DE INTEGRACIÓN              │                 │
├─────────┼──────────────────────┼──────────────────────┼─────────────────┤
│         ▼                      ▼                      ▼                 │
│  ┌─────────────┐        ┌─────────────┐       ┌─────────────┐         │
│  │   Firebase  │        │   Firebase  │       │   Twilio    │         │
│  │   Storage   │◄───────┤  Firestore  │──────►│  WhatsApp   │         │
│  │             │        │             │       │     API     │         │
│  │ Almacena    │        │ Guarda:     │       │             │         │
│  │ archivos    │        │ • Metadata  │       │ Envía/Recibe│         │
│  │ originales  │        │ • Contenido │       │  mensajes   │         │
│  │             │        │ • Estados   │       │             │         │
│  └─────────────┘        └─────────────┘       └─────────────┘         │
│                                │                      │                │
│                                │                      │                │
│                         ┌──────┴──────┐       ┌──────┴──────┐         │
│                         │  Firebase   │       │  DeepSeek   │         │
│                         │    Auth     │       │     API     │         │
│                         │             │       │             │         │
│                         │ Autentica   │       │ Genera      │         │
│                         │  usuarios   │       │ respuestas  │         │
│                         └─────────────┘       └─────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Flujo de Datos Detallado

### 1️⃣ Flujo de Subida y Procesamiento de Documentos

```
Usuario Web
    │
    ├─► 1. Selecciona archivo (PDF/DOCX/XLSX/PPTX)
    │
    ├─► 2. Click "Subir documento"
    │
    ▼
Firebase Storage
    │
    ├─► 3. Almacena archivo en: clientes/{userId}/{filename}
    │
    ├─► 4. Genera URL pública
    │
    ▼
Firestore (Colección: documentos)
    │
    ├─► 5. Guarda documento:
    │       {
    │         nombre: "archivo.pdf",
    │         url: "https://firebasestorage...",
    │         tipo: "application/pdf",
    │         fechaSubida: "2025-11-02T...",
    │         usuarioId: "abc123",
    │         descripcion: "...",
    │         estado: "pendiente"  ◄── IMPORTANTE
    │       }
    │
    ▼
Document Processor (cada 10 segundos)
    │
    ├─► 6. Query: WHERE estado == "pendiente"
    │
    ├─► 7. Detecta nuevo documento
    │
    ├─► 8. Actualiza estado: "procesando"
    │
    ├─► 9. Descarga de Firebase Storage
    │
    ├─► 10. Llama a ETL:
    │        - extract_pdf()
    │        - extract_docx()
    │        - extract_xlsx()
    │        - extract_pptx()
    │
    ├─► 11. Normaliza texto extraído
    │
    ├─► 12. Actualiza Firestore:
    │        {
    │          contenidoProcesado: "Texto completo...",
    │          estado: "procesado",
    │          fechaProcesado: "2025-11-02T...",
    │          caracteresTotales: 15000
    │        }
    │
    ▼
Dashboard (Auto-refresh)
    │
    └─► 13. Muestra estado "Procesado" ✅
```

### 2️⃣ Flujo de Consulta por WhatsApp

```
Usuario WhatsApp
    │
    ├─► 1. Envía mensaje: "¿Cuál es el precio del producto X?"
    │
    ▼
Twilio API
    │
    ├─► 2. POST /webhook
    │       Body: "¿Cuál es el precio del producto X?"
    │       From: "whatsapp:+56912345678"
    │
    ▼
Intexta Chatbot
    │
    ├─► 3. Extrae número de teléfono
    │
    ├─► 4. Busca usuario en Firestore:
    │       Query: WHERE telefono == "+56912345678"
    │
    ├─► 5. Obtiene userId
    │
    ├─► 6. Busca documentos del usuario:
    │       Query: WHERE usuarioId == userId
    │              AND estado == "procesado"
    │
    ├─► 7. Obtiene contenido procesado de todos los docs
    │
    ├─► 8. Construye contexto para IA:
    │       "=== DOCUMENTOS DEL USUARIO ===
    │        --- catalogo.pdf ---
    │        Producto X: $50.000
    │        Producto Y: $75.000
    │        ..."
    │
    ├─► 9. Llama a DeepSeek API:
    │       POST https://api.deepseek.com/v1/chat/completions
    │       {
    │         model: "deepseek-chat",
    │         messages: [
    │           {role: "system", content: "Eres asistente..."},
    │           {role: "system", content: CONTEXTO},
    │           {role: "user", content: "¿Precio producto X?"}
    │         ]
    │       }
    │
    ├─► 10. DeepSeek responde:
    │        "El precio del Producto X es $50.000 según el catálogo."
    │
    ├─► 11. Guarda en historial de conversación
    │
    ├─► 12. Crea TwiML response
    │
    ▼
Twilio API
    │
    └─► 13. Envía mensaje a WhatsApp del usuario
```

### 3️⃣ Estructura de Datos en Firestore

```javascript
// Colección: documentos
{
  "doc_id_123": {
    nombre: "catalogo_productos.pdf",
    url: "https://firebasestorage.googleapis.com/...",
    tipo: "application/pdf",
    fechaSubida: "2025-11-02T10:30:00Z",
    usuarioId: "user_abc123",
    descripcion: "Catálogo oficial de productos",
    
    // Procesamiento
    estado: "procesado",  // pendiente | procesando | procesado | error
    fechaProcesamiento: "2025-11-02T10:30:05Z",
    fechaProcesado: "2025-11-02T10:30:15Z",
    
    // Contenido extraído
    contenidoProcesado: "Texto completo del PDF...",
    caracteresTotales: 15000,
    
    // Errores (si aplica)
    errorMensaje: null
  }
}

// Colección: usuarios
{
  "user_abc123": {
    uid: "user_abc123",
    telefono: "+56912345678",
    fechaActualizacion: SERVER_TIMESTAMP
  }
}
```

## Componentes Técnicos

### ETL (`etl.py`)
```python
# Funciones principales:
- parse_drive_url()          # Detecta tipo de URL de Google Drive
- download_from_firebase()   # Descarga de Firebase Storage
- download_from_http_url()   # Descarga de URL HTTP
- extract_pdf()              # Extrae texto de PDF
- extract_docx()             # Extrae texto de Word
- extract_xlsx()             # Extrae texto de Excel
- extract_pptx()             # Extrae texto de PowerPoint
- normalize_text()           # Limpia y normaliza texto
- choose_extractor()         # Selecciona extractor según formato
```

### Document Processor (`document_processor.py`)
```python
# Clase principal: DocumentProcessor
- initialize_firebase()           # Conecta con Firebase
- download_from_storage()         # Descarga archivo
- extract_storage_path_from_url() # Extrae ruta de Storage
- process_document()              # Procesa un documento
- process_pending_documents()     # Procesa todos los pendientes
- listen_for_changes()            # Escucha cambios (loop)
- reprocess_document()            # Reprocesa un doc específico
```

### Chatbot (`intexta_chatbot.py`)
```python
# Clase principal: IntextaChatbot
- get_user_documents()              # Obtiene docs del usuario
- get_user_by_phone()               # Busca user por teléfono
- build_context_from_documents()    # Construye contexto para IA
- call_deepseek_api()               # Llama a DeepSeek
- process_message()                 # Procesa mensaje entrante
- get_help_message()                # Mensaje de ayuda
- get_authentication_message()      # Msg de autenticación
```

### Django Views (`core/views.py`)
```python
# Endpoints de API:
- api_list_docs()           # GET  /api/docs/?uid=...
- api_document_status()     # GET  /api/docs/status/?uid=...
- api_process_document()    # POST /api/docs/process/
- api_search_documents()    # GET  /api/docs/search/?uid=...&query=...
- api_trigger_processor()   # POST /api/processor/trigger/
- api_update_phone()        # POST /api/user/update-phone/
```

## Tecnologías Utilizadas

| Componente | Tecnología | Versión |
|------------|------------|---------|
| Backend Web | Django | 5.2.7 |
| Chatbot | Flask | 3.0.0 |
| Base de datos | Firestore | - |
| Almacenamiento | Firebase Storage | - |
| Autenticación | Firebase Auth | - |
| WhatsApp | Twilio API | 8.10.0 |
| IA | DeepSeek API | v1 |
| PDF | pdfplumber | 0.11.4 |
| Word | python-docx | 1.1.2 |
| Excel | pandas + openpyxl | 2.2.2 |
| PowerPoint | python-pptx | 1.0.2 |

## Seguridad

### Autenticación
- Firebase Authentication para usuarios web
- Número de teléfono para WhatsApp
- Tokens de sesión para API

### Autorización
- Firestore Rules: solo el dueño puede acceder a sus documentos
- Storage Rules: solo el dueño puede leer/escribir sus archivos
- API endpoints verifican UID del usuario

### Datos Sensibles
- Credenciales en archivos .json (no en código)
- API Keys en variables de entorno
- .gitignore protege archivos sensibles

## Escalabilidad

### Horizontal
- Django puede correr en múltiples instancias (load balancer)
- Procesador puede tener múltiples workers
- Chatbot puede escalar con contenedores

### Vertical
- Firebase escala automáticamente
- DeepSeek API maneja alto volumen
- Twilio soporta millones de mensajes

### Optimizaciones
- Caché de documentos procesados
- Índices en Firestore para queries rápidas
- Lazy loading en frontend
- Compresión de texto procesado

---

**Última actualización**: 2 de noviembre, 2025
