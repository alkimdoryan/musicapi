import numpy as np
import scipy.io.wavfile as wav
import os
from pathlib import Path

def generate_dummy_audio(path: Path, duration_sec: int = 5, sample_rate: int = 44100):
    """Generates a simple sine wave audio file for testing."""
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    # Generate a 440 Hz sine wave
    audio = 0.5 * np.sin(2 * np.pi * 440 * t)
    # Convert to 16-bit PCM
    audio_int16 = (audio * 32767).astype(np.int16)
    wav.write(str(path), sample_rate, audio_int16)
    return path
