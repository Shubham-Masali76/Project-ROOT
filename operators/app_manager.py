import subprocess
from google import genai
from google.genai import types
import json

def parse_winget_command(command_text):
    """Uses Gemini to extract the target application and whether to install or uninstall."""
    prompt = f"""
    You are a package manager assistant. The user wants to install or uninstall an application using winget.
    Extract the action ("install" or "uninstall") and the exact application name.
    
    User Command: "{command_text}"
    
    Respond with ONLY a valid JSON object.
    Example 1: {{"action": "install", "app": "Google Chrome"}}
    Example 2: {{"action": "uninstall", "app": "Spotify"}}
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
        return json.loads(response.text)
    except Exception:
        # Fallback heuristic
        cmd = command_text.lower()
        action = "uninstall" if "uninstall" in cmd else "install"
        app = cmd.replace("install", "").replace("uninstall", "").replace("please", "").strip()
        return {"action": action, "app": app}

def execute(command_text):
    print(f"[App Manager] Processing: {command_text}")
    
    parsed = parse_winget_command(command_text)
    action = parsed.get("action", "install")
    app_name = parsed.get("app", "")
    
    if not app_name:
        return "I could not determine which application you want to manage."
        
    print(f"[App Manager] Action: {action.upper()} | App: {app_name}")
    
    # Winget requires specific flags for fully headless operation
    winget_args = [
        "winget", 
        action, 
        app_name, 
        "--silent", 
        "--accept-package-agreements", 
        "--accept-source-agreements"
    ]
    
    try:
        # Run subprocess silently
        # We don't wait for completion synchronously if it takes a long time, but for the sake of the assistant, 
        # we will launch it and let it run, returning a status immediately.
        # However, winget is fast at initiating. Let's run it synchronously to get the output, 
        # or we could thread it so the AI doesn't hang.
        # Since installation takes time, we will spawn a thread and return immediately.
        import threading
        
        def run_winget_thread():
            from core.audio_out import speak
            try:
                result = subprocess.run(winget_args, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                if result.returncode == 0:
                    speak(f"Successfully finished managing {app_name}.")
                else:
                    err_msg = result.stdout + "\n" + result.stderr
                    if "multiple packages found" in err_msg.lower():
                        speak(f"There are multiple packages named {app_name}. Please be more specific.")
                    else:
                        speak(f"Failed to {action} {app_name}. It might require administrator privileges or the package name is incorrect.")
            except Exception as e:
                speak(f"Error executing winget: {str(e)}")
                
        threading.Thread(target=run_winget_thread, daemon=True).start()
        
        return f"I have initiated the silent {action} process for {app_name} in the background. I will notify you when it finishes."
        
    except Exception as e:
        return f"Failed to start package manager: {str(e)}"
