#!/usr/bin/env python3
"""
Setup script for AI-driven proxy filtering system
"""

import subprocess
import sys
import os
import json
from datetime import datetime

def install_dependencies():
    """Install required Python packages"""
    print("Installing dependencies...")
    
    packages = [
        "mitmproxy>=10.1.1",
        "sentence-transformers>=2.2.2", 
        "torch>=2.0.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
        "transformers>=4.30.0"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")
            return False
    
    print("Dependencies installed successfully!")
    return True

def setup_mission():
    """Create or update mission.json file"""
    print("Setting up mission configuration...")
    
    if os.path.exists("mission.json"):
        print("Mission file already exists. Would you like to update it? (y/n)")
        choice = input().lower().strip()
        if choice != 'y':
            return True
    
    print("\nEnter your focus mission (what you want to accomplish):")
    mission_text = input().strip()
    
    if not mission_text:
        mission_text = "Focus on productive work and learning, avoiding social media and entertainment distractions"
        print(f"Using default mission: {mission_text}")
    
    mission_data = {
        "mission": mission_text,
        "created": datetime.now().isoformat(),
        "description": "Mission-driven web filtering configuration",
        "settings": {
            "similarity_threshold": 0.4,
            "cache_enabled": True,
            "log_level": "INFO"
        }
    }
    
    with open("mission.json", "w") as f:
        json.dump(mission_data, f, indent=2)
    
    print("Mission configuration saved!")
    return True

def test_ai_filter():
    """Test the AI filter functionality"""
    print("Testing AI filter...")
    
    try:
        import ai_filter
        
        # Test URLs
        test_urls = [
            "https://github.com/python/cpython",
            "https://stackoverflow.com/questions/python",
            "https://facebook.com",
            "https://docs.python.org/3/",
            "https://youtube.com/watch?v=cat_video",
            "https://medium.com/programming-tutorials"
        ]
        
        print("Setting test mission...")
        ai_filter.set_mission("Focus on Python programming and software development")
        
        print("\nTesting URL filtering:")
        for url in test_urls:
            allowed = ai_filter.is_url_allowed(url)
            status = "ALLOW" if allowed else "BLOCK"
            print(f"  {status}: {url}")
        
        print("\nAI filter test completed!")
        return True
        
    except ImportError as e:
        print(f"Error importing ai_filter: {e}")
        print("Make sure all dependencies are installed correctly.")
        return False
    except Exception as e:
        print(f"Error testing AI filter: {e}")
        return False

def create_run_script():
    """Create a script to easily run the proxy"""
    print("Creating run script...")
    
    run_script = """#!/bin/bash
# Run the AI-driven proxy filter
echo "Starting AI-driven proxy filter..."
echo "Configure your browser to use proxy: 127.0.0.1:8080"
echo "Press Ctrl+C to stop"
echo ""

mitmdump -s proxy_filter.py --listen-port 8080
"""
    
    with open("run_proxy.sh", "w") as f:
        f.write(run_script)
    
    # Make script executable on Unix systems
    try:
        os.chmod("run_proxy.sh", 0o755)
    except:
        pass
    
    # Create Windows batch file too
    windows_script = """@echo off
echo Starting AI-driven proxy filter...
echo Configure your browser to use proxy: 127.0.0.1:8080
echo Press Ctrl+C to stop
echo.

mitmdump -s proxy_filter.py --listen-port 8080
pause
"""
    
    with open("run_proxy.bat", "w") as f:
        f.write(windows_script)
    
    print("Run scripts created: run_proxy.sh (Linux/Mac) and run_proxy.bat (Windows)")
    return True

def main():
    """Main setup process"""
    print("🔒 AI-Driven Proxy Filter Setup")
    print("=" * 40)
    
    steps = [
        ("Installing dependencies", install_dependencies),
        ("Setting up mission", setup_mission),
        ("Testing AI filter", test_ai_filter),
        ("Creating run scripts", create_run_script)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Failed: {step_name}")
            sys.exit(1)
        print(f"✅ Completed: {step_name}")
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run the proxy: ./run_proxy.sh (or run_proxy.bat on Windows)")
    print("2. Configure your browser to use proxy 127.0.0.1:8080")
    print("3. Browse the web - distracting sites will be blocked based on your mission!")
    print("\nLogs will be written to activity.log")
    print("Cache database: filter_cache.db")

if __name__ == "__main__":
    main()