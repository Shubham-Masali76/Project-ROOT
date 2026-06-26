import edge_tts
import asyncio
import pygame
import os
import sys
import time
import numpy as np

from core.state import STATE_DICT, tts_queue, SILENT_MODE

pygame.mixer.init()

def speak(text):
    """Throws text into the Mouth Queue, or prints it silently."""
    if SILENT_MODE:
        if sys.stdout:
            print(f"\n[R.O.O.T. (Silent)]: {text}\n> ", end="")
            sys.stdout.flush()
    else:
        tts_queue.put(text)

def tts_worker():
    """THE MOUTH: Constantly processes the queue and speaks out loud with True Audio Sync."""
    print("[System] R.O.O.T. Mouth Online.")
    while True:
        text = tts_queue.get()
        if text is None: # Poison pill
            break
        if sys.stdout:
            print(f"\n[R.O.O.T.]: {text}\n> ", end="")
            sys.stdout.flush()
            
        STATE_DICT["CURRENT_LOG"] = text
        
        try:
            STATE_DICT["STATE"] = "SPEAKING"
            
            output_file = ".voice_cache.mp3"
            if os.path.exists(output_file):
                os.remove(output_file)
                
            # Generate Audio
            communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural", rate="+20%")
            asyncio.run(communicate.save(output_file))
            
            # 1. Pre-load Audio into Numpy Array for Volume Analysis
            try:
                import pygame.sndarray
                sound = pygame.mixer.Sound(output_file)
                arr = pygame.sndarray.samples(sound)
                exact_sample_rate = pygame.mixer.get_init()[0]
                window = int(0.1 * exact_sample_rate)
            except Exception:
                arr = None
                exact_sample_rate = 24000
                window = 2400

            # 2. Play Audio via Pygame Buffer
            pygame.mixer.music.load(output_file)
            pygame.mixer.music.play()
            
            # 3. Block queue until speaking is finished, updating Mouth
            while pygame.mixer.music.get_busy():
                if arr is not None:
                    pos_ms = pygame.mixer.music.get_pos()
                    if pos_ms >= 0:
                        idx = int((pos_ms / 1000.0) * exact_sample_rate)
                        chunk = arr[max(0, idx - window//2) : min(len(arr), idx + window//2)]
                        if len(chunk) > 0:
                            rms = np.sqrt(np.mean(chunk.astype(float)**2))
                            STATE_DICT["MOUTH_AMPLITUDE"] = min(1.0, rms / 10000.0)
                time.sleep(0.03)
                
            pygame.mixer.music.unload()
            
            # Clean up the cache file immediately so it doesn't clutter the directory
            try:
                time.sleep(0.1) # Give Pygame a moment to fully release the file lock
                os.remove(output_file)
            except Exception:
                pass
                
            STATE_DICT["STATE"] = "IDLE"
            STATE_DICT["MOUTH_AMPLITUDE"] = 0.0
            STATE_DICT["EMOTION"] = "NEUTRAL"
        except Exception as e:
            print(f"\n[Voice Engine Error]: {e}")
            STATE_DICT["STATE"] = "IDLE"
            STATE_DICT["MOUTH_AMPLITUDE"] = 0.0
            STATE_DICT["EMOTION"] = "NEUTRAL"
            
        tts_queue.task_done()
