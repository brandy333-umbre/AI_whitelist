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
echo [1] RL AI System (Recommended)
echo [2] GUI Interface  
echo [3] Setup and Configuration Menu
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo Starting RL AI System...
    run_rl_proxy.bat
) else if "%choice%"=="2" (
    echo Starting GUI Interface...
    python focus_gui_controller.py
) else if "%choice%"=="3" (
    echo Starting Setup Menu...
    python setup_and_run.py
) else (
    echo Invalid choice. Starting RL AI System by default...
    run_rl_proxy.bat
)

pause 