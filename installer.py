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

def start_install(api_key, create_desktop, create_startup, progress_var, status_label, root):
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
            extracted_folder = None
            for d in os.listdir(INSTALL_DIR):
                full_path = os.path.join(INSTALL_DIR, d)
                if os.path.isdir(full_path) and ("Project-Root" in d or "Project-ROOT" in d):
                    extracted_folder = full_path
                    break
                    
            if extracted_folder:
                for item in os.listdir(extracted_folder):
                    src = os.path.join(extracted_folder, item)
                    dst = os.path.join(INSTALL_DIR, item)
                    if os.path.exists(dst):
                        if os.path.isdir(dst):
                            shutil.rmtree(dst, ignore_errors=True)
                        else:
                            os.remove(dst)
                    shutil.move(src, INSTALL_DIR)
                shutil.rmtree(extracted_folder, ignore_errors=True)
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
            progress_var.set(80)
            
            # 6.5 Download Vosk Offline Voice Model
            status_label.config(text="Downloading Ear Cortex (Offline Voice Model)...")
            model_dir = os.path.join(INSTALL_DIR, "model")
            if not os.path.exists(model_dir):
                vosk_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
                vosk_zip = os.path.join(INSTALL_DIR, "vosk_model.zip")
                urllib.request.urlretrieve(vosk_url, vosk_zip)
                
                with zipfile.ZipFile(vosk_zip, 'r') as zip_ref:
                    zip_ref.extractall(INSTALL_DIR)
                os.remove(vosk_zip)
                
                # Find the extracted folder and rename it to 'model'
                for d in os.listdir(INSTALL_DIR):
                    full_path = os.path.join(INSTALL_DIR, d)
                    if os.path.isdir(full_path) and "vosk-model" in d:
                        os.rename(full_path, model_dir)
                        break
            
            progress_var.set(90)
            
            # 7. Generate VBS AutoStart
            if create_startup:
                status_label.config(text="Injecting into Windows Startup...")
                vbs_path = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup", "ROOT_AutoStart.vbs")
                pythonw_exe = os.path.join(INSTALL_DIR, "venv", "Scripts", "pythonw.exe")
                main_py = os.path.join(INSTALL_DIR, "main.py")
                
                vbs_content = f'Set WshShell = CreateObject("WScript.Shell")\nWshShell.CurrentDirectory = "{INSTALL_DIR}"\nWshShell.Run """{pythonw_exe}"" ""{main_py}""", 0, False\n'
                with open(vbs_path, "w") as f:
                    f.write(vbs_content)
                
            # 8. Create Desktop Shortcut
            if create_desktop:
                pythonw_exe = os.path.join(INSTALL_DIR, "venv", "Scripts", "pythonw.exe")
                main_py = os.path.join(INSTALL_DIR, "main.py")
                shortcut_path = os.path.join(os.environ["USERPROFILE"], "Desktop", "Start R.O.O.T..lnk")
                
                vbs_script = f"""
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{pythonw_exe}"
oLink.Arguments = "main.py"
oLink.WorkingDirectory = "{INSTALL_DIR}"
oLink.Description = "Launch R.O.O.T. Artificial Intelligence"
oLink.Save
"""
                vbs_path = os.path.join(INSTALL_DIR, "create_shortcut.vbs")
                with open(vbs_path, "w") as f:
                    f.write(vbs_script)
                
                subprocess.run(["cscript.exe", "//Nologo", vbs_path], creationflags=subprocess.CREATE_NO_WINDOW)
                if os.path.exists(vbs_path):
                    os.remove(vbs_path)
                    
            progress_var.set(100)
            status_label.config(text="Installation Complete! Waking R.O.O.T. up...")
            
            # 9. First Launch
            pythonw_exe = os.path.join(INSTALL_DIR, "venv", "Scripts", "pythonw.exe")
            main_py = os.path.join(INSTALL_DIR, "main.py")
            
            # CRITICAL FIX: Strip PyInstaller's temporary Tkinter paths from the environment
            # otherwise the child process will look for libraries in a folder that gets deleted!
            clean_env = os.environ.copy()
            clean_env.pop("TCL_LIBRARY", None)
            clean_env.pop("TK_LIBRARY", None)
            
            subprocess.Popen([pythonw_exe, main_py], cwd=INSTALL_DIR, env=clean_env, creationflags=subprocess.CREATE_NO_WINDOW)
            
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
    root.geometry("550x450")
    root.configure(bg="#121212")
    
    title = tk.Label(root, text="Install R.O.O.T. AI", font=("Segoe UI", 20, "bold"), bg="#121212", fg="#00e5ff")
    title.pack(pady=(30, 10))
    
    desc_text = (
        "Welcome to R.O.O.T. (Reactive Operational Orchestration Technology).\n\n"
        "This assistant runs entirely locally on your machine for maximum privacy.\n"
        "To power its deep-learning brain, please provide your Gemini API Key below."
    )
    desc = tk.Label(root, text=desc_text, bg="#121212", fg="#b3b3b3", font=("Segoe UI", 10), justify=tk.CENTER)
    desc.pack(pady=10)
    
    key_entry = tk.Entry(root, width=55, show="*", font=("Segoe UI", 11), bg="#1e1e1e", fg="white", insertbackground="white", relief=tk.FLAT)
    key_entry.pack(pady=10, ipady=5)
    
    # Auto-fill API key if .env already exists
    env_path = os.path.join(INSTALL_DIR, ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r") as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        key_entry.insert(0, line.split("=", 1)[1].strip())
                        break
        except Exception:
            pass

    def open_api_page():
        webbrowser.open("https://aistudio.google.com/app/apikey")
        
    help_btn = tk.Button(root, text="Don't have an API Key? Get one for FREE here", 
                         bg="#121212", fg="#00e5ff", font=("Segoe UI", 9, "underline"), 
                         activebackground="#121212", activeforeground="white",
                         relief=tk.FLAT, cursor="hand2", command=open_api_page)
    help_btn.pack(pady=(0, 5))
    
    # Transparency Checkboxes
    desktop_var = tk.BooleanVar(value=True)
    startup_var = tk.BooleanVar(value=True)
    
    chk_frame = tk.Frame(root, bg="#121212")
    chk_frame.pack(pady=5)
    
    tk.Checkbutton(chk_frame, text="Create Desktop Shortcut", variable=desktop_var, bg="#121212", fg="#00e5ff", 
                   selectcolor="#1e1e1e", activebackground="#121212", activeforeground="white", font=("Segoe UI", 9)).pack(anchor=tk.W)
    tk.Checkbutton(chk_frame, text="Launch automatically on Windows Startup", variable=startup_var, bg="#121212", fg="#00e5ff", 
                   selectcolor="#1e1e1e", activebackground="#121212", activeforeground="white", font=("Segoe UI", 9)).pack(anchor=tk.W)
    
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
                    command=lambda: start_install(key_entry.get().strip(), desktop_var.get(), startup_var.get(), progress_var, status_label, root))
    btn.pack(pady=20, ipadx=20, ipady=5)
    
    root.mainloop()

if __name__ == "__main__":
    build_gui()
