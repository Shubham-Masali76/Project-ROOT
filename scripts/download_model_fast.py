import urllib.request
import zipfile
import os

url = "https://github.com/rhasspy/rhasspy-asr-vosk-hermes/releases/download/v0.1.0/vosk-model-small-en-us-0.15.zip"
zip_path = "vosk_model.zip"
extract_path = "model"

# Clean up any partial download first
if os.path.exists(zip_path):
    try:
        os.remove(zip_path)
    except Exception:
        pass

if os.path.exists(extract_path):
    print("Model already exists.")
else:
    print("Downloading Vosk model from GitHub Mirror (50MB)...")
    try:
        # Request with User-Agent to prevent blockages
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
            
        print("Extracting model...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
            
        # The zip extracts into a folder named "vosk-model-small-en-us-0.15"
        if os.path.exists("vosk-model-small-en-us-0.15"):
            os.rename("vosk-model-small-en-us-0.15", extract_path)
            print("Model successfully downloaded and extracted to 'model/'")
        else:
            # Search for the directory in case of naming mismatch
            found = False
            for f in os.listdir("."):
                if "vosk-model-small" in f and os.path.isdir(f):
                    os.rename(f, extract_path)
                    print(f"Renamed {f} to 'model/'")
                    found = True
                    break
            if not found:
                raise Exception("Extracted model folder not found.")
                
        os.remove(zip_path)
    except Exception as e:
        print(f"GitHub Mirror download failed: {e}")
        print("Falling back to original URL...")
        slow_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
        try:
            urllib.request.urlretrieve(slow_url, zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(".")
            os.rename("vosk-model-small-en-us-0.15", extract_path)
            os.remove(zip_path)
            print("Model successfully downloaded from original URL.")
        except Exception as ex:
            print(f"Fallback also failed: {ex}")
