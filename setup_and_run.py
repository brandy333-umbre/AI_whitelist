#!/usr/bin/env python3
"""
Setup and Run Script for Focus Blocker Pro
Handles dependency installation and provides easy launching options
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.11 or higher"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python 3.11+ required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def check_admin_privileges():
    """Check if running with administrator privileges"""
    try:
        if platform.system().lower() == "windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0
    except:
        return False


def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install packages from requirements.txt
        if Path("requirements.txt").exists():
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        else:
            # Install packages individually if requirements.txt not found
            packages = [
                "mitmproxy>=10.0.0",
                "requests>=2.31.0", 
                "psutil>=5.9.0",
                "cryptography>=41.0.0",
                "watchdog>=3.0.0",
                "appdirs>=1.4.4"
            ]
            
            for package in packages:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                
        print("✅ Dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = {
        "mitmproxy": "mitmproxy",
        "requests": "requests",
        "psutil": "psutil", 
        "cryptography": "cryptography",
        "watchdog": "watchdog",
        "appdirs": "appdirs"
    }
    
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - Not installed")
            missing_packages.append(package_name)
            
    return len(missing_packages) == 0, missing_packages


def create_windows_shortcuts():
    """Create Windows shortcuts for easy launching"""
    if platform.system().lower() != "windows":
        return
        
    try:
        # Create batch file for GUI
        gui_batch = """@echo off
title Focus Blocker Pro - GUI
echo Starting Focus Blocker Pro GUI...
python "%~dp0focus_gui_controller.py"
pause
"""
        with open("start_gui.bat", "w") as f:
            f.write(gui_batch)
            
        # Create batch file for daemon
        daemon_batch = """@echo off
title Focus Blocker Pro - Background Agent
echo Starting Focus Blocker Pro Background Agent...
echo This window will run the agent in the background.
echo Close this window to stop the agent (only when no session is active).
python "%~dp0proxy_focus_agent.py" daemon
pause
"""
        with open("start_daemon.bat", "w") as f:
            f.write(daemon_batch)
            
        print("✅ Windows batch files created (start_gui.bat, start_daemon.bat)")
        
    except Exception as e:
        print(f"⚠️ Failed to create Windows shortcuts: {e}")


def configure_proxy_settings():
    """Help user configure proxy settings in their browser"""
    print("\n🌐 Proxy Configuration Instructions:")
    print("=" * 50)
    print("To use Focus Blocker Pro, configure your browser to use the proxy:")
    print()
    print("Manual Proxy Configuration:")
    print("  HTTP Proxy: 127.0.0.1:8080")
    print("  HTTPS Proxy: 127.0.0.1:8080")
    print("  No proxy for: localhost,127.0.0.1")
    print()
    print("For Chrome:")
    print("  1. Settings > Advanced > System > Open proxy settings")
    print("  2. Manual proxy setup")
    print("  3. Use a proxy server: ON")
    print("  4. Address: 127.0.0.1, Port: 8080")
    print()
    print("For Firefox:")
    print("  1. Settings > Network Settings > Settings")
    print("  2. Manual proxy configuration")
    print("  3. HTTP/HTTPS Proxy: 127.0.0.1, Port: 8080")
    print()
    print("IMPORTANT: You must trust the mitmproxy certificate!")
    print("Visit http://mitm.it when the proxy is running to install the certificate.")
    print()


def test_installation():
    """Test if the installation is working"""
    print("\n🧪 Testing installation...")
    
    # Test importing our modules
    try:
        from proxy_focus_agent import ProxyFocusAgent
        print("✅ proxy_focus_agent module imports successfully")
        
        # Test agent creation
        agent = ProxyFocusAgent()
        print("✅ ProxyFocusAgent creates successfully")
        
        # Test configuration loading
        agent.load_config()
        print("✅ Configuration system works")
        
        # Test mission loading
        mission = agent.load_mission()
        print("✅ Mission system works")
        
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main_menu():
    """Display main menu and handle user choices"""
    while True:
        print("\n" + "=" * 50)
        print("🔒 Focus Blocker Pro - Setup & Launcher")
        print("=" * 50)
        print("1. Check system requirements")
        print("2. Install/update dependencies")
        print("3. Test installation")
        print("4. Launch GUI interface")
        print("5. Start background daemon")
        print("6. Show proxy configuration help")
        print("7. Create Windows shortcuts")
        print("8. Exit")
        print()
        
        choice = input("Select an option (1-8): ").strip()
        
        if choice == "1":
            print("\n🔍 Checking system requirements...")
            print(f"Operating System: {platform.system()} {platform.release()}")
            print(f"Python executable: {sys.executable}")
            
            check_python_version()
            
            is_admin = check_admin_privileges()
            if is_admin:
                print("✅ Running with administrator privileges")
            else:
                print("⚠️ Not running as administrator (may need for proxy features)")
                
            deps_ok, missing = check_dependencies()
            if not deps_ok:
                print(f"❌ Missing packages: {', '.join(missing)}")
            else:
                print("✅ All dependencies are installed")
                
        elif choice == "2":
            if not check_python_version():
                continue
            install_dependencies()
            
        elif choice == "3":
            test_installation()
            
        elif choice == "4":
            print("\n🚀 Starting GUI interface...")
            try:
                subprocess.run([sys.executable, "focus_gui_controller.py"])
            except Exception as e:
                print(f"❌ Failed to start GUI: {e}")
                
        elif choice == "5":
            print("\n🔄 Starting background daemon...")
            print("The daemon will run in the background. Press Ctrl+C to stop.")
            try:
                subprocess.run([sys.executable, "proxy_focus_agent.py", "daemon"])
            except KeyboardInterrupt:
                print("\n✅ Daemon stopped")
            except Exception as e:
                print(f"❌ Failed to start daemon: {e}")
                
        elif choice == "6":
            configure_proxy_settings()
            
        elif choice == "7":
            create_windows_shortcuts()
            
        elif choice == "8":
            print("\n👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please select 1-8.")


def quick_start():
    """Quick start for command line usage"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "install":
            print("🔒 Focus Blocker Pro - Quick Install")
            if not check_python_version():
                sys.exit(1)
            if install_dependencies():
                print("✅ Installation complete!")
                configure_proxy_settings()
            else:
                sys.exit(1)
                
        elif command == "gui":
            subprocess.run([sys.executable, "focus_gui_controller.py"])
            
        elif command == "daemon":
            subprocess.run([sys.executable, "proxy_focus_agent.py", "daemon"])
            
        elif command == "test":
            if test_installation():
                print("✅ All systems ready!")
            else:
                sys.exit(1)
                
        else:
            print("Usage: python setup_and_run.py [install|gui|daemon|test]")
            
        return True
    return False


if __name__ == "__main__":
    try:
        # Handle command line arguments for quick actions
        if not quick_start():
            # Show interactive menu
            main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)