# 🚀 INICIO RÁPIDO - INTEXTA

## ✅ Comandos para Iniciar el Sistema

### OPCIÓN 1: Iniciar TODO el Sistema (Recomendado)

Abre **2 terminales PowerShell** en esta carpeta y ejecuta:

**Terminal 1 - Django Server:**
```powershell
cd cliente_web
python manage.py runserver
```

**Terminal 2 - Document Processor:**
```powershell
python document_processor.py --mode listen --interval 30
```

---

### OPCIÓN 2: Solo Django (sin procesamiento automático)

```powershell
cd cliente_web
python manage.py runserver
```

Luego abre: http://localhost:8000

---

### OPCIÓN 3: Solo Processor (la web debe estar corriendo)

```powershell
python document_processor.py --mode listen --interval 30
```

---

## 📋 Verificar que Todo Funciona

### 1. Ver si Python está instalado:
```powershell
python --version
```

### 2. Ver archivos del proyecto:
```powershell
Get-ChildItem *.py
```

### 3. Ver si Django está corriendo:
```powershell
netstat -ano | findstr ":8000"
```

---

## 🎯 Flujo Completo para Probar

1. **Abre Terminal 1:**
   ```powershell
   cd cliente_web
   python manage.py runserver
   ```
   ✅ Espera ver: `Starting development server at http://127.0.0.1:8000/`

2. **Abre Terminal 2:**
   ```powershell
   python document_processor.py --mode listen --interval 30
   ```
   ✅ Espera ver: `[INFO] Iniciando monitoreo de documentos pendientes...`

3. **Abre navegador:**
   ```
   http://localhost:8000/login
   ```

4. **Inicia sesión** con tu cuenta Firebase

5. **Sube un documento PDF**

6. **Espera ~30 segundos**

7. **Verás el cambio de estado:** Pendiente ⏳ → Procesado ✅

---

## 🐛 Solución de Problemas

### Error: "python no se reconoce"
```powershell
# Verifica la instalación de Python
python --version

# Si no funciona, usa:
py --version
# O
python3 --version
```

### Error: Puerto 8000 ya en uso
```powershell
# Ver qué proceso usa el puerto
netstat -ano | findstr ":8000"

# Matar el proceso (reemplaza PID)
taskkill /PID <número_pid> /F
```

### Error: ModuleNotFoundError
```powershell
# Instalar dependencias
pip install -r requirements.txt
```

### Processor no detecta archivos
```powershell
# Procesar manualmente una vez
python document_processor.py --mode process-pending
```

---

## 📊 Monitoreo

### Ver logs en tiempo real del Processor:
El output aparece directamente en la terminal

### Ver logs de Django:
Aparecen en la terminal donde corre `manage.py runserver`

### Dashboard en tiempo real:
- Auto-refresh cada 30 segundos
- Estadísticas actualizadas
- Cambios de estado visibles

---

## 🔥 Atajos Útiles

### Detener servicios:
- Presiona `Ctrl + C` en cada terminal

### Reiniciar Processor con intervalo diferente:
```powershell
# Cada 10 segundos (más rápido)
python document_processor.py --mode listen --interval 10

# Cada 60 segundos (más lento)
python document_processor.py --mode listen --interval 60
```

### Reprocesar un documento específico:
```powershell
python document_processor.py --mode reprocess --doc-id ABC123XYZ
```

---

## ✨ ¡Listo!

Con estos 2 comandos tu sistema está completamente funcional:

1️⃣ `cd cliente_web ; python manage.py runserver`

2️⃣ `python document_processor.py --mode listen --interval 30`

**¡El procesamiento es automático!** 🎉
