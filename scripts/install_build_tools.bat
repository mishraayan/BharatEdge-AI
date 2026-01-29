@echo off
echo [INFO] BharatEdge AI - Build Tools Installer
echo ============================================
echo.
echo [WARN] This script will check for and attempt to install:
echo 1. Visual Studio C++ Build Tools (Required for Tauri/Connectors)
echo 2. Rust Programming Language (Required for Tauri)
echo.
echo [NOTE] This may require Administrator privileges and a system RESTART.
echo.
pause

echo.
echo [STEP 1/2] Checking for Visual Studio Build Tools...
winget list "Visual Studio Build Tools" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] VS Build Tools likely installed.
) else (
    echo [INFO] Installing VS Build Tools 2022...
    echo [INFO] Please accept any UAC prompts.
    winget install --id Microsoft.VisualStudio.2022.BuildTools --override "--passive --wait --add Microsoft.VisualStudio.Workload.VCTools;includeRecommended"
)

echo.
echo [STEP 2/2] Checking for Rust...
where cargo >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Rust is installed.
) else (
    echo [INFO] Installing Rust (Rustup)...
    winget install --id Rustlang.Rustup
    echo.
    echo [IMPORTANT] After this finishes, you might need to RESTART your terminal/PC.
)

echo.
echo [DONE] Please CLOSE this terminal and open a NEW one to refresh PATH variables.
pause
