import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime, timedelta

def main():
    """Enhanced mission setup per aim.txt specification"""
    
    # Step 1: Mission statement (aim.txt lines 24-30)
    mission = get_mission_statement()
    if not mission:
        return
        
    # Step 2: Time allocation (aim.txt lines 32-39)
    duration = get_time_allocation() 
    if not duration:
        return
        
    # Save and activate proxy (aim.txt line 39)
    save_mission_and_activate(mission, duration)

def get_mission_statement():
    """Get mission statement with 50+ character requirement per aim.txt"""
    root = tk.Tk()
    root.title("Focus Blocker Pro - Mission Setup")
    root.geometry("500x400")
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (250)
    y = (root.winfo_screenheight() // 2) - (200)
    root.geometry(f"500x400+{x}+{y}")
    
    main_frame = ttk.Frame(root, padding="30")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title and instruction per aim.txt
    ttk.Label(main_frame, text="🎯 What would you like to achieve in this session?", 
             font=("Arial", 14, "bold")).pack(pady=(0, 10))
    
    ttk.Label(main_frame, text="Please be specific. Your response must be at least 50 characters long.",
             wraplength=400).pack(pady=(0, 20))
    
    # Mission entry
    mission_text = tk.Text(main_frame, height=6, width=50, wrap=tk.WORD, font=("Arial", 11))
    mission_text.pack(pady=(0, 10))
    mission_text.focus()
    
    # Character counter
    char_counter = ttk.Label(main_frame, text="Characters: 0 (minimum: 50)", foreground="red")
    char_counter.pack(pady=(0, 20))
    
    def update_counter(*args):
        content = mission_text.get("1.0", tk.END).strip()
        char_count = len(content)
        char_counter.config(
            text=f"Characters: {char_count} (minimum: 50)",
            foreground="green" if char_count >= 50 else "red"
        )
    
    mission_text.bind('<KeyRelease>', update_counter)
    
    result = {"mission": None}
    
    def on_next():
        content = mission_text.get("1.0", tk.END).strip()
        if len(content) < 50:
            # Exact error message per aim.txt line 29
            messagebox.showerror("Error", "Your mission statement must be at least 50 characters long")
            return
            
        result["mission"] = content
        root.destroy()
        
    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X)
    ttk.Button(button_frame, text="Next →", command=on_next).pack(side=tk.RIGHT)
    
    root.mainloop()
    return result["mission"]

def get_time_allocation():
    """Get time allocation with 300-minute maximum per aim.txt"""
    root = tk.Tk()
    root.title("Focus Blocker Pro - Time Allocation")
    root.geometry("400x300")
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (200)
    y = (root.winfo_screenheight() // 2) - (150)
    root.geometry(f"400x300+{x}+{y}")
    
    main_frame = ttk.Frame(root, padding="30")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title per aim.txt
    ttk.Label(main_frame, text="⏱️ How many minutes would you like to allocate to this task?", 
             font=("Arial", 12, "bold"), wraplength=300).pack(pady=(0, 20))
    
    ttk.Label(main_frame, text="Maximum: 300 minutes").pack(pady=(0, 20))
    
    # Time entry
    time_var = tk.StringVar(value="60")
    time_spinbox = ttk.Spinbox(main_frame, from_=1, to=300, width=10, 
                              textvariable=time_var, font=("Arial", 12))
    time_spinbox.pack(pady=(0, 20))
    
    result = {"duration": None}
    
    def on_complete():
        try:
            minutes = int(time_var.get())
            if minutes > 300:
                # Exact error message per aim.txt line 37
                messagebox.showerror("Error", "The time must be less than 300 minutes")
                return
                
            result["duration"] = minutes
            root.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
    
    # Complete button per aim.txt line 36
    ttk.Button(main_frame, text="Complete", command=on_complete).pack()
    
    root.mainloop()
    return result["duration"]

def save_mission_and_activate(mission, duration):
    """Save mission and activate proxy per aim.txt line 39"""
    # Save to mission.json
    mission_data = {
        "mission": mission,
        "created": datetime.now().isoformat(),
        "description": "User-defined mission",
        "duration_minutes": duration,
        "start_time": datetime.now().isoformat(),
        "end_time": (datetime.now() + timedelta(minutes=duration)).isoformat()
    }
    
    with open("mission.json", "w") as f:
        json.dump(mission_data, f, indent=2)
    
    print(f"✅ Mission saved: {duration} minutes for '{mission[:50]}...'")
    
    # Activate proxy per aim.txt line 39
    try:
        from proxy_focus_agent import ProxyFocusAgent
        agent = ProxyFocusAgent()
        agent.start_focus_session(mission, duration)
        print("🚀 Focus session started! Window closes per aim.txt.")
    except Exception as e:
        print(f"❌ Error starting proxy: {e}")
        messagebox.showinfo("Mission Saved", "Mission saved! Please start the proxy manually.")

if __name__ == "__main__":
    main()
