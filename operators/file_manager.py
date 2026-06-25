import os
import shutil
import json
import ollama
import speech_recognition as sr

LOCAL_MODEL = "llama3.2:1b"
# Lock the sandbox to the Desktop for safety
BASE_DIR = os.path.join(os.path.expanduser("~"), "Desktop")

def ask_confirmation(prompt_text, speak_func):
    """Asks the user for voice confirmation before executing a dangerous action."""
    if speak_func:
        speak_func(prompt_text)
    else:
        print(prompt_text)
        
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("[File Manager] Listening for confirmation (Yes/No)...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            response = recognizer.recognize_google(audio).lower()
            print(f"[Confirmation Heard]: {response}")
            return "yes" in response or "yeah" in response or "sure" in response or "do it" in response
        except Exception:
            return False

def extract_parameters(command_text):
    """Extracts the exact CRUD parameters from the voice command."""
    prompt = f"""
    Extract the file management parameters from this command: "{command_text}"
    Return ONLY a raw JSON object with keys: "action" (create, read, update, delete), "type" (file, folder), "name" (the name of the file/folder), "content" (the text to write/update, if any).
    Do not use markdown blocks.
    Example: {{"action": "create", "type": "folder", "name": "Project Alpha", "content": ""}}
    """
    try:
        response = ollama.chat(model=LOCAL_MODEL, messages=[{'role': 'user', 'content': prompt}])
        result_text = response['message']['content'].strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:-3]
        elif result_text.startswith("```"):
            result_text = result_text[3:-3]
        return json.loads(result_text)
    except Exception:
        return None

def execute(command_text, speak_func=None):
    print("[File Manager] Initiated.")
    params = extract_parameters(command_text)
    if not params:
        return "I could not understand the file operation you want to perform."
        
    action = params.get('action', '').lower()
    item_type = params.get('type', 'file').lower()
    name = params.get('name', '')
    content = params.get('content', '')
    
    if not name:
        return "I could not extract the name of the file or folder."
        
    # Append .txt to files if not explicitly provided
    if item_type == "file" and "." not in name:
        name += ".txt"
        
    # Lock execution to the Desktop sandbox
    target_path = os.path.join(BASE_DIR, name)
    
    if action == "create":
        if item_type == "folder":
            try:
                os.makedirs(target_path, exist_ok=True)
                return f"I have created the folder {name} on your desktop."
            except Exception as e:
                return f"Failed to create folder: {str(e)}"
        else:
            try:
                with open(target_path, 'w') as f:
                    f.write(content)
                return f"I have created the file {name}."
            except Exception as e:
                return f"Failed to create file: {str(e)}"
                
    elif action == "read":
        if not os.path.exists(target_path):
            return f"I could not find {name} on your desktop."
        if item_type == "folder":
            files = os.listdir(target_path)
            if not files:
                return f"The folder {name} is empty."
            return f"The folder {name} contains: {', '.join(files)}"
        else:
            try:
                with open(target_path, 'r') as f:
                    file_content = f.read()
                if not file_content.strip():
                    return f"The file {name} is empty."
                return f"Here is the content of {name}: {file_content}"
            except Exception as e:
                return f"Failed to read file: {str(e)}"
                
    elif action == "update":
        if item_type == "folder":
            return "I cannot update the text content of a folder."
        try:
            with open(target_path, 'a') as f:
                # Add a space or newline before appending
                f.write("\n" + content)
            return f"I have updated the file {name}."
        except Exception as e:
            return f"Failed to update file: {str(e)}"
            
    elif action == "delete":
        if not os.path.exists(target_path):
            return f"I could not find {name} to delete."
            
        # SAFETY SWITCH
        confirmed = ask_confirmation(f"Are you sure you want to permanently delete {name}?", speak_func)
        if not confirmed:
            return "Deletion cancelled."
            
        try:
            if item_type == "folder" or os.path.isdir(target_path):
                shutil.rmtree(target_path)
            else:
                os.remove(target_path)
            return f"I have permanently deleted {name}."
        except Exception as e:
            return f"Failed to delete: {str(e)}"
            
    return "I did not recognize that file operation."
