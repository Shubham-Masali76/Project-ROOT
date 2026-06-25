from plyer import notification
import json
import os
from google import genai
from google.genai import types

def execute(command_text):
    print("[Notifier Protocol] Generating visual alert...")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "I am offline. Please set your GEMINI_API_KEY."
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are the Notifier Node of an AI OS Orchestrator. 
    The user is asking you to set a reminder or notify them of something.
    
    User Request: "{command_text}"
    
    Extract the core message the user wants to be reminded of.
    Respond strictly in JSON format with two keys:
    "title": A short 2-3 word title for the notification.
    "message": The actual reminder text.
    
    Example: {{"title": "Water Reminder", "message": "It is time to drink water!"}}
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
            
        data = json.loads(result_text)
        title = data.get("title", "R.O.O.T. Alert")
        message = data.get("message", "You have a new notification.")
        
        notification.notify(
            title=title,
            message=message,
            app_name='R.O.O.T.',
            timeout=10
        )
        
        return "I have pushed a visual notification to your screen."
        
    except Exception as e:
        print(f"[Error] The Notifier encountered an issue: {e}")
        return "I encountered an error pushing the visual notification."
