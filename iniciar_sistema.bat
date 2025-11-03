@echo off
REM ========================================
REM INTEXTA - Script de Inicio Completo
REM ========================================

echo.
echo ========================================
echo   INTEXTA - Iniciando Sistema Completo
echo ========================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "cliente_web" (
    echo ERROR: No se encuentra la carpeta cliente_web
    echo Por favor ejecuta este script desde la raiz del proyecto capstone
    pause
    exit /b 1
)

echo [1/4] Iniciando servidor Django...
start "Django Server" cmd /k "cd cliente_web && python manage.py runserver"
timeout /t 3 /nobreak > nul

echo [2/4] Iniciando chatbot WhatsApp...
start "WhatsApp Chatbot" cmd /k "python intexta_chatbot.py"
timeout /t 3 /nobreak > nul

echo [3/4] Iniciando ngrok (tunel publico)...
start "ngrok Tunnel" cmd /k "ngrok http 5000"
timeout /t 2 /nobreak > nul

echo.
echo ========================================
echo   SISTEMA INICIADO CORRECTAMENTE
echo ========================================
echo.
echo Servicios activos:
echo   - Django Web:    http://localhost:8000
echo   - Chatbot API:   http://localhost:5000
echo   - ngrok Tunnel:  Ver ventana de ngrok
echo.
echo IMPORTANTE:
echo   1. Copia la URL de ngrok (https://xxxxx.ngrok-free.app)
echo   2. Configurala en Twilio Sandbox Settings
echo   3. Agrega /webhook al final de la URL
echo.
echo Presiona cualquier tecla para abrir el navegador...
pause > nul

start http://localhost:8000/login

echo.
echo Para detener todos los servicios, cierra las ventanas.
echo.
pause
