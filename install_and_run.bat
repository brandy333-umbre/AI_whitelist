@echo off
title Anchorite - AI-Powered Focus System Setup
echo ================================================
echo   Anchorite - AI-Powered Focus System
echo ================================================
echo.

REM Check if Python is installed
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Install dependencies
echo.
echo [2/6] Installing dependencies...
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo ❌ ERROR: Failed to install dependencies
    echo.
    echo Try running: pip install --upgrade pip
    echo Then run this script again
    echo.
    pause
    exit /b 1
)

echo ✅ Dependencies installed

REM Generate certificates
echo.
echo [3/6] Generating certificates...
python generate_certs.py --install
if %errorLevel% neq 0 (
    echo ⚠️ WARNING: Certificate generation had issues
    echo The system will continue, but you may need to install certificates manually
    echo.
)

REM Setup mission
echo.
echo [4/6] Setting up mission configuration...
if not exist "mission.json" (
    echo Creating default mission...
    python -c "import json; import time; open('mission.json', 'w').write(json.dumps({'mission': 'Focus on productive work and learning, avoiding social media and entertainment distractions', 'created': time.strftime('%Y-%m-%d %H:%M:%S'), 'description': 'Default mission for productivity-focused browsing'}, indent=2))"
    echo ✅ Default mission created
) else (
    echo ✅ Mission file already exists
)

REM Show instructions
echo.
echo [5/6] Setup complete!
echo ================================================
echo 🌐 BROWSER PROXY CONFIGURATION REQUIRED
echo ================================================
echo.
echo Chrome/Edge:
echo 1. Settings → Advanced → System → Open proxy settings
echo 2. LAN Settings → Use proxy server
echo 3. Address: 127.0.0.1, Port: 8080
echo 4. Click OK
echo.
echo Firefox:
echo 1. Settings → General → Network Settings
echo 2. Manual proxy configuration
echo 3. HTTP Proxy: 127.0.0.1, Port: 8080
echo 4. Check 'Use this proxy for all protocols'
echo.
echo 🔐 CERTIFICATE INSTALLATION:
echo 1. Start the proxy (next step)
echo 2. Visit http://mitm.it in your browser
echo 3. Download and install the certificate for Windows
echo 4. Trust the certificate in your system
echo.
echo ================================================

REM Start proxy
echo [6/6] Starting Anchorite proxy system...
echo.
echo 🚀 Proxy starting on 127.0.0.1:8080
echo 📋 Configure your browser proxy settings (see above)
echo 🔐 If you see certificate errors, visit: http://mitm.it
echo ⏹️  Press Ctrl+C to stop the proxy
echo.
echo ================================================

REM Start the RL proxy
mitmdump -s RL\rl_proxy_filter.py --listen-port 8080 --set confdir=certs

echo.
echo Proxy stopped.
pause
