import threading
from dotenv import load_dotenv

# MUST LOAD ENV BEFORE ANY OTHER IMPORTS
load_dotenv()

from core.immune_system import install_immune_system
install_immune_system()

from core.state import STATE_DICT
from core.audio_out import tts_worker
from core.executor import executor_worker
from core.keyboard import keyboard_worker
from core.audio_in import listen_loop
from gui.face import start_gui

from core.auto_updater import check_and_update
check_and_update()

if __name__ == "__main__":
    # Start Hand, Mouth, and Keyboard Threads
    threading.Thread(target=tts_worker, daemon=True).start()
    threading.Thread(target=executor_worker, daemon=True).start()
    threading.Thread(target=keyboard_worker, daemon=True).start()
    
    # Run Ear on a background thread
    threading.Thread(target=listen_loop, daemon=True).start()
    
    # Run GUI on Main Thread (Blocks here)
    start_gui(STATE_DICT)
