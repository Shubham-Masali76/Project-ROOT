import re
from google import genai
from google.genai import types
import json

def extract_time_delay(text):
    """Instantly parses natural language time constraints using Regex."""
    match = re.search(r'in (\d+) (second|minute|hour)s?', text)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        if unit == 'second': return amount
        if unit == 'minute': return amount * 60
        if unit == 'hour': return amount * 3600
    return 0

def get_intent(text):
    """Uses Fast Heuristics first, then Ollama JSON mode fallback."""
    text_lower = text.lower()
    
    # 1. FAST HEURISTICS (Zero-Latency, 100% Accuracy)
    if any(w in text_lower for w in ["organize", "sort"]) and "download" in text_lower:
        return "ORGANIZE_DOWNLOADS"
    if any(w in text_lower for w in ["clean", "empty", "recycle bin", "temp"]):
        return "CLEAN_SYSTEM"
    if any(w in text_lower for w in ["message", "discord", "whatsapp", "telegram", "send"]):
        return "MESSENGER"
    if any(w in text_lower for w in ["look at", "click", "vision", "see"]):
        return "VISION_AGENT"
    if any(w in text_lower for w in ["comment", "subscribe"]):
        return "SOCIAL_AGENT"
    if any(w in text_lower for w in ["open", "launch", "start", "play", "close", "kill", "minimize", "maximize"]):
        return "OS_CONTROL"
    if any(w in text_lower for w in ["create", "delete", "read", "update", "file", "folder", "directory", "make"]):
        return "FILE_MANAGER"
    if any(w in text_lower for w in ["weather", "temperature", "time", "date", "who is", "what is", "tell me about"]):
        return "INFORMATION_AGENT"
    if any(w in text_lower for w in ["pause", "resume", "skip track", "next track", "previous", "mute", "unmute", "volume up", "volume down", "louder", "quieter"]):
        return "MEDIA_CONTROL"
    if any(w in text_lower for w in ["diagnostic", "cpu", "ram", "memory", "how is my pc", "system status", "hardware"]):
        return "DIAGNOSTIC_AGENT"
    if any(w in text_lower for w in ["type", "press", "hit", "scroll", "hotkey"]):
        return "GUI_CONTROL"
    if any(w in text_lower for w in ["clipboard", "copied text", "what did i copy", "paste buffer"]):
        return "CLIPBOARD_AGENT"
    if any(w in text_lower for w in ["remind me", "notify me", "alert me", "send a notification"]):
        return "NOTIFIER_AGENT"
        
    print("[System] Fast Heuristics Failed. Querying Gemini Intent Engine...")

    # 2. GEMINI FALLBACK (For complex phrasing)
    prompt = f"""
    Map the user's text to EXACTLY ONE of the following action categories:
    ORGANIZE_DOWNLOADS, CLEAN_SYSTEM, OS_CONTROL, SOCIAL_AGENT, VISION_AGENT, MESSENGER, FILE_MANAGER, INFORMATION_AGENT, MEDIA_CONTROL, DIAGNOSTIC_AGENT, GUI_CONTROL, CLIPBOARD_AGENT, NOTIFIER_AGENT
    
    Examples:
    "open roblox" -> OS_CONTROL
    "close chrome" -> OS_CONTROL
    "clean my pc" -> CLEAN_SYSTEM
    "send a message to mom" -> MESSENGER
    "what is the weather" -> INFORMATION_AGENT
    "pause the music" -> MEDIA_CONTROL
    
    If nothing perfectly matches, return UNKNOWN.   
    Respond with ONLY a valid JSON object containing the "intent" key.
    
    User Text: "{text}"
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
        intent = data.get('intent', '').strip().upper()
        
        valid_intents = ["ORGANIZE_DOWNLOADS", "CLEAN_SYSTEM", "OS_CONTROL", "SOCIAL_AGENT", "VISION_AGENT", "MESSENGER", "FILE_MANAGER", "INFORMATION_AGENT", "MEDIA_CONTROL", "DIAGNOSTIC_AGENT", "GUI_CONTROL", "CLIPBOARD_AGENT", "NOTIFIER_AGENT"]
        for valid in valid_intents:
            if valid in intent:
                return valid
        return "UNKNOWN"
    except Exception as e:
        print(f"[Error] Intent routing failed: {e}")
        return "ERROR"
