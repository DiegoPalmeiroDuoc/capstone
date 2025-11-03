@echo off
chcp 65001 >nul
title Intexta - Sistema Completo

echo.
echo ========================================
echo   Intexta - Inicio del Sistema
echo ========================================
echo.

REM Verificar si estamos en el directorio correcto
if not exist "document_processor.py" (
    echo [ERROR] No se encuentra document_processor.py
    echo Por favor ejecuta este script desde la carpeta del proyecto
    pause
    exit /b 1
)

echo Preparando el sistema...
echo.

REM Crear directorio para logs si no existe
if not exist "logs" mkdir logs

REM Obtener timestamp para logs (compatible con PowerShell)
set LOGFILE=logs\sistema_%date:~-4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
set LOGFILE=%LOGFILE: =0%

echo [%date% %time%] Iniciando sistema Intexta >> %LOGFILE%

echo ┌──────────────────────────────────────┐
echo │  ¿Qué componentes deseas iniciar?   │
echo └──────────────────────────────────────┘
echo.
echo   1. TODO - Servidor Web + Processor
echo   2. Solo Servidor Web (Django)
echo   3. Solo Document Processor
echo   4. Ver logs del sistema
echo   5. Verificar estado de servicios
echo   6. Salir
echo.

set /p OPCION="Selecciona una opción (1-6): "

if "%OPCION%"=="1" goto TODO
if "%OPCION%"=="2" goto WEB
if "%OPCION%"=="3" goto PROCESSOR
if "%OPCION%"=="4" goto LOGS
if "%OPCION%"=="5" goto STATUS
if "%OPCION%"=="6" goto SALIR

echo Opción inválida
pause
exit /b 1

:TODO
echo.
echo ========================================
echo   Iniciando Sistema Completo
echo ========================================
echo.

echo [1/3] Verificando dependencias...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado o no está en PATH
    pause
    exit /b 1
)
echo ✓ Python detectado

echo.
echo [2/3] Iniciando Document Processor...
echo.
start "Intexta - Document Processor" cmd /k "cd /d "%~dp0" && echo Iniciando Document Processor... && python document_processor.py --mode listen --interval 30"

timeout /t 3 /nobreak >nul

echo.
echo [3/3] Iniciando Servidor Web Django...
echo.
start "Intexta - Django Server" cmd /k "cd /d "%~dp0cliente_web" && echo Iniciando Django Server... && python manage.py runserver"

echo.
echo ========================================
echo   ✓ Sistema Iniciado Correctamente
echo ========================================
echo.
echo Se han abierto 2 ventanas:
echo   - Document Processor (escuchando cada 30s)
echo   - Django Server (http://localhost:8000)
echo.
echo Para detener los servicios:
echo   - Cierra ambas ventanas
echo   - O presiona Ctrl+C en cada una
echo.
echo Abre tu navegador en: http://localhost:8000
echo.

echo [%date% %time%] Sistema iniciado completamente >> %LOGFILE%

echo Presiona cualquier tecla para cerrar esta ventana...
pause >nul
exit /b 0

:WEB
echo.
echo ========================================
echo   Iniciando Solo Servidor Web
echo ========================================
echo.

cd cliente_web

echo Verificando manage.py...
if not exist "manage.py" (
    echo [ERROR] No se encuentra manage.py en cliente_web/
    cd ..
    pause
    exit /b 1
)

echo.
echo Iniciando Django Development Server...
echo Servidor disponible en: http://localhost:8000
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

echo [%date% %time%] Iniciando Django server >> ..\%LOGFILE%

python manage.py runserver

cd ..
goto FIN

:PROCESSOR
echo.
echo ========================================
echo   Iniciando Document Processor
echo ========================================
echo.

set /p INTERVALO="Intervalo en segundos (default: 30): "
if "%INTERVALO%"=="" set INTERVALO=30

echo.
echo Iniciando en modo escucha con intervalo de %INTERVALO% segundos...
echo Presiona Ctrl+C para detener
echo.

echo [%date% %time%] Iniciando Document Processor (intervalo: %INTERVALO%s) >> %LOGFILE%

python document_processor.py --mode listen --interval %INTERVALO%

goto FIN

:LOGS
echo.
echo ========================================
echo   Logs del Sistema
echo ========================================
echo.

if not exist "logs" (
    echo No hay logs disponibles
    pause
    goto FIN
)

echo Archivos de log disponibles:
echo.
dir /b logs\*.log

echo.
set /p LOGVIEW="¿Ver el log más reciente? (S/N): "
if /i "%LOGVIEW%"=="S" (
    for /f "delims=" %%f in ('dir /b /o-d logs\*.log 2^>nul') do (
        type "logs\%%f"
        goto LOGEND
    )
)

:LOGEND
echo.
pause
goto FIN

:STATUS
echo.
echo ========================================
echo   Estado de Servicios
echo ========================================
echo.

echo Verificando Python...
python --version 2>nul
if errorlevel 1 (
    echo ✗ Python NO detectado
) else (
    echo ✓ Python detectado
)

echo.
echo Verificando archivo de credenciales Firebase...
if exist "cliente_web\admin-doc-ia-firebase-adminsdk-fbsvc-82d2fcac61.json" (
    echo ✓ Credenciales Firebase encontradas
) else (
    echo ✗ Credenciales Firebase NO encontradas
)

echo.
echo Verificando estructura del proyecto...
if exist "document_processor.py" (
    echo ✓ document_processor.py
) else (
    echo ✗ document_processor.py NO encontrado
)

if exist "cliente_web\manage.py" (
    echo ✓ cliente_web/manage.py
) else (
    echo ✗ cliente_web/manage.py NO encontrado
)

if exist "etl.py" (
    echo ✓ etl.py
) else (
    echo ✗ etl.py NO encontrado
)

echo.
echo Verificando procesos activos...
tasklist /FI "WINDOWTITLE eq Intexta - Django Server" 2>nul | find "cmd.exe" >nul
if errorlevel 1 (
    echo ✗ Django Server NO está corriendo
) else (
    echo ✓ Django Server está corriendo
)

tasklist /FI "WINDOWTITLE eq Intexta - Document Processor" 2>nul | find "cmd.exe" >nul
if errorlevel 1 (
    echo ✗ Document Processor NO está corriendo
) else (
    echo ✓ Document Processor está corriendo
)

echo.
echo Verificando puertos...
netstat -ano | findstr ":8000" >nul 2>&1
if errorlevel 1 (
    echo ✗ Puerto 8000 (Django) está LIBRE
) else (
    echo ✓ Puerto 8000 (Django) está EN USO
)

echo.
pause
goto FIN

:SALIR
echo.
echo Saliendo...
exit /b 0

:FIN
echo.
pause
exit /b 0
