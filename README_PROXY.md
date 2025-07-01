# Focus Blocker Pro - Proxy-Based Productivity Enforcer

An advanced productivity enforcement system that uses HTTPS proxy filtering to create truly unbreakable focus sessions. Unlike simple host file blockers, this system intercepts all web traffic and intelligently filters it based on your mission and productivity goals.

## 🚀 Features

### Core Capabilities
- **HTTPS Proxy Filtering**: Intercepts all web traffic through a local proxy
- **Mission-Based Filtering**: Allows only websites relevant to your current goal
- **Unbreakable Sessions**: Password-protected sessions that resist tampering
- **Automatic Restart**: Watchdog system restarts proxy if it crashes
- **Comprehensive Logging**: Track all allowed and blocked requests
- **Smart Keyword Filtering**: AI-like content filtering based on mission keywords

### Security & Resistance
- **Password Splitting**: Emergency unlock password split into 3 parts for friends
- **Process Monitoring**: Prevents easy termination of the monitoring process
- **Session Persistence**: Resumes sessions after system restart
- **Tamper Resistance**: Multiple layers of protection against circumvention

### User Experience
- **Modern GUI**: Intuitive tabbed interface for all features
- **Real-time Monitoring**: Live countdown and status updates
- **Mission Configuration**: Easy setup of allowed domains and keywords
- **Activity Logs**: View detailed logs of blocked and allowed requests

## 📋 Requirements

- **Python 3.11+** (Required for modern security features)
- **Windows 10/11** (Primary support, Linux/macOS compatible)
- **Administrator/sudo privileges** (Required for proxy operations)
- **Modern web browser** (Chrome, Firefox, Edge supported)

## 🛠️ Installation

### Quick Installation
```bash
# 1. Download the project files
# 2. Run the setup script
python setup_and_run.py install

# 3. Configure your browser proxy settings (see instructions below)
```

### Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Test the installation
python setup_and_run.py test
```

## ⚙️ Browser Configuration

To use Focus Blocker Pro, you must configure your browser to route traffic through the proxy:

### Chrome/Edge
1. Settings → Advanced → System → Open proxy settings
2. Manual proxy setup → Use a proxy server: ON
3. Address: `127.0.0.1`, Port: `8080`
4. Bypass proxy for: `localhost;127.0.0.1`

### Firefox
1. Settings → Network Settings → Settings
2. Manual proxy configuration
3. HTTP/HTTPS Proxy: `127.0.0.1`, Port: `8080`
4. No proxy for: `localhost,127.0.0.1`

### Certificate Installation
**IMPORTANT**: You must install the mitmproxy certificate for HTTPS filtering:
1. Start a focus session
2. Visit `http://mitm.it` in your browser
3. Download and install the certificate for your browser
4. This step is required for HTTPS sites to work properly

## 🎯 Usage

### Starting a Focus Session

#### Method 1: GUI Interface
```bash
python focus_gui_controller.py
```
1. Enter your task description
2. Select session duration
3. Configure your mission in the "Mission Config" tab
4. Click "Start Unbreakable Focus Session"
5. Save the 3-part password (share with trusted friends)

#### Method 2: Command Line
```bash
# Start a 2-hour focus session
python proxy_focus_agent.py start 2 "Learn Python programming"

# Check session status
python proxy_focus_agent.py status

# End session early (requires password)
python proxy_focus_agent.py stop <full_password>
```

#### Method 3: Background Daemon
```bash
# Run as background service
python proxy_focus_agent.py daemon
```

### Mission Configuration

Edit your mission to define what websites and content are allowed:

```json
{
  "title": "Learn Python Programming",
  "description": "Focus on learning Python development skills",
  "allowed_domains": [
    "python.org",
    "docs.python.org", 
    "stackoverflow.com",
    "github.com",
    "pypi.org",
    "realpython.com"
  ],
  "allowed_keywords": [
    "python",
    "programming", 
    "coding",
    "development",
    "tutorial",
    "documentation"
  ]
}
```

### Emergency Unlock

If you need to end a session early:
1. Get all 3 password parts from your trusted friends
2. Combine them into one string (part1+part2+part3)
3. Use the emergency unlock feature in the GUI
4. Or use command line: `python proxy_focus_agent.py stop <combined_password>`

## 📁 File Structure

```
focus-blocker-pro/
├── proxy_focus_agent.py      # Main background agent
├── focus_gui_controller.py   # GUI interface
├── proxy_filter.py          # Proxy filtering logic  
├── setup_and_run.py         # Installation & launcher
├── requirements.txt         # Python dependencies
├── README_PROXY.md          # This documentation
└── config files/            # Auto-generated
    ├── config.json          # Agent configuration
    ├── mission.json         # Current mission
    ├── active_session.json  # Session state
    └── logs/               # Activity logs
```

## 🔧 Configuration Options

### Agent Configuration (`config.json`)
```json
{
  "proxy_port": 8080,
  "check_interval": 5,
  "max_restart_attempts": 10,
  "log_all_requests": true,
  "strict_mode": true
}
```

### Mission Configuration (`mission.json`)
```json
{
  "title": "Your Mission Title",
  "description": "Detailed description of your goal",
  "allowed_domains": ["domain1.com", "domain2.com"],
  "allowed_keywords": ["keyword1", "keyword2"],
  "blocked_domains": ["distraction1.com", "social-media.com"]
}
```

## 🛡️ Security Features

### Password Protection
- **Cryptographically secure**: Uses `secrets` module for password generation
- **Split authentication**: Password divided into 3 parts for social accountability
- **Hash verification**: Passwords are hashed before storage
- **Encrypted storage**: Session data encrypted at rest

### Tamper Resistance
- **Process monitoring**: Watchdog prevents proxy termination
- **Session persistence**: Survives system restarts
- **Multi-layer protection**: Multiple mechanisms prevent circumvention
- **Admin requirements**: Requires elevated privileges for system modifications

### Privacy Protection
- **Local processing**: All filtering happens locally
- **No external calls**: No data sent to external servers
- **Configurable logging**: Control what gets logged
- **Secure cleanup**: Automatic cleanup of sensitive session data

## 📊 Monitoring & Logs

### Available Logs
- **Blocked Requests**: All blocked websites and reasons
- **Allowed Requests**: All permitted traffic
- **Agent Activity**: System events and errors
- **Session History**: Past session details

### Real-time Monitoring
- Live countdown timer
- Proxy status indicator
- Session information display
- Request statistics

## 🔍 Troubleshooting

### Common Issues

**Proxy not starting:**
- Ensure you're running as administrator/sudo
- Check if port 8080 is available
- Verify all dependencies are installed

**HTTPS sites not working:**
- Install the mitmproxy certificate from `http://mitm.it`
- Restart your browser after certificate installation
- Check browser proxy settings

**Sites not being blocked:**
- Verify browser is using proxy settings
- Check mission configuration
- Ensure session is active

**Cannot end session:**
- Verify you have the complete password (all 3 parts)
- Check that session is actually active
- Use command line if GUI fails

### Getting Help

1. Check the Activity Logs tab in the GUI
2. Run `python setup_and_run.py test` to verify installation
3. Ensure all dependencies are up to date
4. Check that you have administrator privileges

## ⚖️ Legal & Ethical Considerations

- **Personal Use**: Intended for personal productivity enhancement
- **Network Monitoring**: Only monitors traffic you explicitly route through it
- **Data Privacy**: All processing happens locally on your machine
- **Workplace Use**: Check company policies before using on work devices

## 🎯 Example Use Cases

### Learning & Education
- **Programming**: Allow coding sites, block social media
- **Research**: Allow academic sites, block entertainment
- **Online Courses**: Allow educational platforms, block distractions

### Work & Business
- **Writing**: Allow research sites, block news/social media
- **Design**: Allow design resources, block shopping sites
- **Data Analysis**: Allow data sites, block everything else

### Personal Goals
- **Health**: Allow fitness sites, block junk food sites
- **Finance**: Allow financial tools, block shopping sites
- **Mindfulness**: Allow meditation sites, block all distractions

## 🔮 Advanced Features

### Custom Filtering Rules
Extend the proxy filter with custom rules for specific needs:
- Time-based filtering
- Content analysis
- Machine learning classification
- API integrations

### Integration Options
- **Calendar integration**: Auto-start sessions based on calendar events
- **Productivity tools**: Integration with task managers
- **Team coordination**: Shared accountability features
- **Analytics**: Detailed productivity analytics

## 📈 Performance

- **Minimal overhead**: Efficient proxy filtering
- **Resource usage**: Low CPU and memory footprint
- **Response time**: Millisecond-level filtering decisions
- **Scalability**: Handles hundreds of requests per second

---

## 🚨 Important Notes

1. **Certificate Installation**: HTTPS filtering requires certificate installation
2. **Admin Rights**: Must run with administrator/sudo privileges  
3. **Browser Configuration**: Proxy must be configured in browser settings
4. **Backup Passwords**: Keep password parts in multiple safe locations
5. **Testing**: Test thoroughly before important focus sessions

**Remember**: This tool is designed to help you maintain focus and achieve your goals. Use it responsibly and in accordance with your personal and professional obligations.