
import os
import tempfile
import subprocess
import shutil
import soundfile as sf
import librosa
import logging
from typing import Optional

logger = logging.getLogger(__name__)

RUBBERBAND_BIN = shutil.which("rubberband") or "rubberband"


def _detect_bpm(input_file_path: str) -> float:
    """Auto-detect BPM using librosa."""
    data, sample_rate = sf.read(input_file_path, dtype='float32', always_2d=True)
    y_mono = librosa.to_mono(data.T)
    tempo, _ = librosa.beat.beat_track(y=y_mono, sr=sample_rate)
    return float(tempo)


def stretch_r2(input_file_path: str, rate: float) -> str:
    """
    R2 engine — fast, multi-threaded.
    -c 2 + --threads for maximum speed.
    """
    fd, out_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    args = [RUBBERBAND_BIN, '-q', '--threads', '-c', '2', '-T', str(rate), input_file_path, out_path]

    try:
        subprocess.check_call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        if os.path.exists(out_path):
            os.unlink(out_path)
        raise RuntimeError(f"Rubberband R2 failed: {e}")

    return out_path


def stretch_r3(input_file_path: str, rate: float) -> str:
    """
    R3 (finer) engine — highest quality time-stretch.
    Single-threaded but produces the best results.
    """
    fd, out_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    args = [RUBBERBAND_BIN, '-q', '--fine', '-T', str(rate), input_file_path, out_path]

    try:
        subprocess.check_call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        if os.path.exists(out_path):
            os.unlink(out_path)
        raise RuntimeError(f"Rubberband R3 failed: {e}")

    return out_path
