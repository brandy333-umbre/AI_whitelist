@echo off
title Focus Blocker Pro - Proxy-Based Productivity Enforcer
color 0A
echo =======================================
echo  FOCUS BLOCKER PRO - Starting Up...
echo =======================================
echo.
echo This application requires administrator privileges for proxy operations.
echo If prompted, please allow the application to run as administrator.
echo.
echo Choose your interface:
echo [1] GUI Interface (Recommended)
echo [2] Setup and Configuration Menu
echo [3] Background Daemon Mode
echo [4] Original Focus Blocker
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo Starting GUI Interface...
    python focus_gui_controller.py
) else if "%choice%"=="2" (
    echo Starting Setup Menu...
    python setup_and_run.py
) else if "%choice%"=="3" (
    echo Starting Background Daemon...
    python proxy_focus_agent.py daemon
) else if "%choice%"=="4" (
    echo Starting Original Focus Blocker...
    python focus_blocker.py
) else (
    echo Invalid choice. Starting GUI by default...
    python focus_gui_controller.py
)

pause 