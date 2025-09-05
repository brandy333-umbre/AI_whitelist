# Anchorite Certificate Architecture

## Overview
Anchorite uses a multi-layered certificate system to enable HTTPS interception for productivity filtering. The system generates, installs, and manages SSL/TLS certificates automatically to ensure seamless operation for end users.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ANCHORITE CERTIFICATE SYSTEM                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   USER TRIGGER  │    │  AUTO-TRIGGER   │    │  MANUAL TRIGGER │
│                 │    │                 │    │                 │
│ • Double-click  │    │ • GUI startup   │    │ • Command line  │
│   Anchorite.bat │    │ • Proxy start   │    │ • Direct call   │
│ • Launch app    │    │ • System check  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CERTIFICATE MANAGER (generate_certs.py)              │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    CertificateManager Class                        │   │
│  │                                                                     │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │   │
│  │  │   __init__()    │  │ ensure_certs_   │  │ check_existing_ │     │   │
│  │  │                 │  │ directory()     │  │ certificates()  │     │   │
│  │  │ • Setup paths   │  │ • Create certs/ │  │ • Scan for      │     │   │
│  │  │ • Configure     │  │   directory     │  │   existing      │     │   │
│  │  │   logging       │  │ • Set platform  │  │   files         │     │   │
│  │  │ • Define        │  │   detection     │  │ • Return        │     │   │
│  │  │   cert types    │  │                 │  │   status        │     │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        GENERATION METHODS (4 Fallback Layers)              │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────┐ │
│  │   Method 1:     │  │   Method 2:     │  │   Method 3:     │  │Method 4:│ │
│  │   mitmproxy     │  │   subprocess    │  │ cryptography    │  │OpenSSL  │ │
│  │   command line  │  │   with trigger  │  │   library       │  │command  │ │
│  │                 │  │                 │  │                 │  │line     │ │
│  │ • Start         │  │ • Create        │  │ • Generate      │  │         │ │
│  │   mitmdump      │  │   trigger file  │  │   RSA key       │  │ • Check │ │
│  │ • Wait 3s       │  │ • Start         │  │ • Create X.509  │  │   for   │ │
│  │ • Terminate     │  │   mitmdump      │  │   certificate   │  │   OpenSSL│ │
│  │ • Check output  │  │ • Wait 2s       │  │ • Sign with     │  │ • Gen   │ │
│  │ • Copy from     │  │ • Terminate     │  │   private key   │  │ • Gen   │ │
│  │   default loc   │  │ • Check output  │  │ • Convert       │  │   key   │ │
│  │                 │  │                 │  │   formats       │  │ • Gen   │ │
│  │                 │  │                 │  │   cert          │  │   cert  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CERTIFICATE FILES GENERATED                       │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │ mitmproxy-ca-   │  │ mitmproxy-ca-   │  │ mitmproxy-ca-   │             │
│  │ cert.pem        │  │ cert.cer        │  │ cert.p12        │             │
│  │                 │  │                 │  │                 │             │
│  │ • PEM format    │  │ • DER format    │  │ • PKCS12 format │             │
│  │ • Base64        │  │ • Binary        │  │ • Binary with   │             │
│  │   encoded       │  │ • Windows       │  │   password      │             │
│  │ • Text file     │  │   compatible    │  │ • Key + cert    │             │
│  │ • 1,172 bytes   │  │ • 1,172 bytes   │  │ • 1,035 bytes   │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐                                  │
│  │ mitmproxy-ca-   │  │ mitmproxy-      │                                  │
│  │ cert-key.pem    │  │ dhparam.pem     │                                  │
│  │                 │  │                 │                                  │
│  │ • Private key   │  │ • Diffie-       │                                  │
│  │ • RSA 2048-bit  │  │   Hellman      │                                  │
│  │ • PEM format    │  │   parameters    │                                  │
│  │ • Unencrypted   │  │ • For key       │                                  │
│  │ • 1,704 bytes   │  │   exchange      │                                  │
│  │                 │  │ • 770 bytes     │                                  │
│  └─────────────────┘  └─────────────────┘                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AUTOMATIC INSTALLATION                               │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │   Windows       │  │   macOS         │  │   Linux         │             │
│  │   Installation  │  │   Installation  │  │   Installation  │             │
│  │                 │  │                 │  │                 │             │
│  │ Method 1:       │  │ • security      │  │ • Copy to       │             │
│  │   certutil      │  │   add-trusted-  │  │   /usr/local/   │             │
│  │   -user Root    │  │   cert          │  │   share/ca-     │             │
│  │                 │  │ • -d -r         │  │   certificates/ │             │
│  │ Method 2:       │  │   trustRoot     │  │ • update-ca-    │             │
│  │   certutil      │  │ • -k System.    │  │   certificates  │             │
│  │   -f Root       │  │   keychain      │  │                 │             │
│  │                 │  │                 │  │                 │             │
│  │ Method 3:       │  │                 │  │                 │             │
│  │   PowerShell    │  │                 │  │                 │             │
│  │   Import-       │  │                 │  │                 │             │
│  │   Certificate   │  │                 │  │                 │             │
│  │                 │  │                 │  │                 │             │
│  │ Method 4:       │  │                 │  │                 │             │
│  │   runas admin   │  │                 │  │                 │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INTEGRATION POINTS                                │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │   run_rl_proxy. │  │   focus_gui_    │  │   app.py        │             │
│  │   bat           │  │   controller.py │  │                 │             │
│  │                 │  │                 │  │                 │             │
│  │ • Line 26:      │  │ • Line 32:      │  │ • Line 45:      │             │
│  │   python        │  │   self.ensure_  │  │   self.ensure_  │             │
│  │   generate_     │  │   certificates_ │  │   certificates_ │             │
│  │   certs.py      │  │   installed()   │  │   installed()   │             │
│  │   --install     │  │                 │  │                 │             │
│  │                 │  │ • Line 52:      │  │ • Line 52:      │             │
│  │                 │  │   subprocess.   │  │   subprocess.   │             │
│  │                 │  │   run([...])    │  │   run([...])    │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MITMPROXY INTEGRATION                             │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │   RL Proxy      │  │   HTTPS         │  │   Certificate   │             │
│  │   Filter        │  │   Interception  │  │   Validation    │             │
│  │                 │  │                 │  │                 │             │
│  │ • Loads         │  │ • Intercepts    │  │ • Browser       │             │
│  │   certificates  │  │   HTTPS traffic │  │   validates     │             │
│  │ • Uses for      │  │ • Decrypts with │  │   certificate   │             │
│  │   SSL/TLS       │  │   private key   │  │ • Checks        │             │
│  │   connections   │  │ • Re-encrypts   │  │   trust store   │             │
│  │ • Filters       │  │   with new cert │  │ • Accepts if    │             │
│  │   content       │  │                 │  │   trusted       │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Code References

### 1. Certificate Manager Class (`generate_certs.py`)

**Key Methods:**
- `__init__()`: Lines 18-35 - Initializes paths, logging, and required certificate types
- `ensure_certs_directory()`: Lines 37-40 - Creates certs/ directory
- `check_existing_certificates()`: Lines 42-56 - Scans for existing certificates
- `generate_bundled_certificates()`: Lines 380-420 - Main orchestration method

**Required Certificate Files:**
```python
self.required_certs = {
    'ca_cert_pem': 'mitmproxy-ca-cert.pem',      # PEM format certificate
    'ca_cert_cer': 'mitmproxy-ca-cert.cer',      # DER format for Windows
    'ca_cert_p12': 'mitmproxy-ca-cert.p12',      # PKCS12 format
    'ca_key_pem': 'mitmproxy-ca-cert-key.pem',   # Private key
    'dhparam': 'mitmproxy-dhparam.pem'           # DH parameters
}
```

### 2. Generation Methods

**Method 1 - mitmproxy command line** (Lines 58-95):
```python
def generate_certificates_mitmproxy(self) -> bool:
    # Start mitmdump in background
    process = subprocess.Popen([
        sys.executable, "-m", "mitmproxy.tools.dump",
        "--confdir", str(self.certs_dir),
        "--listen-port", "8082",
        "--set", "ssl_insecure=true"
    ])
    # Wait 3 seconds, terminate, check for certificates
```

**Method 2 - subprocess with trigger** (Lines 97-135):
```python
def generate_certificates_subprocess(self) -> bool:
    # Create trigger file, start mitmdump, wait 2 seconds
    # Terminate and check for certificates
```

**Method 3 - cryptography library** (Lines 137-200):
```python
def generate_certificates_cryptography(self) -> bool:
    # Generate RSA private key
    # Create X.509 certificate
    # Sign with private key
    # Convert to multiple formats
```

**Method 4 - OpenSSL command line** (Lines 202-240):
```python
def generate_certificates_openssl(self) -> bool:
    # Check for OpenSSL
    # Generate private key with openssl genrsa
    # Generate certificate with openssl req
    # Convert to DER format
```

### 3. Installation Methods

**Windows Installation** (Lines 270-330):
```python
def install_certificate_windows(self) -> bool:
    # Method 1: certutil -addstore -user Root
    # Method 2: certutil -addstore -f Root
    # Method 3: PowerShell Import-Certificate
    # Method 4: runas Administrator
```

**macOS Installation** (Lines 332-355):
```python
def install_certificate_macos(self) -> bool:
    # security add-trusted-cert -d -r trustRoot
    # -k /Library/Keychains/System.keychain
```

**Linux Installation** (Lines 357-385):
```python
def install_certificate_linux(self) -> bool:
    # Copy to /usr/local/share/ca-certificates/
    # Run update-ca-certificates
```

### 4. Integration Points

**run_rl_proxy.bat** (Line 26):
```batch
python generate_certs.py --install
```

**focus_gui_controller.py** (Lines 32, 52):
```python
def __init__(self):
    # Line 32: Check certificates on startup
    self.ensure_certificates_installed()

def ensure_certificates_installed(self):
    # Line 52: Generate and install certificates
    subprocess.run([sys.executable, "generate_certs.py", "--install"])
```

**app.py** (Lines 45, 52):
```python
def __init__(self):
    # Line 45: Check certificates on startup
    self.ensure_certificates_installed()

def ensure_certificates_installed(self):
    # Line 52: Generate and install certificates
    subprocess.run([sys.executable, "generate_certs.py", "--install"])
```

## Certificate Flow

1. **Trigger**: User action or system startup
2. **Check**: Scan for existing certificates
3. **Generate**: Try 4 methods in sequence until success
4. **Install**: Platform-specific automatic installation
5. **Verify**: Confirm certificates are trusted
6. **Use**: mitmproxy uses certificates for HTTPS interception

## Security Considerations

- **Private Key**: Stored unencrypted in `mitmproxy-ca-cert-key.pem`
- **Certificate Authority**: Self-signed CA certificate
- **Trust**: Automatically installed in system trust store
- **Validity**: 365 days from generation
- **Key Size**: 2048-bit RSA keys

## Error Handling

- **Fallback Methods**: 4 different generation approaches
- **Timeout Protection**: 30-second timeouts for operations
- **Platform Detection**: Automatic OS-specific installation
- **Manual Instructions**: Fallback to manual installation if needed

## File Locations

- **Generated Certificates**: `./certs/` directory
- **Default mitmproxy**: `~/.mitmproxy/` (Unix) or `%USERPROFILE%\.mitmproxy\` (Windows)
- **System Trust Store**: Platform-specific certificate stores
