# 📦 Ejemplos Antiguos - Chatbots Standalone

Esta carpeta contiene las versiones anteriores de chatbots que funcionaban de manera independiente, antes de la integración con Firebase.

---

## 📄 Archivos en esta carpeta

### **consultaInventario.py**
Chatbot de WhatsApp para consultar inventario de productos electrónicos.

**Características:**
- Lee inventario desde Google Sheets
- Consultas por tipo, marca, modelo, color
- Flujo de compra completo
- Integración con DeepSeek API

**Uso:**
```bash
python consultaInventario.py
```

---

### **convivencia_escolar.py**
Chatbot de WhatsApp para responder preguntas sobre normas de convivencia escolar.

**Características:**
- Lee contenido desde Google Docs (URL hardcodeada)
- Respuestas limitadas a 3 frases
- Registro de uso de tokens

**Uso:**
```bash
python convivencia_escolar.py
```

---

### **manualPython.py**
Script de ejemplo o prueba (revisar contenido para uso específico).

---

### **presentacion.py**
Servidor Flask simple para mostrar una página de presentación.

**Uso:**
```bash
python presentacion.py
# Accede a http://localhost:8080
```

---

### **templates/** y **static/**
Archivos HTML y CSS antiguos usados por `presentacion.py`.

---

## ⚠️ Nota Importante

**Estos archivos NO son parte del sistema integrado de Intexta.**

El sistema actual usa:
- `intexta_chatbot.py` - Chatbot integrado con Firebase
- `document_processor.py` - Procesador automático
- `etl.py` - Extractor de texto
- `cliente_web/` - Aplicación web Django

---

## 🔄 Migración

Si deseas usar estos ejemplos como base:

1. **Para adaptar a Firebase:**
   - Reemplaza la carga de Google Docs/Sheets por consultas a Firestore
   - Usa `firebase_config.py` para conectar
   - Consulta `intexta_chatbot.py` como referencia

2. **Ejemplo de migración:**

**Antes (Google Docs):**
```python
GOOGLE_DOC_TXT_EXPORT = "https://docs.google.com/document/d/.../export?format=txt"
file_content = requests.get(GOOGLE_DOC_TXT_EXPORT).text
```

**Después (Firebase):**
```python
from firebase_config import db
docs = db.collection('documentos').where('usuarioId', '==', uid).stream()
file_content = doc.to_dict()['contenidoProcesado']
```

---

## 📚 Referencias

Para entender cómo funciona el sistema integrado actual, consulta:
- `/docs/QUICKSTART.md` - Inicio rápido
- `/docs/ARCHITECTURE.md` - Arquitectura del sistema
- `README.md` - Documentación principal

---

**Estos archivos se mantienen como referencia y ejemplos de aprendizaje.**
