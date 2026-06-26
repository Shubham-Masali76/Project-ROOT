import os
from groq import Groq

def chat(model, messages, **kwargs):
    # Retrieve the API key from environment
    key = os.environ.get("GROQ_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("No API key was provided for local Ollama mock.")
        
    client = Groq(api_key=key)
    
    # Translate messages to Groq format
    groq_messages = []
    for msg in messages:
        groq_messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        })
        
    # Check if the prompt asks for JSON
    response_format = None
    last_content = groq_messages[-1]["content"].lower() if groq_messages else ""
    if "json" in last_content:
        response_format = {"type": "json_object"}
        
    try:
        chat_completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=groq_messages,
            response_format=response_format,
            temperature=0.0
        )
        text_result = chat_completion.choices[0].message.content
        
        # Return a dictionary that mirrors Ollama's structure
        return {
            "message": {
                "content": text_result
            }
        }
    except Exception as e:
        print(f"[Ollama Mock Error] {e}")
        # Return a fallback JSON or text depending on the prompt
        if response_format:
            return {
                "message": {
                    "content": "{}"
                }
            }
        return {
            "message": {
                "content": "Error calling Groq: " + str(e)
            }
        }
