@echo off
cd /d "%~dp0.."

echo [INFO] Setting up Backend Environment...
cd backend

:: 1. Clean up old broken venv if it exists
if exist "venv" (
    echo [INFO] Removing old virtual environment...
    rmdir /s /q "venv"
)

:: 2. Create new venv using Python 3.11 explicitly
echo [INFO] Creating Python Virtual Environment (Trying Python 3.11)...
py -3.11 -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] 'py -3.11' failed. Trying default 'python'...
    python -m venv venv
)

echo [INFO] Activating venv and Installing Dependencies...
call venv\Scripts\activate
pip install -r requirements.txt

echo [INFO] Installing llama-cpp-python (Pre-built CPU Wheel)...
:: Force install a version that has pre-built wheels for Windows
pip install llama-cpp-python==0.2.90 --prefer-binary --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu


echo.
echo [INFO] Dependencies Installed.
echo [INFO] Please ensure 'backend/models' directory has the GGUF model as per TEST_INSTRUCTIONS.md
echo.
pause
