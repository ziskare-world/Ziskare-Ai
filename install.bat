@echo off
setlocal enabledelayedexpansion
title Ziskare AI - Universal System Installer
color 0B

echo ===================================================================
echo             Ziskare AI - Universal System-Wide Installer
echo ===================================================================
echo.

:: 1. Check Python
echo [1/5] Checking Python installation...
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    color 0C
    echo [ERROR] Python was not found in your system PATH!
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check 'Add python.exe to PATH' during installation.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PY_VER=%%i
echo   Found %PY_VER%
echo.

:: 2. Check NVIDIA GPU
echo [2/5] Checking NVIDIA GPU and CUDA Driver...
where nvidia-smi >nul 2>nul
if %ERRORLEVEL% equ 0 (
    for /f "tokens=1,2 delims=," %%a in ('nvidia-smi --query-gpu=name,driver_version --format=csv,noheader') do (
        echo   Detected GPU: %%a (Driver: %%b)
    )
) else (
    echo   [Notice] nvidia-smi not found. Ziskare AI will use CPU mode.
)
echo.

:: 3. Install PyTorch with CUDA & Dependencies
echo [3/5] Installing CUDA PyTorch, Transformers, and Accelerate...
echo   (This may take a couple minutes on first run)...
python -m pip install --upgrade pip >nul 2>nul
python -m pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cu126 --force-reinstall
python -m pip install transformers accelerate
echo.

:: 4. Install Ziskare AI Package Globally
echo [4/5] Installing Ziskare AI globally to Python site-packages...
cd /d "%~dp0"
python -m pip install -e .

:: Register global CLI commands
for /f "delims=" %%i in ('python -c "import sys, os; print(os.path.dirname(sys.executable))"') do set PY_DIR=%%i
set CMD_FILE=%PY_DIR%\ziskare-ai.cmd
set SHORT_CMD=%PY_DIR%\ziskare.cmd

echo @echo off > "%CMD_FILE%"
echo python -m ziskare_ai %%* >> "%CMD_FILE%"

echo @echo off > "%SHORT_CMD%"
echo python -m ziskare_ai %%* >> "%SHORT_CMD%"

echo   Created global command: ziskare-ai
echo.

:: 5. Warm-up / Pre-cache Model
echo [5/5] Pre-caching and verifying Ziskare AI model weights...
python -c "from ziskare_ai import ZiskareAI; ai = ZiskareAI(); res = ai.ask('Say hello in 3 words'); print('  Engine test response:', res)"
echo.

color 0A
echo ===================================================================
echo     SUCCESS: Ziskare AI is now globally installed on your PC!
echo ===================================================================
echo.
echo You can now use Ziskare AI from ANYWHERE on your computer:
echo.
echo   1. In ANY Terminal / CMD / PowerShell:
echo      ziskare-ai "Your question here"
echo.
echo   2. In ANY Python file in ANY folder:
echo      import ziskare_ai as zai
echo      print(zai.ask("Your question"))
echo.
echo   3. Launch Local REST API Microservice:
echo      ziskare-ai --server 5005
echo.
pause
