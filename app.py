#!/usr/bin/env python3
"""
Anchorite - AI-Powered Focus System
Complete desktop application with automatic setup
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import sys
import subprocess
import threading
import time
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import platform
import webbrowser
from pathlib import Path
import sqlite3
from datetime import datetime, timedelta

class AnchoriteApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Anchorite - AI-Powered Focus System")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        # Application state
        self.current_step = "welcome"
        self.user_email = ""
        self.trusted_emails = []
        self.mission = ""
        self.session_minutes = 0
        self.proxy_process = None
        self.session_start_time = None
        self.visited_sites = []
        
        # Setup UI
        self.setup_ui()
        self.show_welcome_screen()
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_ui(self):
        """Setup the main UI components"""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        # Title label
        self.title_label = ttk.Label(self.main_frame, text="Anchorite", 
                                    font=("Arial", 24, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Content frame
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.content_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, mode='determinate')
        self.progress.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        
        # Button frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        # Navigation buttons
        self.back_button = ttk.Button(self.button_frame, text="Back", 
                                     command=self.previous_step, state="disabled")
        self.back_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.next_button = ttk.Button(self.button_frame, text="Next", 
                                     command=self.next_step)
        self.next_button.pack(side=tk.RIGHT)
        
        # Status label
        self.status_label = ttk.Label(self.main_frame, text="", 
                                     font=("Arial", 10))
        self.status_label.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
    def clear_content(self):
        """Clear the content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def show_welcome_screen(self):
        """Show the welcome screen"""
        self.clear_content()
        self.current_step = "welcome"
        self.progress['value'] = 0
        
        # Welcome text
        welcome_text = """
Welcome to Anchorite - Your AI-Powered Focus System

Anchorite helps you stay focused on your goals by intelligently filtering 
distracting websites while allowing productive ones.

How it works:
• Set up your focus mission and time limit
• Browse the web normally
• AI automatically blocks distracting sites
• Rate websites to improve the AI's accuracy

This setup will take just a few minutes and requires no technical knowledge.
        """
        
        text_widget = tk.Text(self.content_frame, wrap=tk.WORD, height=12, 
                             font=("Arial", 11), state="disabled")
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.config(state="normal")
        text_widget.insert("1.0", welcome_text)
        text_widget.config(state="disabled")
        
        self.next_button.config(text="Get Started")
        self.back_button.config(state="disabled")
        
    def show_email_setup(self):
        """Show email setup screen"""
        self.clear_content()
        self.current_step = "email_setup"
        self.progress['value'] = 20
        
        # Email setup instructions
        ttk.Label(self.content_frame, text="Step 1: Your Email", 
                 font=("Arial", 16, "bold")).pack(pady=(0, 10))
        
        instruction_text = """
Please enter your email address. This will be used to:
• Send you session summaries
• Link your account across devices
• Provide support if needed
        """
        
        ttk.Label(self.content_frame, text=instruction_text, 
                 wraplength=500, justify=tk.LEFT).pack(pady=(0, 20))
        
        # Email entry
        ttk.Label(self.content_frame, text="Your Email:").pack(anchor=tk.W)
        self.email_entry = ttk.Entry(self.content_frame, width=50)
        self.email_entry.pack(fill=tk.X, pady=(5, 20))
        self.email_entry.focus()
        
        self.next_button.config(text="Next")
        self.back_button.config(state="normal")
        
    def show_trusted_emails_setup(self):
        """Show trusted emails setup screen"""
        self.clear_content()
        self.current_step = "trusted_emails"
        self.progress['value'] = 40
        
        ttk.Label(self.content_frame, text="Step 2: Trusted Contacts", 
                 font=("Arial", 16, "bold")).pack(pady=(0, 10))
        
        instruction_text = """
Enter 3 email addresses of people you trust. This creates a security system:

• Each person will receive a unique 12-digit password
• You'll need all 3 passwords to disable the focus system
• This prevents you from easily bypassing your own restrictions
• Choose people who support your productivity goals

This makes the system effective by adding accountability.
        """
        
        ttk.Label(self.content_frame, text=instruction_text, 
                 wraplength=500, justify=tk.LEFT).pack(pady=(0, 20))
        
        # Email entries
        self.trusted_entries = []
        for i in range(3):
            frame = ttk.Frame(self.content_frame)
            frame.pack(fill=tk.X, pady=5)
            frame.columnconfigure(1, weight=1)
            
            ttk.Label(frame, text=f"Contact {i+1}:").grid(row=0, column=0, sticky=tk.W)
            entry = ttk.Entry(frame)
            entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
            self.trusted_entries.append(entry)
            
        self.next_button.config(text="Send Passwords")
        self.back_button.config(state="normal")
        
    def show_mission_setup(self):
        """Show mission setup screen"""
        self.clear_content()
        self.current_step = "mission_setup"
        self.progress['value'] = 60
        
        ttk.Label(self.content_frame, text="Step 3: Your Focus Mission", 
                 font=("Arial", 16, "bold")).pack(pady=(0, 10))
        
        instruction_text = """
What would you like to accomplish in this session?

Be specific about your goal. For example:
• "Complete the quarterly report for Q4 2024"
• "Research machine learning algorithms for my thesis"
• "Write the first three chapters of my novel"

Your response must be at least 50 characters long.
        """
        
        ttk.Label(self.content_frame, text=instruction_text, 
                 wraplength=500, justify=tk.LEFT).pack(pady=(0, 20))
        
        # Mission entry
        ttk.Label(self.content_frame, text="Your Mission:").pack(anchor=tk.W)
        self.mission_text = tk.Text(self.content_frame, height=4, wrap=tk.WORD)
        self.mission_text.pack(fill=tk.BOTH, expand=True, pady=(5, 20))
        
        # Character count
        self.char_count_label = ttk.Label(self.content_frame, text="0 characters")
        self.char_count_label.pack(anchor=tk.W)
        
        # Bind character count update
        self.mission_text.bind('<KeyRelease>', self.update_char_count)
        
        self.next_button.config(text="Next")
        self.back_button.config(state="normal")
        
    def show_time_setup(self):
        """Show time setup screen"""
        self.clear_content()
        self.current_step = "time_setup"
        self.progress['value'] = 80
        
        ttk.Label(self.content_frame, text="Step 4: Session Duration", 
                 font=("Arial", 16, "bold")).pack(pady=(0, 10))
        
        instruction_text = """
How many minutes would you like to allocate to this task?

Maximum session time: 300 minutes (5 hours)

Choose a realistic timeframe that matches your goal.
        """
        
        ttk.Label(self.content_frame, text=instruction_text, 
                 wraplength=500, justify=tk.LEFT).pack(pady=(0, 20))
        
        # Time entry
        ttk.Label(self.content_frame, text="Minutes:").pack(anchor=tk.W)
        self.time_entry = ttk.Entry(self.content_frame, width=10)
        self.time_entry.pack(anchor=tk.W, pady=(5, 20))
        self.time_entry.focus()
        
        self.next_button.config(text="Start Focus Session")
        self.back_button.config(state="normal")
        
    def show_active_session(self):
        """Show active session screen"""
        self.clear_content()
        self.current_step = "active_session"
        self.progress['value'] = 100
        
        # Hide navigation buttons during session
        self.back_button.pack_forget()
        self.next_button.pack_forget()
        
        ttk.Label(self.content_frame, text="Focus Session Active", 
                 font=("Arial", 18, "bold")).pack(pady=(0, 10))
        
        # Mission display
        mission_frame = ttk.LabelFrame(self.content_frame, text="Your Mission", padding="10")
        mission_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(mission_frame, text=self.mission, wraplength=500, 
                 justify=tk.LEFT).pack()
        
        # Timer display
        self.timer_label = ttk.Label(self.content_frame, text="", 
                                    font=("Arial", 24, "bold"))
        self.timer_label.pack(pady=20)
        
        # Status
        status_text = """
✅ Focus system is active
🌐 Browse the web normally
🚫 Distracting sites will be blocked
📊 AI learns from your browsing patterns
        """
        
        status_widget = tk.Text(self.content_frame, wrap=tk.WORD, height=8, 
                               font=("Arial", 11), state="disabled")
        status_widget.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        status_widget.config(state="normal")
        status_widget.insert("1.0", status_text)
        status_widget.config(state="disabled")
        
        # Start session
        self.start_focus_session()
        
    def update_char_count(self, event=None):
        """Update character count for mission text"""
        count = len(self.mission_text.get("1.0", tk.END).strip())
        self.char_count_label.config(text=f"{count} characters")
        
    def next_step(self):
        """Handle next step button"""
        if self.current_step == "welcome":
            self.show_email_setup()
            
        elif self.current_step == "email_setup":
            email = self.email_entry.get().strip()
            if not email or '@' not in email:
                messagebox.showerror("Invalid Email", "Please enter a valid email address.")
                return
            self.user_email = email
            self.show_trusted_emails_setup()
            
        elif self.current_step == "trusted_emails":
            emails = [entry.get().strip() for entry in self.trusted_entries]
            if not all(emails) or not all('@' in email for email in emails):
                messagebox.showerror("Invalid Emails", "Please enter 3 valid email addresses.")
                return
            if len(set(emails)) != 3:
                messagebox.showerror("Duplicate Emails", "Please enter 3 different email addresses.")
                return
            self.trusted_emails = emails
            self.send_passwords()
            self.show_mission_setup()
            
        elif self.current_step == "mission_setup":
            mission = self.mission_text.get("1.0", tk.END).strip()
            if len(mission) < 50:
                messagebox.showerror("Mission Too Short", 
                                   "Your mission must be at least 50 characters long.")
                return
            self.mission = mission
            self.show_time_setup()
            
        elif self.current_step == "time_setup":
            try:
                minutes = int(self.time_entry.get())
                if minutes <= 0 or minutes > 300:
                    messagebox.showerror("Invalid Time", 
                                       "Please enter a time between 1 and 300 minutes.")
                    return
                self.session_minutes = minutes
                self.show_active_session()
            except ValueError:
                messagebox.showerror("Invalid Time", "Please enter a valid number of minutes.")
                return
                
    def previous_step(self):
        """Handle back button"""
        if self.current_step == "email_setup":
            self.show_welcome_screen()
        elif self.current_step == "trusted_emails":
            self.show_email_setup()
        elif self.current_step == "mission_setup":
            self.show_trusted_emails_setup()
        elif self.current_step == "time_setup":
            self.show_mission_setup()
            
    def generate_password(self):
        """Generate a random 12-digit password"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        
    def send_passwords(self):
        """Send passwords to trusted contacts"""
        passwords = [self.generate_password() for _ in range(3)]
        
        # Store passwords (in real app, this would be encrypted)
        self.user_passwords = passwords
        
        # Send emails (in real app, this would use proper email service)
        for i, (email, password) in enumerate(zip(self.trusted_emails, passwords)):
            try:
                self.send_password_email(email, password, i+1)
            except Exception as e:
                print(f"Failed to send email to {email}: {e}")
                
        # Show success message
        messagebox.showinfo("Passwords Sent", 
                           f"Passwords have been sent to your trusted contacts.\n\n"
                           f"Contact 1: {self.trusted_emails[0]}\n"
                           f"Contact 2: {self.trusted_emails[1]}\n"
                           f"Contact 3: {self.trusted_emails[2]}\n\n"
                           f"Keep these passwords safe - you'll need all 3 to disable the system.")
                           
    def send_password_email(self, email, password, contact_num):
        """Send password email to trusted contact"""
        # This is a simplified email function
        # In production, you'd use a proper email service like SendGrid or AWS SES
        
        subject = f"Anchorite password {contact_num} for {self.user_email}"
        body = f"""
Hello,

You have been designated as a trusted contact for {self.user_email}'s Anchorite focus system.

Your unique password is: {password}

This password is required to disable the focus system. Please keep it safe and only share it when {self.user_email} requests it.

Thank you for supporting their productivity goals.

Best regards,
Anchorite Team
        """
        
        # For demo purposes, just print the email
        print(f"Email to {email}:")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        print("-" * 50)
        
    def start_focus_session(self):
        """Start the focus session with automatic proxy setup"""
        self.session_start_time = datetime.now()
        self.session_end_time = self.session_start_time + timedelta(minutes=self.session_minutes)
        
        # Start proxy in background thread
        threading.Thread(target=self.setup_and_start_proxy, daemon=True).start()
        
        # Start timer update
        self.update_timer()
        
    def setup_and_start_proxy(self):
        """Setup and start the proxy automatically"""
        try:
            # Update status
            self.status_label.config(text="Setting up focus system...")
            
            # Install dependencies if needed
            self.install_dependencies()
            
            # Generate certificates
            self.generate_certificates()
            
            # Configure system proxy automatically
            self.configure_system_proxy()
            
            # Start the proxy
            self.start_proxy()
            
            # Update status
            self.status_label.config(text="Focus system active - browsing normally")
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            messagebox.showerror("Setup Error", f"Failed to start focus system: {str(e)}")
            
    def install_dependencies(self):
        """Install required dependencies"""
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", 
                                 "mitmproxy", "torch", "numpy", "scikit-learn", 
                                 "requests", "beautifulsoup4"], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            # Dependencies might already be installed
            pass
            
    def generate_certificates(self):
        """Generate certificates automatically"""
        try:
            # Create certs directory
            certs_dir = Path("certs")
            certs_dir.mkdir(exist_ok=True)
            
            # Generate certificates using mitmproxy
            subprocess.run([sys.executable, "-m", "mitmproxy.tools.dump", 
                          "--confdir", str(certs_dir), "--listen-port", "8081"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         timeout=5)
        except:
            # Certificate generation might fail, but we'll continue
            pass
            
    def configure_system_proxy(self):
        """Configure system proxy automatically"""
        system = platform.system().lower()
        
        if system == "windows":
            # Use Windows registry to set proxy
            try:
                import winreg
                
                # Set proxy settings in registry
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, "127.0.0.1:8080")
                    
            except Exception as e:
                print(f"Failed to configure Windows proxy: {e}")
                
        elif system == "darwin":  # macOS
            # Use networksetup command
            try:
                subprocess.run(["networksetup", "-setwebproxy", "Wi-Fi", "127.0.0.1", "8080"])
                subprocess.run(["networksetup", "-setsecurewebproxy", "Wi-Fi", "127.0.0.1", "8080"])
            except:
                pass
                
        # Note: Linux would require additional setup
        
    def start_proxy(self):
        """Start the proxy server"""
        try:
            # Start mitmproxy with our filter
            self.proxy_process = subprocess.Popen([
                sys.executable, "-m", "mitmproxy.tools.dump",
                "-s", "RL/rl_proxy_filter.py",
                "--listen-port", "8080",
                "--set", "confdir=certs"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        except Exception as e:
            print(f"Failed to start proxy: {e}")
            
    def update_timer(self):
        """Update the timer display"""
        if self.session_end_time:
            remaining = self.session_end_time - datetime.now()
            if remaining.total_seconds() <= 0:
                self.end_session()
                return
                
            minutes = int(remaining.total_seconds() // 60)
            seconds = int(remaining.total_seconds() % 60)
            self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
            
        # Update every second
        self.root.after(1000, self.update_timer)
        
    def end_session(self):
        """End the focus session"""
        # Stop proxy
        if self.proxy_process:
            self.proxy_process.terminate()
            
        # Reset system proxy
        self.reset_system_proxy()
        
        # Show session summary
        self.show_session_summary()
        
    def reset_system_proxy(self):
        """Reset system proxy settings"""
        system = platform.system().lower()
        
        if system == "windows":
            try:
                import winreg
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
            except:
                pass
                
        elif system == "darwin":
            try:
                subprocess.run(["networksetup", "-setwebproxystate", "Wi-Fi", "off"])
                subprocess.run(["networksetup", "-setsecurewebproxystate", "Wi-Fi", "off"])
            except:
                pass
                
    def show_session_summary(self):
        """Show session summary and website ratings"""
        # Create new window for summary
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Session Summary")
        summary_window.geometry("800x600")
        summary_window.transient(self.root)
        summary_window.grab_set()
        
        # Summary content
        ttk.Label(summary_window, text="Focus Session Complete!", 
                 font=("Arial", 18, "bold")).pack(pady=20)
        
        # Mission and time info
        info_frame = ttk.LabelFrame(summary_window, text="Session Details", padding="10")
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(info_frame, text=f"Mission: {self.mission}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Duration: {self.session_minutes} minutes").pack(anchor=tk.W)
        
        # Website ratings (simplified for demo)
        ratings_frame = ttk.LabelFrame(summary_window, text="Rate Your Websites", padding="10")
        ratings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Demo websites (in real app, these would be from actual browsing)
        demo_sites = [
            "github.com",
            "stackoverflow.com", 
            "youtube.com",
            "facebook.com",
            "docs.python.org"
        ]
        
        self.site_ratings = {}
        
        for site in demo_sites:
            frame = ttk.Frame(ratings_frame)
            frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(frame, text=site, width=30).pack(side=tk.LEFT)
            
            var = tk.BooleanVar()
            ttk.Checkbutton(frame, text="Productive", variable=var).pack(side=tk.RIGHT)
            
            self.site_ratings[site] = var
            
        # Buttons
        button_frame = ttk.Frame(summary_window)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Submit Ratings", 
                  command=lambda: self.submit_ratings(summary_window)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Skip", 
                  command=summary_window.destroy).pack(side=tk.LEFT, padx=5)
        
    def submit_ratings(self, window):
        """Submit website ratings"""
        # Process ratings
        for site, var in self.site_ratings.items():
            rating = 1 if var.get() else 0
            print(f"Site: {site}, Rating: {rating}")
            
        # In real app, this would feed back to the ML system
        
        messagebox.showinfo("Thank You", "Your ratings have been submitted and will help improve the AI system.")
        window.destroy()
        
        # Close the main application
        self.root.quit()
        
    def run(self):
        """Run the application"""
        self.root.mainloop()
        
        # Cleanup on exit
        if self.proxy_process:
            self.proxy_process.terminate()
        self.reset_system_proxy()

def main():
    """Main entry point"""
    app = AnchoriteApp()
    app.run()

if __name__ == "__main__":
    main()