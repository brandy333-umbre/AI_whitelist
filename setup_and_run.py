#!/usr/bin/env python3
"""
Anchorite Setup and Run Script - Distribution Ready
Handles certificate generation, installation, and proxy startup
"""

import os
import sys
import subprocess
import platform
import time
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def generate_certificates():
    """Generate and install certificates"""
    print("🔐 Generating certificates...")
    
    try:
        # Run the certificate generation script
        result = subprocess.run([
            sys.executable, "generate_certs.py", "--install"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Certificates generated and installed!")
            return True
        else:
            print(f"⚠️ Certificate generation output: {result.stdout}")
            print(f"⚠️ Certificate generation errors: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Certificate generation failed: {e}")
        return False

def setup_mission():
    """Setup mission configuration"""
    print("🎯 Setting up mission...")
    
    mission_file = Path("mission.json")
    if mission_file.exists():
        print("✅ Mission file already exists")
        return True
    
    # Create default mission
    default_mission = {
        "mission": "Focus on productive work and learning, avoiding social media and entertainment distractions",
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "description": "Default mission for productivity-focused browsing"
    }
    
    try:
        with open(mission_file, 'w') as f:
            json.dump(default_mission, f, indent=2)
        print("✅ Default mission created")
        return True
    except Exception as e:
        print(f"❌ Failed to create mission: {e}")
        return False

def start_proxy():
    """Start the RL proxy system"""
    print("🚀 Starting Anchorite proxy system...")
    print("\n📋 IMPORTANT: Configure your browser proxy settings:")
    print("   Proxy: 127.0.0.1")
    print("   Port: 8080")
    print("   Enable for HTTP and HTTPS")
    print("\n🔐 If you see certificate errors, visit: http://mitm.it")
    print("   Download and install the certificate for your system")
    print("\n⏹️  Press Ctrl+C to stop the proxy")
    print("=" * 60)
    
    try:
        # Start the RL proxy
        subprocess.run([
            sys.executable, "-m", "mitmproxy.tools.dump",
            "-s", "RL/rl_proxy_filter.py",
            "--listen-port", "8080",
            "--set", "confdir=certs"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Proxy stopped by user")
    except Exception as e:
        print(f"❌ Proxy failed to start: {e}")

def show_browser_instructions():
    """Show browser-specific proxy configuration instructions"""
    print("\n" + "="*60)
    print("🌐 BROWSER PROXY CONFIGURATION")
    print("="*60)
    
    system = platform.system().lower()
    
    if system == "windows":
        print("Chrome/Edge:")
        print("1. Settings → Advanced → System → Open proxy settings")
        print("2. LAN Settings → Use proxy server")
        print("3. Address: 127.0.0.1, Port: 8080")
        print("4. Click OK")
        
        print("\nFirefox:")
        print("1. Settings → General → Network Settings")
        print("2. Manual proxy configuration")
        print("3. HTTP Proxy: 127.0.0.1, Port: 8080")
        print("4. Check 'Use this proxy for all protocols'")
        
    elif system == "darwin":  # macOS
        print("Safari:")
        print("1. Safari → Preferences → Advanced")
        print("2. Click 'Change Settings' next to Proxies")
        print("3. Check 'Web Proxy (HTTP)' and 'Secure Web Proxy (HTTPS)'")
        print("4. Server: 127.0.0.1, Port: 8080")
        
        print("\nChrome:")
        print("1. Settings → Advanced → System → Open proxy settings")
        print("2. Web Proxy (HTTP): 127.0.0.1:8080")
        print("3. Secure Web Proxy (HTTPS): 127.0.0.1:8080")
        
    else:  # Linux
        print("Chrome/Firefox:")
        print("1. Settings → Network → Proxy")
        print("2. Manual proxy configuration")
        print("3. HTTP Proxy: 127.0.0.1, Port: 8080")
        print("4. HTTPS Proxy: 127.0.0.1, Port: 8080")
    
    print("\n🔐 CERTIFICATE INSTALLATION:")
    print("1. Start the proxy first")
    print("2. Visit http://mitm.it in your browser")
    print("3. Download and install the certificate for your OS")
    print("4. Trust the certificate in your system/browser")
    print("="*60)

def main():
    """Main setup and run process"""
    print("🔒 Anchorite - AI-Powered Focus System")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        print("💡 Try running: pip install -r requirements.txt")
        return 1
    
    # Generate certificates
    if not generate_certificates():
        print("⚠️ Certificate generation failed, but continuing...")
    
    # Setup mission
    if not setup_mission():
        return 1
    
    # Show browser instructions
    show_browser_instructions()
    
    # Start proxy
    start_proxy()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())