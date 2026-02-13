import numpy as np
import soundfile as sf
import io
import os
import tempfile
import logging
from typing import List, Tuple
from pedalboard import (
    Compressor, Limiter, Gain, NoiseGate,
    Reverb, Delay, Convolution,
    LowpassFilter, HighpassFilter,
    PeakFilter, LowShelfFilter, HighShelfFilter, LadderFilter,
    Chorus, Phaser, Distortion, Clipping, Bitcrush,
    PitchShift
)

from app.schemas import FXCommitJob, Point

logger = logging.getLogger(__name__)

# ── Standard Pedalboard effects ──────────────────────────────────────
EFFECT_MAP = {
    "compressor": Compressor,
    "limiter": Limiter,
    "gain": Gain,
    "noisegate": NoiseGate,
    "reverb": Reverb,
    "delay": Delay,
    "lowpass": LowpassFilter,
    "highpass": HighpassFilter,
    "peak": PeakFilter,
    "notch": PeakFilter,        # Notch = PeakFilter with gain_db=-24
    "lowshelf": LowShelfFilter,
    "highshelf": HighShelfFilter,
    "ladder": LadderFilter,
    "chorus": Chorus,
    "phaser": Phaser,
    "distortion": Distortion,
    "clipping": Clipping,
    "bitcrush": Bitcrush,
    "bitcrusher": Bitcrush,     # alias
    "pitchshift": PitchShift,
}

# Effects that need custom (non-Pedalboard) processing
CUSTOM_EFFECTS = {"bandpass", "panner", "invert", "resample", "convolution"}

# Frontend param names → Pedalboard attribute names (only where they differ)
PARAM_NAME_MAP = {
    "cutoff_hz": "cutoff_frequency_hz",
    "threshold": "threshold_db",
    "ceiling": "threshold_db",
    "frequency": "cutoff_frequency_hz",
    "center_hz": "cutoff_frequency_hz",
    "bits": "bit_depth",
    "wet": "wet_level",
}


def interpolate_value(time: float, points: List[Point]) -> float:
    """Linear interpolation between automation curve points."""
    if not points:
        return 0.0
    if time <= points[0].t:
        return points[0].v
    if time >= points[-1].t:
        return points[-1].v
    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i + 1]
        if p1.t <= time <= p2.t:
            ratio = (time - p1.t) / (p2.t - p1.t)
            return p1.v + ratio * (p2.v - p1.v)
    return points[-1].v


def _prepare_automation_lanes(
    job: FXCommitJob,
) -> List[Tuple[str, List[Point]]]:
    """Parse and sort automation lanes, applying param name remapping."""
    lanes = []
    if not job.automation:
        return lanes
    for lane in job.automation:
        if not lane.curve:
            continue
        param_name = PARAM_NAME_MAP.get(lane.param, lane.param)
        sorted_curve = sorted(lane.curve, key=lambda p: p.t)
        lanes.append((param_name, sorted_curve))
    return lanes


def _remap_static_params(params: dict) -> dict:
    """Remap static param names to Pedalboard-compatible names."""
    mapped = {}
    for k, v in params.items():
        mapped[PARAM_NAME_MAP.get(k, k)] = v
    return mapped


def _block_process(
    data: np.ndarray,
    sample_rate: int,
    effect,
    active_lanes: List[Tuple[str, List[Point]]],
    block_size: int = 1024,
) -> np.ndarray:
    """Block-based processing with per-block automation parameter updates."""
    total_samples = len(data)
    output = np.zeros_like(data)
    cursor = 0
    while cursor < total_samples:
        end = min(cursor + block_size, total_samples)
        current_time = cursor / sample_rate
        for param_name, curve in active_lanes:
            val = interpolate_value(current_time, curve)
            setattr(effect, param_name, val)
        chunk = data[cursor:end]
        output[cursor:end] = effect.process(chunk, sample_rate, reset=(cursor == 0))
        cursor = end
    return output


# ── Custom effect processors ─────────────────────────────────────────

def _process_bandpass(
    data: np.ndarray, sr: int, params: dict, lanes: List[Tuple[str, List[Point]]]
) -> np.ndarray:
    bandwidth = params.get("bandwidth", 1.0)
    center = params.get("cutoff_frequency_hz", 1000.0)
    hp = HighpassFilter(cutoff_frequency_hz=max(20, center / max(0.1, bandwidth)))
    lp = LowpassFilter(cutoff_frequency_hz=min(20000, center * max(0.1, bandwidth)))

    if not lanes:
        out = hp.process(data, sr)
        return lp.process(out, sr)

    block_size = 1024
    total = len(data)
    output = np.zeros_like(data)
    cursor = 0
    while cursor < total:
        end = min(cursor + block_size, total)
        t = cursor / sr
        for pn, curve in lanes:
            if pn == "cutoff_frequency_hz":
                c = interpolate_value(t, curve)
                hp.cutoff_frequency_hz = max(20, c / max(0.1, bandwidth))
                lp.cutoff_frequency_hz = min(20000, c * max(0.1, bandwidth))
        chunk = data[cursor:end]
        processed = hp.process(chunk, sr, reset=(cursor == 0))
        processed = lp.process(processed, sr, reset=(cursor == 0))
        output[cursor:end] = processed
        cursor = end
    return output


def _process_panner(
    data: np.ndarray, sr: int, params: dict, lanes: List[Tuple[str, List[Point]]]
) -> np.ndarray:
    # Ensure stereo
    if data.ndim == 1:
        data = np.column_stack([data, data])

    pan = params.get("pan", 0.0)  # -1 to 1

    if not lanes:
        left_gain = min(1.0, 1.0 - pan) if pan > 0 else 1.0
        right_gain = min(1.0, 1.0 + pan) if pan < 0 else 1.0
        out = np.copy(data)
        out[:, 0] *= left_gain
        out[:, 1] *= right_gain
        return out

    block_size = 1024
    total = len(data)
    output = np.copy(data)
    cursor = 0
    while cursor < total:
        end = min(cursor + block_size, total)
        t = cursor / sr
        for pn, curve in lanes:
            if pn == "pan":
                pan = interpolate_value(t, curve)
        left_gain = min(1.0, 1.0 - pan) if pan > 0 else 1.0
        right_gain = min(1.0, 1.0 + pan) if pan < 0 else 1.0
        output[cursor:end, 0] = data[cursor:end, 0] * left_gain
        output[cursor:end, 1] = data[cursor:end, 1] * right_gain
        cursor = end
    return output


def _process_invert(
    data: np.ndarray, sr: int, params: dict, lanes: List[Tuple[str, List[Point]]]
) -> np.ndarray:
    return data * -1


def _process_resample(
    data: np.ndarray, sr: int, params: dict, lanes: List[Tuple[str, List[Point]]]
) -> tuple:
    import librosa

    target_sr = int(params.get("target_sample_rate", 44100))
    if target_sr == sr:
        return data, sr
    if data.ndim == 1:
        resampled = librosa.resample(data, orig_sr=sr, target_sr=target_sr)
    else:
        channels = []
        for ch in range(data.shape[1]):
            channels.append(librosa.resample(data[:, ch], orig_sr=sr, target_sr=target_sr))
        resampled = np.column_stack(channels)
    return resampled, target_sr


def _process_convolution(
    data: np.ndarray, sr: int, params: dict, lanes: List[Tuple[str, List[Point]]]
) -> np.ndarray:
    mix = params.get("mix", 1.0)

    # Generate a default impulse response (hall-like reverb)
    ir_duration = 2.0
    ir_decay = 2.0
    ir_length = int(sr * ir_duration)
    n_channels = data.shape[1] if data.ndim > 1 else 1
    ir = np.random.RandomState(42).randn(ir_length, max(2, n_channels)).astype(np.float32)
    for i in range(ir_length):
        ir[i] *= (1 - i / ir_length) ** ir_decay

    fd, ir_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    try:
        sf.write(ir_path, ir, sr, format="WAV", subtype="PCM_24")
        conv = Convolution(ir_path, mix)
        if not lanes:
            return conv.process(data, sr)
        return _block_process(data, sr, conv, lanes)
    finally:
        if os.path.exists(ir_path):
            os.unlink(ir_path)


CUSTOM_PROCESSORS = {
    "bandpass": _process_bandpass,
    "panner": _process_panner,
    "invert": _process_invert,
    "resample": _process_resample,
    "convolution": _process_convolution,
}


# ── Main entry point ─────────────────────────────────────────────────

def process_commit_job(audio_bytes: bytes, job: FXCommitJob) -> io.BytesIO:
    # 1. Load audio
    data, sample_rate = sf.read(io.BytesIO(audio_bytes))
    if data.dtype != np.float32:
        data = data.astype(np.float32)

    fx_name = job.fx.lower()
    mapped_params = _remap_static_params(job.static_params)
    active_lanes = _prepare_automation_lanes(job)

    # 2. Custom effects (no direct Pedalboard class)
    if fx_name in CUSTOM_PROCESSORS:
        result = CUSTOM_PROCESSORS[fx_name](data, sample_rate, mapped_params, active_lanes)
        # Resample returns (data, new_sr) tuple
        if isinstance(result, tuple):
            output, output_sr = result
        else:
            output, output_sr = result, sample_rate
    else:
        # 3. Standard Pedalboard effect
        EffectClass = EFFECT_MAP.get(fx_name)
        if not EffectClass:
            raise ValueError(f"Unknown effect: {job.fx}")

        # Filter out params not accepted by the effect constructor
        # (e.g. 'bandwidth' for standard filters)
        valid_params = {}
        try:
            effect_test = EffectClass()
            for k, v in mapped_params.items():
                if hasattr(effect_test, k):
                    valid_params[k] = v
        except TypeError:
            valid_params = mapped_params

        effect = EffectClass(**valid_params)

        if not active_lanes:
            output = effect.process(data, sample_rate)
        else:
            # Validate automation params exist on effect
            validated_lanes = []
            for param_name, curve in active_lanes:
                if hasattr(effect, param_name):
                    validated_lanes.append((param_name, curve))
                else:
                    logger.warning(
                        f"Effect {fx_name} has no attribute '{param_name}', skipping automation lane"
                    )
            output = _block_process(data, sample_rate, effect, validated_lanes)
        output_sr = sample_rate

    # 4. Encode to WAV
    out_buffer = io.BytesIO()
    sf.write(out_buffer, output, output_sr, format="WAV", subtype="PCM_24")
    out_buffer.seek(0)
    return out_buffer
