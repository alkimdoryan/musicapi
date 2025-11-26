import requests
from pathlib import Path
from app.services.utils import generate_dummy_audio
import os

def test_analysis_endpoint():
    url = "http://127.0.0.1:8000/analysis/analyze"
    
    # Create dummy audio
    audio_path = Path("test_analysis.wav")
    generate_dummy_audio(audio_path, duration_sec=5)
    
    try:
        with open(audio_path, "rb") as f:
            files = {"file": ("test_analysis.wav", f, "audio/wav")}
            print(f"Sending request to {url}...")
            response = requests.post(url, files=files)
            
        if response.status_code == 200:
            print("Success!")
            print("Response:", response.json())
        else:
            print(f"Failed with status {response.status_code}")
            print("Response:", response.text)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if audio_path.exists():
            os.remove(audio_path)

if __name__ == "__main__":
    test_analysis_endpoint()
