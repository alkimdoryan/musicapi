import matchering as mg
import os
from pathlib import Path
from app.config import OUTPUT_DIR
import numpy as np
import scipy.io.wavfile as wav

PRESETS_DIR = Path("app/assets/presets")

def ensure_presets():
    """Generates default reference tracks if they don't exist."""
    PRESETS_DIR.mkdir(parents=True, exist_ok=True)
    
    neutral_path = PRESETS_DIR / "neutral.wav"
    if not neutral_path.exists():
        print("Generating neutral reference track...")
        # Generate 10 seconds of Pink Noise as a neutral reference
        sample_rate = 44100
        duration = 10
        samples = int(sample_rate * duration)
        
        # Pink noise generation (approximate)
        uneven = samples % 2
        X = np.random.randn(samples // 2 + 1 + uneven) + 1j * np.random.randn(samples // 2 + 1 + uneven)
        S = np.sqrt(np.arange(len(X)) + 1.)
        y = (np.fft.irfft(X / S)).real
        if uneven:
            y = y[:-1]
        
        # Normalize to -12 dBFS peak roughly
        y = y / np.max(np.abs(y)) * 0.25
        
        wav.write(str(neutral_path), sample_rate, (y * 32767).astype(np.int16))

def get_preset_path(preset_name: str) -> Path:
    """Returns the path to a preset reference track."""
    ensure_presets()
    preset_path = PRESETS_DIR / f"{preset_name}.wav"
    if not preset_path.exists():
        # Fallback to neutral if preset not found
        return PRESETS_DIR / "neutral.wav"
    return preset_path

def process_audio(target_path: str, reference_path: str = None, preset: str = None) -> str:
    """
    Masters the target audio using Matchering.
    
    Args:
        target_path: Path to the target audio file.
        reference_path: Path to the reference audio file (optional).
        preset: Name of the preset to use if reference_path is not provided.
        
    Returns:
        Path to the mastered audio file.
    """
    ensure_presets()
    
    if reference_path is None:
        if preset:
            reference_path = str(get_preset_path(preset))
        else:
            reference_path = str(get_preset_path("neutral"))
            
    # Prepare output path
    target_filename = Path(target_path).stem
    output_dir = OUTPUT_DIR / "mastering"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{target_filename}_mastered.wav"
    
    # Run Matchering
    # mg.process(target, reference, results)
    mg.process(
        target=target_path,
        reference=reference_path,
        results=[
            mg.pcm24(str(output_path))
        ]
    )
    
    return str(output_path)
