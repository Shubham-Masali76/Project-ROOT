import tkinter as tk
from tkinter import messagebox, ttk
import urllib.request
import zipfile
import os
import subprocess
import threading
import shutil
import webbrowser

# --- CONFIGURATION ---
# REPLACE THIS WITH YOUR GITHUB REPO ZIP DOWNLOAD LINK
GITHUB_ZIP_URL = "https://github.com/Shubham-Masali76/Project-Root/archive/refs/heads/main.zip"
INSTALL_DIR = os.path.join(os.environ["USERPROFILE"], "ROOT_AI")
# ---------------------

def start_install(api_key, progress_var, status_label, root):
    if not api_key:
        messagebox.showerror("Error", "API Key is required to power the AI's brain.")
        return
        
    def install_thread():
        try:
            # 1. Create Install Dir
            status_label.config(text="Creating directories...")
            if not os.path.exists(INSTALL_DIR):
                os.makedirs(INSTALL_DIR)
            progress_var.set(10)
            
            # 2. Generate .env
            status_label.config(text="Securing API Key...")
            with open(os.path.join(INSTALL_DIR, ".env"), "w") as f:
                f.write(f"GEMINI_API_KEY={api_key}\n")
            progress_var.set(20)
            
            # 3. Download Source Code
            status_label.config(text="Downloading R.O.O.T. brain (this may take a moment)...")
            zip_path = os.path.join(INSTALL_DIR, "source.zip")
            urllib.request.urlretrieve(GITHUB_ZIP_URL, zip_path)
            progress_var.set(40)
            
            # 4. Extract Source Code
            status_label.config(text="Extracting source code...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(INSTALL_DIR)
            os.remove(zip_path)
            
            # Move files from extracted subfolder to root install dir
            # Github zips extract into a folder named like "RepoName-main"
            extracted_folders = [f for f in os.listdir(INSTALL_DIR) if os.path.isdir(os.path.join(INSTALL_DIR, f))]
            extracted_folder = os.path.join(INSTALL_DIR, extracted_folders[0])
            for item in os.listdir(extracted_folder):
                shutil.move(os.path.join(extracted_folder, item), INSTALL_DIR)
            os.rmdir(extracted_folder)
            progress_var.set(50)
            
            # 5. Build venv
            status_label.config(text="Building Python environment (venv)...")
            subprocess.run(["python", "-m", "venv", "venv"], cwd=INSTALL_DIR, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            progress_var.set(70)
            
            # 6. Install Requirements
            status_label.config(text="Installing neural dependencies (this takes a minute)...")
            pip_exe = os.path.join(INSTALL_DIR, "venv", "Scripts", "pip.exe")
            req_file = os.path.join(INSTALL_DIR, "requirements.txt")
            subprocess.run([pip_exe, "install", "-r", req_file], cwd=INSTALL_DIR, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            progress_var.set(90)
            
            # 7. Generate VBS AutoStart
            status_label.config(text="Injecting into Windows Startup...")
            vbs_path = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup", "ROOT_AutoStart.vbs")
            pythonw_exe = os.path.join(INSTALL_DIR, "venv", "Scripts", "pythonw.exe")
            main_py = os.path.join(INSTALL_DIR, "main.py")
            
            vbs_content = f'Set WshShell = CreateObject("WScript.Shell")\nWshShell.CurrentDirectory = "{INSTALL_DIR}"\nWshShell.Run """{pythonw_exe}"" ""{main_py}""", 0, False\n'
            with open(vbs_path, "w") as f:
                f.write(vbs_content)
                
            # 8. Create Desktop Shortcut
            bat_path = os.path.join(os.environ["USERPROFILE"], "Desktop", "Start R.O.O.T..bat")
            bat_content = f"""@echo off\ncd /d "{INSTALL_DIR}"\nstart "" "{pythonw_exe}" "{main_py}"\n"""
            with open(bat_path, "w") as f:
                f.write(bat_content)
            progress_var.set(100)
            status_label.config(text="Installation Complete! Waking R.O.O.T. up...")
            
            # 9. First Launch
            subprocess.Popen([pythonw_exe, main_py], cwd=INSTALL_DIR, creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Close the installer
            root.after(2000, root.destroy)
            
        except Exception as e:
            messagebox.showerror("Installation Failed", f"An error occurred:\n{str(e)}")
            status_label.config(text="Failed.")

    # Run in background to keep GUI responsive
    threading.Thread(target=install_thread, daemon=True).start()

def build_gui():
    root = tk.Tk()
    root.title("R.O.O.T. OS Installer")
    root.geometry("550x400")
    root.configure(bg="#121212")
    
    title = tk.Label(root, text="Install R.O.O.T. AI", font=("Segoe UI", 20, "bold"), bg="#121212", fg="#00e5ff")
    title.pack(pady=(30, 10))
    
    desc_text = (
        "Welcome to R.O.O.T. (Realtime Omni-Operational Terminal).\n\n"
        "This assistant runs entirely locally on your machine for maximum privacy.\n"
        "To power its deep-learning brain, please provide your Gemini API Key below."
    )
    desc = tk.Label(root, text=desc_text, bg="#121212", fg="#b3b3b3", font=("Segoe UI", 10), justify=tk.CENTER)
    desc.pack(pady=10)
    
    key_entry = tk.Entry(root, width=55, show="*", font=("Segoe UI", 11), bg="#1e1e1e", fg="white", insertbackground="white", relief=tk.FLAT)
    key_entry.pack(pady=10, ipady=5)
    
    def open_api_page():
        webbrowser.open("https://aistudio.google.com/app/apikey")
        
    help_btn = tk.Button(root, text="Don't have an API Key? Get one for FREE here", 
                         bg="#121212", fg="#00e5ff", font=("Segoe UI", 9, "underline"), 
                         activebackground="#121212", activeforeground="white",
                         relief=tk.FLAT, cursor="hand2", command=open_api_page)
    help_btn.pack(pady=(0, 10))
    
    progress_var = tk.DoubleVar()
    style = ttk.Style()
    style.theme_use('default')
    style.configure("TProgressbar", thickness=8, background='#00e5ff', troughcolor='#1e1e1e', bordercolor='#121212')
    
    progress = ttk.Progressbar(root, style="TProgressbar", variable=progress_var, maximum=100)
    progress.pack(pady=20, fill=tk.X, padx=50)
    
    status_label = tk.Label(root, text="Waiting to start...", bg="#121212", fg="#666666", font=("Segoe UI", 9))
    status_label.pack()
    
    btn = tk.Button(root, text="Install & Launch", bg="#00e5ff", fg="black", font=("Segoe UI", 12, "bold"), 
                    activebackground="#00b3cc", relief=tk.FLAT, cursor="hand2",
                    command=lambda: start_install(key_entry.get().strip(), progress_var, status_label, root))
    btn.pack(pady=20, ipadx=20, ipady=5)
    
    root.mainloop()

if __name__ == "__main__":
    build_gui()
