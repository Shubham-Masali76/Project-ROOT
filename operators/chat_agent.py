import os
import json
from groq import Groq

def execute(command_text, state_dict):
    print("[Chat Protocol] Processing conversational response...")
    
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        state_dict["EMOTION"] = "SAD"
        return "I am offline. Please set your GROQ_API_KEY so we can talk."
        
    client = Groq(api_key=api_key)
    
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
        chat_completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        data = json.loads(chat_completion.choices[0].message.content)
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
