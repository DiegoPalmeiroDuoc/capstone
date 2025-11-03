@echo off
chcp 65001 >nul
title Intexta - Asistente de Configuración Twilio
color 0B

:MENU
cls
echo.
echo ╔════════════════════════════════════════════╗
echo ║  INTEXTA - Configuración Twilio WhatsApp   ║
echo ╚════════════════════════════════════════════╝
echo.
echo  Esta herramienta te guiará paso a paso
echo  para configurar Twilio con tu chatbot.
echo.
echo ────────────────────────────────────────────
echo.
echo  [1] Ver estado actual
echo  [2] Iniciar chatbot (puerto 5000)
echo  [3] Iniciar ngrok (túnel)
echo  [4] Probar webhook localmente
echo  [5] Ver guía completa
echo  [6] Abrir URLs importantes
echo  [0] Salir
echo.
echo ────────────────────────────────────────────
set /p OPCION="  Selecciona opción: "

if "%OPCION%"=="1" goto ESTADO
if "%OPCION%"=="2" goto CHATBOT
if "%OPCION%"=="3" goto NGROK
if "%OPCION%"=="4" goto PRUEBA
if "%OPCION%"=="5" goto GUIA
if "%OPCION%"=="6" goto URLS
if "%OPCION%"=="0" goto SALIR

echo.
echo  [ERROR] Opción inválida
timeout /t 2 >nul
goto MENU

:ESTADO
cls
echo.
echo ════════════════════════════════════════════
echo   Estado de Configuración Twilio
echo ════════════════════════════════════════════
echo.

echo  [1/5] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo   ✗ Python NO instalado
) else (
    python --version
    echo   ✓ Python OK
)

echo.
echo  [2/5] Verificando archivos del chatbot...
if exist "intexta_chatbot.py" (
    echo   ✓ intexta_chatbot.py
) else (
    echo   ✗ intexta_chatbot.py NO encontrado
)

if exist "cliente_web\firebase_config.py" (
    echo   ✓ firebase_config.py
) else (
    echo   ✗ firebase_config.py NO encontrado
)

echo.
echo  [3/5] Verificando dependencias...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo   ✗ Flask NO instalado
    echo      Instalar: pip install flask
) else (
    echo   ✓ Flask instalado
)

python -c "import twilio" >nul 2>&1
if errorlevel 1 (
    echo   ✗ Twilio NO instalado
    echo      Instalar: pip install twilio
) else (
    echo   ✓ Twilio instalado
)

echo.
echo  [4/5] Verificando ngrok...
where ngrok >nul 2>&1
if errorlevel 1 (
    echo   ✗ ngrok NO instalado
    echo      Descargar: https://ngrok.com/download
) else (
    echo   ✓ ngrok instalado
)

echo.
echo  [5/5] Verificando puerto 5000...
netstat -ano | findstr ":5000" >nul 2>&1
if errorlevel 1 (
    echo   ✗ Puerto 5000 LIBRE (chatbot no está corriendo)
) else (
    echo   ✓ Puerto 5000 EN USO (chatbot corriendo)
)

echo.
echo ════════════════════════════════════════════
pause
goto MENU

:CHATBOT
cls
echo.
echo ════════════════════════════════════════════
echo   Iniciando Chatbot de WhatsApp
echo ════════════════════════════════════════════
echo.

if not exist "intexta_chatbot.py" (
    echo  [ERROR] No se encuentra intexta_chatbot.py
    echo.
    pause
    goto MENU
)

echo  Verificando dependencias...
python -c "import flask, twilio" >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [ERROR] Faltan dependencias
    echo.
    set /p INSTALAR="  ¿Instalar ahora? (S/N): "
    if /i "%INSTALAR%"=="S" (
        echo.
        echo  Instalando Flask y Twilio...
        pip install flask twilio
    )
)

echo.
echo  Iniciando chatbot en puerto 5000...
echo  URL local: http://localhost:5000
echo  Endpoint webhook: http://localhost:5000/webhook
echo.
echo  ──────────────────────────────────────────
echo  SIGUIENTE PASO:
echo  1. Deja esta ventana abierta
echo  2. Vuelve al menú (otra terminal)
echo  3. Selecciona opción 3: Iniciar ngrok
echo  ──────────────────────────────────────────
echo.
echo  Presiona Ctrl+C para detener
echo.

python intexta_chatbot.py

pause
goto MENU

:NGROK
cls
echo.
echo ════════════════════════════════════════════
echo   Iniciando ngrok Tunnel
echo ════════════════════════════════════════════
echo.

where ngrok >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] ngrok no está instalado
    echo.
    echo  Descarga desde: https://ngrok.com/download
    echo.
    set /p ABRIR="  ¿Abrir página de descarga? (S/N): "
    if /i "%ABRIR%"=="S" (
        start https://ngrok.com/download
    )
    pause
    goto MENU
)

echo  ngrok creará un túnel público a tu chatbot local
echo.
echo  ──────────────────────────────────────────
echo  IMPORTANTE:
echo  1. Copia la URL HTTPS que aparecerá
echo  2. Ve a Twilio Console
echo  3. Configura webhook: URL_COPIADA/webhook
echo  ──────────────────────────────────────────
echo.
echo  Iniciando túnel...
echo.

ngrok http 5000

pause
goto MENU

:PRUEBA
cls
echo.
echo ════════════════════════════════════════════
echo   Prueba Local del Webhook
echo ════════════════════════════════════════════
echo.

netstat -ano | findstr ":5000" >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] El chatbot no está corriendo
    echo.
    echo  Inicia el chatbot primero (Opción 2)
    echo.
    pause
    goto MENU
)

echo  Enviando petición de prueba al webhook...
echo.

curl -X POST http://localhost:5000/webhook -d "Body=Hola" -d "From=whatsapp:+56912345678" >nul 2>&1

if errorlevel 1 (
    echo  [ERROR] curl no está disponible
    echo.
    echo  Prueba manual:
    echo  1. Abre: http://localhost:5000
    echo  2. Deberías ver la página de inicio del chatbot
) else (
    echo  ✓ Petición enviada
    echo.
    echo  Revisa la terminal del chatbot para ver los logs
)

echo.
pause
goto MENU

:GUIA
cls
echo.
echo ════════════════════════════════════════════
echo   Guía Rápida de Configuración
echo ════════════════════════════════════════════
echo.
echo  PASO 1: Crear cuenta en Twilio
echo  ────────────────────────────────────────
echo  1. Ve a: https://www.twilio.com/try-twilio
echo  2. Regístrate (gratis)
echo  3. Verifica tu email y teléfono
echo  4. Guarda tu Account SID y Auth Token
echo.
echo  PASO 2: Activar WhatsApp Sandbox
echo  ────────────────────────────────────────
echo  1. En Twilio: Messaging ^> Try it out ^> WhatsApp
echo  2. Envía desde tu WhatsApp:
echo     - A: +1 415 523 8886
echo     - Mensaje: join ^<codigo-unico^>
echo  3. Espera confirmación
echo.
echo  PASO 3: Iniciar servicios locales
echo  ────────────────────────────────────────
echo  1. Opción 2: Iniciar chatbot
echo  2. Opción 3: Iniciar ngrok
echo  3. Copia la URL de ngrok
echo.
echo  PASO 4: Configurar webhook en Twilio
echo  ────────────────────────────────────────
echo  1. Ve a: Messaging ^> Settings ^> WhatsApp Sandbox
echo  2. En "When a message comes in":
echo     URL: https://TU-URL-NGROK.ngrok.io/webhook
echo     Method: HTTP POST
echo  3. Click Save
echo.
echo  PASO 5: Probar
echo  ────────────────────────────────────────
echo  1. Envía "Hola" desde WhatsApp
echo  2. Deberías recibir respuesta del chatbot
echo.
echo ════════════════════════════════════════════
echo.
pause
goto MENU

:URLS
cls
echo.
echo ════════════════════════════════════════════
echo   URLs Importantes
echo ════════════════════════════════════════════
echo.
echo  [1] Twilio Console
echo  [2] WhatsApp Sandbox (activar)
echo  [3] Webhook Settings
echo  [4] Logs de Mensajes
echo  [5] ngrok Download
echo  [6] ngrok Dashboard
echo  [0] Volver
echo.
set /p URL_OPCION="  Selecciona opción: "

if "%URL_OPCION%"=="1" start https://console.twilio.com
if "%URL_OPCION%"=="2" start https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
if "%URL_OPCION%"=="3" start https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox
if "%URL_OPCION%"=="4" start https://console.twilio.com/us1/monitor/logs/sms
if "%URL_OPCION%"=="5" start https://ngrok.com/download
if "%URL_OPCION%"=="6" start https://dashboard.ngrok.com
if "%URL_OPCION%"=="0" goto MENU

echo.
echo  ✓ Abriendo navegador...
timeout /t 2 >nul
goto URLS

:SALIR
cls
echo.
echo ════════════════════════════════════════════
echo.
echo  Para más información detallada, lee:
echo  docs\CONFIGURACION_TWILIO.md
echo.
echo  ¡Hasta pronto!
echo.
echo ════════════════════════════════════════════
echo.
timeout /t 2 >nul
exit /b 0
