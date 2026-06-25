import os
import pyautogui
import mss
import json
from google import genai
from PIL import Image

def execute(command_text):
    print("[Visionary Protocol] Capturing screen with mss...")
    
    client = genai.Client()
    
    screenshot_path = "screenshot_temp.png"
    with mss.mss() as sct:
        # Grab the primary monitor
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=screenshot_path)
    
    img = Image.open(screenshot_path)
    width, height = img.size
    
    prompt = f"""
    You are R.O.O.T., an advanced AI OS Orchestrator. You are looking at the user's screen.
    Screen Resolution: {width}x{height}.
    
    The user says: "{command_text}"
    
    If the user is asking a question about the screen (e.g. "what is this error?", "read this to me", "what am I looking at?"), answer the question clearly and concisely.
    If the user is asking you to click on something (e.g. "click the Chrome icon", "close the window"), find the exact center X and Y pixel coordinates of that element.
    
    Respond strictly in JSON format with the following keys:
    "action": either "speak" or "click".
    "response": What you want to say to the user out loud. Keep it conversational but concise. Do not say 'Response:'.
    "x": the x coordinate (only if action is "click", else 0).
    "y": the y coordinate (only if action is "click", else 0).
    
    Example 1: {{"action": "speak", "response": "The error on your screen is a SyntaxError on line 42.", "x": 0, "y": 0}}
    Example 2: {{"action": "click", "response": "Clicking the Chrome icon.", "x": 550, "y": 1040}}
    """
    
    print("[Visionary Protocol] Processing visual data through Gemini...")
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[img, prompt]
        )
        
        # Clean up
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)
            
        result_text = response.text.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:-3]
        elif result_text.startswith("```"):
            result_text = result_text[3:-3]
            
        data = json.loads(result_text)
        action = data.get("action", "speak")
        voice_response = data.get("response", "I have analyzed your screen.")
        
        if action == "click":
            x = data.get("x", 0)
            y = data.get("y", 0)
            if x > 0 and y > 0:
                print(f"[Visionary Protocol] Moving ghost hand to {x}, {y}...")
                pyautogui.moveTo(x, y, duration=0.5)
                pyautogui.click()
                
        return voice_response
        
    except Exception as e:
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)
        return f"My visual cortex encountered an error: {str(e)}"
