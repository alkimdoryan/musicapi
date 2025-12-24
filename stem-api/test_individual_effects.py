
import io
import numpy as np
import requests
from pedalboard.io import AudioFile

def test_individual_endpoint():
    print("Generating dummy audio...")
    sr = 44100
    duration = 2.0
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    audio = 0.5 * np.sin(2 * np.pi * 440 * t)
    audio = np.stack([audio, audio])
    
    buf = io.BytesIO()
    buf.name = "test.wav"
    with AudioFile(buf, 'w', sr, 2) as f:
        f.write(audio)
    buf.seek(0)
    
    # Test Gain Endpoint
    print("\nTesting POST /effects/gain...")
    files = {"file": ("test.wav", buf, "audio/wav")}
    # Params as Query parameters (default behavior of Depends with Pydantic)
    params = {"gain_db": 10.0}
    
    # Note: re-opening buf or seeking for retry? 
    # requests.post reads the file. We need to reset if we reuse.
    # Actually let's just make a new buffer or seek.
    buf.seek(0)
    
    url = "http://127.0.0.1:8000/effects/gain"
    response = requests.post(url, files={"file": ("test.wav", buf, "audio/wav")}, params=params)
    
    if response.status_code != 200:
        print(f"FAILED: {response.text}")
        exit(1)
        
    print("Success! Checking gain application...")
    # Check amplitude
    out_buf = io.BytesIO(response.content)
    with AudioFile(out_buf) as f:
        out_audio = f.read(f.frames)
        peak = np.max(np.abs(out_audio))
        print(f"Input Peak: 0.5, Output Peak: {peak}")
        if peak < 0.6:
            print("WARNING: Gain might not have been applied.")
        else:
            print("Gain verified.")

    # Test Reverb
    print("\nTesting POST /effects/reverb...")
    buf.seek(0)
    url = "http://127.0.0.1:8000/effects/reverb"
    params = {"room_size": 0.9, "wet_level": 0.5}
    response = requests.post(url, files={"file": ("test.wav", buf, "audio/wav")}, params=params)
    
    if response.status_code != 200:
        print(f"FAILED: {response.text}")
        exit(1)
    print("Reverb Success!")

if __name__ == "__main__":
    test_individual_endpoint()
