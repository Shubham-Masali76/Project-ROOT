import os
import urllib.request
import json
import zipfile
import shutil
import sys
import threading
import time

from core.state import STATE_DICT

# --- CONFIGURATION ---
# Replace these with your actual GitHub repo details before publishing!
GITHUB_USER = "Shubham-Masali76"
GITHUB_REPO = "Project-Root"
BRANCH = "main"
# ---------------------

API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/commits/{BRANCH}"
ZIP_URL = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/archive/refs/heads/{BRANCH}.zip"
LOCAL_HASH_FILE = "commit_hash.txt"

def update_thread():
    if GITHUB_USER == "YOUR_USERNAME" or GITHUB_USER == "":
        print("[AutoUpdater] GitHub Username not configured. Skipping auto-update.")
        return
        
    time.sleep(3) # Wait a few seconds so the user can read the welcome message first
    STATE_DICT["CURRENT_LOG"] = "AutoUpdater: Ping sent to GitHub for OTA updates..."
    print("[AutoUpdater] Checking for OTA updates...")
    try:
        # 1. Fetch latest commit hash
        req = urllib.request.Request(API_URL, headers={'User-Agent': 'ROOT-AI-Updater'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            remote_hash = data['sha']
            
        # 2. Check local hash
        local_hash = ""
        if os.path.exists(LOCAL_HASH_FILE):
            with open(LOCAL_HASH_FILE, "r") as f:
                local_hash = f.read().strip()
                
        if remote_hash == local_hash:
            print("[AutoUpdater] System is up to date.")
            return
            
        STATE_DICT["CURRENT_LOG"] = f"AutoUpdater: New update found! Downloading commit {remote_hash[:7]}..."
        print(f"[AutoUpdater] New update found! Downloading commit {remote_hash[:7]}...")
        
        # 3. Download update
        zip_path = "update.zip"
        urllib.request.urlretrieve(ZIP_URL, zip_path)
        
        # 4. Extract
        extract_dir = "update_extracted"
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            
        extracted_folders = [f for f in os.listdir(extract_dir) if os.path.isdir(os.path.join(extract_dir, f))]
        if not extracted_folders:
            raise Exception("Invalid zip format")
        source_dir = os.path.join(extract_dir, extracted_folders[0])
        
        # 5. Safe Copy (Protect .env and memory)
        # Only overwrite these exact folders/files from the repo
        safe_to_copy = ["core", "gui", "operators", "main.py", "requirements.txt", "installer.py", "build_installer.bat"]
        
        for item in safe_to_copy:
            src_path = os.path.join(source_dir, item)
            dst_path = os.path.join(os.getcwd(), item)
            
            if os.path.exists(src_path):
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(src_path, dst_path)
                    
        # 6. Cleanup
        shutil.rmtree(extract_dir)
        os.remove(zip_path)
        
        # 7. Save new hash
        with open(LOCAL_HASH_FILE, "w") as f:
            f.write(remote_hash)
            
        STATE_DICT["CURRENT_LOG"] = f"AutoUpdater: Update to {remote_hash[:7]} successful! Rebooting R.O.O.T. to apply changes..."
        print(f"[AutoUpdater] Update to {remote_hash[:7]} successful! Rebooting R.O.O.T. to apply changes...")
        time.sleep(2)
        
        # 8. Reboot the system to load new code!
        os.execv(sys.executable, [sys.executable] + sys.argv)
        
    except Exception as e:
        print(f"[AutoUpdater] Update check failed: {e}")

def check_and_update():
    """Starts the updater in a background thread so it doesn't block boot."""
    threading.Thread(target=update_thread, daemon=True).start()
