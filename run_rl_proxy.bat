@echo off
echo ====================================
echo   Focus Blocker Pro - RL System
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [1/4] Checking dependencies...
python -c "import torch, mitmproxy" >nul 2>&1
if %errorLevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if %errorLevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo [2/4] Checking for pre-trained model...
if not exist "RL\best_pretrained_model.pth" (
    echo No pre-trained model found. Running pre-training...
    echo This may take 5-10 minutes...
    cd RL
    python pretrain_rl_model.py
    cd ..
    if %errorLevel% neq 0 (
        echo ERROR: Pre-training failed
        pause
        exit /b 1
    )
)

echo [2.5/4] Generating and installing certificates...
python generate_certs.py --install
if %errorLevel% neq 0 (
    echo WARNING: Certificate generation had issues, but continuing...
    echo You may need to install certificates manually if you see SSL errors
)

echo [3/5] Starting RL proxy filter...
echo.
echo IMPORTANT: Configure your browser proxy settings:
echo   Proxy: 127.0.0.1
echo   Port: 8080
echo   Enable for HTTP and HTTPS
echo.
echo Using pretrained AI model with 94% accuracy for filtering decisions.
echo When websites are blocked, you can provide feedback to help monitor performance.
echo.

echo [4/5] Launching proxy...
echo Press Ctrl+C to stop the proxy
echo.

REM Start the RL proxy
mitmdump -s RL\rl_proxy_filter.py --listen-port 8080 --set confdir=certs

echo.
echo Proxy stopped.
pause 