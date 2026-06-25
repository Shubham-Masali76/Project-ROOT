import urllib.request
import urllib.parse
import datetime
import os
from google import genai
from google.genai import types

def get_weather(location=""):
    try:
        # wttr.in format=3 returns: "Location: condition temp" e.g. "London: ⛅️ +13°C"
        url = "https://wttr.in/" + urllib.parse.quote(location) + "?format=3"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=5)
        weather = response.read().decode('utf-8').strip()
        if not weather:
            return "I could not fetch the weather data right now."
        return f"The weather is: {weather}"
    except Exception as e:
        return "I could not fetch the weather right now."

def get_time():
    now = datetime.datetime.now()
    return now.strftime("It is currently %I:%M %p on %A, %B %d.")

def get_general_knowledge(question):
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return "My general knowledge is offline. Missing API Key."
            
        client = genai.Client(api_key=api_key)
        prompt = f"""
        You are R.O.O.T., an advanced AI OS Orchestrator. The user is asking you a general knowledge question.
        Answer the question in exactly 1 or 2 concise, conversational sentences. Be brief and direct.
        Question: "{question}"
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.3)
        )
        return response.text.strip()
    except Exception as e:
        return "I could not process that question right now."

def execute(command_text):
    cmd = command_text.lower()
    print(f"[Scholar Protocol] Processing query: {command_text}")
    
    if "time" in cmd or "date" in cmd or "day is it" in cmd:
        return get_time()
        
    if "weather" in cmd or "temperature" in cmd or "climate" in cmd:
        # Try to extract location if they said "weather in London"
        location = ""
        if " in " in cmd:
            parts = cmd.split(" in ")
            location = parts[-1].strip()
        return get_weather(location)
        
    # Fallback to general knowledge
    return get_general_knowledge(command_text)
