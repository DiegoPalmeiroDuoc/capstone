# Diagnóstico: WhatsApp No Reconoce Documentos Procesados

## Problema Reportado

El chatbot de WhatsApp no está reconociendo los documentos procesados, impidiendo que los usuarios consulten información a través de Twilio.

## Diagnóstico Realizado

### ✅ Herramienta Creada: `diagnostico_whatsapp.py`

Este script verifica **7 aspectos críticos** del sistema:

1. **Usuarios con WhatsApp vinculado**
2. **Documentos procesados por usuario**
3. **Configuración del chatbot**
4. **Firebase config**
5. **Test de conexión simulada**
6. **Checklist de problemas comunes**
7. **Guía de soluciones**

### Ejecución del Diagnóstico

```bash
python diagnostico_whatsapp.py
```

## Resultados del Diagnóstico

### 🔍 Usuarios Registrados

| Email | UID | WhatsApp | Documentos |
|-------|-----|----------|------------|
| gi.espinosa@duocuc.cl | NlsLIaYnDRXReBE23i2zVcYmikB2 | ✅ +56930104972 | ❌ 0 |
| gionara.espinosa@gmail.com | BODa19voUWT8DxvflAOErlhr3ro2 | ❌ Sin WhatsApp | ✅ 1 procesado |
| gi.espinosa1@duocuc.cl | 2T302y80PCWj6YKbRw3EeXcyux52 | ❌ Sin WhatsApp | ❌ 0 |
| gioespn14@gmail.com | GsoWaPV3Z7RYaUTAlLEKn9g1YfH3 | ❌ Sin WhatsApp | ❌ 0 |
| gioesp14@gmail.com | jCOghExmclW9KGwZENzSUNc2R3D3 | ❌ Sin WhatsApp | ❌ 0 |

### 📄 Documentos en Firestore

| Documento | Estado | Usuario | WhatsApp |
|-----------|--------|---------|----------|
| [Migración Softys] Documentación... | procesado (47,457 chars) | YJloOGOc3UUlGnz79rnZ1NhY53m2 | ❌ Usuario no existe |
| jerar_tab_sap.xlsx | procesado (2,903 chars) | gionara.espinosa@gmail.com | ❌ Sin WhatsApp |
| Plan_Gestion_Riesgos... | procesado (12,207 chars) | Rk1KYLCibWXd4bY3Wrc1ZChGwZ12 | ❌ Usuario no existe |

## Problema Identificado: ❌ Desvinculación Usuario-Documentos

**El usuario con WhatsApp vinculado NO tiene documentos.**

```
Usuario con WhatsApp:     gi.espinosa@duocuc.cl (+56930104972)
Documentos disponibles:   0 ❌

Usuario con documentos:   gionara.espinosa@gmail.com
WhatsApp vinculado:       No ❌
```

**Resultado:** El chatbot encuentra al usuario por WhatsApp, pero al buscar sus documentos no encuentra ninguno procesado.

## Flujo Actual (ROTO)

```
1. Usuario envía WhatsApp desde +56930104972
   ↓
2. Chatbot busca usuario con telefono == +56930104972
   ✅ Encuentra: gi.espinosa@duocuc.cl (UID: NlsLIaYnDRXReBE23i2zVcYmikB2)
   ↓
3. Chatbot busca documentos con usuarioId == NlsLIaYnDRXReBE23i2zVcYmikB2
   ❌ No encuentra documentos
   ↓
4. Chatbot responde: "No tienes documentos procesados disponibles"
```

## Soluciones Disponibles

### Solución 1: Transferir Documentos entre Usuarios ⭐ RECOMENDADO

**Herramienta:** `transferir_documentos.py`

Transfiere los documentos de `gionara.espinosa@gmail.com` (sin WhatsApp) a `gi.espinosa@duocuc.cl` (con WhatsApp).

**Ejecución:**
```bash
python transferir_documentos.py
```

**Resultado esperado:**
```
✅ 1 documento transferido
   gi.espinosa@duocuc.cl ahora tiene acceso vía WhatsApp
```

**Flujo después de la transferencia:**
```
1. Usuario envía WhatsApp desde +56930104972
   ↓
2. Chatbot encuentra: gi.espinosa@duocuc.cl
   ↓
3. Chatbot encuentra: 1 documento procesado (jerar_tab_sap.xlsx)
   ↓
4. Chatbot responde con información del documento ✅
```

### Solución 2: Vincular WhatsApp al Usuario con Documentos

**Proceso manual:**

1. Cerrar sesión de `gi.espinosa@duocuc.cl`
2. Iniciar sesión con `gionara.espinosa@gmail.com`
3. Ir a `localhost:8000/perfil`
4. Ingresar número de WhatsApp: `+56930104972`
5. Guardar

**Ventaja:** Mantiene la relación original usuario-documentos

**Desventaja:** Requiere cambiar de cuenta

### Solución 3: Subir Documento Nuevo con Usuario Correcto

**Proceso:**

1. Iniciar sesión con `gi.espinosa@duocuc.cl` (el que tiene WhatsApp)
2. Ir a `localhost:8000/dashboard`
3. Subir un documento (PDF, DOCX, XLSX, etc.)
4. Esperar a que se procese:
   ```bash
   python document_processor.py --mode process-pending
   ```
5. Verificar:
   ```bash
   python check_documents.py
   ```

**Ventaja:** Solución limpia y definitiva

**Desventaja:** Requiere tener un documento para subir

## Scripts de Verificación Creados

### 1. `diagnostico_whatsapp.py` - Diagnóstico Completo ⭐

Verifica todo el flujo de integración WhatsApp + Documentos.

**Uso:**
```bash
python diagnostico_whatsapp.py
```

**Output:**
- Lista de usuarios con WhatsApp
- Documentos por usuario
- Test de conexión simulada
- Checklist de problemas
- Guía de soluciones

### 2. `ver_documentos_usuarios.py` - Ver Relación Docs-Users

Muestra todos los documentos y a qué usuarios pertenecen.

**Uso:**
```bash
python ver_documentos_usuarios.py
```

**Output:**
- Lista completa de usuarios
- Lista completa de documentos
- Análisis de vinculación

### 3. `transferir_documentos.py` - Transferir Documentos

Transfiere documentos de un usuario a otro.

**Uso:**
```bash
python transferir_documentos.py
```

**Configuración:**
```python
origen_uid = "BODa19voUWT8DxvflAOErlhr3ro2"   # gionara.espinosa@gmail.com
destino_uid = "NlsLIaYnDRXReBE23i2zVcYmikB2"  # gi.espinosa@duocuc.cl
```

### 4. `check_documents.py` - Ver Estado de Documentos

Muestra el estado de todos los documentos (pendiente/procesado/error).

**Uso:**
```bash
python check_documents.py
```

## Verificación Post-Solución

### Paso 1: Ejecutar Solución Elegida

```bash
# Opción A: Transferir documentos
python transferir_documentos.py

# Opción B: Subir documento nuevo
# (a través del dashboard web)
```

### Paso 2: Verificar con Diagnóstico

```bash
python diagnostico_whatsapp.py
```

**Resultado esperado:**
```
Usuario: gi.espinosa@duocuc.cl (+56930104972)
✅ jerar_tab_sap.xlsx
   Estado: procesado
   Caracteres: 2,903

Resumen documentos:
ℹ️  Total: 1
✅ Procesados: 1
```

### Paso 3: Probar con WhatsApp

1. **Iniciar chatbot:**
   ```bash
   python intexta_chatbot.py
   ```

2. **Iniciar ngrok:**
   ```bash
   ngrok http 5000
   ```

3. **Configurar webhook en Twilio:**
   - URL: `https://YOUR-NGROK-URL.ngrok.io/webhook`

4. **Enviar mensaje de prueba:**
   ```
   WhatsApp: Hola
   
   Respuesta esperada: Mensaje de bienvenida o confirmación de acceso
   
   WhatsApp: ¿Qué información tienes sobre SAP?
   
   Respuesta esperada: Información del documento jerar_tab_sap.xlsx
   ```

## Logs de Verificación

### Logs del Chatbot (intexta_chatbot.py)

**Lo que deberías ver:**
```
[INFO] ✅ Firebase conectado correctamente
[INFO] Usuario autenticado: +56930104972 -> NlsLIaYnDRXReBE23i2zVcYmikB2
[INFO] Usuario NlsLIaYnDRXReBE23i2zVcYmikB2: 1 documentos encontrados
[INFO] DeepSeek status: 200
[INFO] Tokens - prompt: 450, completion: 85, total: 535
```

**Si ves esto, hay un problema:**
```
[INFO] Usuario NlsLIaYnDRXReBE23i2zVcYmikB2: 0 documentos encontrados
```

### Logs de ngrok

**Deberías ver requests POST:**
```
POST /webhook               200 OK
POST /webhook               200 OK
```

**Si no ves requests:**
- Verifica que el webhook en Twilio esté configurado
- Verifica que ngrok esté corriendo
- Revisa la URL del webhook

## Troubleshooting

### Problema: "No tienes documentos procesados disponibles"

**Diagnóstico:**
```bash
python diagnostico_whatsapp.py
```

**Buscar en output:**
```
Usuario: [tu email] ([tu whatsapp])
Documentos procesados: 0  ← Si es 0, aplicar solución
```

**Soluciones:**
1. Transferir documentos: `python transferir_documentos.py`
2. Subir documento nuevo desde dashboard
3. Verificar que documento esté procesado: `python check_documents.py`

### Problema: Usuario no encontrado por WhatsApp

**Diagnóstico:**
```bash
python ver_documentos_usuarios.py
```

**Buscar:**
```
⚠️  [tu email] - WhatsApp: +56XXX - ❌ SIN DOCUMENTOS
```

**Solución:**
- Verificar que el número en perfil coincida exactamente
- Formato correcto: `+56912345678` (con +)
- Sin espacios ni guiones

### Problema: Chatbot no recibe mensajes

**Verificaciones:**

1. **Chatbot corriendo:**
   ```bash
   python intexta_chatbot.py
   # Deberías ver: "Running on http://127.0.0.1:5000"
   ```

2. **ngrok corriendo:**
   ```bash
   ngrok http 5000
   # Deberías ver: "Forwarding https://XXXX.ngrok.io -> http://localhost:5000"
   ```

3. **Webhook configurado en Twilio:**
   - URL: `https://XXXX.ngrok.io/webhook`
   - Método: HTTP POST

4. **Código de sandbox enviado:**
   - Enviar: `join [código]` al número de Twilio

### Problema: Documentos no se procesan

**Diagnóstico:**
```bash
python check_documents.py
```

**Si ves documentos pendientes:**
```bash
python document_processor.py --mode process-pending
```

**Si hay errores:**
```bash
python reset_errors.py
python document_processor.py --mode process-pending
```

## Resumen de Comandos Útiles

```bash
# Diagnóstico completo
python diagnostico_whatsapp.py

# Ver documentos y usuarios
python ver_documentos_usuarios.py

# Transferir documentos (solución rápida)
python transferir_documentos.py

# Ver estado de documentos
python check_documents.py

# Procesar documentos pendientes
python document_processor.py --mode process-pending

# Iniciar chatbot
python intexta_chatbot.py

# Iniciar túnel ngrok
ngrok http 5000
```

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUJO COMPLETO                           │
└─────────────────────────────────────────────────────────────┘

1. UPLOAD
   Usuario web → dashboard.html → Firebase Storage
                                → Firestore (estado: pendiente)

2. PROCESAMIENTO
   document_processor.py → ETL (choose_extractor)
                        → Firestore (contenidoProcesado, estado: procesado)

3. VINCULACIÓN
   Usuario → perfil.html → Firestore usuarios.telefono = "+56XXX"

4. CHATBOT
   WhatsApp +56XXX → Twilio → ngrok → intexta_chatbot.py
                                    → Busca usuario por telefono
                                    → Busca documentos por usuarioId
                                    → Construye contexto
                                    → DeepSeek API
                                    → Respuesta a WhatsApp

5. VERIFICACIÓN
   diagnostico_whatsapp.py → Verifica todo el flujo
```

## Conclusión

**Problema raíz:** Desvinculación entre el usuario con WhatsApp y los documentos procesados.

**Solución recomendada:** Ejecutar `python transferir_documentos.py` para transferir el documento existente al usuario con WhatsApp.

**Verificación:** Ejecutar `python diagnostico_whatsapp.py` para confirmar que todo funciona.

**Test final:** Enviar mensaje por WhatsApp y verificar que el chatbot responda con información del documento.
