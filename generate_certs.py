#!/usr/bin/env python3
"""
Enhanced Certificate Generation Script for Anchorite Distribution
Generates all certificate formats and provides automatic installation
"""

import os
import sys
import subprocess
import time
import platform
import logging
from pathlib import Path
from typing import Optional, List, Tuple


class CertificateManager:
    """Enhanced certificate manager for Anchorite distribution"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.certs_dir = self.project_dir / "certs"
        self.platform_system = platform.system().lower()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Certificate files we need to generate
        self.required_certs = {
            'ca_cert_pem': 'mitmproxy-ca-cert.pem',
            'ca_cert_cer': 'mitmproxy-ca-cert.cer', 
            'ca_cert_p12': 'mitmproxy-ca-cert.p12',
            'ca_key_pem': 'mitmproxy-ca-cert-key.pem',
            'dhparam': 'mitmproxy-dhparam.pem'
        }
        
    def ensure_certs_directory(self):
        """Create certs directory if it doesn't exist"""
        self.certs_dir.mkdir(exist_ok=True)
        self.logger.info(f"📁 Certificates directory: {self.certs_dir}")
        
    def check_existing_certificates(self) -> Tuple[bool, List[str]]:
        """Check which certificates already exist"""
        existing = []
        missing = []
        
        for cert_type, filename in self.required_certs.items():
            cert_path = self.certs_dir / filename
            if cert_path.exists() and cert_path.stat().st_size > 0:
                existing.append(filename)
            else:
                missing.append(filename)
                
        all_exist = len(missing) == 0
        return all_exist, existing, missing
        
    def generate_certificates_mitmproxy(self) -> bool:
        """Generate certificates using mitmproxy command line"""
        self.logger.info("🔧 Method 1: Using mitmproxy command line...")
        
        try:
            # Start mitmdump in background to generate certificates
            process = subprocess.Popen([
                sys.executable, "-m", "mitmproxy.tools.dump",
                "--confdir", str(self.certs_dir),
                "--listen-port", "8082",  # Use different port
                "--set", "ssl_insecure=true",
                "--set", "termlog_verbosity=error",
                "--set", "console_eventlog_verbosity=error"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
               creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
            
            # Wait a moment for mitmdump to start and generate certificates
            time.sleep(3)
            
            # Stop the process
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            
            # Check if certificates were generated in the confdir
            cert_file = self.certs_dir / self.required_certs['ca_cert_pem']
            key_file = self.certs_dir / self.required_certs['ca_key_pem']
            
            if cert_file.exists() and cert_file.stat().st_size > 0:
                # Check if private key is missing and copy from default location if needed
                if not key_file.exists():
                    default_cert_dir = Path.home() / ".mitmproxy"
                    default_key_file = default_cert_dir / self.required_certs['ca_key_pem']
                    if default_key_file.exists():
                        import shutil
                        shutil.copy2(default_key_file, key_file)
                        self.logger.info("✅ Private key copied from default mitmproxy location!")
                
                self.logger.info("✅ Certificates generated using mitmproxy command line!")
                return True
            else:
                # Check if certificates were generated in the default location
                default_cert_dir = Path.home() / ".mitmproxy"
                default_cert_file = default_cert_dir / self.required_certs['ca_cert_pem']
                if default_cert_file.exists() and default_cert_file.stat().st_size > 0:
                    # Copy certificates to our certs directory
                    import shutil
                    for cert_type, filename in self.required_certs.items():
                        src_file = default_cert_dir / filename
                        dst_file = self.certs_dir / filename
                        if src_file.exists():
                            shutil.copy2(src_file, dst_file)
                    self.logger.info("✅ Certificates copied from default mitmproxy location!")
                    return True
                else:
                    self.logger.warning("mitmproxy command line method failed: no certificates generated")
                    return False
            
        except subprocess.TimeoutExpired:
            self.logger.warning("mitmproxy command line method timed out")
            return False
        except Exception as e:
            self.logger.warning(f"mitmproxy command line method failed: {e}")
            return False
            
    def generate_certificates_subprocess(self) -> bool:
        """Generate certificates using mitmdump subprocess with file trigger"""
        self.logger.info("🔧 Method 2: Using mitmdump subprocess with file trigger...")
        
        try:
            # Create a temporary file to trigger certificate generation
            trigger_file = self.certs_dir / "trigger.txt"
            trigger_file.write_text("Generate certificates")
            
            # Start mitmdump briefly to generate certificates
            process = subprocess.Popen([
                sys.executable, "-m", "mitmproxy.tools.dump",
                "--confdir", str(self.certs_dir),
                "--listen-port", "8081",  # Use different port
                "--set", "ssl_insecure=true",
                "--set", "termlog_verbosity=error",
                "--set", "console_eventlog_verbosity=error"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
               creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
            
            # Give it time to start and create certificates
            time.sleep(2)
            
            # Stop the process
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                
            # Clean up trigger file
            trigger_file.unlink(missing_ok=True)
            
            # Check if certificates were generated
            cert_file = self.certs_dir / self.required_certs['ca_cert_pem']
            if cert_file.exists() and cert_file.stat().st_size > 0:
                self.logger.info("✅ Certificates generated using mitmdump subprocess!")
                return True
            else:
                self.logger.warning("mitmdump subprocess method failed: no certificates generated")
                return False
            
        except Exception as e:
            self.logger.warning(f"mitmdump subprocess method failed: {e}")
            return False
            
    def generate_certificates_cryptography(self) -> bool:
        """Generate certificates using cryptography library"""
        self.logger.info("🔧 Method 3: Using cryptography library...")
        
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            import datetime
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # Create certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "mitmproxy"),
                x509.NameAttribute(NameOID.COMMON_NAME, "mitmproxy"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=365)
            ).add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True,
            ).sign(private_key, hashes.SHA256())
            
            # Write PEM certificate
            cert_pem_path = self.certs_dir / self.required_certs['ca_cert_pem']
            with open(cert_pem_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
                
            # Write PEM private key
            key_pem_path = self.certs_dir / self.required_certs['ca_key_pem']
            with open(key_pem_path, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
                
            # Convert to other formats
            self._convert_certificate_formats(cert, private_key)
            
            self.logger.info("✅ Certificates generated using cryptography library!")
            return True
            
        except ImportError:
            self.logger.warning("❌ cryptography library not available")
            return False
        except Exception as e:
            self.logger.warning(f"cryptography method failed: {e}")
            return False
            
    def generate_certificates_openssl(self) -> bool:
        """Generate certificates using OpenSSL command line"""
        self.logger.info("🔧 Method 4: Using OpenSSL command line...")
        
        try:
            # Check if OpenSSL is available
            result = subprocess.run(["openssl", "version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                self.logger.warning("OpenSSL not available")
                return False
                
            # Generate private key
            key_file = self.certs_dir / self.required_certs['ca_key_pem']
            subprocess.run([
                "openssl", "genrsa", "-out", str(key_file), "2048"
            ], check=True, capture_output=True, timeout=30)
            
            # Generate certificate
            cert_file = self.certs_dir / self.required_certs['ca_cert_pem']
            subprocess.run([
                "openssl", "req", "-new", "-x509", "-key", str(key_file),
                "-out", str(cert_file), "-days", "365",
                "-subj", "/C=US/ST=CA/L=San Francisco/O=mitmproxy/CN=mitmproxy"
            ], check=True, capture_output=True, timeout=30)
            
            # Convert to .cer format
            cer_file = self.certs_dir / self.required_certs['ca_cert_cer']
            subprocess.run([
                "openssl", "x509", "-inform", "PEM", "-outform", "DER",
                "-in", str(cert_file), "-out", str(cer_file)
            ], check=True, capture_output=True, timeout=30)
            
            self.logger.info("✅ Certificates generated using OpenSSL!")
            return True
            
        except subprocess.TimeoutExpired:
            self.logger.warning("OpenSSL method timed out")
            return False
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"OpenSSL method failed: {e}")
            return False
        except Exception as e:
            self.logger.warning(f"OpenSSL method failed: {e}")
            return False
            
    def _convert_certificate_formats(self, cert, private_key):
        """Convert certificate to different formats (.cer, .p12)"""
        try:
            from cryptography.hazmat.primitives import serialization
            
            # Generate .cer format (DER encoding)
            cer_path = self.certs_dir / self.required_certs['ca_cert_cer']
            with open(cer_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.DER))
                
            # Generate .p12 format (PKCS12)
            try:
                p12_path = self.certs_dir / self.required_certs['ca_cert_p12']
                p12_data = serialization.pkcs12.serialize_key_and_certificates(
                    name=b"mitmproxy",
                    key=private_key,
                    cert=cert,
                    cas=None,
                    encryption_algorithm=serialization.NoEncryption()
                )
                with open(p12_path, "wb") as f:
                    f.write(p12_data)
                    
            except Exception as e:
                self.logger.warning(f"Failed to generate .p12 format: {e}")
                
        except Exception as e:
            self.logger.warning(f"Failed to convert certificate formats: {e}")
            
    def install_certificate_windows(self) -> bool:
        """Install certificate in Windows certificate store"""
        if self.platform_system != "windows":
            return False
            
        cer_file = self.certs_dir / self.required_certs['ca_cert_cer']
        if not cer_file.exists():
            self.logger.error("Certificate file not found for Windows installation")
            return False
            
        try:
            # Method 1: Try automatic installation using certutil (user store)
            print("🔧 Installing certificate in Windows user store...")
            result = subprocess.run([
                "certutil", "-addstore", "-user", "Root", str(cer_file)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.logger.info("✅ Certificate installed in Windows user store")
                return True
                
            # Method 2: Try system store (requires admin)
            print("🔧 Trying system store installation...")
            result = subprocess.run([
                "certutil", "-addstore", "-f", "Root", str(cer_file)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.logger.info("✅ Certificate installed in Windows system store")
                return True
                
            # Method 3: Try PowerShell method
            print("🔧 Trying PowerShell installation method...")
            ps_command = f'Import-Certificate -FilePath "{cer_file}" -CertStoreLocation Cert:\\LocalMachine\\Root'
            result = subprocess.run([
                "powershell", "-Command", ps_command
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.logger.info("✅ Certificate installed via PowerShell")
                return True
                
            # Method 4: Try with elevated privileges
            print("🔧 Trying elevated installation...")
            result = subprocess.run([
                "runas", "/user:Administrator", f'certutil -addstore -f Root "{cer_file}"'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.logger.info("✅ Certificate installed with elevated privileges")
                return True
                
            # If all automatic methods fail, show manual instructions
            self.logger.warning(f"⚠️ All automatic installation methods failed")
            self.logger.warning(f"Last error: {result.stderr}")
            self._show_manual_installation_instructions()
            return False
                
        except subprocess.TimeoutExpired:
            self.logger.warning("⚠️ Certificate installation timed out")
            return False
        except Exception as e:
            self.logger.warning(f"⚠️ Certificate installation error: {e}")
            self._show_manual_installation_instructions()
            return False
            
    def install_certificate_macos(self) -> bool:
        """Install certificate on macOS"""
        if self.platform_system != "darwin":
            return False
            
        pem_file = self.certs_dir / self.required_certs['ca_cert_pem']
        if not pem_file.exists():
            return False
            
        try:
            # Use security command to add to keychain
            result = subprocess.run([
                "security", "add-trusted-cert", "-d", "-r", "trustRoot",
                "-k", "/Library/Keychains/System.keychain", str(pem_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("✅ Certificate installed in macOS keychain")
                return True
            else:
                self.logger.warning(f"⚠️ macOS installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.warning(f"⚠️ macOS certificate installation error: {e}")
            return False
            
    def install_certificate_linux(self) -> bool:
        """Install certificate on Linux"""
        if self.platform_system != "linux":
            return False
            
        pem_file = self.certs_dir / self.required_certs['ca_cert_pem']
        if not pem_file.exists():
            return False
            
        try:
            # Try common Linux certificate locations
            cert_dirs = [
                "/usr/local/share/ca-certificates/",
                "/etc/ssl/certs/",
                "/usr/share/ca-certificates/"
            ]
            
            for cert_dir in cert_dirs:
                if os.path.exists(cert_dir) and os.access(cert_dir, os.W_OK):
                    dest_file = os.path.join(cert_dir, "mitmproxy-ca.crt")
                    subprocess.run(["cp", str(pem_file), dest_file])
                    subprocess.run(["update-ca-certificates"])
                    self.logger.info("✅ Certificate installed in Linux")
                    return True
                    
            self.logger.warning("⚠️ No writable certificate directory found on Linux")
            return False
            
        except Exception as e:
            self.logger.warning(f"⚠️ Linux certificate installation error: {e}")
            return False
            
    def _show_manual_installation_instructions(self):
        """Show manual installation instructions"""
        cer_file = self.certs_dir / self.required_certs['ca_cert_cer']
        
        print("\n" + "="*60)
        print("📋 MANUAL CERTIFICATE INSTALLATION REQUIRED")
        print("="*60)
        print(f"Certificate file: {cer_file}")
        print("\nWindows Instructions:")
        print("1. Double-click the certificate file")
        print("2. Click 'Install Certificate'")
        print("3. Select 'Current User' and click Next")
        print("4. Select 'Place all certificates in the following store'")
        print("5. Click Browse and select 'Trusted Root Certification Authorities'")
        print("6. Click OK, then Next, then Finish")
        print("="*60)
        
    def create_certificate_info(self, generated_files: List[str]):
        """Create certificate information file"""
        info_file = self.certs_dir / "cert_info.txt"
        
        with open(info_file, 'w') as f:
            f.write("Anchorite mitmproxy certificates for distribution\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Platform: {platform.system()} {platform.release()}\n")
            f.write(f"Files generated: {', '.join(generated_files)}\n")
            f.write(f"Total files: {len(generated_files)}\n")
            
    def generate_bundled_certificates(self) -> bool:
        """Main method to generate all certificates for bundling"""
        print("🔐 Generating certificates for Anchorite distribution...")
        print(f"🖥️ Platform: {platform.system()} {platform.release()}")
        
        self.ensure_certs_directory()
        
        # Check existing certificates
        all_exist, existing, missing = self.check_existing_certificates()
        
        if all_exist:
            print(f"✅ All certificates already exist ({len(existing)} files)")
            print("🔄 Use --force to regenerate")
            return True
            
        if existing:
            print(f"📋 Found {len(existing)} existing certificates")
            print(f"🔄 Missing: {', '.join(missing)}")
            
        # Try different methods to generate certificates
        methods = [
            self.generate_certificates_mitmproxy,
            self.generate_certificates_subprocess,
            self.generate_certificates_cryptography,
            self.generate_certificates_openssl
        ]
        
        success = False
        for i, method in enumerate(methods, 1):
            print(f"\n🔧 Trying method {i}/4...")
            if method():
                success = True
                break
                
        if not success:
            self.logger.error("❌ All certificate generation methods failed!")
            return False
            
        # Verify generated files
        all_exist, existing, missing = self.check_existing_certificates()
        
        if existing:
            print(f"\n🎉 Successfully generated {len(existing)} certificate files!")
            for filename in existing:
                file_path = self.certs_dir / filename
                file_size = file_path.stat().st_size
                print(f"✅ {filename} ({file_size:,} bytes)")
                
            # Create info file
            self.create_certificate_info(existing)
            
            # Auto-install certificates on all platforms
            print("\n🔧 Attempting automatic certificate installation...")
            if self.platform_system == "windows":
                self.install_certificate_windows()
            elif self.platform_system == "darwin":
                self.install_certificate_macos()
            elif self.platform_system == "linux":
                self.install_certificate_linux()
                
        if missing:
            print(f"\n⚠️ Some certificates are still missing: {', '.join(missing)}")
            
        return len(existing) > 0


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate certificates for Anchorite")
    parser.add_argument("--force", action="store_true", 
                       help="Force regeneration of existing certificates")
    parser.add_argument("--install", action="store_true",
                       help="Install certificates in system store")
    
    args = parser.parse_args()
    
    cert_manager = CertificateManager()
    
    if args.force:
        # Remove existing certificates
        for filename in cert_manager.required_certs.values():
            cert_path = cert_manager.certs_dir / filename
            cert_path.unlink(missing_ok=True)
            
    success = cert_manager.generate_bundled_certificates()
    
    if success and args.install:
        print("\n🔧 Installing certificates in system store...")
        if cert_manager.platform_system == "windows":
            cert_manager.install_certificate_windows()
        elif cert_manager.platform_system == "darwin":
            cert_manager.install_certificate_macos()
        elif cert_manager.platform_system == "linux":
            cert_manager.install_certificate_linux()
            
    if success:
        print("\n🎉 Certificate generation complete!")
        print("📁 Check the 'certs' folder for the generated files.")
        print("🌐 Configure your browser to use proxy: 127.0.0.1:8080")
    else:
        print("\n❌ Certificate generation failed!")
        print("💡 Try installing dependencies: pip install cryptography mitmproxy")
        
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())