@echo off
REM ========================================
REM Intexta Document Processor - Launcher
REM ========================================

echo.
echo ========================================
echo   Intexta Document Processor
echo ========================================
echo.

:MENU
echo Selecciona el modo de operacion:
echo.
echo   1. Modo Escucha (Listen) - Continuo
echo   2. Procesar Pendientes - Una vez
echo   3. Reprocesar Documento
echo   4. Ver Ayuda
echo   5. Salir
echo.

set /p choice="Ingresa tu opcion (1-5): "

if "%choice%"=="1" goto LISTEN
if "%choice%"=="2" goto PROCESS
if "%choice%"=="3" goto REPROCESS
if "%choice%"=="4" goto HELP
if "%choice%"=="5" goto EXIT
goto MENU

:LISTEN
echo.
set /p interval="Intervalo en segundos (default: 30): "
if "%interval%"=="" set interval=30

echo.
echo Iniciando modo escucha con intervalo de %interval% segundos...
echo Presiona Ctrl+C para detener
echo.

python document_processor.py --mode listen --interval %interval%
goto END

:PROCESS
echo.
echo Procesando documentos pendientes...
echo.

python document_processor.py --mode process-pending
pause
goto MENU

:REPROCESS
echo.
set /p docid="Ingresa el ID del documento: "

if "%docid%"=="" (
    echo Error: Debes proporcionar un ID de documento
    pause
    goto MENU
)

echo.
echo Reprocesando documento: %docid%
echo.

python document_processor.py --mode reprocess --doc-id %docid%
pause
goto MENU

:HELP
echo.
python document_processor.py --help
echo.
pause
goto MENU

:EXIT
echo.
echo Saliendo...
exit /b 0

:END
echo.
pause
goto MENU
