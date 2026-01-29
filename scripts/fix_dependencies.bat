@echo off
cd /d "%~dp0.."
cd backend

if not exist "venv" (
    echo [ERROR] Virtual environment not found! Please run setup_dev_env.bat first.
    pause
    exit /b 1
)

echo [INFO] Activating Python 3.11 Environment...
call venv\Scripts\activate

echo [INFO] Updating Dependencies (Fixing NumPy)...
pip install -r requirements.txt

echo.
echo [INFO] Done. You can now run 'python -m src.main'
pause
