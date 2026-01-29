@echo off
setlocal

:: Get the directory of this script
set "SCRIPT_DIR=%~dp0"
set "ROOT_DIR=%SCRIPT_DIR%.."

:: Paths to Embedded Python and Source
:: Assuming generic layout after build:
:: AppRoot/
::   BharatEdge.exe
::   _internal/
::      python/
::      backend_src/
::
:: But for DEV mode, we point to venv. 
:: For PROD (Sidecar), Tauri puts the executable in a specific path.
:: We will write a generic launcher that looks relative to itself.

:: Configuration for Prod (Embedded)
set "PYTHON_EXE=%SCRIPT_DIR%_internal\python\python.exe"
set "APP_MODULE=src.main:app"
set "BACKEND_DIR=%SCRIPT_DIR%_internal\backend_src"

:: Fallback to local venv if embedded not found (Dev Mode)
if not exist "%PYTHON_EXE%" (
    echo [INFO] Embedded Python not found. Trying local venv...
    set "PYTHON_EXE=%ROOT_DIR%\backend\venv\Scripts\python.exe"
    set "BACKEND_DIR=%ROOT_DIR%\backend"
)

:: Check if Python exists
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python interpreter not found at %PYTHON_EXE%
    exit /b 1
)

:: Set working directory to backend src so imports work
cd /d "%BACKEND_DIR%"

echo [INFO] Starting BharatEdge Backend...
echo [INFO] Python: %PYTHON_EXE%
echo [INFO] Dir: %BACKEND_DIR%

:: Run Uvicorn
:: --workers 1 used because we rely on global state (RAG engine)
"%PYTHON_EXE%" -m uvicorn %APP_MODULE% --host 127.0.0.1 --port 8000 --no-server-header

endlocal
