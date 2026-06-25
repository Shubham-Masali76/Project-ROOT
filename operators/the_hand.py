import pyautogui
import json
import os
from google import genai
from google.genai import types

def execute(command_text):
    print("[The Hand Protocol] Mapping physical keystrokes...")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "I am offline. Please set your GEMINI_API_KEY."
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are the physical "Hand" of an AI OS Orchestrator. 
    The user wants to physically interact with their keyboard or mouse.
    
    User Request: "{command_text}"
    
    Convert this request into a sequence of GUI automation steps.
    Respond strictly with a JSON ARRAY of objects. Each object must have these keys:
    "action": "type", "press", "hotkey", or "scroll"
    "payload": 
      - If action="type", the exact string to type.
      - If action="press", the exact key name (e.g. "enter", "space", "esc", "win", "tab").
      - If action="hotkey", a comma-separated string of keys (e.g. "ctrl,c" or "alt,tab" or "win,r").
      - If action="scroll", an integer representing scroll clicks (e.g. -500 for down, 500 for up).
      
    Example for 'type hello world and press enter':
    [
      {{"action": "type", "payload": "hello world"}},
      {{"action": "press", "payload": "enter"}}
    ]
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.1)
        )
        
        result_text = response.text.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:-3]
        elif result_text.startswith("```"):
            result_text = result_text[3:-3]
            
        actions = json.loads(result_text)
        
        for act in actions:
            action_type = act.get("action")
            payload = act.get("payload")
            
            if action_type == "type":
                pyautogui.write(str(payload), interval=0.02)
            elif action_type == "press":
                pyautogui.press(str(payload))
            elif action_type == "hotkey":
                keys = [k.strip() for k in str(payload).split(",")]
                pyautogui.hotkey(*keys)
            elif action_type == "scroll":
                pyautogui.scroll(int(payload))
                
        return "I have physically executed those actions."
        
    except Exception as e:
        print(f"[Error] The Hand encountered an issue: {e}")
        return "I could not figure out how to physically execute that command."
