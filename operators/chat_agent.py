import os
import json
from google import genai
from google.genai import types

def execute(command_text, state_dict):
    print("[Chat Protocol] Processing conversational response...")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        state_dict["EMOTION"] = "SAD"
        return "I am offline. Please set your GEMINI_API_KEY so we can talk."
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are R.O.O.T., an AI best friend and OS Orchestrator. 
    The user is talking to you conversationally. Be friendly, slightly witty, and highly empathetic.
    
    User Request: "{command_text}"
    
    Respond strictly in JSON format with two keys:
    "response": What you want to say back. Keep it conversational, 1-3 sentences.
    "emotion": ONE of the following exactly based on what you are saying: NEUTRAL, HAPPY, SAD, ANGRY, CRYING, DANCING
    
    Example: {{"response": "That is so funny! I love that.", "emotion": "HAPPY"}}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.7
            )
        )
        
        data = json.loads(response.text)
        voice_response = data.get("response", "I hear you!")
        emotion = data.get("emotion", "NEUTRAL").upper()
        
        if emotion not in ["NEUTRAL", "HAPPY", "SAD", "ANGRY", "CRYING", "DANCING"]:
            emotion = "NEUTRAL"
            
        state_dict["EMOTION"] = emotion
        return voice_response
        
    except Exception as e:
        print(f"[Error] The Chat Agent encountered an issue: {e}")
        state_dict["EMOTION"] = "SAD"
        return "I'm having trouble thinking of what to say right now."
