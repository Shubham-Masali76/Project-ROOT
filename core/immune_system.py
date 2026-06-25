import sys
import traceback
import os
import time
import json
import shutil
import threading
from google import genai
from google.genai import types

def diagnose_and_repair(exc_type, exc_value, exc_traceback):
    from core.state import STATE_DICT
    from core.audio_out import speak
    
    # Ignore KeyboardInterrupt (User manually stopping the program)
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(f"\n[Immune System] FATAL ERROR CAUGHT:\n{tb_str}")
    
    try:
        STATE_DICT["EMOTION"] = "SAD"
        STATE_DICT["STATE"] = "THINKING"
        STATE_DICT["CURRENT_LOG"] = "CRITICAL ERROR. Immune System engaging... [System damage detected]"
        speak("Core damage detected. Engaging immune system self repair.")
        time.sleep(1)
        
        STATE_DICT["CURRENT_LOG"] = "Extracting Python traceback... [Finding the exact location of the bug]"
    except Exception:
        pass # If GUI or speech engine itself crashed, just continue repairing silently
    
    # Extract the file path that caused the crash
    target_file = None
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    for frame in reversed(traceback.extract_tb(exc_traceback)):
        if frame.filename.startswith(project_root):
            target_file = frame.filename
            break
            
    if not target_file:
        print("[Immune System] Error did not originate from core project files. Cannot repair.")
        return
        
    print(f"[Immune System] Fault identified in {target_file}. Requesting AI genetic patch...")
    
    # --- SAFE MODE: Prevent Infinite Death Loops ---
    crash_log_file = os.path.join(project_root, "crash_log.json")
    crash_data = {}
    if os.path.exists(crash_log_file):
        try:
            with open(crash_log_file, "r") as f:
                crash_data = json.load(f)
        except Exception: pass
        
    error_signature = f"{target_file}:{exc_type.__name__}"
    
    if crash_data.get(error_signature, 0) >= 2:
        print("[Immune System] This exact fault has crashed twice. Reverting to backup!")
        backup_file = target_file + ".bak"
        if os.path.exists(backup_file):
            shutil.copy(backup_file, target_file)
            print(f"[Immune System] Restored {backup_file}. Restarting...")
            crash_data[error_signature] = 0 # Reset count
            with open(crash_log_file, "w") as f: json.dump(crash_data, f)
            time.sleep(2)
            os.execv(sys.executable, [sys.executable] + sys.argv)
        return
        
    crash_data[error_signature] = crash_data.get(error_signature, 0) + 1
    with open(crash_log_file, "w") as f: json.dump(crash_data, f)

    # --- AUTO-REPAIR ---
    # 1. Create Backup
    backup_file = target_file + ".bak"
    shutil.copy(target_file, backup_file)
    print(f"[Immune System] Created backup at {backup_file}")
    
    # 2. Read Broken File
    with open(target_file, "r", encoding="utf-8") as f:
        broken_code = f.read()
        
    STATE_DICT["CURRENT_LOG"] = "Transmitting traceback to Gemini LLM... [Asking Neural Network for a code fix]"
        
    # 3. Query LLM for the Patch
    client = genai.Client()
    prompt = f"""
    You are the Auto-Healing Immune System of an advanced AI called R.O.O.T.
    A fatal exception occurred in the following Python file.
    
    Traceback:
    {tb_str}
    
    Original Code in {target_file}:
    ```python
    {broken_code}
    ```
    
    Fix the bug in the code. You MUST return the ENTIRE completely rewritten python file. 
    Do not use placeholders like '# rest of the code here'. I will literally overwrite the file with your exact output.
    Return ONLY valid python code inside a single ```python code block.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        
        STATE_DICT["CURRENT_LOG"] = "Patch received. Overwriting source code... [Applying the fix to system files]"
        
        result = response.text
        if "```python" in result:
            result = result.split("```python")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].split("```")[0].strip()
            
        # 4. Overwrite File
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(result)
            
        print("[Immune System] Code patched successfully. Restarting the organism...")
        try:
            STATE_DICT["CURRENT_LOG"] = "Genetic patch applied. Rebooting..."
            STATE_DICT["CURRENT_LOG"] = "Self-repair complete. Forcing hot-restart... [Rebooting to activate repairs]"
            speak("Repair complete. Restarting systems.")
        except Exception: pass
        
        time.sleep(3) # Give TTS time to speak
        os.execv(sys.executable, [sys.executable] + sys.argv)
        
    except Exception as e:
        STATE_DICT["CURRENT_LOG"] = f"Immune System AI query failed: {e}"
        print(f"[Immune System] Failed to generate a patch: {e}")

def handle_thread_exception(args):
    """Catches exceptions thrown in background threads."""
    diagnose_and_repair(args.exc_type, args.exc_value, args.exc_traceback)

def install_immune_system():
    """Hooks the auto-healing function into the global python interpreter."""
    sys.excepthook = diagnose_and_repair
    threading.excepthook = handle_thread_exception
    print("[System] Digital Immune System is active and watching for faults.")
