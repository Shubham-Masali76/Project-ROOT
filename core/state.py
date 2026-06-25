import queue
import threading

STATE_DICT = {
    "STATE": "IDLE",
    "CURRENT_LOG": "R.O.O.T. Core Initialized.",
    "MOUTH_AMPLITUDE": 0.0,
    "EMOTION": "NEUTRAL"
}

# Thread-safe queues for async communication
tts_queue = queue.Queue()
execution_queue = queue.Queue()
audio_queue = queue.Queue()

# Locks
GUI_LOCK = threading.Lock()

# Configuration Flags
SILENT_MODE = False
MIC_ACTIVE = True
