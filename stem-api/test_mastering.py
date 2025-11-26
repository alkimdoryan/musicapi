import requests
from pathlib import Path
from app.services.utils import generate_dummy_audio
import os

def test_mastering_endpoint():
    url = "http://127.0.0.1:8000/mastering/process"
    
    # Create dummy target audio
    target_path = Path("test_target.wav")
    generate_dummy_audio(target_path, duration_sec=5)
    
    # Test 1: Preset (Reference-Free)
    print("\n--- Test 1: Preset (Reference-Free) ---")
    try:
        with open(target_path, "rb") as f:
            files = {"target": ("test_target.wav", f, "audio/wav")}
            data = {"preset": "neutral"}
            print(f"Sending request to {url} with preset='neutral'...")
            response = requests.post(url, files=files, data=data)
            
        if response.status_code == 200:
            print("Success!")
            print("Response:", response.json())
        else:
            print(f"Failed with status {response.status_code}")
            print("Response:", response.text)
            
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Reference-Based
    print("\n--- Test 2: Reference-Based ---")
    ref_path = Path("test_reference.wav")
    generate_dummy_audio(ref_path, duration_sec=5) # Using same dummy as ref for simplicity
    
    try:
        with open(target_path, "rb") as f_target, open(ref_path, "rb") as f_ref:
            files = {
                "target": ("test_target.wav", f_target, "audio/wav"),
                "reference": ("test_reference.wav", f_ref, "audio/wav")
            }
            print(f"Sending request to {url} with custom reference...")
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
        if target_path.exists():
            os.remove(target_path)
        if ref_path.exists():
            os.remove(ref_path)

if __name__ == "__main__":
    test_mastering_endpoint()
