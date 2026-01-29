@echo off
setlocal

:: Define Paths
set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%backend"
set "APP_DIR=%PROJECT_ROOT%app\src-tauri\target\release"
set "APP_EXE=%APP_DIR%\app.exe"

echo [Launcher] Starting BharatEdge AI...

:: 1. Start Backend (Hidden/Background)
:: 1. Start Backend (Hidden/Background)
echo [Launcher] booting backend server...
cd /d "%PROJECT_ROOT%"
:: Use helper script if available, else standard start
if exist "scripts\headless_backend.vbs" (
    wscript "scripts\headless_backend.vbs"
) else (
    start /B scripts\start_backend.bat > nul 2>&1
)

:: Wait for Boot (Simple 5s delay, ideally curl healthcheck)
echo [Launcher] Waiting for AI engine...
timeout /t 5 /nobreak > nul

:: 2. Launch Frontend (Blocking)
echo [Launcher] Launching UI...
if exist "%APP_EXE%" (
    "%APP_EXE%"
) else (
    echo [ERROR] Frontend Executable not found at: %APP_EXE%
    echo Please ensure you ran 'npm run tauri build' successfully.
    pause
    exit /b 1
)

:: 3. Cleanup on Exit
echo [Launcher] Shutting down...
taskkill /F /IM "python.exe" /FI "WINDOWTITLE eq BharatEdgeBackend*" > nul 2>&1
:: Also force kill by path if possible, or relying on uvicorn generic kill might be risky if other pythons run.
:: For now, we rely on the user closing the window.

endlocal
exit /b 0
