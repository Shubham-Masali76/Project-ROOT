import time
import psutil

from core.state import STATE_DICT, execution_queue, GUI_LOCK
from core.intent import get_intent
from core.audio_out import speak
from core.memory import neuro_memory

from operators import organize_downloads
from operators import clean_system
from operators import os_controller
from operators import youtube_bot
from operators import visionary
from operators import messenger
from operators import file_manager
from operators import scholar
from operators import media_controller
from operators import doctor
from operators import the_hand
from operators import secretary
from operators import notifier
from operators import chat_agent

def executor_worker():
    """THE HANDS: Constantly processes the execution queue and routes commands to operators."""
    while True:
        task_text = execution_queue.get()
        STATE_DICT["STATE"] = "THINKING"
        STATE_DICT["CURRENT_LOG"] = f"Orchestrator: Analyzing command '{task_text}'..."
        
        if task_text is None: # Poison pill
            break
            
        # CPU THROTTLE SAFETY SWITCH
        while psutil.cpu_percent(interval=0.5) > 85:
            print("[System] High CPU usage (>85%) detected. Throttling Execution Queue...")
            time.sleep(2)
            
        print(f"\n[Hands] Processing Queue Item: {task_text}")
        STATE_DICT["CURRENT_LOG"] = f"Processing: {task_text}..."
        
        # --- LTM Application (Neuroplasticity) ---
        original_text = task_text
        task_text, modified = neuro_memory.apply_ltm_overrides(task_text)
        if modified:
            STATE_DICT["CURRENT_LOG"] = f"LTM Auto-Corrected: {original_text} -> {task_text}"
            print(f"[Neuroplasticity] Overrode text to: {task_text}")
            time.sleep(1.5) # Let the user see the autonomous correction!
            
        intent = get_intent(task_text)
        STATE_DICT["CURRENT_LOG"] = f"Intent Identified: {intent}"
        print(f"[Hands] Intent Identified: {intent}")
        
        res = "Completed"
        
        if "ORGANIZE_DOWNLOADS" in intent:
            speak("Organizing downloads in the background.")
            res = organize_downloads.execute()
            speak(res)
            
        elif "CLEAN_SYSTEM" in intent:
            speak("Scrubbing system in the background.")
            res = clean_system.execute()
            speak(res)
            
        elif "OS_CONTROL" in intent:
            res = os_controller.execute(task_text)
            speak(res)
            
        elif "SOCIAL_AGENT" in intent:
            with GUI_LOCK:
                speak("Engaging Ghost Protocol.")
                res = youtube_bot.execute(task_text)
                speak(res)
                
        elif "VISION_AGENT" in intent:
            with GUI_LOCK:
                speak("Activating visual cortex.")
                res = visionary.execute(task_text)
                speak(res)
                
        elif "MESSENGER" in intent:
            with GUI_LOCK:
                speak("Opening communications channel.")
                res = messenger.execute(task_text)
                speak(res)
                
        elif "FILE_MANAGER" in intent:
            speak("Accessing file system.")
            res = file_manager.execute(task_text, speak)
            speak(res)
            
        elif "INFORMATION_AGENT" in intent:
            res = scholar.execute(task_text)
            speak(res)
            
        elif "MEDIA_CONTROL" in intent:
            res = media_controller.execute(task_text)
            speak(res)
            
        elif "DIAGNOSTIC_AGENT" in intent:
            res = doctor.execute(task_text)
            speak(res)
            
        elif "GUI_CONTROL" in intent:
            res = the_hand.execute(task_text)
            speak(res)
            
        elif "CLIPBOARD_AGENT" in intent:
            res = secretary.execute(task_text)
            speak(res)
            
        elif "NOTIFIER_AGENT" in intent:
            res = notifier.execute(task_text)
            speak(res)
            
        elif intent == "UNKNOWN":
            res = chat_agent.execute(task_text, STATE_DICT)
            speak(res)
            
        elif intent == "ERROR":
            speak("My local language core seems offline.")
            res = "Error processing language"
            
        else:
            speak("I did not catch that properly.")
            res = "Unrecognized command"
            
        # --- STM Logging (Neuroplasticity Buffer) ---
        neuro_memory.log_interaction(original_text, intent, res)
            
        STATE_DICT["STATE"] = "IDLE"
        execution_queue.task_done()
