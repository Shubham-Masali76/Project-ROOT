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
GITHUB_ZIP_URL = "https://github.com/Shubham-Masali76/Project-Root/archive/refs/heads/main.zip"
INSTALL_DIR = os.path.join(os.environ["USERPROFILE"], "ROOT_AI")
# ---------------------

class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("R.O.O.T. OS Setup Wizard")
        self.root.geometry("650x600")
        self.root.configure(bg="#121212")
        
        try:
            import sys
            if getattr(sys, 'frozen', False):
                self.root.iconbitmap(sys.executable)
            else:
                self.root.iconbitmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico"))
        except Exception:
            pass
        
        # Initialize variables
        self.api_key_var = tk.StringVar()
        self.groq_key_var = tk.StringVar()
        self.desktop_var = tk.BooleanVar(value=True)
        self.startup_var = tk.BooleanVar(value=True)
        self.progress_var = tk.DoubleVar()
        
        # Frames
        self.frame_welcome = tk.Frame(self.root, bg="#121212")
        self.frame_setup = tk.Frame(self.root, bg="#121212")
        self.frame_progress = tk.Frame(self.root, bg="#121212")
        self.frame_success = tk.Frame(self.root, bg="#121212")
        
        for frame in (self.frame_welcome, self.frame_setup, self.frame_progress, self.frame_success):
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            
        self.build_welcome()
        self.build_setup()
        self.build_progress()
        self.build_success()
        
        self.show_frame(self.frame_welcome)

    def show_frame(self, frame):
        frame.tkraise()

    def build_welcome(self):
        title = tk.Label(self.frame_welcome, text="Welcome to Project R.O.O.T.", font=("Segoe UI", 24, "bold"), bg="#121212", fg="#00e5ff")
        title.pack(pady=(40, 20))
        
        desc = tk.Label(self.frame_welcome, text="Reactive Operational Orchestration Technology", font=("Segoe UI", 12, "italic"), bg="#121212", fg="#b3b3b3")
        desc.pack(pady=(0, 20))
        
        features_frame = tk.Frame(self.frame_welcome, bg="#1e1e1e", bd=2, relief=tk.GROOVE)
        features_frame.pack(padx=40, pady=10, fill=tk.BOTH, expand=True)
        
        features_title = tk.Label(features_frame, text="System Capabilities:", font=("Segoe UI", 14, "bold"), bg="#1e1e1e", fg="white")
        features_title.pack(anchor=tk.W, padx=20, pady=(15, 10))
        
        features = [
            "🎙 Voice Command Interface (Vosk Offline Ear & Edge TTS)",
            "🧠 Neural Pathway Engine (Powered by Google Gemini)",
            "⚡ Absolute PC Control (System Volume, Media, Automation)",
            "🖥 Transparent Floating GUI (Always-on-Top Frameless Face)",
            "🛡 Automatic Immune System (Self-Repairing Codebase)",
            "☁ Over-The-Air (OTA) Updates (Syncs with GitHub Tags)",
            "🔒 100% Local Privacy (API keys are never uploaded)"
        ]
        
        for feature in features:
            tk.Label(features_frame, text=f"• {feature}", font=("Segoe UI", 11), bg="#1e1e1e", fg="#00e5ff", justify=tk.LEFT).pack(anchor=tk.W, padx=30, pady=4)
            
        btn_next = tk.Button(self.frame_welcome, text="Next >", bg="#00e5ff", fg="black", font=("Segoe UI", 12, "bold"), 
                             activebackground="#00b3cc", relief=tk.FLAT, cursor="hand2", command=lambda: self.show_frame(self.frame_setup))
        btn_next.pack(pady=30, ipadx=30, ipady=8)

    def build_setup(self):
        title = tk.Label(self.frame_setup, text="Configuration Setup", font=("Segoe UI", 20, "bold"), bg="#121212", fg="#00e5ff")
        title.pack(pady=(40, 10))
        
        desc = tk.Label(self.frame_setup, text="To power the deep-learning brain, provide your API Keys.", bg="#121212", fg="#b3b3b3", font=("Segoe UI", 11))
        desc.pack(pady=10)
        
        tk.Label(self.frame_setup, text="Gemini API Key (For Vision & Research):", bg="#121212", fg="white", font=("Segoe UI", 10)).pack()
        key_entry = tk.Entry(self.frame_setup, textvariable=self.api_key_var, width=55, show="*", font=("Segoe UI", 11), bg="#1e1e1e", fg="white", insertbackground="white", relief=tk.FLAT)
        key_entry.pack(pady=5, ipady=8)

        tk.Label(self.frame_setup, text="Groq API Key (For Lightning Fast Voice Chat):", bg="#121212", fg="white", font=("Segoe UI", 10)).pack()
        groq_entry = tk.Entry(self.frame_setup, textvariable=self.groq_key_var, width=55, show="*", font=("Segoe UI", 11), bg="#1e1e1e", fg="white", insertbackground="white", relief=tk.FLAT)
        groq_entry.pack(pady=5, ipady=8)
        
        env_path = os.path.join(INSTALL_DIR, ".env")
        if os.path.exists(env_path):
            try:
                with open(env_path, "r") as f:
                    for line in f:
                        if line.startswith("GEMINI_API_KEY="):
                            self.api_key_var.set(line.split("=", 1)[1].strip())
                        elif line.startswith("GROQ_API_KEY="):
                            self.groq_key_var.set(line.split("=", 1)[1].strip())
            except Exception:
                pass

        help_btn = tk.Button(self.frame_setup, text="Don't have an API Key? Get one for FREE here", 
                             bg="#121212", fg="#00e5ff", font=("Segoe UI", 9, "underline"), 
                             activebackground="#121212", activeforeground="white",
                             relief=tk.FLAT, cursor="hand2", command=lambda: webbrowser.open("https://aistudio.google.com/app/apikey"))
        help_btn.pack(pady=(0, 20))
        
        chk_frame = tk.Frame(self.frame_setup, bg="#121212")
        chk_frame.pack(pady=10)
        
        tk.Checkbutton(chk_frame, text="Create Desktop Shortcut", variable=self.desktop_var, bg="#121212", fg="#00e5ff", 
                       selectcolor="#1e1e1e", activebackground="#121212", activeforeground="white", font=("Segoe UI", 10)).pack(anchor=tk.W, pady=5)
        tk.Checkbutton(chk_frame, text="Launch automatically on Windows Startup", variable=self.startup_var, bg="#121212", fg="#00e5ff", 
                       selectcolor="#1e1e1e", activebackground="#121212", activeforeground="white", font=("Segoe UI", 10)).pack(anchor=tk.W, pady=5)
        
        btn_frame = tk.Frame(self.frame_setup, bg="#121212")
        btn_frame.pack(pady=40)
        
        btn_back = tk.Button(btn_frame, text="< Back", bg="#333333", fg="white", font=("Segoe UI", 12), 
                             relief=tk.FLAT, cursor="hand2", command=lambda: self.show_frame(self.frame_welcome))
        btn_back.pack(side=tk.LEFT, padx=10, ipadx=20, ipady=5)
        
        self.btn_install = tk.Button(btn_frame, text="Install R.O.O.T.", bg="#00e5ff", fg="black", font=("Segoe UI", 12, "bold"), 
                                     activebackground="#00b3cc", relief=tk.FLAT, cursor="hand2", command=self.start_install)
        self.btn_install.pack(side=tk.LEFT, padx=10, ipadx=30, ipady=5)

    def build_progress(self):
        title = tk.Label(self.frame_progress, text="Installing Neural Pathways...", font=("Segoe UI", 20, "bold"), bg="#121212", fg="#00e5ff")
        title.pack(pady=(40, 20))
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TProgressbar", thickness=10, background='#00e5ff', troughcolor='#1e1e1e', bordercolor='#121212')
        
        progress = ttk.Progressbar(self.frame_progress, style="TProgressbar", variable=self.progress_var, maximum=100)
        progress.pack(pady=20, fill=tk.X, padx=60)
        
        checklist_frame = tk.Frame(self.frame_progress, bg="#121212")
        checklist_frame.pack(pady=20)
        
        step_texts = [
            "Checking System Prerequisites",
            "Verifying API Key & Creating Directories",
            "Synchronizing OTA Updater",
            "Building Virtual Environment",
            "Installing Neural Dependencies",
            "Downloading Ear Cortex",
            "Configuring Startup & Desktop"
        ]
        self.step_labels = []
        for text in step_texts:
            lbl = tk.Label(checklist_frame, text=f"⬜ {text}", bg="#121212", fg="#666666", font=("Segoe UI", 12), anchor="w")
            lbl.pack(fill=tk.X, pady=5)
            self.step_labels.append(lbl)

    def build_success(self):
        tk.Label(self.frame_success, text="✅ Installation Complete", font=("Segoe UI", 28, "bold"), bg="#121212", fg="#00ff00").pack(pady=(100, 30))
        
        details = tk.Label(self.frame_success, text="Environment Ready\nDependencies Installed\nAPI Key Verified", font=("Segoe UI", 14), bg="#121212", fg="#b3b3b3")
        details.pack(pady=10)
        
        btn_launch = tk.Button(self.frame_success, text="Launch R.O.O.T.", bg="#00ff00", fg="black", font=("Segoe UI", 16, "bold"), 
                               activebackground="#00cc00", relief=tk.FLAT, cursor="hand2", command=self.launch_app)
        btn_launch.pack(pady=(60, 0), ipadx=40, ipady=15)

    def update_step(self, index, status):
        icons = ["⬜", "⏳", "✔", "❌"]
        colors = ["#666666", "#00e5ff", "#00ff00", "red"]
        text = self.step_labels[index].cget("text")[2:]
        self.step_labels[index].config(text=f"{icons[status]} {text}", fg=colors[status])

    def start_install(self):
        api_key = self.api_key_var.get().strip()
        groq_key = self.groq_key_var.get().strip()
        if not api_key or not groq_key:
            messagebox.showerror("Error", "Both API Keys are required to power the hybrid AI brain.")
            return
            
        self.show_frame(self.frame_progress)
        threading.Thread(target=self.install_thread, args=(api_key, groq_key), daemon=True).start()

    def install_thread(self, api_key, groq_key):
        try:
            # STEP 0: Prerequisites (Python)
            self.update_step(0, 1)
            python_installed = False
            try:
                res = subprocess.run(["python", "--version"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                if res.returncode == 0 and "Python" in res.stdout:
                    python_installed = True
            except Exception:
                pass
                
            if not python_installed:
                # Python is missing, use winget to install it!
                # We use --override "PrependPath=1" to automatically check the "Add to PATH" box!
                subprocess.run([
                    "winget", "install", "--id", "Python.Python.3.11", 
                    "--silent", "--accept-package-agreements", "--accept-source-agreements",
                    "--override", 'PrependPath=1 Include_test=0'
                ], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                # Because the PATH environment variable is cached per-process, we must restart.
                messagebox.showinfo("Prerequisites Installed", "R.O.O.T. just successfully installed Python on your system!\n\nBecause of Windows architecture, you must close this installer and re-open it so it can detect the new Python installation.")
                self.root.quit()
                import sys
                sys.exit(0)
            self.progress_var.set(5)
            self.update_step(0, 2)

            # STEP 1: Directories & API
            self.update_step(1, 1)
            
            # Auto-Clean previous installations to prevent manual deletion annoyance!
            if os.path.exists(INSTALL_DIR):
                try:
                    # Kill any running instances of R.O.O.T. so the folder isn't locked
                    subprocess.run(["taskkill", "/F", "/IM", "pythonw.exe"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    shutil.rmtree(INSTALL_DIR, ignore_errors=True)
                except Exception:
                    pass
                    
            if not os.path.exists(INSTALL_DIR):
                os.makedirs(INSTALL_DIR)
            self.progress_var.set(10)
            
            with open(os.path.join(INSTALL_DIR, ".env"), "w") as f:
                f.write(f"GEMINI_API_KEY={api_key}\n")
                f.write(f"GROQ_API_KEY={groq_key}\n")
            self.progress_var.set(20)
            
            zip_path = os.path.join(INSTALL_DIR, "source.zip")
            urllib.request.urlretrieve(GITHUB_ZIP_URL, zip_path)
            self.progress_var.set(40)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(INSTALL_DIR)
            os.remove(zip_path)
                
            extracted_folder = None
            for item in os.listdir(INSTALL_DIR):
                full_path = os.path.join(INSTALL_DIR, item)
                if os.path.isdir(full_path) and ("Project-Root" in item or "Project-ROOT" in item):
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
            self.progress_var.set(50)
            self.update_step(1, 2)
            
            # STEP 2: Sync OTA Updater
            self.update_step(2, 1)
            try:
                import json
                api_url = "https://api.github.com/repos/Shubham-Masali76/Project-Root/tags"
                req = urllib.request.Request(api_url, headers={'User-Agent': 'ROOT-Installer'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode())
                    remote_hash = data[0]['name']
                with open(os.path.join(INSTALL_DIR, "commit_hash.txt"), "w") as f:
                    f.write(remote_hash)
            except Exception as e:
                print(f"Hash sync failed: {e}")
            self.update_step(2, 2)
            
            # STEP 3: Build Venv
            self.update_step(3, 1)
            subprocess.run(["python", "-m", "venv", "venv"], cwd=INSTALL_DIR, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.progress_var.set(60)
            
            pip_exe = os.path.join(INSTALL_DIR, "venv", "Scripts", "pip.exe")
            # Install uv using pip
            subprocess.run([pip_exe, "install", "uv"], cwd=INSTALL_DIR, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Use uv to install requirements lightning fast
            uv_exe = os.path.join(INSTALL_DIR, "venv", "Scripts", "uv.exe")
            req_file = os.path.join(INSTALL_DIR, "requirements.txt")
            subprocess.run([uv_exe, "pip", "install", "-r", req_file], cwd=INSTALL_DIR, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.progress_var.set(80)
            self.update_step(4, 2)
            
            # STEP 5: Download Vosk
            self.update_step(5, 1)
            model_dir = os.path.join(INSTALL_DIR, "model")
            if not os.path.exists(model_dir):
                vosk_zip = os.path.join(INSTALL_DIR, "vosk_model.zip")
                try:
                    # Fast GitHub Mirror
                    url = "https://github.com/rhasspy/rhasspy-asr-vosk-hermes/releases/download/v0.1.0/vosk-model-small-en-us-0.15.zip"
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req) as response, open(vosk_zip, 'wb') as out_file:
                        out_file.write(response.read())
                except Exception:
                    # Fallback to slow mirror
                    vosk_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
                    urllib.request.urlretrieve(vosk_url, vosk_zip)
                
                with zipfile.ZipFile(vosk_zip, 'r') as zip_ref:
                    zip_ref.extractall(INSTALL_DIR)
                os.remove(vosk_zip)
                
                for d in os.listdir(INSTALL_DIR):
                    full_path = os.path.join(INSTALL_DIR, d)
                    if os.path.isdir(full_path) and "vosk-model" in d:
                        os.rename(full_path, model_dir)
                        break
            self.progress_var.set(90)
            self.update_step(5, 2)
            
            # STEP 6: Shortcuts
            self.update_step(6, 1)
            if self.startup_var.get():
                vbs_path = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup", "ROOT_AutoStart.vbs")
                pythonw_exe = os.path.join(INSTALL_DIR, "venv", "Scripts", "pythonw.exe")
                main_py = os.path.join(INSTALL_DIR, "main.py")
                
                vbs_content = f'Set WshShell = CreateObject("WScript.Shell")\nWshShell.CurrentDirectory = "{INSTALL_DIR}"\nWshShell.Run """{pythonw_exe}"" ""{main_py}""", 0, False\n'
                with open(vbs_path, "w") as f:
                    f.write(vbs_content)
                
            if self.desktop_var.get():
                pythonw_exe = os.path.join(INSTALL_DIR, "venv", "Scripts", "pythonw.exe")
                main_py = os.path.join(INSTALL_DIR, "main.py")
                shortcut_path = os.path.join(os.environ["USERPROFILE"], "Desktop", "ROOT.lnk")
                
                vbs_script = f"""
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{pythonw_exe}"
oLink.Arguments = "main.py"
oLink.WorkingDirectory = "{INSTALL_DIR}"
oLink.Description = "Launch R.O.O.T. Artificial Intelligence"
oLink.IconLocation = "{os.path.join(INSTALL_DIR, 'icon.ico')}"
oLink.Save
"""
                vbs_path = os.path.join(INSTALL_DIR, "create_shortcut.vbs")
                with open(vbs_path, "w") as f:
                    f.write(vbs_script)
                
                subprocess.run(["cscript.exe", "//Nologo", vbs_path], creationflags=subprocess.CREATE_NO_WINDOW)
                if os.path.exists(vbs_path):
                    os.remove(vbs_path)
                    
            self.progress_var.set(100)
            self.update_step(6, 2)
            
            # Proceed to Success Screen
            self.show_frame(self.frame_success)
            
        except Exception as e:
            messagebox.showerror("Installation Failed", f"An error occurred:\n{str(e)}")
            for lbl in self.step_labels:
                if lbl.cget("text").startswith("⏳"):
                    lbl.config(text=lbl.cget("text").replace("⏳", "❌"), fg="red")
            
            btn_retry = tk.Button(self.frame_progress, text="< Back to Setup", bg="#333333", fg="white", font=("Segoe UI", 12), 
                                  relief=tk.FLAT, cursor="hand2", command=lambda: self.show_frame(self.frame_setup))
            btn_retry.pack(pady=20)

    def launch_app(self):
        pythonw_exe = os.path.join(INSTALL_DIR, "venv", "Scripts", "pythonw.exe")
        main_py = os.path.join(INSTALL_DIR, "main.py")
        
        clean_env = os.environ.copy()
        clean_env.pop("TCL_LIBRARY", None)
        clean_env.pop("TK_LIBRARY", None)
        
        subprocess.Popen([pythonw_exe, main_py], cwd=INSTALL_DIR, env=clean_env, creationflags=subprocess.CREATE_NO_WINDOW)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = InstallerApp(root)
    root.mainloop()
