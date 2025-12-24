
import requests
import io
import time
import numpy as np
import soundfile as sf

def test_time_stretch():
    print("Generating dummy audio (1.0 sec at 44100Hz)...")
    sr = 44100
    duration = 1.0 # 1 second
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    # Simple sine wave
    audio = 0.5 * np.sin(2 * np.pi * 440 * t)
    
    buf = io.BytesIO()
    buf.name = "test_bpm.wav"
    sf.write(buf, audio, sr, format='WAV', subtype='PCM_16')
    buf.seek(0)
    
    print("Testing /api/v1/audio/time-stretch (100 -> 120)")
    # Ratio = 1.2. New duration should be 1.0 / 1.2 = 0.8333 sec.
    
    url = "http://127.0.0.1:8000/api/v1/audio/time-stretch"
    files = {"file": ("test_bpm.wav", buf, "audio/wav")}
    data = {
        "original_bpm": "100",
        "target_bpm": "120",
        "quality_mode": "UNIVERSAL"
    }
    
    try:
        response = requests.post(url, files=files, data=data)
        
        if response.status_code != 200:
            print(f"FAILED: Status {response.status_code}")
            print(response.text)
            exit(1)
            
        print("Success! Checking duration...")
        out_buf = io.BytesIO(response.content)
        data, out_sr = sf.read(out_buf)
        
        # Check duration
        out_duration = len(data) / out_sr
        expected_duration = duration * (100 / 120)
        
        print(f"Input Duration: {duration}s")
        print(f"Expected: ~{expected_duration:.4f}s")
        print(f"Actual: {out_duration:.4f}s")
        
        if abs(out_duration - expected_duration) < 0.05:
            print("Time stretch verified (within tolerance).")
        else:
            print("WARNING: Duration mismatch significantly.")
            
    except Exception as e:
        print(f"Test Execution Failed: {e}")

if __name__ == "__main__":
    test_time_stretch()
