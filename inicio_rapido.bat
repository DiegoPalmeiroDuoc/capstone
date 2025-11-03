@echo off
chcp 65001 >nul
title Intexta - Sistema Completo
color 0A

:MENU
cls
echo.
echo ╔════════════════════════════════════════╗
echo ║   INTEXTA - Sistema de Procesamiento   ║
echo ╚════════════════════════════════════════╝
echo.
echo  [1] Iniciar TODO (Web + Processor)
echo  [2] Solo Servidor Web Django
echo  [3] Solo Document Processor  
echo  [4] Verificar Estado
echo  [5] Ayuda
echo  [0] Salir
echo.
echo ────────────────────────────────────────
set /p OPCION="  Selecciona opción: "

if "%OPCION%"=="1" goto INICIAR_TODO
if "%OPCION%"=="2" goto INICIAR_WEB
if "%OPCION%"=="3" goto INICIAR_PROCESSOR
if "%OPCION%"=="4" goto VERIFICAR
if "%OPCION%"=="5" goto AYUDA
if "%OPCION%"=="0" goto SALIR

echo.
echo  [ERROR] Opción inválida
timeout /t 2 >nul
goto MENU

:INICIAR_TODO
cls
echo.
echo ════════════════════════════════════════
echo   Iniciando Sistema Completo
echo ════════════════════════════════════════
echo.

echo  [1/2] Iniciando Document Processor...
start "Intexta Processor" cmd /k "title Intexta Processor && color 0B && cd /d "%~dp0" && python document_processor.py --mode listen --interval 30"
timeout /t 2 /nobreak >nul

echo  [2/2] Iniciando Django Server...
start "Intexta Django" cmd /k "title Intexta Django && color 0E && cd /d "%~dp0cliente_web" && python manage.py runserver"

echo.
echo ════════════════════════════════════════
echo   ✓ Sistema Iniciado
echo ════════════════════════════════════════
echo.
echo  Se abrieron 2 ventanas:
echo   • Processor (azul) - procesa cada 30s
echo   • Django (amarillo) - puerto 8000
echo.
echo  Abre tu navegador en:
echo   http://localhost:8000
echo.
echo  Para detener: Ctrl+C en cada ventana
echo.
pause
goto MENU

:INICIAR_WEB
cls
echo.
echo ════════════════════════════════════════
echo   Iniciando Servidor Web Django
echo ════════════════════════════════════════
echo.
echo  URL: http://localhost:8000
echo  Presiona Ctrl+C para detener
echo.

cd cliente_web
python manage.py runserver
cd ..
pause
goto MENU

:INICIAR_PROCESSOR
cls
echo.
echo ════════════════════════════════════════
echo   Iniciando Document Processor
echo ════════════════════════════════════════
echo.

set /p INTERVALO="  Intervalo en segundos [30]: "
if "%INTERVALO%"=="" set INTERVALO=30

echo.
echo  Modo: Escucha continua
echo  Intervalo: %INTERVALO% segundos
echo  Presiona Ctrl+C para detener
echo.

python document_processor.py --mode listen --interval %INTERVALO%
pause
goto MENU

:VERIFICAR
cls
echo.
echo ════════════════════════════════════════
echo   Estado del Sistema
echo ════════════════════════════════════════
echo.

echo  Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo   ✗ Python NO instalado
) else (
    python --version
    echo   ✓ Python OK
)

echo.
echo  Verificando archivos del proyecto...
if exist "document_processor.py" (
    echo   ✓ document_processor.py
) else (
    echo   ✗ document_processor.py NO encontrado
)

if exist "cliente_web\manage.py" (
    echo   ✓ cliente_web\manage.py
) else (
    echo   ✗ cliente_web\manage.py NO encontrado
)

if exist "etl.py" (
    echo   ✓ etl.py
) else (
    echo   ✗ etl.py NO encontrado
)

if exist "cliente_web\admin-doc-ia-firebase-adminsdk-fbsvc-82d2fcac61.json" (
    echo   ✓ Credenciales Firebase
) else (
    echo   ✗ Credenciales Firebase NO encontradas
)

echo.
echo  Verificando puerto 8000...
netstat -ano | findstr ":8000" >nul 2>&1
if errorlevel 1 (
    echo   ✗ Puerto 8000 LIBRE (Django no está corriendo)
) else (
    echo   ✓ Puerto 8000 EN USO (Django está corriendo)
)

echo.
pause
goto MENU

:AYUDA
cls
echo.
echo ════════════════════════════════════════
echo   Guía Rápida de Uso
echo ════════════════════════════════════════
echo.
echo  FLUJO DE PROCESAMIENTO:
echo.
echo   1. Usuario sube PDF en la web
echo      ↓
echo   2. Se guarda en Firebase (estado: pendiente)
echo      ↓
echo   3. Processor detecta el archivo (cada 30s)
echo      ↓
echo   4. Extrae texto y procesa
echo      ↓
echo   5. Actualiza estado a "procesado"
echo      ↓
echo   6. Dashboard muestra el cambio
echo.
echo ════════════════════════════════════════
echo.
echo  OPCIÓN 1: TODO
echo   Inicia ambos servicios automáticamente
echo   Recomendado para uso normal
echo.
echo  OPCIÓN 2: Solo Web
echo   Para desarrollo del frontend
echo   Sin procesamiento automático
echo.
echo  OPCIÓN 3: Solo Processor
echo   Para debugging del procesamiento
echo   La web debe estar corriendo aparte
echo.
echo ════════════════════════════════════════
echo.
echo  PASOS PARA USAR:
echo.
echo   1. Ejecuta opción 1 (TODO)
echo   2. Espera que abran las 2 ventanas
echo   3. Abre http://localhost:8000
echo   4. Inicia sesión
echo   5. Sube un documento
echo   6. Espera ~30 segundos
echo   7. Verás el cambio de estado
echo.
echo ════════════════════════════════════════
echo.
pause
goto MENU

:SALIR
cls
echo.
echo  Cerrando sistema...
echo  Hasta pronto!
echo.
timeout /t 1 >nul
exit /b 0
