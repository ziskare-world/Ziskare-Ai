@echo off
title Ziskare AI - Auto Re-Setup
echo ========================================================
echo        Ziskare AI - Automatic Recovery Setup
echo ========================================================
echo.
echo Launching PowerShell setup script...
powershell -ExecutionPolicy Bypass -File "%~dp0setup_ziskare_ai.ps1"
echo.
pause
