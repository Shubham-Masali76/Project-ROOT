import os
import sys
import urllib.request
import urllib.error

# IMPORT ALL MODULES USED BY INSTALLER.PY
# This guarantees PyInstaller bundles them into the frozen .exe
import tkinter as tk
from tkinter import messagebox, ttk
import zipfile
import subprocess
import threading
import shutil
import webbrowser
import time

def run_bootstrapper():
    # 1. Show sleek splash screen
    splash = tk.Tk()
    splash.title("R.O.O.T.")
    splash.geometry("400x120")
    splash.overrideredirect(True)
    splash.eval('tk::PlaceWindow . center')
    splash.configure(bg="#121212")
    
    title_lbl = tk.Label(splash, text="R.O.O.T. Initializing", font=("Segoe UI", 16, "bold"), bg="#121212", fg="#00e5ff")
    title_lbl.pack(pady=(20, 5))
    
    status_lbl = tk.Label(splash, text="Connecting to Neural Network...", font=("Consolas", 10), bg="#121212", fg="#b3b3b3")
    status_lbl.pack()
    
    splash.update()
    
    try:
        # 2. Download the absolute latest installer.py from GitHub
        url = f"https://raw.githubusercontent.com/Shubham-Masali76/Project-Root/main/installer.py?t={time.time()}"

        temp_installer = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "live_installer.py")
        
        urllib.request.urlretrieve(url, temp_installer)
        
        # 3. Read the downloaded code
        with open(temp_installer, "r", encoding="utf-8") as f:
            code = f.read()
            
        # 4. Close the splash screen
        splash.destroy()
        
        # 5. Execute the live installer code dynamically in the global scope
        exec(code, globals())
        
    except Exception as e:
        status_lbl.config(text=f"Connection Failed: {e}", fg="red")
        splash.update()
        # Keep window open for 5 seconds so they can read the error
        splash.after(5000, splash.destroy)
        splash.mainloop()

if __name__ == "__main__":
    run_bootstrapper()
