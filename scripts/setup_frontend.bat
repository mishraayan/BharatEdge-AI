@echo off
cd /d "%~dp0.."
cd app

echo [INFO] Installing Frontend Dependencies...
call npm install

echo.
echo [INFO] Frontend Setup Complete.
echo [INFO] To launch the app:
echo        cd app
echo        npm run tauri dev
pause
