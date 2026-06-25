import pyautogui

def execute(command_text):
    cmd = command_text.lower()
    print(f"[Media Protocol] Processing media command: {command_text}")
    
    if "pause" in cmd or "resume" in cmd:
        pyautogui.press('playpause')
        action = "Paused" if "pause" in cmd else "Resumed"
        return f"{action} the media."
        
    elif "next" in cmd or "skip" in cmd:
        pyautogui.press('nexttrack')
        return "Skipped to the next track."
        
    elif "previous" in cmd or "back" in cmd:
        pyautogui.press('prevtrack')
        return "Playing the previous track."
        
    elif "mute" in cmd or "unmute" in cmd:
        pyautogui.press('volumemute')
        return "Toggled the system mute."
        
    elif "volume up" in cmd or "louder" in cmd:
        # Increase by roughly 10% (5 presses of 2%)
        for _ in range(5):
            pyautogui.press('volumeup')
        return "Volume increased."
        
    elif "volume down" in cmd or "quieter" in cmd:
        # Decrease by roughly 10%
        for _ in range(5):
            pyautogui.press('volumedown')
        return "Volume decreased."
        
    return "I am not exactly sure which media button to press."
