# 🔒 Focus Blocker - Unbreakable Focus Sessions

A cross-platform desktop productivity tool designed to help people with ADHD stay focused by blocking access to distracting websites during focus sessions. The tool is designed to be hard to bypass or uninstall during an active session.

## 🎯 Core Features

- **Unbreakable Focus Sessions**: Start sessions of 30 minutes to 5 hours where distracting websites are completely blocked
- **Multi-Part Password System**: Emergency unlock requires a 36-character password split into 3 parts sent to trusted friends
- **Cross-Platform Support**: Works on Windows, macOS, and Linux
- **Hosts File Blocking**: Modifies system hosts file to redirect distracting sites to localhost
- **Session Persistence**: Sessions survive app restarts and system reboots
- **Simple GUI**: Clean Tkinter interface for easy session management

## 🚀 Quick Start

### Prerequisites

- Python 3.6 or higher
- Administrator/root privileges (required to modify hosts file)

### Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd focus-blocker
   ```

2. **Run the application**
   
   **Windows:**
   ```bash
   # Run as Administrator
   python focus_blocker.py
   ```
   
   **macOS/Linux:**
   ```bash
   # Run with sudo
   sudo python3 focus_blocker.py
   ```

## 📋 How It Works

### 1. Starting a Focus Session

1. Enter what you're working on in the task field
2. Select your desired session duration (30 min to 5 hours)
3. Click "🚀 Start Unbreakable Focus Session"
4. The app will:
   - Generate a secure 36-character password
   - Split it into 3 parts of 12 characters each
   - Show you the password parts to send to trusted friends
   - Block distracting websites by modifying your hosts file
   - Start a countdown timer

### 2. During the Session

- **Website Blocking**: All distracting sites (Facebook, YouTube, Twitter, Reddit, etc.) are redirected to localhost
- **Unbreakable Protection**: You cannot close the app, uninstall it, or stop the blocking during the session
- **Countdown Timer**: Real-time display of remaining session time
- **Session Persistence**: If you restart your computer, the session continues automatically

### 3. Emergency Unlock

To end a session early, you need the full 36-character password:

1. Click "🔓 Enter Unlock Password"
2. Enter the complete password (all 3 parts combined)
3. If correct, the session ends and websites are unblocked
4. If incorrect, access is denied

### 4. Session Completion

When the timer reaches zero:
- Websites are automatically unblocked
- Session data is cleaned up
- You're ready to start a new session

## 🛡️ Blocked Websites

The app blocks access to:
- **Social Media**: Facebook, Twitter/X, Instagram, Reddit, TikTok, Snapchat, Discord
- **Video Platforms**: YouTube, Twitch, Netflix, Hulu, Disney+
- **Shopping Sites**: Amazon, eBay
- **Other Distractions**: Pinterest, LinkedIn, Spotify

## 🔧 Technical Details

### Hosts File Modification

The app modifies your system's hosts file to redirect distracting domains to `127.0.0.1`:

**Windows**: `C:\Windows\System32\drivers\etc\hosts`
**macOS/Linux**: `/etc/hosts`

Example entries added:
```
# FOCUS BLOCKER ENTRIES
127.0.0.1 facebook.com
127.0.0.1 www.facebook.com
127.0.0.1 youtube.com
127.0.0.1 www.youtube.com
...
```

### Password Security

- 36-character random password generated using `secrets.token_urlsafe()`
- Password is hashed using SHA-256 before storage
- Split into 3 parts of 12 characters each
- Stored locally in `focus_session_password.json`

### Session Persistence

- Session data stored in `focus_session.json`
- App checks for existing sessions on startup
- Automatically resumes blocking if session is still active

## ⚠️ Important Notes

### Administrator Privileges Required

This app requires administrator/root privileges because it needs to modify the system hosts file. Without these privileges, website blocking will not work.

### Security Considerations

- The app is designed to be hard to bypass during active sessions
- The multi-part password system prevents impulsive session termination
- Password parts should be sent to trusted friends who understand the purpose
- Consider the psychological impact of being unable to access certain sites

### Backup and Recovery

If you lose the password and need to end a session:
1. **Manual hosts file editing**: Remove the "FOCUS BLOCKER ENTRIES" section from your hosts file
2. **System restore**: Use system restore points (Windows) or Time Machine (macOS)
3. **Reinstall OS**: As a last resort (not recommended)

## 🐛 Troubleshooting

### "Permission Error" when starting session
- **Windows**: Right-click PowerShell/Command Prompt and select "Run as Administrator"
- **macOS/Linux**: Use `sudo python3 focus_blocker.py`

### Websites still accessible after blocking
- Try flushing DNS cache manually:
  - **Windows**: `ipconfig /flushdns`
  - **macOS**: `sudo dscacheutil -flushcache`
  - **Linux**: `sudo systemctl restart systemd-resolved`
- Restart your web browser
- Check if your browser uses a proxy or VPN

### App won't start
- Ensure Python 3.6+ is installed
- Check that all required modules are available (tkinter, threading, etc.)
- Try running from command line to see error messages

## 🔮 Future Enhancements

Potential features for future versions:
- Website usage tracking and analytics
- AI-powered whitelist suggestions based on productivity patterns
- Remote password validation (friends click links to unlock)
- Custom website blacklist/whitelist management
- Integration with productivity tools and calendars
- Background service mode for automatic startup

## 📄 License

This project is open source. Feel free to modify and distribute according to your needs.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

---

**Disclaimer**: This tool is designed to help with focus and productivity. Use responsibly and consider the psychological impact of being unable to access certain websites. The developers are not responsible for any consequences of using this software. 