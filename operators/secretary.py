import pyperclip
import os
from google import genai
from google.genai import types

def execute(command_text):
    print("[Secretary Protocol] Reading system clipboard...")
    
    clipboard_content = pyperclip.paste()
    
    if not clipboard_content or not clipboard_content.strip():
        return "Your clipboard is currently empty. There is nothing for me to read."
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "I am offline. Please set your GEMINI_API_KEY to process clipboard text."
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are the "Secretary" of an AI OS Orchestrator. 
    The user has copied some text to their clipboard and is asking you to process it.
    
    User Request: "{command_text}"
    Clipboard Contents:
    ---
    {clipboard_content}
    ---
    
    Analyze the clipboard contents based on the user's request. 
    If they ask for a summary, summarize it. If they ask for a translation, translate it.
    If they just say "read my clipboard", read it out or briefly summarize if it is too long.
    Respond with EXACTLY what you want to say out loud to the user. Keep it conversational but concise.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.3)
        )
        return response.text.strip()
        
    except Exception as e:
        print(f"[Error] The Secretary encountered an issue: {e}")
        return "I encountered a neural error while processing your clipboard."
