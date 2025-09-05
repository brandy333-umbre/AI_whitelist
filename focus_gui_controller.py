#!/usr/bin/env python3
"""
Focus GUI Controller - Enhanced interface for proxy-based focus sessions
Combines the original GUI with advanced proxy functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import subprocess
import sys
import platform
from pathlib import Path
from datetime import datetime, timedelta
import os

from proxy_focus_agent import ProxyFocusAgent
from initial_setup import run_initial_setup, is_setup_complete
from password_unlock import show_unlock_dialog


class FocusGUIController:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Focus Blocker Pro - Proxy-Based Productivity Enforcer")
        self.root.geometry("700x800")
        self.root.resizable(True, True)
        
        # Initialize the proxy agent
        self.agent = ProxyFocusAgent()
        
        # GUI state
        self.session_password = None
        self.password_parts = []
        self.monitoring_thread = None
        self.running = True
        
        # Check and install certificates
        self.ensure_certificates_installed()
        
        # Setup GUI
        self.setup_gui()
        
        # Check for existing session
        self.check_existing_session()
        
        # Setup periodic updates
        self.update_gui()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def ensure_certificates_installed(self):
        """Ensure certificates are generated and installed"""
        try:
            # Check if certificates exist
            certs_dir = Path("certs")
            if not certs_dir.exists() or not list(certs_dir.glob("*.pem")):
                print("🔐 Generating certificates...")
                subprocess.run([sys.executable, "generate_certs.py", "--install"], 
                             capture_output=True, timeout=60)
                print("✅ Certificates generated and installed")
            else:
                print("✅ Certificates already exist")
        except Exception as e:
            print(f"⚠️ Certificate setup warning: {e}")
            # Continue anyway - certificates might still work
        
    def setup_gui(self):
        """Setup the enhanced GUI interface"""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Session tab
        self.session_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.session_frame, text="Focus Session")
        self.setup_session_tab()
        
        # Mission tab
        self.mission_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.mission_frame, text="Mission Config")
        self.setup_mission_tab()
        
        # Logs tab
        self.logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_frame, text="Activity Logs")
        self.setup_logs_tab()
        
        # Settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        self.setup_settings_tab()
        
    def setup_session_tab(self):
        """Setup the main session control tab"""
        main_frame = ttk.Frame(self.session_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🔒 Focus Blocker Pro", 
                               font=("Arial", 24, "bold"))
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Proxy-Based Productivity Enforcement", 
                                  font=("Arial", 12))
        subtitle_label.pack(pady=(0, 30))
        
        # Task input
        task_label = ttk.Label(main_frame, text="What are you working on?", 
                              font=("Arial", 12, "bold"))
        task_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.task_entry = ttk.Entry(main_frame, width=60, font=("Arial", 11))
        self.task_entry.pack(fill=tk.X, pady=(0, 20))
        self.task_entry.insert(0, "Learn Python programming")
        
        # Duration selection
        duration_label = ttk.Label(main_frame, text="Focus Session Duration:", 
                                  font=("Arial", 12, "bold"))
        duration_label.pack(anchor=tk.W, pady=(0, 5))
        
        duration_frame = ttk.Frame(main_frame)
        duration_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.duration_var = tk.StringVar(value="2")
        durations = [("30 min", "0.5"), ("1 hour", "1"), ("2 hours", "2"), 
                    ("3 hours", "3"), ("4 hours", "4"), ("5 hours", "5")]
        
        for i, (text, value) in enumerate(durations):
            row = i // 3
            col = i % 3
            ttk.Radiobutton(duration_frame, text=text, variable=self.duration_var, 
                           value=value).grid(row=row, column=col, padx=10, pady=5, sticky=tk.W)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="🚀 Start Unbreakable Focus Session", 
                                      command=self.start_session, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.unlock_button = ttk.Button(button_frame, text="🔑 Emergency Unlock", 
                                       command=self.show_unlock_dialog)
        self.unlock_button.pack(side=tk.LEFT)
        
        # Status display
        self.status_frame = ttk.LabelFrame(main_frame, text="Session Status", padding="15")
        self.status_frame.pack(fill=tk.X, pady=20)
        
        self.countdown_label = ttk.Label(self.status_frame, text="", 
                                        font=("Arial", 18, "bold"), foreground="red")
        self.countdown_label.pack(pady=5)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready to start a focus session", 
                                     font=("Arial", 11), foreground="green")
        self.status_label.pack(pady=5)
        
        self.proxy_status_label = ttk.Label(self.status_frame, text="Proxy: Not running", 
                                           font=("Arial", 10))
        self.proxy_status_label.pack(pady=2)
        
        # Session info
        info_frame = ttk.LabelFrame(main_frame, text="Session Information", padding="15")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.session_info = scrolledtext.ScrolledText(info_frame, height=8, width=70, 
                                                     font=("Arial", 9), wrap=tk.WORD)
        self.session_info.pack(fill=tk.BOTH, expand=True)
        self.session_info.insert(tk.END, "Session information will appear here...")
        self.session_info.config(state=tk.DISABLED)
        
    def setup_mission_tab(self):
        """Setup mission configuration tab"""
        main_frame = ttk.Frame(self.mission_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Mission Configuration", 
                 font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Mission title
        ttk.Label(main_frame, text="Mission Title:", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        self.mission_title = ttk.Entry(main_frame, width=60)
        self.mission_title.pack(fill=tk.X, pady=(5, 15))
        
        # Mission description
        ttk.Label(main_frame, text="Description:", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        self.mission_desc = tk.Text(main_frame, height=3, width=60, wrap=tk.WORD)
        self.mission_desc.pack(fill=tk.X, pady=(5, 15))
        
        # Allowed domains
        ttk.Label(main_frame, text="Allowed Domains (one per line):", 
                 font=("Arial", 11, "bold")).pack(anchor=tk.W)
        self.allowed_domains = scrolledtext.ScrolledText(main_frame, height=6, width=60)
        self.allowed_domains.pack(fill=tk.X, pady=(5, 15))
        
        # Allowed keywords
        ttk.Label(main_frame, text="Allowed Keywords (one per line):", 
                 font=("Arial", 11, "bold")).pack(anchor=tk.W)
        self.allowed_keywords = scrolledtext.ScrolledText(main_frame, height=4, width=60)
        self.allowed_keywords.pack(fill=tk.X, pady=(5, 15))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Load Mission", 
                  command=self.load_mission_config).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Save Mission", 
                  command=self.save_mission_config).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Reset to Default", 
                  command=self.reset_mission_config).pack(side=tk.RIGHT)
        
        # Load current mission
        self.load_mission_config()
        
    def setup_logs_tab(self):
        """Setup activity logs tab"""
        main_frame = ttk.Frame(self.logs_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Activity Logs", 
                 font=("Arial", 16, "bold")).pack(pady=(0, 10))
        
        # Log type selection
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.X, pady=10)
        
        self.log_type_var = tk.StringVar(value="blocked")
        ttk.Radiobutton(log_frame, text="Blocked Requests", variable=self.log_type_var, 
                       value="blocked", command=self.refresh_logs).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(log_frame, text="Allowed Requests", variable=self.log_type_var, 
                       value="allowed", command=self.refresh_logs).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(log_frame, text="Agent Logs", variable=self.log_type_var, 
                       value="agent", command=self.refresh_logs).pack(side=tk.LEFT)
        
        # Refresh button
        ttk.Button(log_frame, text="Refresh", command=self.refresh_logs).pack(side=tk.RIGHT)
        
        # Log display
        self.log_display = scrolledtext.ScrolledText(main_frame, height=20, width=80, 
                                                    font=("Courier", 9))
        self.log_display.pack(fill=tk.BOTH, expand=True, pady=10)
        
    def setup_settings_tab(self):
        """Setup settings configuration tab"""
        main_frame = ttk.Frame(self.settings_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Settings", 
                 font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Proxy settings
        proxy_frame = ttk.LabelFrame(main_frame, text="Proxy Settings", padding="15")
        proxy_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(proxy_frame, text="Proxy Port:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.proxy_port = ttk.Entry(proxy_frame, width=10)
        self.proxy_port.grid(row=0, column=1, sticky=tk.W)
        self.proxy_port.insert(0, str(self.agent.config.get("proxy_port", 8080)))
        
        # Monitoring settings
        monitor_frame = ttk.LabelFrame(main_frame, text="Monitoring Settings", padding="15")
        monitor_frame.pack(fill=tk.X, pady=10)
        
        self.log_all_var = tk.BooleanVar(value=self.agent.config.get("log_all_requests", True))
        ttk.Checkbutton(monitor_frame, text="Log all requests", 
                       variable=self.log_all_var).pack(anchor=tk.W, pady=2)
        
        self.strict_mode_var = tk.BooleanVar(value=True)  # Default strict mode
        ttk.Checkbutton(monitor_frame, text="Strict mode (block everything not explicitly allowed)", 
                       variable=self.strict_mode_var).pack(anchor=tk.W, pady=2)
        
        # Watchdog settings
        watchdog_frame = ttk.LabelFrame(main_frame, text="Watchdog Settings", padding="15")
        watchdog_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(watchdog_frame, text="Check interval (seconds):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.check_interval = ttk.Entry(watchdog_frame, width=10)
        self.check_interval.grid(row=0, column=1, sticky=tk.W)
        self.check_interval.insert(0, str(self.agent.config.get("check_interval", 5)))
        
        ttk.Label(watchdog_frame, text="Max restart attempts:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.max_restarts = ttk.Entry(watchdog_frame, width=10)
        self.max_restarts.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        self.max_restarts.insert(0, str(self.agent.config.get("max_restart_attempts", 10)))
        
        # Save button
        ttk.Button(main_frame, text="Save Settings", 
                  command=self.save_settings).pack(pady=20)
        
    def start_session(self):
        """Start a new focus session"""
        if self.agent.session_active:
            messagebox.showwarning("Session Active", "A focus session is already running!")
            return
            
        task = self.task_entry.get().strip()
        if not task:
            messagebox.showerror("Error", "Please enter a task description!")
            return
            
        try:
            duration_hours = float(self.duration_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please select a valid duration!")
            return
            
        # Save current mission before starting
        self.save_mission_config()
        
        # Start the session
        result = self.agent.start_session(duration_hours, task)
        if result:
            success, password, parts = result
            if success:
                self.session_password = password
                self.password_parts = parts
                self.show_password_parts()
                self.update_session_info()
                messagebox.showinfo("Session Started", 
                                   f"Focus session started for {duration_hours} hours!\n"
                                   f"Proxy running on port {self.agent.proxy_port}")
        else:
            messagebox.showerror("Error", "Failed to start focus session!")
            
    def show_password_parts(self):
        """Show password parts dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("🔑 Emergency Unlock Password")
        dialog.geometry("600x400")
        dialog.resizable(False, False)
        dialog.attributes('-topmost', True)
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="⚠️ EMERGENCY UNLOCK PASSWORD", 
                 font=("Arial", 16, "bold")).pack(pady=(0, 10))
        ttk.Label(main_frame, text="Send each part to a trusted friend:", 
                 font=("Arial", 12)).pack(pady=(0, 20))
        
        for i, part in enumerate(self.password_parts, 1):
            part_frame = ttk.Frame(main_frame)
            part_frame.pack(fill=tk.X, pady=5)
            ttk.Label(part_frame, text=f"Part {i}:", 
                     font=("Arial", 11, "bold")).pack(side=tk.LEFT)
            part_entry = ttk.Entry(part_frame, font=("Courier", 12), width=20)
            part_entry.pack(side=tk.LEFT, padx=(10, 0))
            part_entry.insert(0, part)
            part_entry.config(state="readonly")
            
        ttk.Label(main_frame, text="\nTo unlock early, you'll need ALL 3 parts combined.", 
                 font=("Arial", 11, "bold"), foreground="red").pack(pady=(20, 0))
        ttk.Button(main_frame, text="I Understand", 
                  command=dialog.destroy).pack(pady=(20, 0))
        
    def show_unlock_dialog(self):
        """Show unlock password dialog using 3-fragment system"""
        if not self.agent.session_active:
            messagebox.showinfo("No Active Session", "No focus session is currently active.")
            return
            
        # Use our new password unlock system
        unlock_successful = show_unlock_dialog(self.root)
        if unlock_successful:
            # End the session
            if hasattr(self.agent, 'end_session'):
                self.agent.end_session()
            messagebox.showinfo("Success", "Focus session ended successfully!")
            self.update_session_info()
        
    def load_mission_config(self):
        """Load mission configuration into GUI"""
        mission = self.agent.load_mission()
        
        self.mission_title.delete(0, tk.END)
        self.mission_title.insert(0, mission.get("title", ""))
        
        self.mission_desc.delete(1.0, tk.END)
        self.mission_desc.insert(tk.END, mission.get("description", ""))
        
        self.allowed_domains.delete(1.0, tk.END)
        domains = mission.get("allowed_domains", [])
        self.allowed_domains.insert(tk.END, "\n".join(domains))
        
        self.allowed_keywords.delete(1.0, tk.END)
        keywords = mission.get("allowed_keywords", [])
        self.allowed_keywords.insert(tk.END, "\n".join(keywords))
        
    def save_mission_config(self):
        """Save mission configuration from GUI"""
        description = self.mission_desc.get(1.0, tk.END).strip()
        
        # 50-character minimum validation for AI system effectiveness
        if len(description) < 50:
            messagebox.showerror("Error", "Mission description must be at least 50 characters long for the AI system to work effectively.")
            return
            
        mission = {
            "title": self.mission_title.get(),
            "description": description,
            "allowed_domains": [d.strip() for d in self.allowed_domains.get(1.0, tk.END).split('\n') if d.strip()],
            "allowed_keywords": [k.strip() for k in self.allowed_keywords.get(1.0, tk.END).split('\n') if k.strip()]
        }
        
        try:
            with open(self.agent.mission_file, 'w') as f:
                json.dump(mission, f, indent=2)
            messagebox.showinfo("Success", "Mission configuration saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save mission: {e}")
            
    def reset_mission_config(self):
        """Reset mission to default configuration"""
        if messagebox.askyesno("Reset Mission", "Reset mission to default configuration?"):
            self.agent.mission_file.unlink(missing_ok=True)
            self.load_mission_config()
            
    def save_settings(self):
        """Save settings configuration"""
        try:
            self.agent.config["proxy_port"] = int(self.proxy_port.get())
            self.agent.config["log_all_requests"] = self.log_all_var.get()
            self.agent.config["check_interval"] = int(self.check_interval.get())
            self.agent.config["max_restart_attempts"] = int(self.max_restarts.get())
            
            self.agent.save_config()
            messagebox.showinfo("Success", "Settings saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            
    def refresh_logs(self):
        """Refresh the log display"""
        log_type = self.log_type_var.get()
        
        try:
            if log_type == "blocked":
                log_file = self.agent.app_dir / "blocked_requests.log"
            elif log_type == "allowed":
                log_file = self.agent.app_dir / "allowed_requests.log"
            else:  # agent
                log_file = self.agent.app_dir / "activity.log"
                
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Show last 1000 lines
                    lines = content.split('\n')
                    if len(lines) > 1000:
                        content = '\n'.join(lines[-1000:])
            else:
                content = f"No {log_type} log file found."
                
        except Exception as e:
            content = f"Error reading log file: {e}"
            
        self.log_display.config(state=tk.NORMAL)
        self.log_display.delete(1.0, tk.END)
        self.log_display.insert(tk.END, content)
        self.log_display.config(state=tk.DISABLED)
        self.log_display.see(tk.END)
        
    def check_existing_session(self):
        """Check for existing session on startup"""
        if self.agent.check_existing_session():
            self.update_session_info()
            messagebox.showinfo("Session Resumed", "Existing focus session has been resumed!")
            
    def update_session_info(self):
        """Update session information display"""
        if self.agent.session_active and self.agent.session_file.exists():
            try:
                with open(self.agent.session_file, 'r') as f:
                    session_data = json.load(f)
                    
                info_text = f"Active Focus Session\n"
                info_text += f"Task: {session_data['task']}\n"
                info_text += f"Started: {session_data['start_time'][:19]}\n"
                info_text += f"Duration: {session_data['duration_hours']} hours\n"
                info_text += f"Proxy Port: {session_data.get('proxy_port', 'Unknown')}\n"
                info_text += f"Status: BLOCKING DISTRACTING WEBSITES\n\n"
                info_text += "The proxy is filtering all web traffic based on your mission.\n"
                info_text += "Only websites relevant to your current goals are allowed.\n\n"
                info_text += "To configure allowed sites, use the Mission Config tab."
                
            except Exception as e:
                info_text = f"Error reading session data: {e}"
        else:
            info_text = "No active session.\n\n"
            info_text += "Ready to start a new focus session.\n\n"
            info_text += "The proxy-based blocker will:\n"
            info_text += "• Filter all web traffic through an HTTPS proxy\n"
            info_text += "• Block distracting websites and social media\n"
            info_text += "• Allow only mission-relevant sites\n"
            info_text += "• Log all browsing activity\n"
            info_text += "• Resist tampering and process termination"
            
        self.session_info.config(state=tk.NORMAL)
        self.session_info.delete(1.0, tk.END)
        self.session_info.insert(tk.END, info_text)
        self.session_info.config(state=tk.DISABLED)
        
    def update_gui(self):
        """Periodic GUI updates"""
        if not self.running:
            return
            
        try:
            # Update countdown
            if self.agent.session_active and self.agent.session_end_time:
                remaining = self.agent.session_end_time - datetime.now()
                if remaining.total_seconds() > 0:
                    hours, remainder = divmod(remaining.total_seconds(), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    countdown_text = f"⏰ {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
                    self.countdown_label.config(text=countdown_text, foreground="red")
                    self.status_label.config(text="Focus session ACTIVE - Stay focused!", foreground="red")
                else:
                    self.countdown_label.config(text="Session Complete!", foreground="green")
                    self.status_label.config(text="Focus session completed successfully!", foreground="green")
            else:
                self.countdown_label.config(text="")
                self.status_label.config(text="Ready to start a focus session", foreground="green")
                
            # Update proxy status
            if self.agent.is_proxy_running():
                self.proxy_status_label.config(text=f"Proxy: Running on port {self.agent.proxy_port}", 
                                              foreground="green")
            else:
                self.proxy_status_label.config(text="Proxy: Not running", foreground="gray")
                
            # Update button states
            if self.agent.session_active:
                self.start_button.config(state="disabled")
                self.task_entry.config(state="disabled")
            else:
                self.start_button.config(state="normal")
                self.task_entry.config(state="normal")
                
        except Exception as e:
            pass  # Ignore update errors
            
        # Schedule next update
        self.root.after(1000, self.update_gui)
        
    def on_closing(self):
        """Handle window closing"""
        if self.agent.session_active:
            # Show unlock dialog for emergency session termination
            response = messagebox.askyesnocancel(
                "Session Active", 
                "A focus session is currently active!\n\n"
                "Do you want to:\n"
                "• Yes: Emergency unlock (requires 3 password fragments)\n"
                "• No: Continue the session\n"
                "• Cancel: Return to the application"
            )
            
            if response is True:  # Yes - Emergency unlock
                unlock_successful = show_unlock_dialog(self.root)
                if unlock_successful:
                    # Stop the session and close
                    if hasattr(self.agent, 'end_session'):
                        self.agent.end_session()
                    self.running = False
                    self.root.destroy()
                # If unlock failed, do nothing (stay in session)
            elif response is False:  # No - Continue session
                # Just ignore the close request
                pass
            # Cancel or window close - do nothing
        else:
            self.running = False
            self.root.destroy()
            
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()


def main():
    """Main entry point per aim.txt specification"""
    try:
        # Check if initial setup is required
        if not is_setup_complete():
            print("Initial setup required...")
            setup_completed = run_initial_setup()
            if not setup_completed:
                print("Setup was cancelled or incomplete. Exiting.")
                return
                
        # Setup completed, start mission setup per aim.txt lines 23-51
        import set_mission
        set_mission.main()
        print("🎯 Mission setup completed per aim.txt specification.")
            
    except Exception as e:
        print(f"Error starting Focus Blocker Pro: {e}")
        messagebox.showerror("Error", f"Failed to start Focus Blocker Pro: {e}")


if __name__ == "__main__":
    main()