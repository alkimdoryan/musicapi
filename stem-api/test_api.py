import requests
import time
from pathlib import Path
from app.services.utils import generate_dummy_audio

def test_api():
    # 1. Generate dummy audio
    test_file = Path("test_audio.wav")
    generate_dummy_audio(test_file, duration_sec=2)
    print(f"Generated dummy audio: {test_file}")

    # 2. Define API endpoint
    url = "http://127.0.0.1:8000/stems/extract"

    # 3. Test Demucs (using a mock/stub approach if server not fully ready with models, 
    # but here we assume we want to hit the real endpoint. 
    # Note: Real models take time and might fail if not installed.
    # For this test script, we'll try to hit it and see if we get a valid response structure,
    # even if it fails due to missing model weights (which returns 500).
    
    # We'll test with 'eleven_labs' first as it's a stub and should return 500 (NotImplemented) or 400 quickly.
    # Or 'demucs' if we want to try real processing.
    
    files = {'audio_file': open(test_file, 'rb')}
    data = {
        "separation_model": "ht_demucs"
    }
    
    print(f"Sending request to {url} with model=eleven_labs...")
    try:
        response = requests.post(url, files=files, data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")
        
    # Clean up
    test_file.unlink()

if __name__ == "__main__":
    test_api()
