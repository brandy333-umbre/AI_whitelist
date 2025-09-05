#!/usr/bin/env python3
"""
Password Unlock System - Emergency unlock for Focus Blocker Pro
Allows users to disable the blocker by entering 3 password fragments
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import hashlib
from datetime import datetime

class PasswordUnlock:
    def __init__(self, parent=None):
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        self.root.title("Focus Blocker Pro - Emergency Unlock")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        # Make it modal if parent exists
        if parent:
            self.root.transient(parent)
            self.root.grab_set()
        
        # Configuration
        self.config_file = "user_config.json"
        self.password_fragments = ["", "", ""]
        self.master_password_hash = None
        self.user_config = None
        
        # Load user configuration
        self.load_user_config()
        
        # Setup GUI
        self.setup_gui()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Result
        self.unlock_successful = False
        
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def load_user_config(self):
        """Load user configuration"""
        try:
            with open(self.config_file, 'r') as f:
                self.user_config = json.load(f)
            self.master_password_hash = self.user_config.get('master_password_hash')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load user configuration:\n\n{str(e)}")
            self.root.destroy()
            
    def setup_gui(self):
        """Setup the unlock GUI"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🔓 Emergency Unlock", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Warning message
        warning_text = """⚠️ FOCUS SESSION ACTIVE ⚠️

To disable the Focus Blocker, you need to collect the 3 password fragments that were sent to your trusted contacts when you first set up the application.

Contact each person and ask them for their password fragment, then enter all 3 below."""
        
        warning_label = ttk.Label(main_frame, text=warning_text, 
                                 wraplength=350, justify=tk.CENTER,
                                 font=("Arial", 10))
        warning_label.pack(pady=(0, 20))
        
        # Trusted contacts info
        if self.user_config and 'trusted_contacts' in self.user_config:
            contacts_frame = ttk.LabelFrame(main_frame, text="Your Trusted Contacts", padding="10")
            contacts_frame.pack(fill=tk.X, pady=(0, 20))
            
            for i, contact in enumerate(self.user_config['trusted_contacts']):
                if contact:
                    contact_label = ttk.Label(contacts_frame, text=f"{i+1}. {contact}")
                    contact_label.pack(anchor=tk.W, pady=2)
        
        # Password fragment entries
        password_frame = ttk.LabelFrame(main_frame, text="Password Fragments", padding="10")
        password_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.fragment_vars = []
        self.fragment_entries = []
        
        for i in range(3):
            # Label
            fragment_label = ttk.Label(password_frame, text=f"Password Fragment #{i+1}:", 
                                     font=("Arial", 10, "bold"))
            fragment_label.pack(anchor=tk.W, pady=(10, 2))
            
            # Entry
            fragment_var = tk.StringVar()
            fragment_entry = ttk.Entry(password_frame, textvariable=fragment_var, 
                                     width=40, font=("Courier", 12))
            fragment_entry.pack(pady=(0, 5))
            
            self.fragment_vars.append(fragment_var)
            self.fragment_entries.append(fragment_entry)
            
            # Bind validation
            fragment_var.trace('w', self.validate_fragments)
        
        # Validation status
        self.validation_label = ttk.Label(main_frame, text="", font=("Arial", 10))
        self.validation_label.pack(pady=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel", command=self.on_closing)
        self.cancel_button.pack(side=tk.LEFT)
        
        self.unlock_button = ttk.Button(button_frame, text="Unlock Focus Blocker", 
                                       command=self.attempt_unlock)
        self.unlock_button.pack(side=tk.RIGHT)
        self.unlock_button.config(state="disabled")
        
        # Focus on first entry
        self.fragment_entries[0].focus()
        
    def validate_fragments(self, *args):
        """Validate password fragments as user types"""
        fragments = [var.get().strip().upper() for var in self.fragment_vars]
        
        # Check if all fragments are filled
        all_filled = all(len(fragment) >= 12 for fragment in fragments)
        
        if all_filled:
            # Check format (12 characters, alphanumeric)
            all_valid = all(len(fragment) == 12 and fragment.isalnum() for fragment in fragments)
            
            if all_valid:
                self.validation_label.config(text="✓ All fragments entered", foreground="green")
                self.unlock_button.config(state="normal")
            else:
                self.validation_label.config(text="✗ Invalid fragment format (must be 12 alphanumeric characters)", 
                                           foreground="red")
                self.unlock_button.config(state="disabled")
        else:
            fragment_count = sum(1 for fragment in fragments if len(fragment) >= 12)
            self.validation_label.config(text=f"Enter all 3 fragments ({fragment_count}/3)", 
                                       foreground="orange")
            self.unlock_button.config(state="disabled")
            
    def attempt_unlock(self):
        """Attempt to unlock using the provided fragments"""
        fragments = [var.get().strip().upper() for var in self.fragment_vars]
        
        # Combine fragments to create master password
        master_password = ''.join(fragments)
        
        # Verify against stored hash
        if hash(master_password) == self.master_password_hash:
            # Success!
            self.unlock_successful = True
            
            # Log the unlock event
            self.log_unlock_event()
            
            messagebox.showinfo("Unlock Successful", 
                "✅ Focus Blocker has been successfully disabled!\n\n"
                "Remember: Focus sessions help you achieve your goals. "
                "Consider starting a new session when you're ready to focus again.")
            
            self.root.destroy()
        else:
            # Failed
            messagebox.showerror("Unlock Failed", 
                "❌ Incorrect password fragments!\n\n"
                "Please verify you have the correct fragments from all 3 trusted contacts.\n\n"
                "Remember: The fragments are case-sensitive and must be entered exactly as received.")
            
            # Clear entries for retry
            for var in self.fragment_vars:
                var.set("")
            self.fragment_entries[0].focus()
            
    def log_unlock_event(self):
        """Log the emergency unlock event"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event": "emergency_unlock",
                "user_email": self.user_config.get('user_email', 'unknown'),
                "method": "password_fragments"
            }
            
            # Append to activity log
            with open("activity.log", "a") as f:
                f.write(f"{json.dumps(log_entry)}\n")
                
        except Exception as e:
            print(f"Failed to log unlock event: {e}")
            
    def on_closing(self):
        """Handle window closing"""
        self.unlock_successful = False
        self.root.destroy()
        
    def run(self):
        """Run the unlock dialog"""
        self.root.mainloop()
        return self.unlock_successful


def show_unlock_dialog(parent=None):
    """Show the unlock dialog and return whether unlock was successful"""
    unlock_dialog = PasswordUnlock(parent)
    return unlock_dialog.run()


if __name__ == "__main__":
    # Test the unlock dialog
    dialog = PasswordUnlock()
    success = dialog.run()
    print(f"Unlock successful: {success}") 