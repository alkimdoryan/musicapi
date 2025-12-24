import requests
import numpy as np
import soundfile as sf
import io

def generate_click_track(bpm=120, duration_sec=5.0, sr=22050):
    # Generates a simple click track
    t = np.linspace(0, duration_sec, int(duration_sec * sr), False)
    # 120 BPM = 2 beats per second = every 0.5s
    interval = 60.0 / bpm
    
    # Create clicks
    audio = np.zeros_like(t)
    click_len = int(0.01 * sr)
    
    beat_samples = int(interval * sr)
    for i in range(0, len(t), beat_samples):
        if i + click_len < len(t):
            audio[i:i+click_len] = 0.8
            
    return audio, sr

def test_autobpm():
    print("Generating click track at ~120 BPM...")
    audio, sr = generate_click_track(bpm=120.0, duration_sec=4.0)
    
    buf = io.BytesIO()
    sf.write(buf, audio, sr, format='WAV')
    buf.seek(0)
    
    url = "http://localhost:8000/api/v1/audio/time-stretch"
    
    # Send WITH original_bpm = 0 (simulating swagger/client default)
    data = {
        "original_bpm": 0,
        "target_bpm": 150,
        "quality_mode": "UNIVERSAL"
    }
    files = {
        "file": ("click_120.wav", buf, "audio/wav")
    }
    
    print("Sending request (target=150, original unspecified)...")
    res = requests.post(url, data=data, files=files)
    
    if res.status_code == 200:
        print("Success! Response 200 OK.")
        print(f"Content-Length: {len(res.content)}")
    else:
        print(f"First attempt failed: {res.status_code}")
        print(res.text)
        
        # Retry with null explicitly? No, parameter omitted is best test.
        # Check if form handling requires explicit None? 
        # In requests, omitting key implies None if backend defaults to None.

if __name__ == "__main__":
    test_autobpm()
