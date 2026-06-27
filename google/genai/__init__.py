import os
from groq import Groq
from .types import GenerateContentConfig

class ModelsService:
    def __init__(self, client):
        self.client = client
        
    def generate_content(self, model, contents, config=None):
        import io
        import base64
        
        # 1. Parse contents
        text_content = ""
        image_base64 = None
        audio_bytes = None
        
        if isinstance(contents, str):
            text_content = contents
        elif isinstance(contents, list):
            for item in contents:
                if isinstance(item, str):
                    text_content += "\n" + item
                elif hasattr(item, 'save'): # PIL Image
                    buffered = io.BytesIO()
                    item.save(buffered, format="JPEG")
                    image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                elif hasattr(item, 'data'): # types.Part (audio bytes)
                    audio_bytes = item.data
                    
        # 2. Call Groq
        if audio_bytes:
            # Audio transcription request!
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.wav"
            try:
                transcription = self.client.groq_client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3",
                    response_format="text",
                )
                text_result = transcription.strip()
                if not text_result:
                    text_result = "SILENCE"
                return ResponseMock(text_result)
            except Exception as e:
                print(f"[Groq Audio Error] {e}")
                return ResponseMock("SILENCE")
                
        elif image_base64:
            # Vision request!
            try:
                chat_completion = self.client.groq_client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": text_content or "Analyze this image."},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_base64}",
                                    },
                                },
                            ],
                        }
                    ],
                    temperature=0.0
                )
                text_result = chat_completion.choices[0].message.content
                return ResponseMock(text_result)
            except Exception as e:
                print(f"[Groq Vision Error] {e}")
                return ResponseMock(f"Vision analysis failed: {e}")
                
        else:
            # Text generation request!
            response_format = None
            if config and hasattr(config, 'response_mime_type') and config.response_mime_type == "application/json":
                response_format = {"type": "json_object"}
                
            temperature = 0.0
            if config and hasattr(config, 'temperature') and config.temperature is not None:
                temperature = config.temperature
                
            try:
                chat_completion = self.client.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "user",
                            "content": text_content
                        }
                    ],
                    response_format=response_format,
                    temperature=temperature
                )
                text_result = chat_completion.choices[0].message.content
                return ResponseMock(text_result)
            except Exception as e:
                print(f"[Groq Text Error] {e}")
                return ResponseMock(f"Error: {e}")

class ResponseMock:
    def __init__(self, text):
        self.text = text

class Client:
    def __init__(self, api_key=None):
        key = api_key or os.environ.get("GROQ_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not key:
            raise ValueError("No API key was provided for Groq/Gemini client.")
        self.groq_client = Groq(api_key=key)
        self.models = ModelsService(self)
