import os
import webbrowser
import difflib
import subprocess
import concurrent.futures
import urllib.request
import re
import psutil
import threading
from google import genai
from google.genai import types
import json
import pygetwindow as gw
from core.memory import neuro_memory

# Standard Start Menu paths for instant .lnk search
SEARCH_DIRS = [
    r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
    os.path.join(os.environ.get('USERPROFILE', ''), r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs"),
    r"C:\Users\Public\Desktop",
    os.path.join(os.environ.get('USERPROFILE', ''), "Desktop")
]

def search_dir_for_lnk(directory):
    links = {}
    if not os.path.exists(directory): return links
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".lnk"):
                name = os.path.splitext(file)[0].lower()
                links[name] = os.path.join(root, file)
    return links

def get_all_shortcuts():
    all_links = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(SEARCH_DIRS)) as executor:
        futures = [executor.submit(search_dir_for_lnk, d) for d in SEARCH_DIRS]
        for f in concurrent.futures.as_completed(futures):
            all_links.update(f.result())
    return all_links

def scrape_youtube_video(query):
    """Scrapes YouTube search results to auto-play the top video."""
    try:
        search_url = "https://www.youtube.com/results?search_query=" + query.replace(" ", "+")
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        if video_ids:
            return "https://www.youtube.com/watch?v=" + video_ids[0]
    except Exception as e:
        print(f"[YouTube Scraper Error] {e}")
    return None

def deep_search_drive(drive_path, target_exe, stop_event, result_list):
    """Deep scans a specific drive with targeted heuristics."""
    try:
        target_base = target_exe.replace(".exe", "").lower()
        
        # 1. Heuristic Pathing: Don't scan 1TB of C:\ System files. Target where apps actually install.
        if "C:" in drive_path.upper():
            user_profile = os.environ.get('USERPROFILE', '')
            search_paths = [
                r"C:\Program Files",
                r"C:\Program Files (x86)",
                os.path.join(user_profile, 'AppData', 'Local'),
                os.path.join(user_profile, 'AppData', 'Roaming'),
                os.path.join(user_profile, 'Desktop'),
                r"C:\Games"
            ]
        else:
            # For D:\ or E:\ drives, scan the whole drive but skip junk
            search_paths = [drive_path]

        for base_path in search_paths:
            if not os.path.exists(base_path): continue
            
            for root, dirs, files in os.walk(base_path):
                if stop_event.is_set():
                    return
                    
                # 2. Junk Filter: Skip massive data/cache folders that will never contain the target app
                skip_dirs = ['windows', '$recycle.bin', 'system volume information', 'temp', 'cache', 'node_modules', '.git']
                if any(skip in root.lower() for skip in skip_dirs):
                    dirs[:] = [] # Stop traversing this branch entirely
                    continue
                    
                for file in files:
                    # 3. Substring Match: If target is "cursor", match "Cursor.exe" or "CursorLauncher.exe"
                    if file.lower().endswith(".exe") and target_base in file.lower():
                        result_list.append(os.path.join(root, file))
                        stop_event.set()
                        return
    except Exception:
        pass # Silently handle Permission Denied errors on system folders

def extract_target(text):
    """Uses Gemini to intelligently extract the app name and its domain classification."""
    prompt = f"""
    Extract the exact name of the application, game, or website the user wants to interact with.
    Also, use your world knowledge to determine if this target is primarily a 'website' (like netflix, youtube, amazon) or a 'local_app' (like chrome, notepad, epic games, valorant).
    Ignore all conversational filler words.
    
    User Text: "{text}"
    
    Respond with ONLY a valid JSON object containing "app" and "type" keys.
    Example 1: {{"app": "world of warships", "type": "local_app"}}
    Example 2: {{"app": "netflix", "type": "website"}}
    """
    try:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0,
            )
        )
        data = json.loads(response.text)
        app_name = data.get('app', '').strip().lower()
        app_type = data.get('type', 'local_app').strip().lower()
        return app_name, app_type
    except Exception:
        # Fallback if AI crashes
        clean = text.lower()
        for w in ["open", "launch", "start", "play", "please", "hey"]:
            clean = clean.replace(w, "")
        return clean.strip(), "local_app"

def execute(command_text):
    print(f"[OS Controller] Executing: {command_text}")
    
    # Let the AI figure out what the app is and what type it is!
    target, target_type = extract_target(command_text)
    if not target:
        target = command_text.lower().replace("open", "").strip()
        
    print(f"[OS Controller] AI Extracted Target: {target} (Type: {target_type})")
    cmd = command_text.lower()
    
    # --- NEUROPLASTICITY: Check Structural Memory First ---
    if "app_paths" in neuro_memory.ltm and target in neuro_memory.ltm["app_paths"]:
        path = neuro_memory.ltm["app_paths"][target]
        print(f"[Neuroplasticity] Memory Hit! Launching {target} instantly from {path}")
        try:
            subprocess.Popen(f'cmd /c start "" "{path}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"I remembered exactly where {target} is and opened it instantly."
        except Exception:
            pass # Fall through if the file was moved/deleted
    
    # 0. Process Termination & Window Management
    if "close" in cmd or "kill" in cmd:
        found = False
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if target in proc.info['name'].lower():
                    proc.kill()
                    found = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        if found:
            return f"I have terminated {target}."
        else:
            return f"I could not find a running process for {target}."
            
    if "minimize" in cmd or "maximize" in cmd:
        windows = gw.getWindowsWithTitle(target)
        if not windows:
            all_titles = [w.title for w in gw.getAllWindows() if w.title]
            matches = difflib.get_close_matches(target, all_titles, n=1, cutoff=0.3)
            if matches:
                windows = gw.getWindowsWithTitle(matches[0])
                
        if windows:
            for win in windows:
                if "minimize" in cmd:
                    if not win.isMinimized:
                        win.minimize()
                else:
                    if not win.isMaximized:
                        win.maximize()
            action_str = "minimized" if "minimize" in cmd else "maximized"
            return f"I have {action_str} {target}."
        else:
            return f"I could not find an active window for {target}."
    
    # 1. Website Deep Linking
    if target == "yt":
        target = "youtube"
        target_type = "website"
        
    if target_type == "website" or "website" in cmd:
        clean_target = target.replace("website", "").replace(" ", "").strip()
        webbrowser.open(f"https://www.{clean_target}.com")
        return f"I have opened {target}."
        
    # 2. Threaded OS Start Menu Search (Instant)
    all_links = get_all_shortcuts()
    
    best_match = None
    
    # Step A: Smart Substring Match
    for key in all_links.keys():
        if target in key or key in target:
            best_match = key
            break
            
    # Step B: Looser Fuzzy Match for Transcription Typos
    if not best_match:
        matches = difflib.get_close_matches(target, all_links.keys(), n=1, cutoff=0.5)
        if matches:
            best_match = matches[0]
    
    if best_match:
        app_path = all_links[best_match]
        print(f"[OS Controller] Found Start Menu match: {best_match} -> {app_path}")
        try:
            subprocess.Popen(f'cmd /c start "" "{app_path}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            neuro_memory.learn_app_path(target, app_path) # Learn it!
            return f"I have launched {best_match}."
        except Exception as e:
            return f"Failed to launch {best_match}."

    # 3. Media Auto-Play Engine
    # Trigger if they say 'play', 'listen to', or specifically mention 'video/song' and 'youtube'
    is_media_request = (
        re.search(r'\bplay\b', cmd) or 
        "listen to" in cmd or 
        ("youtube" in cmd and "open" not in cmd) or
        ("video" in cmd and "youtube" in cmd) or
        ("song" in cmd and "youtube" in cmd)
    )
    
    if is_media_request:
        # Extract just the search query by removing command words
        search_query = cmd
        for w in ["open", "play", "a video", "video", "on youtube", "youtube", "listen to", "song"]:
            search_query = search_query.replace(w, "")
        search_query = search_query.strip()
        
        if not search_query: 
            search_query = target
            
        print(f"[OS Controller] Auto-playing: {search_query}")
        video_url = scrape_youtube_video(search_query)
        if video_url:
            webbrowser.open(video_url)
            return f"Playing {search_query} on YouTube."
        else:
            clean_q = search_query.replace(" ", "+")
            webbrowser.open(f"https://www.youtube.com/results?search_query={clean_q}")
            return f"I opened the YouTube search results for {search_query}."
            
    # 4. Global Omni-Search Engine (Deep Search)
    from core.state import STATE_DICT
    STATE_DICT["CURRENT_LOG"] = f"Searching hard drive for '{target}'..."
    target_exe = target + ".exe"
    print(f"[OS Controller] '{target}' not found in Start Menu. Engaging Deep Search for {target_exe}...")
    
    stop_event = threading.Event()
    result_list = []
    
    # Dynamically map all mounted drives (C:\, D:\, USBs)
    partitions = psutil.disk_partitions()
    drives = [p.device for p in partitions if p.fstype]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(drives)) as executor:
        futures = []
        for drive in drives:
            print(f"[Deep Search] Spawning thread for {drive}")
            futures.append(executor.submit(deep_search_drive, drive, target_exe, stop_event, result_list))
        
        # Wait for all threads to finish OR for the stop_event to abort them
        concurrent.futures.wait(futures)
        
    if result_list:
        app_path = result_list[0]
        print(f"[Deep Search] Found: {app_path}")
        try:
            subprocess.Popen(f'cmd /c start "" "{app_path}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            neuro_memory.learn_app_path(target, app_path) # Learn it!
            return f"I found {target} deep in your system and launched it."
        except Exception:
            return f"I found {target} but failed to launch it."
            
    # 5. Fallback Web Search
    webbrowser.open(f"https://www.google.com/search?q={target}")
    return f"I could not find {target} anywhere on your system, so I searched Google for it."
