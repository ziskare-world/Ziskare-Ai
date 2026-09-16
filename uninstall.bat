@echo off
setlocal enabledelayedexpansion
title Ziskare AI - Uninstaller
color 0E

echo ===================================================================
echo                     Ziskare AI - Uninstaller
echo ===================================================================
echo.
echo This utility will remove Ziskare AI and its global CLI commands
echo from your Python environment and system.
echo.

set /p CONFIRM="Are you sure you want to proceed with uninstallation? (Y/N): "
if /i "!CONFIRM!" neq "Y" (
    echo.
    echo Uninstallation cancelled by user.
    pause
    exit /b 0
)

echo.
echo ===================================================================
echo [1/4] Checking Python environment...
echo ===================================================================
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    color 0C
    echo [WARNING] Python executable was not found in your PATH.
    echo Skipping pip package removal.
) else (
    for /f "tokens=*" %%i in ('python --version') do set PY_VER=%%i
    echo Found !PY_VER!
    
    echo.
    echo [2/4] Uninstalling Ziskare AI package...
    python -m pip uninstall -y ziskare-ai >nul 2>nul
    
    :: Remove manual injection in site-packages if present
    python -c "import site, os, shutil; [shutil.rmtree(os.path.join(p, 'ziskare_ai'), ignore_errors=True) for p in site.getsitepackages() if os.path.exists(os.path.join(p, 'ziskare_ai'))]; [os.remove(os.path.join(p, 'ziskare_ai.py')) for p in site.getsitepackages() if os.path.exists(os.path.join(p, 'ziskare_ai.py'))]" >nul 2>nul
    echo   Uninstalled ziskare-ai package and site-packages modules.
)

echo.
echo ===================================================================
echo [3/4] Removing global Windows CLI commands and executables...
echo ===================================================================
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    for /f "delims=" %%i in ('python -c "import sys, os; print(os.path.dirname(sys.executable))"') do set PY_DIR=%%i
    
    if exist "!PY_DIR!\ziskare-ai.cmd" (
        del /f /q "!PY_DIR!\ziskare-ai.cmd"
        echo   Removed: !PY_DIR!\ziskare-ai.cmd
    )
    if exist "!PY_DIR!\ziskare.cmd" (
        del /f /q "!PY_DIR!\ziskare.cmd"
        echo   Removed: !PY_DIR!\ziskare.cmd
    )
    if exist "!PY_DIR!\Scripts\ziskare-ai.exe" (
        del /f /q "!PY_DIR!\Scripts\ziskare-ai.exe"
        echo   Removed: !PY_DIR!\Scripts\ziskare-ai.exe
    )
    if exist "!PY_DIR!\Scripts\ziskare.exe" (
        del /f /q "!PY_DIR!\Scripts\ziskare.exe"
        echo   Removed: !PY_DIR!\Scripts\ziskare.exe
    )
    if exist "!PY_DIR!\Scripts\ziskare-ai-script.py" (
        del /f /q "!PY_DIR!\Scripts\ziskare-ai-script.py"
        echo   Removed: !PY_DIR!\Scripts\ziskare-ai-script.py
    )
    if exist "!PY_DIR!\Scripts\ziskare-script.py" (
        del /f /q "!PY_DIR!\Scripts\ziskare-script.py"
        echo   Removed: !PY_DIR!\Scripts\ziskare-script.py
    )
)

:: Clean local repo build artifacts
cd /d "%~dp0"
if exist "ziskare_ai.egg-info" rmdir /s /q "ziskare_ai.egg-info" >nul 2>nul
if exist "build" rmdir /s /q "build" >nul 2>nul
if exist "dist" rmdir /s /q "dist" >nul 2>nul
if exist "ziskare_ai\__pycache__" rmdir /s /q "ziskare_ai\__pycache__" >nul 2>nul
echo   Cleaned local build and egg-info caches.

echo.
echo ===================================================================
echo [4/4] Model Weights Cache
echo ===================================================================
set HF_MODEL_DIR=%USERPROFILE%\.cache\huggingface\hub\models--Qwen--Qwen2.5-1.5B-Instruct
if exist "%HF_MODEL_DIR%" (
    echo Downloaded local model weights found (~3 GB):
    echo %HF_MODEL_DIR%
    echo.
    set /p DEL_CACHE="Do you want to delete downloaded model weights to free ~3 GB of disk space? (Y/N): "
    if /i "!DEL_CACHE!" equ "Y" (
        echo Deleting cached model weights...
        rmdir /s /q "%HF_MODEL_DIR%" >nul 2>nul
        echo   Cached model weights deleted successfully.
    ) else (
        echo   Retained cached model weights for future re-installation.
    )
) else (
    echo No cached model weights found in default HuggingFace directory.
)

echo.
color 0A
echo ===================================================================
echo     SUCCESS: Ziskare AI has been uninstalled from this PC.
echo ===================================================================
echo.
echo You can reinstall anytime by running install.bat.
echo.
pause
