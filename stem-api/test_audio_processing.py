
import io
import json
import numpy as np
from fastapi.testclient import TestClient
from app.main import app
from pedalboard.io import AudioFile

client = TestClient(app)

def test_process_audio():
    print("Generating dummy audio...")
    # 1. Generate Dummy Audio Use Pedalboard
    sr = 44100
    duration = 2.0
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    # Sine wave 440Hz, amplitude 0.5
    audio = 0.5 * np.sin(2 * np.pi * 440 * t)
    # Stereo
    audio = np.stack([audio, audio])
    
    # Save to bytes
    buf = io.BytesIO()
    buf.name = "test.wav"
    with AudioFile(buf, 'w', sr, 2) as f:
        f.write(audio)
    buf.seek(0)
    
    # 2. Define Effects
    effects = [
        {
            "type": "Gain",
            "params": {"gain_db": 6.0} # +6dB = 2x amplitude -> should become 1.0
        },
        {
            "type": "Reverb",
            "params": {"room_size": 0.8, "wet_level": 0.5},
            "start_time": 0.5,
            "end_time": 1.5
        }
    ]
    
    print("Sending request to /process-audio...")
    # 3. Request
    response = client.post(
        "/process-audio",
        files={"file": ("test.wav", buf, "audio/wav")},
        data={"effects": json.dumps(effects)}
    )
    
    # 4. Verify
    if response.status_code != 200:
        print(f"Failed: {response.text}")
        exit(1)
        
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
    
    print("Response received. Verifying audio content...")
    # Check output audio properties
    out_buf = io.BytesIO(response.content)
    with AudioFile(out_buf) as f:
        out_audio = f.read(f.frames)
        print(f"Output Audio Shape: {out_audio.shape}, SR: {f.samplerate}")
        
        assert f.samplerate == sr
        assert out_audio.shape[1] > 0
        
        # Check if gain applied
        # Input max ~0.5. Output max should be around 1.0 due to Gain(6dB) which is x2.
        # Note: Reverb adds energy too.
        peak = np.max(np.abs(out_audio))
        print(f"Output Peak Amplitude: {peak}")
        
        assert peak > 0.6, "Gain was not applied effectively"
    
    print("Test Passed!")

if __name__ == "__main__":
    test_process_audio()
