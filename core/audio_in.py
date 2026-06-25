import speech_recognition as sr
import os
import time
import queue
import sys
import re
import json
import vosk
import winsound
import sounddevice as sd
import threading
from google import genai
from google.genai import types

from core.state import STATE_DICT, execution_queue, MIC_ACTIVE
from core.audio_out import speak
from core.intent import extract_time_delay

def listen_loop():
    """THE EAR: Constantly listens for the wake word using Vosk, then transcribes with Gemini."""
    print("\n[System] R.O.O.T. Ear Online. Calibrating Local Wake-Word Engine...")
    
    if not os.path.exists("model"):
        print("[Ear Error] Vosk model not found. Please download it using download_model.py")
        # Gracefully exit the thread instead of throwing a fatal process exit
        return

    model = vosk.Model("model")
    samplerate = 16000
    rec = vosk.KaldiRecognizer(model, samplerate)
    
    dynamic_rec = sr.Recognizer()
    dynamic_rec.energy_threshold = 200
    dynamic_rec.pause_threshold = 1.0
    dynamic_rec.dynamic_energy_threshold = True
    
    q = queue.Queue()
    def callback(indata, frames, time, status):
        if status:
            pass
        q.put(bytes(indata))
        
    STATE_DICT["EMOTION"] = "HAPPY"
    speak("Welcome User. All systems online.")
    time.sleep(2)
    
    import pyaudio
    p = pyaudio.PyAudio()
    
    # Use PyAudio which correctly targets the default Windows microphone
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4000)
    stream.start_stream()
    
    while True:
        if not MIC_ACTIVE:
            time.sleep(1)
            continue
            
        STATE_DICT["STATE"] = "IDLE"
        STATE_DICT["CURRENT_LOG"] = "Waiting for 'root'..."
        wake_word_detected = False
        
        while True:
            if not MIC_ACTIVE:
                time.sleep(1)
                continue
                
            try:
                data = stream.read(4000, exception_on_overflow=False)
                import audioop
                data = audioop.mul(data, 2, 4.0) # Boost microphone gain by 400%
            except IOError:
                continue
                
            if rec.AcceptWaveform(data):
                STATE_DICT["CURRENT_LOG"] = "Ear: Transcribing audio signature..."
                result = json.loads(rec.Result())
                text = result.get("text", "")
                
                if text:
                    STATE_DICT["CURRENT_LOG"] = f"Ear: Heard '{text}'"
                    if "stop" in text.lower() or "shut up" in text.lower():
                        pass
                
                # Broadened Wake-Word dictionary to catch Vosk offline translation errors
                wake_words = ["root", "route", "groot", "fruit", "boot", "hey", "hi", "hello", "truth", "ruth", "robot"]
                
                if any(w in text for w in wake_words) and len(text) > 0:
                    winsound.Beep(1000, 200)
                    wake_word_detected = True
                    break
        
        if wake_word_detected:
            STATE_DICT["STATE"] = "LISTENING"
            STATE_DICT["CURRENT_LOG"] = "Listening for your command..."
            try:
                with sr.Microphone() as source:
                    print("[Ear] Listening for your command... (Will stop when you stop talking)")
                    audio = dynamic_rec.listen(source, timeout=10, phrase_time_limit=30)
                    winsound.Beep(800, 150)
                    
                    wav_bytes = audio.get_wav_data()
                    
                    STATE_DICT["STATE"] = "THINKING"
                    STATE_DICT["CURRENT_LOG"] = "Transcribing via Gemini..."
                    gemini_client = genai.Client()
                    response = gemini_client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[
                            types.Part.from_bytes(data=wav_bytes, mime_type="audio/wav"),
                            "Transcribe exactly what is spoken in this audio. If there is no human speech or it is just background noise, output the exact word 'SILENCE'."
                        ]
                    )
                    transcription = response.text.strip().lower()
                    print(f"[Ear] Transcription: {transcription}")
                    
                    if "silence" in transcription and len(transcription) < 10:
                        print("[Ear] Ignored silence. Returning to sleep.")
                        continue
                    if not transcription:
                        continue
                        
                    command = transcription.strip()
                    
                    if command in ["shutdown", "exit", "quit", "stop listening", "kill"]:
                        print("\n[System] Shutdown command received via voice.")
                        STATE_DICT["EMOTION"] = "SAD"
                        speak("Shutting down all core systems. Goodbye.")
                        time.sleep(4)
                        os._exit(0)
                        
                    delay = extract_time_delay(command)
                    if delay > 0:
                        clean_command = re.sub(r'in \d+ (second|minute|hour)s?', '', command).strip()
                        speak(f"Scheduling that for {delay} seconds from now.")
                        print(f"\n[System] Added to Execution Queue (Delayed {delay}s): {clean_command}\n> ", end="")
                        threading.Timer(delay, execution_queue.put, args=[clean_command]).start()
                    else:
                        execution_queue.put(command)
                        if sys.stdout:
                            print(f"\n[System] Added to Execution Queue: {command}\n> ", end="")
                        
                    if sys.stdout:
                        sys.stdout.flush()
                        
            except sr.WaitTimeoutError:
                print("[Ear] You didn't say anything.")
                continue
            except Exception as e:
                print(f"\n[Error] Auditory Cortex issue: {e}")
                time.sleep(1)
