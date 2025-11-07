# 📊 Diagrama de Flujo - Sistema Intexta

Este documento contiene diagramas de flujo completos del sistema Intexta, desde la carga de documentos hasta la consulta por WhatsApp.

---

## 🔄 Flujo Completo del Sistema

```mermaid
flowchart TD
    Start([👤 Usuario]) --> Login{¿Autenticado?}
    
    Login -->|No| Register[📝 Registro/Login<br/>Firebase Auth]
    Register --> EmailVerify[📧 Verificación Email]
    EmailVerify --> Login
    
    Login -->|Sí| Dashboard[📊 Dashboard]
    
    Dashboard --> Choice{Acción del<br/>Usuario}
    
    Choice -->|Subir Documento| Upload[📤 Seleccionar Archivo<br/>PDF/DOCX/XLSX/PPTX]
    Choice -->|Vincular WhatsApp| Profile[👤 Ir a Perfil]
    Choice -->|Consultar| WA[📱 WhatsApp]
    
    %% FLUJO DE SUBIDA Y PROCESAMIENTO
    Upload --> ValidateFile{¿Formato<br/>Válido?}
    ValidateFile -->|No| ErrorMsg[❌ Mostrar Error]
    ErrorMsg --> Dashboard
    
    ValidateFile -->|Sí| FirebaseUpload[☁️ Subir a Firebase Storage<br/>clientes/userId/archivo]
    FirebaseUpload --> CreateDoc[📝 Crear Documento en Firestore<br/>estado: pendiente]
    CreateDoc --> ShowPending[⏳ Mostrar: Pendiente]
    
    ShowPending --> AutoProcess{Procesador<br/>Automático<br/>Activo?}
    
    AutoProcess -->|No| ManualTrigger[⚙️ Trigger Manual<br/>document_processor.py]
    AutoProcess -->|Sí| WaitInterval[⏰ Esperar 30s]
    
    ManualTrigger --> ETLStart
    WaitInterval --> CheckPending{¿Hay Docs<br/>Pendientes?}
    CheckPending -->|No| WaitInterval
    CheckPending -->|Sí| ETLStart
    
    ETLStart[🔄 Iniciar ETL<br/>estado: procesando] --> DownloadFile[📥 Descargar desde Storage]
    DownloadFile --> DetectType{Tipo de<br/>Archivo}
    
    DetectType -->|PDF| ExtractPDF[📄 pdfplumber<br/>extraer texto]
    DetectType -->|DOCX| ExtractDOCX[📝 python-docx<br/>extraer texto]
    DetectType -->|XLSX| ExtractXLSX[📊 openpyxl<br/>extraer datos]
    DetectType -->|PPTX| ExtractPPTX[🎨 python-pptx<br/>extraer texto]
    DetectType -->|TXT/CSV| ExtractTXT[📃 leer texto plano]
    
    ExtractPDF --> ProcessText[🧹 Limpiar y Procesar<br/>Texto]
    ExtractDOCX --> ProcessText
    ExtractXLSX --> ProcessText
    ExtractPPTX --> ProcessText
    ExtractTXT --> ProcessText
    
    ProcessText --> SaveFirestore[💾 Guardar en Firestore<br/>contenidoProcesado<br/>estado: procesado]
    SaveFirestore --> UpdateDashboard[🔄 Actualizar Dashboard<br/>✅ Procesado]
    UpdateDashboard --> Dashboard
    
    %% FLUJO DE VINCULACIÓN WHATSAPP
    Profile --> EnterPhone[📱 Ingresar Teléfono<br/>ej: 930104972]
    EnterPhone --> SavePhone[💾 Guardar en Firestore<br/>usuarios/uid/telefono]
    SavePhone --> PhoneSaved[✅ Teléfono Vinculado]
    PhoneSaved --> Dashboard
    
    %% FLUJO DE CONSULTA WHATSAPP
    WA --> SendMessage[💬 Enviar Mensaje<br/>a Twilio Sandbox]
    SendMessage --> TwilioReceive[📨 Twilio Recibe<br/>Mensaje]
    TwilioReceive --> WebhookCall[🌐 POST a Webhook<br/>ngrok → localhost:5000]
    
    WebhookCall --> ChatbotReceive[🤖 intexta_chatbot.py<br/>Recibe Mensaje]
    ChatbotReceive --> ExtractPhone[📞 Extraer Número<br/>from: whatsapp:+56930104972]
    
    ExtractPhone --> CheckAuth{¿Usuario<br/>Autenticado?}
    
    CheckAuth -->|No| SearchUser[🔍 Buscar en Firestore<br/>usuarios.telefono]
    SearchUser --> UserFound{¿Usuario<br/>Encontrado?}
    
    UserFound -->|No| SendAuthMsg[📤 Mensaje: Registrarse<br/>y Vincular Teléfono]
    SendAuthMsg --> TwilioSend[📲 Twilio Envía<br/>Respuesta]
    TwilioSend --> UserReceives[📱 Usuario Recibe<br/>Mensaje]
    UserReceives --> End([Fin])
    
    UserFound -->|Sí| CacheUser[💾 Cachear Usuario<br/>usuarios_autenticados]
    CacheUser --> CheckAuth
    
    CheckAuth -->|Sí| GetDocs[📚 Obtener Documentos<br/>Firestore Query]
    GetDocs --> HasDocs{¿Tiene<br/>Documentos?}
    
    HasDocs -->|No| SendNoDocsMsg[📤 Mensaje: Subir<br/>Documentos]
    SendNoDocsMsg --> TwilioSend
    
    HasDocs -->|Sí| BuildContext[🧠 Construir Contexto<br/>de Documentos]
    BuildContext --> CheckCommand{¿Comando<br/>Especial?}
    
    CheckCommand -->|/ayuda| SendHelp[📖 Mensaje de Ayuda]
    CheckCommand -->|/reset| ResetConv[🔄 Reiniciar<br/>Conversación]
    CheckCommand -->|Pregunta| PrepareAI
    
    SendHelp --> TwilioSend
    ResetConv --> TwilioSend
    
    PrepareAI[🎯 Preparar Prompt<br/>para IA] --> BuildMessages[📝 Construir Mensajes<br/>System + Context + User]
    BuildMessages --> CallDeepSeek[🚀 Llamar DeepSeek API<br/>deepseek-chat]
    
    CallDeepSeek --> DeepSeekProcess[🤖 IA Procesa<br/>Contexto + Pregunta]
    DeepSeekProcess --> GenerateResponse[✨ Generar Respuesta<br/>Basada en Documentos]
    
    GenerateResponse --> SaveHistory[💾 Guardar en Historial<br/>conversaciones[phone]]
    SaveHistory --> FormatResponse[📝 Formatear Respuesta<br/>para WhatsApp]
    FormatResponse --> TwilioSend
    
    style Start fill:#4CAF50,stroke:#2E7D32,color:#fff
    style End fill:#F44336,stroke:#C62828,color:#fff
    style Dashboard fill:#2196F3,stroke:#1565C0,color:#fff
    style ETLStart fill:#FF9800,stroke:#E65100,color:#fff
    style ChatbotReceive fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style CallDeepSeek fill:#00BCD4,stroke:#006064,color:#fff
    style SaveFirestore fill:#4CAF50,stroke:#2E7D32,color:#fff
```

---

## 📤 Flujo Detallado: Subida de Documentos

```mermaid
flowchart TD
    A([Usuario en Dashboard]) --> B[Click: Subir Archivo]
    B --> C[Seleccionar Archivo<br/>Input type=file]
    C --> D{Validar<br/>Cliente}
    
    D -->|Formato inválido| E[❌ Alert: Formato no soportado]
    E --> A
    
    D -->|Formato válido| F[Crear FormData<br/>+ archivo + metadata]
    F --> G[JavaScript: uploadFile]
    
    G --> H[Obtener Firebase Token<br/>currentUser.getIdToken]
    H --> I[Subir a Firebase Storage<br/>ref: clientes/userId/timestamp_filename]
    
    I --> J{Upload<br/>Success?}
    J -->|Error| K[❌ Mostrar Toast Error]
    K --> A
    
    J -->|Success| L[Obtener Download URL<br/>getDownloadURL]
    L --> M[Crear Documento Firestore<br/>Collection: documentos]
    
    M --> N[Campos del Documento:<br/>- nombre<br/>- url<br/>- usuarioId<br/>- estado: pendiente<br/>- fechaSubida<br/>- tipo]
    
    N --> O[✅ addDoc success]
    O --> P[Toast: Subida Exitosa]
    P --> Q[Recargar Lista<br/>loadFiles]
    Q --> R[Mostrar: Estado Pendiente ⏳]
    
    R --> S{Procesador<br/>Automático?}
    S -->|Activo| T[Esperar próximo ciclo<br/>30 segundos]
    S -->|Inactivo| U[Quedarse en estado<br/>pendiente]
    
    T --> V([Procesamiento ETL])
    
    style A fill:#2196F3,stroke:#1565C0,color:#fff
    style V fill:#FF9800,stroke:#E65100,color:#fff
    style O fill:#4CAF50,stroke:#2E7D32,color:#fff
    style K fill:#F44336,stroke:#C62828,color:#fff
```

---

## ⚙️ Flujo Detallado: Procesamiento ETL

```mermaid
flowchart TD
    Start([document_processor.py]) --> Mode{Modo de<br/>Ejecución}
    
    Mode -->|--mode once| Once[Procesar 1 vez]
    Mode -->|--mode listen| Listen[Loop Infinito]
    
    Once --> Query
    Listen --> Wait[⏰ Sleep interval segundos]
    Wait --> Query
    
    Query[🔍 Query Firestore<br/>estado == pendiente] --> HasDocs{¿Hay<br/>Documentos?}
    
    HasDocs -->|No| Listen
    HasDocs -->|Sí| ProcessLoop[Para cada documento...]
    
    ProcessLoop --> UpdateStatus1[📝 Update Firestore<br/>estado: procesando]
    UpdateStatus1 --> GetURL[Obtener URL del documento]
    GetURL --> Download[📥 Descargar archivo<br/>requests.get URL]
    
    Download --> SaveTemp[💾 Guardar temporal<br/>/tmp/archivo]
    SaveTemp --> DetectExt{Detectar<br/>Extensión}
    
    DetectExt -->|.pdf| CallPDF[ETL.process_pdf<br/>pdfplumber]
    DetectExt -->|.docx| CallDOCX[ETL.process_docx<br/>python-docx]
    DetectExt -->|.xlsx| CallXLSX[ETL.process_excel<br/>openpyxl + pandas]
    DetectExt -->|.pptx| CallPPTX[ETL.process_pptx<br/>python-pptx]
    DetectExt -->|.txt/.csv| CallTXT[ETL.process_text<br/>read + decode]
    
    CallPDF --> ExtractPDF[Extraer texto de páginas<br/>+ tablas + metadata]
    CallDOCX --> ExtractDOCX[Extraer párrafos + tablas<br/>+ estilos]
    CallXLSX --> ExtractXLSX[Leer hojas + celdas<br/>convertir a texto]
    CallPPTX --> ExtractPPTX[Extraer slides + shapes<br/>+ texto]
    CallTXT --> ExtractTXT[Leer contenido<br/>UTF-8/Latin-1]
    
    ExtractPDF --> Clean
    ExtractDOCX --> Clean
    ExtractXLSX --> Clean
    ExtractPPTX --> Clean
    ExtractTXT --> Clean
    
    Clean[🧹 Limpiar Texto<br/>- Espacios múltiples<br/>- Saltos de línea<br/>- Caracteres especiales] --> Format[📝 Formatear<br/>- Estructura<br/>- Secciones<br/>- Metadata]
    
    Format --> Success{Procesamiento<br/>Exitoso?}
    
    Success -->|Error| UpdateError[❌ Update Firestore<br/>estado: error<br/>mensajeError: detalle]
    Success -->|OK| UpdateSuccess[✅ Update Firestore<br/>estado: procesado<br/>contenidoProcesado: texto]
    
    UpdateError --> DeleteTemp
    UpdateSuccess --> DeleteTemp[🗑️ Eliminar archivo temporal]
    
    DeleteTemp --> NextDoc{¿Más<br/>Documentos?}
    NextDoc -->|Sí| ProcessLoop
    NextDoc -->|No| Complete[✅ Procesamiento Completo]
    
    Complete --> ModeCheck{Modo}
    ModeCheck -->|once| End([Fin])
    ModeCheck -->|listen| Listen
    
    style Start fill:#FF9800,stroke:#E65100,color:#fff
    style UpdateSuccess fill:#4CAF50,stroke:#2E7D32,color:#fff
    style UpdateError fill:#F44336,stroke:#C62828,color:#fff
    style End fill:#9E9E9E,stroke:#616161,color:#fff
```

---

## 💬 Flujo Detallado: Chatbot WhatsApp

```mermaid
flowchart TD
    Start([Usuario envía mensaje]) --> Twilio[📨 Twilio Recibe<br/>From: whatsapp:+56930104972<br/>Body: ¿Qué documentos tengo?]
    
    Twilio --> Webhook[🌐 POST a Webhook<br/>https://xxx.ngrok-free.app/webhook]
    Webhook --> Flask[🤖 Flask recibe request<br/>@app.route /webhook POST]
    
    Flask --> Extract[📝 Extraer datos<br/>phone = request.form From<br/>msg = request.form Body]
    Extract --> Normalize[🔧 Normalizar teléfono<br/>whatsapp:+56930104972<br/>→ +56930104972]
    
    Normalize --> CheckCache{¿En caché<br/>usuarios_autenticados?}
    
    CheckCache -->|No| QueryFirestore[🔍 Query Firestore<br/>usuarios.telefono == phone]
    QueryFirestore --> Formats[Probar formatos:<br/>+56930104972<br/>56930104972<br/>930104972]
    
    Formats --> Found{¿Usuario<br/>Encontrado?}
    Found -->|No| ResponseAuth[📤 Respuesta:<br/>Registrarse en web<br/>y vincular teléfono]
    ResponseAuth --> SendTwilio
    
    Found -->|Sí| CacheUser[💾 Cachear:<br/>usuarios_autenticados phone = uid]
    CacheUser --> CheckCache
    
    CheckCache -->|Sí| GetUID[Obtener UID del caché]
    GetUID --> QueryDocs[📚 Query Firestore<br/>documentos.usuarioId == uid<br/>estado == procesado]
    
    QueryDocs --> HasDocs{¿Tiene<br/>Documentos?}
    HasDocs -->|No| ResponseNoDocs[📤 Respuesta:<br/>No tienes documentos<br/>Sube desde la web]
    ResponseNoDocs --> SendTwilio
    
    HasDocs -->|Sí| ExtractContent[📄 Extraer contenidoProcesado<br/>de cada documento]
    ExtractContent --> BuildContext[🧠 Construir contexto:<br/>=== DOC 1 ===<br/>contenido...<br/>=== DOC 2 ===<br/>contenido...]
    
    BuildContext --> CheckSpecial{¿Comando<br/>Especial?}
    CheckSpecial -->|/ayuda| HelpMsg[📖 Mensaje ayuda:<br/>Comandos disponibles]
    CheckSpecial -->|/reset| ResetMsg[🔄 Resetear:<br/>conversaciones phone = ]
    
    HelpMsg --> SendTwilio
    ResetMsg --> SendTwilio
    
    CheckSpecial -->|Pregunta normal| LoadHistory[📜 Cargar historial:<br/>conversaciones phone]
    LoadHistory --> PrepareMessages[📝 Construir mensajes para IA]
    
    PrepareMessages --> SystemPrompt[Sistema:<br/>Eres Intexta, asistente experto<br/>Responde basándote SOLO en docs<br/>Respuestas cortas para WhatsApp]
    
    SystemPrompt --> ContextMsg[Contexto:<br/>Contenido de los documentos]
    ContextMsg --> UserHistory[Historial:<br/>Últimos 5 mensajes<br/>user/assistant]
    UserHistory --> CurrentMsg[Mensaje actual:<br/>user: pregunta]
    
    CurrentMsg --> CallAPI[🚀 POST a DeepSeek API<br/>https://api.deepseek.com/v1/chat]
    CallAPI --> Headers[Headers:<br/>Authorization: Bearer API_KEY<br/>Content-Type: application/json]
    
    Headers --> Payload[Payload:<br/>model: deepseek-chat<br/>messages: array<br/>temperature: 0.7<br/>max_tokens: 500]
    
    Payload --> DeepSeek[🤖 DeepSeek Procesa]
    DeepSeek --> APIResponse[📥 Respuesta API:<br/>choices 0 .message.content]
    
    APIResponse --> SaveConversation[💾 Guardar en historial:<br/>conversaciones phone .append<br/>role: user, content<br/>role: assistant, content]
    
    SaveConversation --> FormatWA[📝 Formatear para WhatsApp:<br/>Max 1600 caracteres<br/>Emojis permitidos]
    
    FormatWA --> SendTwilio[📲 Twilio Response<br/>MessagingResponse]
    SendTwilio --> UserReceives[📱 Usuario recibe<br/>respuesta en WhatsApp]
    
    UserReceives --> End([Fin])
    
    style Start fill:#4CAF50,stroke:#2E7D32,color:#fff
    style CallAPI fill:#00BCD4,stroke:#006064,color:#fff
    style DeepSeek fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style UserReceives fill:#4CAF50,stroke:#2E7D32,color:#fff
    style End fill:#F44336,stroke:#C62828,color:#fff
```

---

## 🔄 Flujo de Estados del Documento

```mermaid
stateDiagram-v2
    [*] --> Pendiente: Documento subido<br/>a Firebase Storage
    
    Pendiente --> Procesando: ETL inicia<br/>procesamiento
    
    Procesando --> Procesado: Extracción exitosa<br/>contenidoProcesado guardado
    Procesando --> Error: Fallo en extracción<br/>mensajeError guardado
    
    Error --> Procesando: Reintentar procesamiento<br/>reset_errors.py
    
    Procesado --> Consultable: Usuario consulta<br/>por WhatsApp
    
    Consultable --> Procesado: Espera nuevas consultas
    
    Procesado --> [*]: Documento eliminado<br/>por usuario
    Error --> [*]: Documento eliminado<br/>por usuario
    Pendiente --> [*]: Documento eliminado<br/>antes de procesar
    
    note right of Pendiente
        estado: "pendiente"
        fechaSubida: timestamp
        usuarioId: uid
    end note
    
    note right of Procesando
        estado: "procesando"
        inicioProcesamiento: timestamp
    end note
    
    note right of Procesado
        estado: "procesado"
        contenidoProcesado: texto
        finProcesamiento: timestamp
    end note
    
    note right of Error
        estado: "error"
        mensajeError: string
        timestampError: timestamp
    end note
```

---

## 🏗️ Arquitectura del Sistema

```mermaid
graph TB
    subgraph "Cliente Web - Frontend"
        A[🌐 Browser] --> B[login.html]
        A --> C[dashboard.html]
        A --> D[perfil.html]
    end
    
    subgraph "Cliente Web - Backend"
        E[⚙️ Django Server<br/>:8000] --> F[views.py]
        F --> G[firebase_config.py]
    end
    
    subgraph "Chatbot WhatsApp"
        H[🤖 Flask Server<br/>:5000] --> I[intexta_chatbot.py]
        I --> J[load_dotenv<br/>.env]
    end
    
    subgraph "ETL Processor"
        K[⚙️ document_processor.py] --> L[etl.py]
        L --> M[pdfplumber<br/>python-docx<br/>openpyxl<br/>python-pptx]
    end
    
    subgraph "Firebase Services"
        N[(🔐 Firebase Auth)]
        O[(📊 Firestore)]
        P[(☁️ Storage)]
    end
    
    subgraph "External APIs"
        Q[🤖 DeepSeek API]
        R[📱 Twilio WhatsApp]
    end
    
    subgraph "Tunnel"
        S[🌐 ngrok<br/>Public URL]
    end
    
    B --> N
    C --> N
    C --> O
    C --> P
    D --> N
    D --> O
    
    G --> N
    G --> O
    G --> P
    
    I --> O
    I --> Q
    
    K --> O
    K --> P
    L --> O
    
    R --> S
    S --> H
    
    style A fill:#2196F3,stroke:#1565C0,color:#fff
    style E fill:#4CAF50,stroke:#2E7D32,color:#fff
    style H fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style K fill:#FF9800,stroke:#E65100,color:#fff
    style N fill:#FFC107,stroke:#F57C00,color:#000
    style O fill:#FFC107,stroke:#F57C00,color:#000
    style P fill:#FFC107,stroke:#F57C00,color:#000
    style Q fill:#00BCD4,stroke:#006064,color:#fff
    style R fill:#25D366,stroke:#128C7E,color:#fff
```

---

## 📋 Resumen de Componentes

### 🌐 Frontend (HTML/CSS/JS)
- **login.html**: Autenticación con Firebase Auth
- **dashboard.html**: Gestión de documentos, subida, visualización
- **perfil.html**: Vinculación de teléfono WhatsApp

### ⚙️ Backend Django (:8000)
- **views.py**: Renderizado de templates
- **firebase_config.py**: Configuración Firebase Admin SDK

### 🤖 Chatbot Flask (:5000)
- **intexta_chatbot.py**: Servidor webhook para WhatsApp
- **Endpoint**: `/webhook` (recibe mensajes de Twilio)
- **Health check**: `/health`

### ⚙️ Procesador ETL
- **document_processor.py**: Orquestador del procesamiento
- **etl.py**: Lógica de extracción por tipo de archivo
- **Modos**: `--mode once` (1 vez) o `--mode listen` (loop)

### ☁️ Firebase
- **Authentication**: Gestión de usuarios
- **Firestore**: Base de datos NoSQL
  - Colección `usuarios`: {uid, email, telefono}
  - Colección `documentos`: {nombre, url, estado, contenidoProcesado, usuarioId}
- **Storage**: Almacenamiento de archivos en `clientes/{userId}/`

### 🔌 APIs Externas
- **DeepSeek**: Generación de respuestas conversacionales
- **Twilio WhatsApp**: Mensajería bidireccional

---

## 🎯 Puntos Clave del Flujo

1. **Autenticación**: Firebase Auth con verificación de email
2. **Subida**: Firebase Storage + documento en Firestore (estado: pendiente)
3. **Procesamiento**: ETL extrae texto y actualiza Firestore (estado: procesado)
4. **Vinculación**: Usuario guarda teléfono en Firestore
5. **Consulta**: WhatsApp → Twilio → ngrok → Flask → DeepSeek → Respuesta

---

**¡Sistema completo de gestión documental con IA! 🚀**
