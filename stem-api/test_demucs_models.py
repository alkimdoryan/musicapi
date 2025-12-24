import requests
import time
from pathlib import Path
from app.services.utils import generate_dummy_audio
import os

def test_demucs_models():
    url = "http://127.0.0.1:8000/stems/extract"
    
    # Create dummy audio
    audio_path = Path("test_demucs.wav")
    generate_dummy_audio(audio_path, duration_sec=5)
    
    models = ["ht_demucs", "ht_demucs_ft"]
    
    try:
        for model in models:
            print(f"\n--- Testing Model: {model} ---")
            start_time = time.time()
            
            with open(audio_path, "rb") as f:
                files = {"audio_file": ("test_demucs.wav", f, "audio/wav")}
                data = {"separation_model": model}
                
                print(f"Sending request...")
                response = requests.post(url, files=files, data=data)
                
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"Success!")
                print(f"Processing Time (Client-side): {duration:.2f}s")
                print(f"Processing Time (Server-side): {result.get('processing_time'):.2f}s")
                print(f"Stems: {list(result.get('stems').keys())}")
            else:
                print(f"Failed with status {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if audio_path.exists():
            os.remove(audio_path)

if __name__ == "__main__":
    test_demucs_models()
