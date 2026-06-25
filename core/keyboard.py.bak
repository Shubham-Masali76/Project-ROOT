import time
import os
import sys
import threading
import re

import core.state
from core.state import execution_queue, STATE_DICT
from core.audio_out import speak
from core.intent import extract_time_delay

HELP_TEXT = """
================================================
          R.O.O.T. SYSTEM TERMINAL
================================================
Available Terminal Commands:
  /silent   - Disables the AI's spoken voice. R.O.O.T. will only communicate via text.
  /voice    - Re-enables the AI's spoken voice (Text-to-Speech).
  /mic off  - Disables the microphone. R.O.O.T. will stop listening to your room.
  /mic on   - Enables the microphone so you can issue voice commands.
  /help     - Displays this detailed list of available commands.
  /exit     - Safely shuts down the AI and all background processes.

Hidden UI Controls:
  - Double-Click Face : Shrinks the window to hide the terminal.
  - Right-Click Face  : Opens a menu to Pin/Unpin the AI from the top of the screen.
  - Drag Bottom Right : Click the (◢) icon to resize the terminal window.
================================================
Type a command below or type '/mic on' to speak...
"""

def keyboard_worker():
    """THE KEYBOARD: Allows the user to type commands directly if they don't want to speak."""
    time.sleep(2) # Give the system time to print boot messages
    print(HELP_TEXT)
    while True:
        try:
            command = input("\n> ")
            if not command.strip():
                continue
                
            if command == "/silent":
                core.state.SILENT_MODE = True
                print("[System] Stealth mode engaged. TTS disabled.")
            elif command == "/voice":
                core.state.SILENT_MODE = False
                print("[System] Voice mode engaged. TTS enabled.")
            elif command == "/mic off":
                core.state.MIC_ACTIVE = False
                print("[System] Microphone muted. The Ear is offline.")
            elif command == "/mic on":
                core.state.MIC_ACTIVE = True
                print("[System] Microphone unmuted. The Ear is online.")
            elif command == "/help":
                print(HELP_TEXT)
            elif command in ["/exit", "exit", "shutdown", "quit"]:
                print("[System] Shutting down core processes. Goodbye.")
                STATE_DICT["EMOTION"] = "SAD"
                speak("Shutting down all core systems. Goodbye.")
                time.sleep(4)
                os._exit(0) # Force kill to terminate all blocking threads instantly
            else:
                delay = extract_time_delay(command)
                if delay > 0:
                    clean_command = re.sub(r'in \d+ (second|minute|hour)s?', '', command).strip()
                    speak(f"Scheduling that for {delay} seconds from now.")
                    print(f"\n[System] Added to Execution Queue (Delayed {delay}s): {clean_command}\n> ", end="")
                    threading.Timer(delay, execution_queue.put, args=[clean_command]).start()
                else:
                    execution_queue.put(command)
        except (EOFError, RuntimeError):
            # If there is no terminal attached (e.g. running in background or via pythonw),
            # the keyboard worker cleanly exits without crashing the system.
            break
