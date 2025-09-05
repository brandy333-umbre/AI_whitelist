# Anchorite - AI-Powered Focus System

## User Guide

### Overview
Anchorite is an AI-powered desktop application that helps you stay focused on your productivity goals. Simply double-click to run, set up your mission, and browse normally - the AI will automatically block distracting websites while allowing productive ones.

### Quick Start

**Windows Users:**
1. **Double-click `Anchorite.bat`**
2. Follow the setup wizard
3. Start your focus session

**Other Platforms:**
1. **Double-click `launch_anchorite.py`** (or run `python launch_anchorite.py`)
2. Follow the setup wizard
3. Start your focus session

### How It Works

1. **Setup (One-time):**
   - Enter your email address
   - Add 3 trusted contacts (for security)
   - Each contact receives a unique password

2. **Start Session:**
   - Describe your specific goal (50+ characters)
   - Set session duration (up to 5 hours)
   - Click "Start Focus Session"

3. **Browse Normally:**
   - Use your browser as usual
   - AI automatically blocks distracting sites
   - Productive sites remain accessible

4. **Session Complete:**
   - Rate visited websites (productive/distracting)
   - AI learns from your feedback
   - System automatically resets

### Features

- **Zero Configuration:** No manual proxy setup required
- **Automatic Setup:** Handles certificates and system configuration
- **AI-Powered Filtering:** Learns what's productive for your goals
- **Security System:** Requires 3 trusted contacts to disable
- **Cross-Platform:** Works on Windows, macOS, and Linux
- **Privacy-First:** All processing happens locally

### System Requirements

- **Python 3.8+** (automatically checked)
- **Windows 10/11, macOS 10.14+, or Linux**
- **4GB RAM minimum**
- **Internet connection**

### Installation

1. **Download** the Anchorite folder
2. **Extract** to any location
3. **Double-click** the launcher file
4. **Follow** the setup wizard

No installation required - just run and go!

### Security & Privacy

- **Local Processing:** All AI analysis happens on your computer
- **No Data Collection:** Nothing is sent to external servers
- **Trusted Contacts:** Security system prevents easy bypass
- **Automatic Cleanup:** System resets after each session

### Troubleshooting

**"Python not found" error:**
- Download Python 3.8+ from https://python.org
- Check "Add Python to PATH" during installation
- Restart your computer

**"Dependencies not found" error:**
- The app will automatically install required packages
- This may take a few minutes on first run

**Browser connection issues:**
- The app automatically configures your system proxy
- If you see certificate warnings, click "Advanced" → "Proceed"
- The app handles all technical setup automatically

### Support

If you encounter issues:

1. Check that Python 3.8+ is installed
2. Ensure you have an internet connection
3. Try running the launcher as administrator (Windows)
4. Check the console output for error messages

### Advanced Usage

**Custom Missions:**
- Be specific about your goals
- Include context and details
- Examples:
  - "Complete the quarterly financial report for Q4 2024"
  - "Research machine learning algorithms for my computer science thesis"
  - "Write the first three chapters of my science fiction novel"

**Session Duration:**
- Choose realistic timeframes
- Start with shorter sessions (30-60 minutes)
- Maximum session: 5 hours (300 minutes)

**Website Ratings:**
- Rate sites as productive (1) or distracting (0)
- This helps the AI learn your preferences
- Ratings are used to improve future filtering

### Files Generated

The app creates these files automatically:
- `mission.json` - Your focus mission
- `activity.log` - System activity logs
- `certs/` - Certificate files (auto-generated)
- `rl_filter_cache.db` - AI learning database

All files are stored locally and can be safely deleted if needed.
