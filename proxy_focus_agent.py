#!/usr/bin/env python3
"""
Proxy Focus Agent - Main background agent for focus session management
Handles session lifecycle, proxy control, and monitoring
"""

import json
import os
import sys
import time
import threading
import subprocess
import secrets
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
import psutil


class ProxyFocusAgent:
    """Main agent for managing focus sessions and proxy control"""
    
    def __init__(self):
        # Initialize paths and directories
        self._init_paths()
        
        # Initialize configuration
        self.config = self.load_config()
        self.proxy_port = self.config.get("proxy_port", 8080)
        
        # Session state
        self.session_active = False
        self.session_end_time = None
        self.proxy_process = None
        self.monitoring_thread = None
        self._shutdown_event = threading.Event()
        
        # Setup logging
        self._setup_logging()
        
        # Load existing session if any
        self._load_existing_session()
        
    def _init_paths(self):
        """Initialize application paths"""
        # Current working directory
        self.app_dir = Path.cwd()
        
        # User data directory
        if sys.platform == "win32":
            self.user_data_dir = Path(os.environ.get("APPDATA", "")) / "ProxyFocusAgent"
        else:
            self.user_data_dir = Path.home() / ".config" / "ProxyFocusAgent"
            
        # Ensure user data directory exists
        self.user_data_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.config_file = self.user_data_dir / "config.json"
        self.mission_file = self.app_dir / "mission.json"
        self.session_file = self.user_data_dir / "active_session.json"
        self.password_file = self.user_data_dir / "session_password.json"
        self.activity_log = self.user_data_dir / "activity.log"
        
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.activity_log),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self) -> Dict[str, Any]:
        """Load agent configuration"""
        default_config = {
            "proxy_port": 8080,
            "log_all_requests": True,
            "check_interval": 5,
            "max_restart_attempts": 10,
            "strict_mode": True,
            "rl_model_path": "RL/best_pretrained_model.pth",
            "rl_script_path": "RL/rl_proxy_filter.py"
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    default_config.update(config)
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
                
        return default_config
        
    def save_config(self):
        """Save agent configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            
    def load_mission(self) -> Dict[str, Any]:
        """Load mission configuration"""
        default_mission = {
            "title": "Focus Session",
            "description": "Stay focused on productive activities and avoid distractions",
            "allowed_domains": [
                "docs.python.org",
                "stackoverflow.com",
                "github.com",
                "youtube.com",  # For educational content
                "coursera.org",
                "udemy.com"
            ],
            "allowed_keywords": [
                "python",
                "programming",
                "tutorial",
                "documentation",
                "machine learning",
                "coding",
                "bladee",  # From user mission
                "yung lean",
                "drain gang"
            ]
        }
        
        if self.mission_file.exists():
            try:
                with open(self.mission_file, 'r') as f:
                    mission_data = json.load(f)
                    # Handle both old and new mission format
                    if "mission" in mission_data:
                        # Old format from set_mission.py
                        return {
                            "title": "User Mission",
                            "description": mission_data["mission"],
                            "allowed_domains": default_mission["allowed_domains"],
                            "allowed_keywords": default_mission["allowed_keywords"]
                        }
                    else:
                        # New format from GUI
                        return mission_data
            except Exception as e:
                self.logger.error(f"Error loading mission: {e}")
                
        return default_mission
        
    def _generate_password_parts(self) -> Tuple[str, List[str]]:
        """Generate 3-part password system for emergency unlock"""
        # Generate a secure random password
        password = secrets.token_urlsafe(32)
        
        # Split into 3 parts for social accountability
        part_length = len(password) // 3
        parts = [
            password[:part_length],
            password[part_length:2*part_length],
            password[2*part_length:]
        ]
        
        return password, parts
        
    def start_session(self, duration_hours: float, task: str) -> Optional[Tuple[bool, str, List[str]]]:
        """Start a new focus session"""
        if self.session_active:
            self.logger.warning("Session already active")
            return None
            
        try:
            # Generate password
            password, parts = self._generate_password_parts()
            
            # Calculate end time
            self.session_end_time = datetime.now() + timedelta(hours=duration_hours)
            
            # Create session data
            session_data = {
                "task": task,
                "start_time": datetime.now().isoformat(),
                "end_time": self.session_end_time.isoformat(),
                "duration_hours": duration_hours,
                "proxy_port": self.proxy_port,
                "password_hash": hashlib.sha256(password.encode()).hexdigest()
            }
            
            # Save session data
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
                
            # Save password parts (encrypted in real implementation)
            with open(self.password_file, 'w') as f:
                json.dump({"parts": parts}, f, indent=2)
                
            # Start proxy
            if self._start_proxy():
                self.session_active = True
                self._start_monitoring()
                self.logger.info(f"Focus session started: {duration_hours}h for '{task}'")
                return True, password, parts
            else:
                # Cleanup on proxy start failure
                self.session_file.unlink(missing_ok=True)
                self.password_file.unlink(missing_ok=True)
                return False, "", []
                
        except Exception as e:
            self.logger.error(f"Error starting session: {e}")
            return None
            
    def start_focus_session(self, mission: str, duration_minutes: int):
        """Alternative start method for compatibility with set_mission.py"""
        duration_hours = duration_minutes / 60.0
        return self.start_session(duration_hours, mission)
        
    def end_session(self):
        """End the current focus session"""
        if not self.session_active:
            return
            
        self.logger.info("Ending focus session")
        
        # Stop monitoring
        self._shutdown_event.set()
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
            
        # Stop proxy
        self._stop_proxy()
        
        # Clear session state
        self.session_active = False
        self.session_end_time = None
        
        # Remove session files
        self.session_file.unlink(missing_ok=True)
        self.password_file.unlink(missing_ok=True)
        
    def check_existing_session(self) -> bool:
        """Check for and resume existing session"""
        return self._load_existing_session()
        
    def _load_existing_session(self) -> bool:
        """Load existing session from file"""
        if not self.session_file.exists():
            return False
            
        try:
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
                
            # Parse end time
            end_time = datetime.fromisoformat(session_data["end_time"])
            
            # Check if session is still valid
            if datetime.now() < end_time:
                self.session_active = True
                self.session_end_time = end_time
                self.proxy_port = session_data.get("proxy_port", 8080)
                
                # Restart proxy if not running
                if not self.is_proxy_running():
                    self._start_proxy()
                    
                # Restart monitoring
                self._start_monitoring()
                
                self.logger.info("Resumed existing focus session")
                return True
            else:
                # Session expired, clean up
                self.session_file.unlink(missing_ok=True)
                self.password_file.unlink(missing_ok=True)
                
        except Exception as e:
            self.logger.error(f"Error loading existing session: {e}")
            
        return False
        
    def _start_proxy(self) -> bool:
        """Start the proxy process"""
        try:
            # Use the RL proxy filter
            script_path = self.app_dir / self.config.get("rl_script_path", "RL/rl_proxy_filter.py")
            
            if not script_path.exists():
                self.logger.error(f"RL proxy script not found: {script_path}")
                return False
                
            # Start mitmproxy with our RL filter using bundled certificates
            certs_dir = self.app_dir / "certs"
            cmd = [
                sys.executable, "-m", "mitmproxy",
                "-s", str(script_path),
                "--listen-port", str(self.proxy_port),
                "--set", f"confdir={certs_dir}"
            ]
            
            # Start process
            self.proxy_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.app_dir
            )
            
            # Give it a moment to start
            time.sleep(2)
            
            if self.proxy_process.poll() is None:
                self.logger.info(f"Proxy started on port {self.proxy_port}")
                return True
            else:
                self.logger.error("Proxy failed to start")
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting proxy: {e}")
            return False
            
    def _stop_proxy(self):
        """Stop the proxy process"""
        if self.proxy_process:
            try:
                self.proxy_process.terminate()
                self.proxy_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proxy_process.kill()
            except Exception as e:
                self.logger.error(f"Error stopping proxy: {e}")
            finally:
                self.proxy_process = None
                
    def is_proxy_running(self) -> bool:
        """Check if proxy process is running"""
        if self.proxy_process:
            return self.proxy_process.poll() is None
            
        # Check for mitmproxy processes on our port
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline']
                    if cmdline and 'mitmproxy' in ' '.join(cmdline) and str(self.proxy_port) in ' '.join(cmdline):
                        return True
        except Exception:
            pass
            
        return False
        
    def _start_monitoring(self):
        """Start monitoring thread"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            return
            
        self._shutdown_event.clear()
        self.monitoring_thread = threading.Thread(target=self._monitor_session, daemon=True)
        self.monitoring_thread.start()
        
    def _monitor_session(self):
        """Monitor session and proxy status"""
        restart_attempts = 0
        max_attempts = self.config.get("max_restart_attempts", 10)
        check_interval = self.config.get("check_interval", 5)
        
        while not self._shutdown_event.wait(check_interval):
            try:
                # Check if session time expired
                if self.session_active and self.session_end_time:
                    if datetime.now() >= self.session_end_time:
                        self.logger.info("Session time completed")
                        self.end_session()
                        break
                        
                # Check proxy status and restart if needed
                if self.session_active and not self.is_proxy_running():
                    if restart_attempts < max_attempts:
                        self.logger.warning(f"Proxy not running, restarting (attempt {restart_attempts + 1})")
                        if self._start_proxy():
                            restart_attempts = 0  # Reset on successful restart
                        else:
                            restart_attempts += 1
                    else:
                        self.logger.error("Max restart attempts reached, ending session")
                        self.end_session()
                        break
                        
            except Exception as e:
                self.logger.error(f"Error in monitoring: {e}")


# Singleton instance for global access
_agent_instance = None

def get_agent():
    """Get the global agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ProxyFocusAgent()
    return _agent_instance
