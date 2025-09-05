@echo off
title Anchorite - AI-Powered Focus System
echo ================================================
echo   Anchorite - AI-Powered Focus System
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ ERROR: Python is not installed
    echo.
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python found
python --version
echo.

REM Launch the application
python launch_anchorite.py

echo.
echo Application closed.
pause
