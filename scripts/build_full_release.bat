@echo off
setlocal enabledelayedexpansion

:: Define file paths
set "PROJECT_ROOT=%~dp0.."
set "BACKEND_DIR=%PROJECT_ROOT%\backend"
set "APP_DIR=%PROJECT_ROOT%\app"
set "TAURI_SIDECAR_DIR=%APP_DIR%\src-tauri"
set "SIDECAR_NAME=bharatedge-backend-x86_64-pc-windows-msvc.exe"

echo [BUILD] 1. Cleanup old build artifacts...
if exist "%BACKEND_DIR%\dist" rmdir /s /q "%BACKEND_DIR%\dist"
if exist "%BACKEND_DIR%\build" rmdir /s /q "%BACKEND_DIR%\build"

echo.
echo [BUILD] 2. Building Backend (PyInstaller)...
cd /d "%BACKEND_DIR%"
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found. Please run setup_dev_env.bat first.
    exit /b 1
)

:: Run PyInstaller
pyinstaller --clean --noconfirm bharatedge-backend.spec
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PyInstaller failed.
    exit /b 1
)

echo.
echo [BUILD] 3. Moving Sidecar to Tauri...
if not exist "dist\bharatedge-backend.exe" (
    echo [ERROR] Output exe not found in dist/
    exit /b 1
)

copy /Y "dist\bharatedge-backend.exe" "%TAURI_SIDECAR_DIR%\%SIDECAR_NAME%"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to move sidecar.
    exit /b 1
)
echo [OK] Sidecar updated: %TAURI_SIDECAR_DIR%\%SIDECAR_NAME%

echo.
echo [BUILD] 4. Building Frontend & Bundle (Tauri)...
cd /d "%APP_DIR%"
call npm install
call npm run tauri build
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Tauri build failed.
    exit /b 1
)

echo.
echo [SUCCESS] Build Complete! Use the installer in app/src-tauri/target/release
pause
