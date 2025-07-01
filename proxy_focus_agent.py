#!/usr/bin/env python3
"""
Proxy Focus Agent - Advanced productivity enforcement using HTTPS proxy
Background agent that monitors and enforces unbreakable focus sessions
"""

import os
import sys
import json
import time
import signal
import logging
import hashlib
import secrets
import subprocess
import threading
import platform
from datetime import datetime, timedelta
from pathlib import Path
import psutil
import appdirs
from cryptography.fernet import Fernet


class ProxyFocusAgent:
    def __init__(self):
        self.app_name = "ProxyFocusAgent"
        self.app_dir = Path(appdirs.user_data_dir(self.app_name))
        self.app_dir.mkdir(exist_ok=True)
        
        # Configuration files
        self.config_file = self.app_dir / "config.json"
        self.mission_file = self.app_dir / "mission.json"
        self.session_file = self.app_dir / "active_session.json"
        self.password_file = self.app_dir / "session_password.json"
        self.log_file = self.app_dir / "activity.log"
        
        # Session state
        self.session_active = False
        self.session_end_time = None
        self.proxy_process = None
        self.proxy_port = 8080
        self.watchdog_thread = None
        self.session_thread = None
        self.running = True
        
        # Setup logging
        self.setup_logging()
        
        # Load configuration
        self.load_config()
        
        # Signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def setup_logging(self):
        """Setup comprehensive logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        """Load application configuration"""
        default_config = {
            "proxy_port": 8080,
            "check_interval": 5,
            "max_restart_attempts": 10,
            "auto_start_proxy": True,
            "log_all_requests": True,
            "blocked_domains": [
                "facebook.com", "twitter.com", "x.com", "instagram.com",
                "youtube.com", "tiktok.com", "reddit.com", "netflix.com",
                "amazon.com", "ebay.com", "linkedin.com", "pinterest.com"
            ]
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                    # Merge with defaults for any missing keys
                    for key, value in default_config.items():
                        if key not in self.config:
                            self.config[key] = value
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
            
        self.proxy_port = self.config["proxy_port"]
        
    def save_config(self):
        """Save current configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
            
    def load_mission(self):
        """Load user's current mission/goal"""
        default_mission = {
            "title": "Focus Session",
            "description": "Stay productive and avoid distractions",
            "allowed_domains": [
                "github.com", "stackoverflow.com", "python.org",
                "docs.python.org", "pypi.org", "readthedocs.io"
            ],
            "allowed_keywords": [
                "python", "programming", "coding", "development",
                "tutorial", "documentation", "api", "framework"
            ]
        }
        
        if self.mission_file.exists():
            try:
                with open(self.mission_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load mission: {e}")
                
        # Create default mission file
        with open(self.mission_file, 'w') as f:
            json.dump(default_mission, f, indent=2)
        return default_mission
        
    def generate_session_password(self):
        """Generate secure session password with multiple parts"""
        password = secrets.token_urlsafe(32)
        
        # Split into 3 parts for friend-sharing
        part_length = len(password) // 3
        parts = [
            password[:part_length],
            password[part_length:2*part_length],
            password[2*part_length:]
        ]
        
        # Encrypt and store
        key = Fernet.generate_key()
        fernet = Fernet(key)
        encrypted_password = fernet.encrypt(password.encode())
        
        password_data = {
            "encrypted_password": encrypted_password.decode(),
            "key": key.decode(),
            "parts": parts,
            "hash": hashlib.sha256(password.encode()).hexdigest(),
            "created": datetime.now().isoformat()
        }
        
        with open(self.password_file, 'w') as f:
            json.dump(password_data, f, indent=2)
            
        return password, parts
        
    def verify_password(self, entered_password):
        """Verify the entered unlock password"""
        if not self.password_file.exists():
            return False
            
        try:
            with open(self.password_file, 'r') as f:
                password_data = json.load(f)
                
            stored_hash = password_data["hash"]
            entered_hash = hashlib.sha256(entered_password.encode()).hexdigest()
            return stored_hash == entered_hash
        except Exception as e:
            self.logger.error(f"Password verification failed: {e}")
            return False
            
    def start_proxy(self):
        """Start the mitmdump proxy process"""
        try:
            # Create proxy filter script path
            proxy_script = Path(__file__).parent / "proxy_filter.py"
            
            if not proxy_script.exists():
                self.logger.error("proxy_filter.py not found!")
                return False
                
            # Build mitmdump command
            cmd = [
                sys.executable, "-m", "mitmproxy.tools.mitmdump",
                "-s", str(proxy_script),
                "-p", str(self.proxy_port),
                "--set", "confdir=" + str(self.app_dir),
                "--set", "block_global=false"
            ]
            
            self.logger.info(f"Starting proxy on port {self.proxy_port}")
            self.proxy_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
            
            # Give proxy time to start
            time.sleep(3)
            
            if self.proxy_process.poll() is None:
                self.logger.info("Proxy started successfully")
                return True
            else:
                stdout, stderr = self.proxy_process.communicate()
                self.logger.error(f"Proxy failed to start: {stderr.decode()}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start proxy: {e}")
            return False
            
    def stop_proxy(self):
        """Stop the proxy process"""
        if self.proxy_process:
            try:
                if platform.system() == "Windows":
                    # Windows-specific termination
                    subprocess.run(["taskkill", "/PID", str(self.proxy_process.pid), "/F"], 
                                 check=False, capture_output=True)
                else:
                    self.proxy_process.terminate()
                    
                # Wait for process to end
                try:
                    self.proxy_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.proxy_process.kill()
                    
                self.logger.info("Proxy stopped")
                self.proxy_process = None
                return True
            except Exception as e:
                self.logger.error(f"Failed to stop proxy: {e}")
                return False
        return True
        
    def is_proxy_running(self):
        """Check if proxy process is still running"""
        if not self.proxy_process:
            return False
            
        try:
            # Check if process is still alive
            if self.proxy_process.poll() is None:
                # Double-check with psutil
                try:
                    process = psutil.Process(self.proxy_process.pid)
                    return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
                except psutil.NoSuchProcess:
                    return False
            return False
        except Exception:
            return False
            
    def watchdog_loop(self):
        """Monitor proxy and restart if needed"""
        restart_attempts = 0
        max_attempts = self.config["max_restart_attempts"]
        
        while self.running and self.session_active:
            try:
                if not self.is_proxy_running():
                    self.logger.warning("Proxy process died, attempting restart...")
                    
                    if restart_attempts >= max_attempts:
                        self.logger.error(f"Max restart attempts ({max_attempts}) reached")
                        self.emergency_session_end()
                        break
                        
                    if self.start_proxy():
                        restart_attempts = 0
                        self.logger.info("Proxy restarted successfully")
                    else:
                        restart_attempts += 1
                        self.logger.error(f"Restart attempt {restart_attempts} failed")
                        
                time.sleep(self.config["check_interval"])
                
            except Exception as e:
                self.logger.error(f"Watchdog error: {e}")
                time.sleep(self.config["check_interval"])
                
    def start_session(self, duration_hours, task_description="Focus Session"):
        """Start a new focus session"""
        if self.session_active:
            self.logger.warning("Session already active")
            return False
            
        self.logger.info(f"Starting {duration_hours}h focus session: {task_description}")
        
        # Generate session password
        password, parts = self.generate_session_password()
        
        # Calculate end time
        self.session_end_time = datetime.now() + timedelta(hours=duration_hours)
        
        # Start proxy
        if not self.start_proxy():
            self.logger.error("Failed to start proxy, aborting session")
            return False
            
        # Save session data
        session_data = {
            "task": task_description,
            "start_time": datetime.now().isoformat(),
            "end_time": self.session_end_time.isoformat(),
            "duration_hours": duration_hours,
            "proxy_port": self.proxy_port
        }
        
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
            
        self.session_active = True
        
        # Start watchdog
        self.watchdog_thread = threading.Thread(target=self.watchdog_loop, daemon=True)
        self.watchdog_thread.start()
        
        # Start session monitoring
        self.session_thread = threading.Thread(target=self.session_monitor, daemon=True)
        self.session_thread.start()
        
        self.logger.info("Session started successfully")
        return True, password, parts
        
    def session_monitor(self):
        """Monitor session time and end when complete"""
        while self.running and self.session_active and self.session_end_time:
            if datetime.now() >= self.session_end_time:
                self.logger.info("Session time completed")
                self.end_session()
                break
            time.sleep(60)  # Check every minute
            
    def end_session(self, password_verified=False):
        """End the current session"""
        if not self.session_active:
            return True
            
        if not password_verified:
            self.logger.warning("Attempted to end session without password verification")
            return False
            
        self.logger.info("Ending focus session")
        self.session_active = False
        self.session_end_time = None
        
        # Stop proxy
        self.stop_proxy()
        
        # Cleanup session files
        for file_path in [self.session_file, self.password_file]:
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception as e:
                    self.logger.error(f"Failed to remove {file_path}: {e}")
                    
        self.logger.info("Session ended successfully")
        return True
        
    def emergency_session_end(self):
        """Emergency session termination (e.g., too many proxy failures)"""
        self.logger.critical("Emergency session termination")
        self.session_active = False
        self.stop_proxy()
        
    def check_existing_session(self):
        """Check for existing active session on startup"""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                    
                end_time = datetime.fromisoformat(session_data["end_time"])
                if end_time > datetime.now():
                    self.logger.info("Resuming active session")
                    self.session_end_time = end_time
                    self.session_active = True
                    
                    # Restart proxy and monitoring
                    if self.start_proxy():
                        self.watchdog_thread = threading.Thread(target=self.watchdog_loop, daemon=True)
                        self.watchdog_thread.start()
                        
                        self.session_thread = threading.Thread(target=self.session_monitor, daemon=True)
                        self.session_thread.start()
                        return True
                else:
                    # Session expired, cleanup
                    self.session_file.unlink()
                    if self.password_file.exists():
                        self.password_file.unlink()
            except Exception as e:
                self.logger.error(f"Failed to resume session: {e}")
                
        return False
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        if self.session_active:
            self.logger.warning("Cannot shutdown during active session!")
            return
            
        self.logger.info("Shutdown signal received")
        self.shutdown()
        
    def shutdown(self):
        """Clean shutdown"""
        self.running = False
        self.stop_proxy()
        self.logger.info("Agent shutdown complete")
        sys.exit(0)
        
    def run_daemon(self):
        """Run as background daemon"""
        self.logger.info("Starting Proxy Focus Agent")
        
        # Check for existing session
        self.check_existing_session()
        
        try:
            while self.running:
                time.sleep(10)  # Keep daemon alive
        except KeyboardInterrupt:
            if not self.session_active:
                self.shutdown()
        except Exception as e:
            self.logger.error(f"Daemon error: {e}")
            if not self.session_active:
                self.shutdown()


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        agent = ProxyFocusAgent()
        
        if command == "start":
            if len(sys.argv) >= 4:
                duration = float(sys.argv[2])
                task = " ".join(sys.argv[3:])
                result = agent.start_session(duration, task)
                if result:
                    password, parts = result[1], result[2]
                    print(f"Session started! Password parts:")
                    for i, part in enumerate(parts, 1):
                        print(f"Part {i}: {part}")
            else:
                print("Usage: python proxy_focus_agent.py start <hours> <task description>")
                
        elif command == "stop":
            if len(sys.argv) >= 3:
                password = sys.argv[2]
                if agent.verify_password(password):
                    agent.end_session(password_verified=True)
                    print("Session ended successfully")
                else:
                    print("Invalid password!")
            else:
                print("Usage: python proxy_focus_agent.py stop <password>")
                
        elif command == "status":
            if agent.session_active and agent.session_end_time:
                print("Session is ACTIVE")
                remaining = agent.session_end_time - datetime.now()
                print(f"Time remaining: {remaining}")
            else:
                print("No active session")
                
        elif command == "daemon":
            agent.run_daemon()
            
    else:
        print("Proxy Focus Agent")
        print("Commands:")
        print("  start <hours> <task> - Start focus session")
        print("  stop <password> - End session early")
        print("  status - Check session status")
        print("  daemon - Run as background daemon")


if __name__ == "__main__":
    main()