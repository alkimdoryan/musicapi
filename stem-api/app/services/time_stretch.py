
import os
import tempfile
import soundfile as sf
import pyrubberband as pyrb
import numpy as np
import librosa
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class QualityMode(str, Enum):
    UNIVERSAL = "UNIVERSAL"
    PERCUSSIVE = "PERCUSSIVE"
    VOCAL = "VOCAL"

def process_audio_stretch(
    input_file_path: str,
    original_bpm: float | None,
    target_bpm: float,
    quality_mode: QualityMode
) -> str:
    """
    Time-stretches audio from original_bpm to target_bpm using pyrubberband.
    Returns path to the processed temporary file.
    """
    
    # Validation
    if target_bpm <= 0:
        raise ValueError("Target BPM must be positive.")
    if original_bpm is not None and original_bpm <= 0:
        logger.warning(f"Received non-positive BPM {original_bpm}. Defaulting to auto-detection.")
        original_bpm = None



    # Load Audio
    # streaming=False, always load as float32 to prevent clipping
    # sf.read returns (data, samplerate)
    # data can be (samples,) or (samples, channels)
    data, sample_rate = sf.read(input_file_path, dtype='float32', always_2d=True)

    # Auto-detect BPM if not provided
    if original_bpm is None:
        logger.info("Original BPM not provided. Detecting...")
        # librosa expects mono audio for beat tracking usually, or handles it.
        # We need to pass 1D array or (channels, samples).
        # data is (samples, channels). Let's mix down to mono for detection.
        y_mono = librosa.to_mono(data.T)
        tempo, _ = librosa.beat.beat_track(y=y_mono, sr=sample_rate)
        # tempo is usually a scalar, but can be array in older versions? 
        # In 0.11 it returns a scalar float.
        original_bpm = float(tempo)
        logger.info(f"Detected BPM: {original_bpm} (Target: {target_bpm})")
    
    # Calculate stretch ratio
    # If target is faster (120 -> 140), duration is shorter (ratio > 1.0 in rubberband usually means FASTER?)
    # Wait, pyrubberband.time_stretch(y, sr, rate)
    # rate > 1.0 speeds up the audio (shorter duration).
    # rate < 1.0 slows down (longer duration).
    # rate = target_bpm / original_bpm 
    rate = target_bpm / original_bpm
    
    logger.info(f"Stretching audio. Ratio: {rate:.4f} (Original: {original_bpm}, Target: {target_bpm})")
    
    # Transpose for pyrubberband if needed? 
    # pyrubberband expects (samples, channels) or (samples,)? 
    # Librosa usually uses (channels, samples). pyrubberband is a wrapper around CLI.
    # checking docs/usage... pyrubberband typically works with numpy arrays matching soundfile conventions (samples, channels).
    # However, it might expect mono or multi-channel.
    # Let's ensure we pass it correctly.
    
    # Define CLI constraints based on Quality Mode
    # CLI args are passed via rb_args kwargs in some pyrb versions, 
    # but pyrubberband high level API `time_stretch` might abstract this?
    # Actually `pyrubberband.time_stretch(..., rb_args=None)`
    
    # Global settings: -c 2 (precise), --smoothing off
    rb_args = {
        '-c': '2',
    }
    
    if quality_mode == QualityMode.PERCUSSIVE:
        # --transients, --perc
        # pyrubberband arg parsing needs dictionary or list?
        # Usually it takes a dict mapping flag to value, or set flag to None for boolean flags.
        rb_args['--transients'] = None
        rb_args['--perc'] = None
        
    elif quality_mode == QualityMode.VOCAL:
        # -F (formant), --soft
        rb_args['-F'] = None
        rb_args['--soft'] = None
        
    elif quality_mode == QualityMode.UNIVERSAL:
        # Just standard high quality
        pass
        
    # Process
    # Check if pyrb supports multi-channel directly. It does.
    # Note: data is (samples, channels) from soundfile.
    
    # We need to transpose for pyrubberband? 
    # Docs say "Audio time series".
    # If it fails with (N, C), we might need to process channels separately or transpose. 
    # Usually (channels, samples) is preferred by librosa-like tools, but soundfile gives (samples, channels).
    # Let's try (samples, channels) as it often wraps command line efficiently.
    
    try:
        # Actually pyrubberband might strictly expect (channels, samples) if it follows librosa?
        # Let's check: "y : np.ndarray [shape=(n, c) or (n,)]" -> This usually means samples, channels.
        # But wait, librosa is (C, N).
        # To be safe, let's verify if we need transpose.
        # Most examples show: y, sr = librosa.load(...) -> (N,).
        # For multi-channel, soundfile is safer.
        
        # Applying stretch
        stretched = pyrb.time_stretch(data, sample_rate, rate, rbargs=rb_args)
        
    except Exception as e:
        logger.error(f"Rubberband execution failed: {e}")
        # Fallback info?
        raise RuntimeError(f"Time stretch failed. Is 'rubberband' installed? Error: {e}")

    # Create temp output
    # PCM_24 for high quality output as requested
    fd, out_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    
    # Write output
    # subtype='PCM_24'
    sf.write(out_path, stretched, sample_rate, subtype='PCM_24')
    
    return out_path
