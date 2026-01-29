@echo off
setlocal

echo [GPU Setup] Starting BharatEdge AI GPU Acceleration Setup...
echo [GPU Setup] This requires NVIDIA CUDA Toolkit installed on your system.
echo.

:: Ask for confirmation
set /p confirm="Do you want to install GPU-enabled AI engine? (y/n): "
if /i "%confirm%" neq "y" (
    echo [GPU Setup] Installation cancelled.
    pause
    exit /b 0
)

echo [GPU Setup] Uninstalling existing CPU-only engine...
pip uninstall -y llama-cpp-python

echo [GPU Setup] Installing CUDA-enabled engine...
echo [GPU Setup] This may take a few minutes as it compiles for your GPU...

:: Setting CUDA arguments for compilation
set "CMAKE_ARGS=-DGGML_CUDA=on"
pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir

if %ERRORLEVEL% equ 0 (
    echo.
    echo [SUCCESS] GPU Engine installed successfully!
    echo [INFO] To enable it, set BHARATEDGE_GPU=true in your environment or launch script.
) else (
    echo.
    echo [ERROR] Installation failed. Please ensure CUDA Toolkit and C++ Build Tools are installed.
    echo [INFO] Reverting to CPU-only version...
    pip install llama-cpp-python
)

pause
endlocal
exit /b 0
