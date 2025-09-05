#!/usr/bin/env python3
"""
Test Launcher for Initial Setup System
Tests the new email-based security system for Focus Blocker Pro
"""

import os
import sys
import json
from pathlib import Path

def reset_setup():
    """Reset setup by removing configuration file"""
    config_file = "user_config.json"
    if os.path.exists(config_file):
        os.remove(config_file)
        print("✅ Reset complete - setup configuration removed")
    else:
        print("ℹ️ No existing setup found")

def show_config():
    """Show current configuration"""
    config_file = "user_config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            print("📋 Current Configuration:")
            print(f"  User Email: {config.get('user_email', 'Not set')}")
            print(f"  Setup Complete: {config.get('setup_completed', False)}")
            print(f"  Setup Date: {config.get('setup_date', 'Not set')}")
            
            trusted_contacts = config.get('trusted_contacts', [])
            print("  Trusted Contacts:")
            for i, contact in enumerate(trusted_contacts):
                if contact:
                    print(f"    {i+1}. {contact}")
                    
            print(f"  SMTP Server: {config.get('smtp_server', 'Not set')}")
            print(f"  SMTP Port: {config.get('smtp_port', 'Not set')}")
            
        except Exception as e:
            print(f"❌ Error reading configuration: {e}")
    else:
        print("❌ No configuration file found")

def test_initial_setup():
    """Test the initial setup process"""
    print("🧪 Testing initial setup process...")
    try:
        from initial_setup import InitialSetup
        setup = InitialSetup()
        setup.run()
        print("✅ Initial setup test completed")
    except Exception as e:
        print(f"❌ Error testing initial setup: {e}")

def test_unlock_dialog():
    """Test the password unlock dialog"""
    print("🔓 Testing password unlock dialog...")
    try:
        from password_unlock import PasswordUnlock
        unlock = PasswordUnlock()
        success = unlock.run()
        print(f"✅ Unlock test completed - Success: {success}")
    except Exception as e:
        print(f"❌ Error testing unlock dialog: {e}")

def test_main_gui():
    """Test the main GUI with setup integration"""
    print("🖥️ Testing main GUI with setup integration...")
    try:
        from focus_gui_controller import main
        main()
        print("✅ Main GUI test completed")
    except Exception as e:
        print(f"❌ Error testing main GUI: {e}")

def main_menu():
    """Show main test menu"""
    while True:
        print("\n" + "=" * 50)
        print("🧪 Focus Blocker Pro - Initial Setup Test Suite")
        print("=" * 50)
        print("1. Show current configuration")
        print("2. Reset setup (delete config)")
        print("3. Test initial setup process")
        print("4. Test password unlock dialog")
        print("5. Test main GUI (with setup check)")
        print("6. Run complete setup workflow")
        print("7. Exit")
        print()
        
        choice = input("Select an option (1-7): ").strip()
        
        if choice == "1":
            show_config()
        elif choice == "2":
            confirm = input("Are you sure you want to reset setup? (y/N): ").strip().lower()
            if confirm == 'y':
                reset_setup()
        elif choice == "3":
            test_initial_setup()
        elif choice == "4":
            test_unlock_dialog()
        elif choice == "5":
            test_main_gui()
        elif choice == "6":
            print("\n🔄 Running complete setup workflow...")
            print("1. Resetting any existing setup...")
            reset_setup()
            print("\n2. Starting initial setup...")
            test_initial_setup()
            print("\n3. Showing final configuration...")
            show_config()
        elif choice == "7":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-7.")

if __name__ == "__main__":
    main_menu() 