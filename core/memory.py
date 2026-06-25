import json
import os
import threading
import time
from google import genai
from google.genai import types

MEMORY_FILE = "memory_ltm.json"

class TriMemorySystem:
    def __init__(self):
        self.stm = [] # Short-Term Memory (The Buffer)
        self.ltm = self.load_ltm() # Long-Term Memory (Stable Knowledge)
        # Permanent Memory (PM) is represented by the hardcoded base heuristics
        
        # Start the background consolidation thread (simulating Hippocampal replay)
        self.consolidation_thread = threading.Thread(target=self._consolidation_loop, daemon=True)
        self.consolidation_thread.start()

    def load_ltm(self):
        """Loads consolidated memory from disk."""
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"aliases": {}, "app_paths": {}}

    def save_ltm(self):
        """Saves consolidated memory to disk."""
        with open(MEMORY_FILE, 'w') as f:
            json.dump(self.ltm, f, indent=4)

    def log_interaction(self, user_command, intent, outcome):
        """Logs an event into Short-Term Memory (STM)."""
        self.stm.append({
            "command": user_command,
            "intent": intent,
            "outcome": outcome,
            "timestamp": time.time()
        })
        # Keep STM small (last 5 interactions) to act as a fast-buffer
        if len(self.stm) > 5:
            self.stm.pop(0)

    def apply_ltm_overrides(self, command):
        """Applies consolidated Long-Term Memory patterns to incoming raw commands."""
        words = command.lower().split()
        modified = False
        for i, w in enumerate(words):
            if w in self.ltm.get("aliases", {}):
                words[i] = self.ltm["aliases"][w]
                modified = True
        return " ".join(words), modified

    def learn_app_path(self, target, path):
        """Structurally remembers where an app is located on the hard drive."""
        if "app_paths" not in self.ltm:
            self.ltm["app_paths"] = {}
            
        if self.ltm["app_paths"].get(target) != path:
            self.ltm["app_paths"][target] = path
            self.save_ltm()
            print(f"\n[Neuroplasticity] Structural Memory updated: {target} -> {path}")

    def _consolidation_loop(self):
        """Background thread that continuously analyzes STM for plasticity events."""
        client = genai.Client()
        last_stm_length = 0
        
        while True:
            time.sleep(20) # Run consolidation check every 20 seconds
            
            # Only consolidate if there's new data in the STM
            if len(self.stm) >= 2 and len(self.stm) != last_stm_length:
                last_stm_length = len(self.stm)
                self._analyze_stm_for_plasticity(client)

    def _analyze_stm_for_plasticity(self, client):
        """Uses LLM to detect user corrections in the STM buffer and extracts LTM rules."""
        history = ""
        for item in self.stm[-3:]: # Look at the last 3 interactions
            history += f"User said: '{item['command']}'\nAI Result: {item['outcome']}\n\n"
            
        prompt = f"""
        You are the Neuroplasticity Consolidator of an AI system. 
        Analyze the following short-term memory log. Look for instances where the AI clearly misunderstood an acronym, abbreviation, or word, and the user immediately corrected it in the next command.
        
        Memory Log:
        {history}
        
        If you detect a correction, extract a persistent mapping (alias) so the AI never makes the mistake again.
        Example: If user says "open yt" and then "no open youtube", the alias is {{"yt": "youtube"}}.
        
        Output ONLY a valid JSON object mapping the incorrect word to the correct word: {{"alias": {{"bad_word": "correct_word"}}}}
        If no correction or new alias is detected, output EXACTLY: {{"alias": {{}}}}
        """
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0,
                )
            )
            data = json.loads(response.text)
            new_aliases = data.get("alias", {})
            
            if new_aliases:
                updated = False
                for bad, good in new_aliases.items():
                    # Only add if it's new to prevent rewriting unchanged memory
                    if bad not in self.ltm["aliases"] or self.ltm["aliases"][bad] != good:
                        self.ltm["aliases"][bad] = good
                        updated = True
                
                if updated:
                    self.save_ltm()
                    print(f"\n[Neuroplasticity] LTM Updated! Consolidated new aliases: {new_aliases}")
                    
        except Exception as e:
            pass # Silent fail for background consolidation

# Global singleton
neuro_memory = TriMemorySystem()
