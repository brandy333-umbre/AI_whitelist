#!/usr/bin/env python3
"""
Test Certificate Installation
Simple script to verify that certificates are properly installed and trusted
"""

import subprocess
import sys
import platform
from pathlib import Path

def test_certificate_installation():
    """Test if certificates are properly installed"""
    print("🔐 Testing Certificate Installation")
    print("=" * 50)
    
    # Check if certificates exist
    certs_dir = Path("certs")
    if not certs_dir.exists():
        print("❌ Certificates directory not found")
        return False
        
    cert_files = list(certs_dir.glob("*"))
    if not cert_files:
        print("❌ No certificate files found")
        return False
        
    print(f"✅ Found {len(cert_files)} certificate files:")
    for cert_file in cert_files:
        print(f"   - {cert_file.name}")
    
    # Test certificate installation based on platform
    system = platform.system().lower()
    
    if system == "windows":
        return test_windows_certificates()
    elif system == "darwin":
        return test_macos_certificates()
    elif system == "linux":
        return test_linux_certificates()
    else:
        print(f"⚠️ Unknown platform: {system}")
        return False

def test_windows_certificates():
    """Test Windows certificate installation"""
    print("\n🔧 Testing Windows certificate installation...")
    
    try:
        # Check if certificate is in user store
        result = subprocess.run([
            "certutil", "-store", "-user", "Root", "mitmproxy"
        ], capture_output=True, text=True, timeout=10)
        
        if "mitmproxy" in result.stdout:
            print("✅ Certificate found in Windows user store")
            return True
            
        # Check if certificate is in system store
        result = subprocess.run([
            "certutil", "-store", "Root", "mitmproxy"
        ], capture_output=True, text=True, timeout=10)
        
        if "mitmproxy" in result.stdout:
            print("✅ Certificate found in Windows system store")
            return True
            
        print("❌ Certificate not found in Windows certificate stores")
        print("💡 Try running: python generate_certs.py --install")
        return False
        
    except Exception as e:
        print(f"❌ Error testing Windows certificates: {e}")
        return False

def test_macos_certificates():
    """Test macOS certificate installation"""
    print("\n🔧 Testing macOS certificate installation...")
    
    try:
        # Check if certificate is in keychain
        result = subprocess.run([
            "security", "find-certificate", "-c", "mitmproxy"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Certificate found in macOS keychain")
            return True
        else:
            print("❌ Certificate not found in macOS keychain")
            print("💡 Try running: python generate_certs.py --install")
            return False
            
    except Exception as e:
        print(f"❌ Error testing macOS certificates: {e}")
        return False

def test_linux_certificates():
    """Test Linux certificate installation"""
    print("\n🔧 Testing Linux certificate installation...")
    
    try:
        # Check common certificate locations
        cert_locations = [
            "/usr/local/share/ca-certificates/mitmproxy-ca.crt",
            "/etc/ssl/certs/mitmproxy-ca.crt",
            "/usr/share/ca-certificates/mitmproxy-ca.crt"
        ]
        
        for location in cert_locations:
            if Path(location).exists():
                print(f"✅ Certificate found at: {location}")
                return True
                
        print("❌ Certificate not found in Linux certificate stores")
        print("💡 Try running: python generate_certs.py --install")
        return False
        
    except Exception as e:
        print(f"❌ Error testing Linux certificates: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Anchorite Certificate Test")
    print("=" * 50)
    
    # Test certificate installation
    success = test_certificate_installation()
    
    if success:
        print("\n🎉 Certificate installation test PASSED!")
        print("✅ Your system should trust the mitmproxy certificates")
        print("✅ HTTPS interception should work without certificate errors")
    else:
        print("\n❌ Certificate installation test FAILED!")
        print("⚠️ You may see certificate errors when using the proxy")
        print("💡 Try running the certificate generation manually:")
        print("   python generate_certs.py --install")
    
    print("\n" + "=" * 50)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
