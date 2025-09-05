#!/usr/bin/env python3
"""
Anchorite Launcher
Simple launcher script for the Anchorite focus system
"""

import sys
import subprocess
import os
from pathlib import Path

def main():
    """Launch Anchorite application"""
    print("🚀 Starting Anchorite - AI-Powered Focus System...")
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ Error: app.py not found. Please run this from the Anchorite directory.")
        input("Press Enter to exit...")
        return 1
    
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Error: Python 3.8+ required. Current version:", sys.version)
            input("Press Enter to exit...")
            return 1
        
        # Install dependencies if needed
        print("📦 Checking dependencies...")
        try:
            import tkinter
            import mitmproxy
            print("✅ Dependencies already installed")
        except ImportError:
            print("📦 Installing dependencies...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "mitmproxy", "torch", "numpy", "scikit-learn", 
                "requests", "beautifulsoup4"
            ])
            print("✅ Dependencies installed")
        
        # Launch the application
        print("🎯 Launching Anchorite...")
        subprocess.run([sys.executable, "app.py"])
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Press Enter to exit...")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
