#!/usr/bin/env python3
"""
Initial Setup - First-time user configuration for Anchorite
Handles email entry and trusted contacts setup with password distribution
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re
import json
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
from datetime import datetime
import logging

# Anchorite Email Configuration (Secure - sent from Anchorite, not user email)
ANCHORITE_EMAIL = "anchorite.focus@gmail.com"
ANCHORITE_PASSWORD = "leyp urpy welx sbxb"
ANCHORITE_SMTP_SERVER = "smtp.gmail.com"
ANCHORITE_SMTP_PORT = 587

class InitialSetup:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Anchorite - Initial Setup")
        self.root.geometry("600x1000")
        self.root.resizable(True, True)
        self.root.minsize(600, 1000)
        
        # Center the window
        self.center_window()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.config_file = "user_config.json"
        self.user_email = ""
        self.trusted_contacts = ["", "", ""]
        self.password_fragments = []
        self.master_password = ""
        
        # Setup GUI
        self.setup_gui()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = 600
        height = 1000
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def setup_gui(self):
        """Setup the initial setup GUI"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🔒 Anchorite", 
                               font=("Arial", 20, "bold"))
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Initial Setup - Security Configuration", 
                                  font=("Arial", 12))
        subtitle_label.pack(pady=(0, 20))
        
        # Create notebook for setup steps
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 80))  # Leave space for buttons
        
        # Step 1: User Email
        self.email_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.email_frame, text="Step 1: Your Email")
        self.setup_email_tab()
        
        # Step 2: Trusted Contacts
        self.contacts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.contacts_frame, text="Step 2: Trusted Contacts")
        self.setup_contacts_tab()
        
        # Navigation buttons (fixed at bottom)
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 20))
        
        self.back_button = ttk.Button(nav_frame, text="← Back", command=self.go_back, width=10)
        self.back_button.pack(side=tk.LEFT)
        
        self.next_button = ttk.Button(nav_frame, text="Next →", command=self.go_next, width=10)
        self.next_button.pack(side=tk.RIGHT)
        
        # Update navigation state
        self.update_navigation()
        
    def setup_email_tab(self):
        """Setup the user email entry tab"""
        frame = ttk.Frame(self.email_frame, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Info text
        info_text = """Welcome to Anchorite!

To ensure maximum effectiveness, this application uses a distributed password system. You'll need to provide your email address and select 3 trusted contacts who will receive password fragments.

This prevents you from easily disabling the blocker during moments of weakness, making your focus sessions truly effective."""
        
        info_label = ttk.Label(frame, text=info_text, wraplength=400, justify=tk.LEFT)
        info_label.pack(pady=(0, 20))
        
        # Email entry
        email_label = ttk.Label(frame, text="Your Email Address:", font=("Arial", 10, "bold"))
        email_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(frame, textvariable=self.email_var, width=40, font=("Arial", 10))
        self.email_entry.pack(pady=(0, 10))
        
        # Validation label
        self.email_validation_label = ttk.Label(frame, text="", foreground="red")
        self.email_validation_label.pack()
        
        # Bind validation
        self.email_var.trace('w', self.validate_email)
        
    def setup_contacts_tab(self):
        """Setup the trusted contacts entry tab"""
        # Create canvas and scrollbar for scrollable content
        canvas = tk.Canvas(self.contacts_frame)
        scrollbar = ttk.Scrollbar(self.contacts_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Content frame with padding
        frame = ttk.Frame(scrollable_frame, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Info text
        info_text = """Enter 3 email addresses of people you trust.

Each person will receive a unique 12-digit password fragment from the Anchorite security system. To disable the Focus Blocker, you'll need to collect all 3 fragments and enter them together.

Choose people who:
• You trust completely
• Check their email regularly (including spam folder)
• Will support your productivity goals

📧 Note: Emails will be sent from anchorite.focus@gmail.com (not your email)"""
        
        info_label = ttk.Label(frame, text=info_text, wraplength=400, justify=tk.LEFT)
        info_label.pack(pady=(0, 20))
        
        # Contact entries
        self.contact_vars = []
        self.contact_entries = []
        self.contact_validation_labels = []
        
        # Create exactly 3 contact fields as specified in aim.txt
        for i in range(3):
            contact_label = ttk.Label(frame, text=f"Trusted Contact #{i+1}:", font=("Arial", 10, "bold"))
            contact_label.pack(anchor=tk.W, pady=(10, 5))
            
            contact_var = tk.StringVar()
            contact_entry = ttk.Entry(frame, textvariable=contact_var, width=40, font=("Arial", 10))
            contact_entry.pack(pady=(0, 5))
            
            validation_label = ttk.Label(frame, text="", foreground="red")
            validation_label.pack(pady=(0, 5))
            
            self.contact_vars.append(contact_var)
            self.contact_entries.append(contact_entry)
            self.contact_validation_labels.append(validation_label)
            
            # Bind validation
            contact_var.trace('w', lambda *args, idx=i: self.validate_contact(idx))
            

        
    def validate_email(self, *args):
        """Validate email address"""
        email = self.email_var.get()
        if not email:
            self.email_validation_label.config(text="")
            return False
            
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, email):
            self.email_validation_label.config(text="✓ Valid email", foreground="green")
            self.user_email = email
            return True
        else:
            self.email_validation_label.config(text="✗ Invalid email format", foreground="red")
            return False
            
    def validate_contact(self, index):
        """Validate contact email address"""
        contact_email = self.contact_vars[index].get()
        validation_label = self.contact_validation_labels[index]
        
        if not contact_email:
            validation_label.config(text="")
            return False
            
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, contact_email):
            # Check for duplicates
            for i, var in enumerate(self.contact_vars):
                if i != index and var.get() == contact_email:
                    validation_label.config(text="✗ Duplicate email", foreground="red")
                    return False
                    
            # Check if same as user email
            if contact_email == self.user_email:
                validation_label.config(text="✗ Cannot be your own email", foreground="red")
                return False
                
            validation_label.config(text="✓ Valid email", foreground="green")
            self.trusted_contacts[index] = contact_email
            return True
        else:
            validation_label.config(text="✗ Invalid email format", foreground="red")
            return False
            
    def validate_all_contacts(self):
        """Validate all contact emails"""
        valid_count = 0
        for i in range(3):
            if self.validate_contact(i):
                valid_count += 1
        return valid_count == 3
        

            
    def go_back(self):
        """Go to previous tab"""
        current = self.notebook.index(self.notebook.select())
        if current > 0:
            self.notebook.select(current - 1)
        self.update_navigation()
        
    def go_next(self):
        """Go to next tab or complete setup if on final tab"""
        current = self.notebook.index(self.notebook.select())
        total_tabs = self.notebook.index("end")
        
        # Validate current tab before proceeding
        if current == 0:  # Email tab
            if not self.validate_email():
                messagebox.showerror("Error", "Please enter a valid email address")
                return
        elif current == 1:  # Contacts tab (final tab)
            if not self.validate_all_contacts():
                messagebox.showerror("Error", "Please enter 3 valid, unique email addresses")
                return
            # If on final tab and validation passes, complete setup
            if current == total_tabs - 1:
                self.finish_setup()
                return
                
        # Move to next tab if not on final tab
        if current < total_tabs - 1:
            self.notebook.select(current + 1)
        self.update_navigation()
        
    def update_navigation(self):
        """Update navigation button states"""
        current = self.notebook.index(self.notebook.select())
        total_tabs = self.notebook.index("end")
        
        # Back button
        if current == 0:
            self.back_button.config(state="disabled")
        else:
            self.back_button.config(state="normal")
            
        # Next button is always visible and handles both navigation and setup completion
        self.next_button.config(state="normal")
        
        # Update Next button text based on current tab
        if current == total_tabs - 1:  # Last tab (contacts)
            self.next_button.config(text="Next →")
        else:
            self.next_button.config(text="Next →")
            
    def generate_password_fragments(self):
        """Generate 12-digit password fragments for each contact"""
        self.password_fragments = []
        for i in range(3):
            fragment = ''.join(random.choices(string.digits + string.ascii_uppercase, k=12))
            self.password_fragments.append(fragment)
            
        # Create master password from all fragments
        self.master_password = ''.join(self.password_fragments)
        
    def send_password_emails(self):
        """Send password fragments to trusted contacts using Anchorite email"""
        try:
            self.logger.info(f"Connecting to Anchorite SMTP server: {ANCHORITE_SMTP_SERVER}:{ANCHORITE_SMTP_PORT}")
            
            # Create SMTP connection using Anchorite credentials
            server = smtplib.SMTP(ANCHORITE_SMTP_SERVER, ANCHORITE_SMTP_PORT)
            server.set_debuglevel(1)  # Enable debug output
            
            # Start TLS encryption
            server.starttls()
            self.logger.info("TLS connection established")
            
            # Authenticate with Anchorite credentials
            server.login(ANCHORITE_EMAIL, ANCHORITE_PASSWORD)
            self.logger.info("Anchorite authentication successful")
            
            # Send emails to each contact
            emails_sent = 0
            for i, contact_email in enumerate(self.trusted_contacts):
                if contact_email:  # Skip empty emails
                    try:
                        msg = MIMEMultipart()
                        msg['From'] = ANCHORITE_EMAIL  # Email comes from Anchorite (security!)
                        msg['To'] = contact_email
                        msg['Subject'] = f"Anchorite password {i+1} for {self.user_email}"
                        
                        body = f"""Hello,

{self.user_email} has set up Anchorite and designated you as a trusted contact.

Your password fragment #{i+1} is: {self.password_fragments[i]}

This is part of a 3-part security system. If {self.user_email} needs to disable their focus blocker, they will need to collect all 3 password fragments from their trusted contacts.

Please keep this password safe and only share it with {self.user_email} when they specifically request it for legitimate reasons.

Thank you for supporting their productivity goals!

- Anchorite Security System
anchorite.focus@gmail.com"""
                        
                        msg.attach(MIMEText(body, 'plain'))
                        
                        # Send the email
                        server.send_message(msg)
                        emails_sent += 1
                        self.logger.info(f"Email {i+1} sent successfully to {contact_email}")
                        
                    except Exception as e:
                        self.logger.error(f"Failed to send email {i+1} to {contact_email}: {e}")
                        raise e
            
            server.quit()
            self.logger.info(f"All {emails_sent} emails sent successfully from Anchorite")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Anchorite email authentication failed!\n\n"
            error_msg += "This is an internal system error. Please contact support.\n\n"
            error_msg += f"Technical error: {str(e)}"
            messagebox.showerror("System Error", error_msg)
            return False
            
        except smtplib.SMTPConnectError as e:
            messagebox.showerror("Connection Error", f"Could not connect to Anchorite email server.\n\nPlease check your internet connection and try again.\n\nTechnical error: {str(e)}")
            return False
            
        except smtplib.SMTPServerDisconnected as e:
            messagebox.showerror("Connection Error", f"Server disconnected unexpectedly.\n\nTry again in a moment.\n\nTechnical error: {str(e)}")
            return False
            
        except Exception as e:
            messagebox.showerror("Email Error", f"Failed to send emails from Anchorite system:\n\n{str(e)}\n\nPlease try again or contact support.")
            return False
            
    def save_user_config(self):
        """Save user configuration to file"""
        config = {
            "user_email": self.user_email,
            "trusted_contacts": self.trusted_contacts,
            "master_password_hash": hash(self.master_password),  # Store hash for verification
            "setup_completed": True,
            "setup_date": datetime.now().isoformat(),
            "anchorite_email_used": True  # Indicates emails sent from Anchorite system
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save configuration:\n\n{str(e)}")
            return False
            
    def finish_setup(self):
        """Complete the setup process"""
        # Final validation
        if not self.validate_email():
            messagebox.showerror("Error", "Invalid email address")
            return
            
        if not self.validate_all_contacts():
            messagebox.showerror("Error", "Invalid trusted contact emails")
            return
            
        # Show confirmation dialog
        contact_list = "\n".join([f"{i+1}. {email}" for i, email in enumerate(self.trusted_contacts) if email])
        
        confirm_msg = f"""Setup Summary:

Your Email: {self.user_email}

Trusted Contacts:
{contact_list}

This will:
1. Generate unique 12-digit password fragments
2. Send each fragment via Anchorite email system
3. Complete your Focus Blocker Pro setup

⚠️ IMPORTANT: Emails will be sent from anchorite.focus@gmail.com
This prevents you from accessing the fragments through your sent folder.

Continue with setup?"""
        
        if not messagebox.askyesno("Confirm Setup", confirm_msg):
            return
            
        # Generate passwords
        self.generate_password_fragments()
        
        # Show progress
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Sending Emails via Anchorite...")
        progress_window.geometry("350x100")
        progress_window.resizable(False, False)
        
        # Center progress window
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        progress_label = ttk.Label(progress_window, text="Sending password emails via Anchorite security system...")
        progress_label.pack(pady=20)
        
        progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
        progress_bar.pack(pady=10, padx=20, fill=tk.X)
        progress_bar.start()
        
        # Send emails in separate thread
        def send_emails_thread():
            success = self.send_password_emails()
            
            # Update UI in main thread
            self.root.after(0, lambda: self.finish_setup_complete(progress_window, success))
            
        threading.Thread(target=send_emails_thread, daemon=True).start()
        
    def finish_setup_complete(self, progress_window, email_success):
        """Complete setup after email sending"""
        progress_window.destroy()
        
        if email_success:
            # Save configuration
            if self.save_user_config():
                messagebox.showinfo("Setup Complete", 
                    "Setup completed successfully!\n\n"
                    "Password fragments have been sent to your trusted contacts\n"
                    "from the Anchorite security system (anchorite.focus@gmail.com).\n\n"
                    "Your trusted contacts should check their email for the fragments.\n"
                    "The application will now close.\n\n"
                    "You can now launch Focus Blocker Pro normally.")
                self.root.destroy()
            else:
                messagebox.showerror("Error", "Failed to save configuration. Please try again.")
        else:
            messagebox.showerror("Setup Failed", 
                "Failed to send emails. Please check your email settings and try again.")
            
    def on_closing(self):
        """Handle window closing"""
        if messagebox.askyesno("Exit Setup", "Are you sure you want to exit setup?\n\nYou'll need to complete setup before using Focus Blocker Pro."):
            self.root.destroy()
            
    def run(self):
        """Run the initial setup"""
        self.root.mainloop()


def is_setup_complete():
    """Check if initial setup has been completed"""
    config_file = "user_config.json"
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config.get('setup_completed', False)
    except FileNotFoundError:
        return False
    except Exception:
        return False


def run_initial_setup():
    """Run the initial setup if needed"""
    if not is_setup_complete():
        setup = InitialSetup()
        setup.run()
        return is_setup_complete()  # Return whether setup was completed
    return True  # Already completed


if __name__ == "__main__":
    setup = InitialSetup()
    setup.run() 