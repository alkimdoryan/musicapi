import essentia.standard as es
import numpy as np
from typing import Dict, Any

def analyze_audio(audio_path: str) -> Dict[str, Any]:
    """
    Analyzes audio using Essentia to extract BPM, Key, Loudness, and other features.
    
    Args:
        audio_path: Path to the input audio file.
        
    Returns:
        Dictionary containing extracted features.
    """
    # Load audio
    # Mono loader for general feature extraction
    loader = es.MonoLoader(filename=audio_path, sampleRate=44100)
    audio = loader()
    
    features = {}
    
    # 1. Rhythm (BPM)
    # RhythmExtractor2013 is a robust beat tracker
    rhythm_extractor = es.RhythmExtractor2013(method="multifeature")
    bpm, beats, beats_confidence, _, beats_intervals = rhythm_extractor(audio)
    features["bpm"] = int(round(bpm))
    features["beats_count"] = len(beats)
    
    # 2. Tonal (Key, Scale)
    # KeyExtractor extracts key and scale
    key_extractor = es.KeyExtractor()
    key, scale, key_strength = key_extractor(audio)
    features["key"] = key
    features["scale"] = scale
    features["key_strength"] = float(key_strength)
    
    # 3. Dynamics (Loudness)
    # LoudnessEbur128 calculates integrated loudness (LUFS)
    # It requires stereo signal usually, but MonoLoader returns mono.
    # We can use standard Loudness algorithm or re-load as stereo if needed.
    # For simplicity/speed on stems, mono is often fine, but let's check standard Loudness.
    loudness_algo = es.Loudness()
    loudness = loudness_algo(audio)
    features["loudness"] = float(loudness)
    
    # 4. Spectral Features (Danceability, etc.)
    # Danceability is often useful
    danceability_algo = es.Danceability()
    danceability, _ = danceability_algo(audio)
    features["danceability"] = float(danceability)
    
    # Dynamic Complexity
    dynamic_complexity_algo = es.DynamicComplexity()
    dynamic_complexity, _ = dynamic_complexity_algo(audio)
    features["dynamic_complexity"] = float(dynamic_complexity)
    
    return features
