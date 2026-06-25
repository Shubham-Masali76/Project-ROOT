import urllib.request
import zipfile
import os

url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
zip_path = "vosk_model.zip"
extract_path = "model"

if os.path.exists(extract_path):
    print("Model already exists.")
else:
    print("Downloading Vosk model (50MB)... This may take a moment.")
    urllib.request.urlretrieve(url, zip_path)

    print("Extracting model...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(".")

    # The zip extracts into a folder named "vosk-model-small-en-us-0.15"
    os.rename("vosk-model-small-en-us-0.15", extract_path)

    # Clean up the zip file
    os.remove(zip_path)

    print("Model successfully downloaded and extracted to 'model/'")
