#!/usr/bin/env python3
"""
Quick test launcher for the improved email setup
"""

import os
import sys

def main():
    print("🧪 Testing Anchorite Secure Email Setup")
    print("=" * 45)
    print()
    print("This will launch the FIXED secure setup with:")
    print("✅ Emails sent from Anchorite (not user email)")
    print("✅ No user email configuration needed") 
    print("✅ All 3 trusted contact fields visible")
    print("✅ Next button properly displayed")
    print("✅ Enhanced security - user can't access sent emails")
    print("✅ Professional Anchorite email system")
    print()
    print("Expected behavior:")
    print("1. Step 1: Enter your email → Next →")
    print("2. Step 2: Enter 3 trusted contacts → Next → (triggers email sending)")
    print("3. Next app launch: Mission setup per aim.txt lines 23-51")
    print()
    
    # Remove any existing config to test fresh setup
    config_file = "user_config.json"
    if os.path.exists(config_file):
        response = input("Remove existing config to test fresh setup? (y/N): ").strip().lower()
        if response == 'y':
            os.remove(config_file)
            print("✅ Existing config removed")
    
    print("\n🚀 Launching secure Anchorite setup...")
    print()
    
    try:
        from initial_setup import InitialSetup
        setup = InitialSetup()
        setup.run()
        print("✅ Setup completed!")
        
        # Ask if user wants to test mission setup
        test_mission = input("\nTest mission setup (y/N)? ").strip().lower()
        if test_mission == 'y':
            print("\n🎯 Testing enhanced mission setup...")
            import set_mission
            set_mission.main()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 