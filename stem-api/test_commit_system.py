import requests
import json
import soundfile as sf
import numpy as np

# Create dummy audio
sr = 44100
duration = 2.0
t = np.linspace(0, duration, int(sr*duration), dtype=np.float32)
audio = 0.5 * np.sin(2 * np.pi * 440 * t)
sf.write("test_commit_input.wav", audio, sr)

# Define Job
job = {
    "fx": "lowpass",
    "range": { "start": 0.0, "end": 2.0 },
    "static_params": {
        "cutoff_hz": 20000.0 # Start open
    },
    "automation": [
        {
            "param": "cutoff_hz",
            "curve": [
                { "t": 0.0, "v": 1000.0 },
                { "t": 1.0, "v": 200.0 }, # Sweep down
                { "t": 2.0, "v": 2000.0 } # Sweep up
            ]
        }
    ]
}

print("Sending Commit Job to 8070...")
with open("test_commit_input.wav", "rb") as f:
    files = {"file": f}
    data = {"job_json": json.dumps(job)}
    
    response = requests.post("http://127.0.0.1:8070/commit/process", files=files, data=data)

if response.status_code == 200:
    print("SUCCESS! Received WAV.")
    with open("test_commit_output.wav", "wb") as f:
        f.write(response.content)
    print("Saved to test_commit_output.wav")
else:
    print("FAILED:", response.text)
