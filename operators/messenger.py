import pyautogui
import pyperclip
import time
import json
import webbrowser
import ollama

LOCAL_MODEL = "llama3.2:1b"

def steal_url():
    """Uses the ghost hand to copy the URL from the active browser."""
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.2)
    pyautogui.press('esc')
    time.sleep(0.2)
    return pyperclip.paste()

def extract_parameters(command_text):
    """Uses the local brain to extract contact name and platform from voice."""
    prompt = f"""
    Extract the contact name and the platform from this voice command: "{command_text}"
    Return ONLY a raw JSON object with keys "contact" and "platform".
    If platform is not mentioned, assume "whatsapp".
    Do not use markdown blocks.
    Example: {{"contact": "mom", "platform": "whatsapp"}}
    """
    try:
        response = ollama.chat(model=LOCAL_MODEL, messages=[{'role': 'user', 'content': prompt}])
        result_text = response['message']['content'].strip()
        
        # Clean markdown if present
        if result_text.startswith("```json"):
            result_text = result_text[7:-3]
        elif result_text.startswith("```"):
            result_text = result_text[3:-3]
            
        data = json.loads(result_text)
        return data.get('contact', '').lower(), data.get('platform', 'whatsapp').lower()
    except Exception:
        return None, None

def execute(command_text):
    print("[Omni-Messenger] Initiated. Stealing media context...")
    
    url = steal_url()
    if not url.startswith("http"):
        return "I could not find a valid link on your screen to share."
        
    print("[Omni-Messenger] Brain analyzing routing intent...")
    contact, platform = extract_parameters(command_text)
    
    if not contact:
        return "I could not figure out who you want to send this to."
        
    print(f"[Omni-Messenger] Routing to '{contact}' on '{platform}'...")
    
    # ROUTING
    if "discord" in platform:
        webbrowser.open("https://discord.com/channels/@me")
        print("Waiting for Discord Web to load...")
        time.sleep(8)
        pyautogui.hotkey('ctrl', 'k')
        time.sleep(1)
        pyautogui.write(contact, interval=0.05)
        time.sleep(1.5)
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.write(url)
        time.sleep(0.5)
        pyautogui.press('enter')
        return f"I have shared the link with {contact} on Discord."
        
    elif "telegram" in platform:
        print("[Omni-Messenger] Routing to Telegram Web...")
        # Telegram Web A supports direct username routing via URL
        webbrowser.open(f"https://web.telegram.org/a/#?tgaddr=tg%3A%2F%2Fresolve%3Fdomain%3D{contact}")
        print("Waiting for Telegram Web to load...")
        time.sleep(10) # Wait for sync
        
        # The message input box is auto-focused when the chat opens
        pyautogui.write(url)
        time.sleep(0.5)
        pyautogui.press('enter')
        return f"I have shared the link with {contact} on Telegram."
        
    elif "instagram" in platform:
        return "Instagram Web requires Visionary Protocol. Please use Visionary Protocol."
        
    else:
        # Default to WhatsApp Web (Zero Config)
        webbrowser.open("https://web.whatsapp.com")
        print("Waiting for WhatsApp Web to load...")
        # WhatsApp Web takes a significant amount of time to load the QR code or sync
        time.sleep(12) 
        
        # Press Ctrl+Alt+/ to focus the universal search bar
        pyautogui.hotkey('ctrl', 'alt', '/')
        time.sleep(1)
        pyautogui.write(contact, interval=0.05)
        time.sleep(1.5)
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.write(url)
        time.sleep(0.5)
        pyautogui.press('enter')
        
        return f"I have shared the link with {contact} on WhatsApp."
