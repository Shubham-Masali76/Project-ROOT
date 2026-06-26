import os
import re
import ctypes
import subprocess
import winreg
from google import genai
from google.genai import types

def set_volume(level):
    """Sets system volume to a specific percentage using pycaw."""
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        level = max(0, min(100, int(level)))
        # pycaw expects a scalar between 0.0 and 1.0 for SetMasterVolumeLevelScalar
        volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        return f"Volume set to {level}%."
    except Exception as e:
        return f"Failed to set volume: {str(e)}"

def set_brightness(level):
    """Sets monitor brightness to a specific percentage."""
    try:
        import screen_brightness_control as sbc
        level = max(0, min(100, int(level)))
        sbc.set_brightness(level)
        return f"Brightness set to {level}%."
    except Exception as e:
        return f"Failed to set brightness: {str(e)}"

def set_wallpaper(image_path):
    """Sets the Windows desktop wallpaper."""
    try:
        if not os.path.exists(image_path):
            return f"Wallpaper image not found at: {image_path}"
        
        SPI_SETDESKWALLPAPER = 20
        # 3 is SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 3)
        return "Wallpaper updated successfully."
    except Exception as e:
        return f"Failed to set wallpaper: {str(e)}"

def set_dark_mode(enabled):
    """Toggles Windows Dark/Light mode via Registry."""
    try:
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        
        with winreg.OpenKey(registry, key_path, 0, winreg.KEY_SET_VALUE) as key:
            value = 0 if enabled else 1
            winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, value)
            winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, value)
            
        mode = "Dark Mode" if enabled else "Light Mode"
        return f"Switched to {mode}."
    except Exception as e:
        return f"Failed to change theme: {str(e)}"

def generate_powershell_script(command_text):
    """Uses Gemini to generate a headless PowerShell script for dynamic system administration."""
    prompt = f"""
    You are a Windows OS Automation Engine. The user wants to change a system setting headlessly.
    Write a PowerShell script that accomplishes this task WITHOUT opening any GUI menus or settings apps.
    
    User Command: "{command_text}"
    
    Rules:
    - Output ONLY the PowerShell script inside a ```powershell code block.
    - Do NOT explain the script.
    - Use standard Windows PowerShell cmdlets or registry edits.
    - If it's impossible to do headlessly, output "IMPOSSIBLE" instead of a script.
    """
    
    try:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.1)
        )
        
        text = response.text
        if "IMPOSSIBLE" in text:
            return None
            
        match = re.search(r'```(?:powershell|ps1)?\n(.*?)```', text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return text.strip()
    except Exception:
        return None

def execute_powershell(script):
    """Executes a powershell script headlessly."""
    try:
        # Save to a temporary file
        temp_ps1 = os.path.join(os.environ.get('TEMP', 'C:\\'), 'root_setting.ps1')
        with open(temp_ps1, "w") as f:
            f.write(script)
            
        result = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", temp_ps1], 
                                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        try:
            os.remove(temp_ps1)
        except: pass
        
        if result.returncode == 0:
            return "System setting applied silently."
        else:
            return f"Failed to apply setting. {result.stderr.strip()[:100]}"
    except Exception as e:
        return f"PowerShell execution error: {str(e)}"

def extract_core_parameters(command_text):
    """Uses Gemini to quickly extract parameters for core hardcoded functions."""
    prompt = f"""
    Analyze the user command and extract settings parameters if they are explicitly asking for them.
    Return a valid JSON object. If a field is not applicable, set it to null.
    
    User Command: "{command_text}"
    
    Fields:
    "volume_percent": int (0-100) if setting volume.
    "brightness_percent": int (0-100) if setting brightness.
    "theme": string ("dark" or "light") if setting system theme.
    
    Example 1 (Set volume to 50): {{"volume_percent": 50, "brightness_percent": null, "theme": null}}
    Example 2 (Max brightness): {{"volume_percent": null, "brightness_percent": 100, "theme": null}}
    Example 3 (Turn on dark mode): {{"volume_percent": null, "brightness_percent": null, "theme": "dark"}}
    Example 4 (Turn off wifi): {{"volume_percent": null, "brightness_percent": null, "theme": null}}
    """
    try:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0
            )
        )
        import json
        return json.loads(response.text)
    except Exception:
        return {"volume_percent": None, "brightness_percent": None, "theme": None}

def execute(command_text):
    print(f"[Settings Controller] Processing: {command_text}")
    
    # 1. Check for core hardcoded logic first (for speed and stability)
    params = extract_core_parameters(command_text)
    
    if params.get("volume_percent") is not None:
        return set_volume(params["volume_percent"])
        
    if params.get("brightness_percent") is not None:
        return set_brightness(params["brightness_percent"])
        
    if params.get("theme") is not None:
        return set_dark_mode(params["theme"] == "dark")
        
    # 2. If it's a wallpaper request, we need a file path.
    if "wallpaper" in command_text.lower() or "background" in command_text.lower():
        match = re.search(r'([a-zA-Z]:\\[^\s]+\.(png|jpg|jpeg|bmp))', command_text, re.IGNORECASE)
        if match:
            return set_wallpaper(match.group(1))
            
    # 3. Dynamic PowerShell Generation (The Omni-Engine)
    print("[Settings Controller] Request is dynamic. Asking Gemini for PowerShell script...")
    ps_script = generate_powershell_script(command_text)
    
    if ps_script:
        print(f"[Settings Controller] Executing Generated PS1:\n{ps_script}")
        return execute_powershell(ps_script)
    else:
        return "I could not figure out how to modify that setting completely headlessly."
