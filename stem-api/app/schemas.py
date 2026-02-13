from typing import List, Optional, Literal, Union, Annotated, Dict, Any
from pydantic import BaseModel, Field

# --- Existing Params Models (CompressorParams, etc.) ---
# (Keeping them as they are useful for the 'static_params' validation if needed, 
#  but for the Commit System, 'static_params' is a Dict matching these)

class CompressorParams(BaseModel):
    threshold_db: float = -20.0
    ratio: float = 4.0
    attack_ms: float = 1.0
    release_ms: float = 100.0

class LimiterParams(BaseModel):
    threshold_db: float = -1.0
    release_ms: float = 100.0

class GainParams(BaseModel):
    gain_db: float = 0.0

class NoiseGateParams(BaseModel):
    threshold_db: float = -100.0
    ratio: float = 10.0
    attack_ms: float = 1.0
    release_ms: float = 100.0

class ReverbParams(BaseModel):
    room_size: float = 0.5
    damping: float = 0.5
    wet_level: float = 0.33
    dry_level: float = 0.4
    width: float = 1.0

class DelayParams(BaseModel):
    delay_seconds: float = 0.5
    feedback: float = 0.0
    mix: float = 0.5

class ConvolutionParams(BaseModel):
    impulse_response_filename: str
    mix: float = 1.0

class LowpassFilterParams(BaseModel):
    cutoff_hz: float = 20000.0

class HighpassFilterParams(BaseModel):
    cutoff_hz: float = 20.0

class BandpassFilterParams(BaseModel):
    cutoff_hz: float = 440.0
    q: float = 0.707

class PeakFilterParams(BaseModel):
    cutoff_hz: float = 440.0
    gain_db: float = 0.0
    q: float = 0.707

class NotchFilterParams(BaseModel):
    cutoff_hz: float = 440.0
    q: float = 0.707

class LowShelfFilterParams(BaseModel):
    cutoff_hz: float = 440.0
    gain_db: float = 0.0
    q: float = 0.707

class HighShelfFilterParams(BaseModel):
    cutoff_hz: float = 440.0
    gain_db: float = 0.0
    q: float = 0.707

class LadderFilterParams(BaseModel):
    mode: Literal["LPF12", "LPF24", "HPF12", "HPF24", "BPF12", "BPF24"] = "LPF12"
    cutoff_hz: float = 200.0
    resonance: float = 0.0
    drive: float = 1.0

class ChorusParams(BaseModel):
    rate_hz: float = 1.0
    depth: float = 0.25
    centre_delay_ms: float = 7.0
    feedback: float = 0.0
    mix: float = 0.5

class PhaserParams(BaseModel):
    rate_hz: float = 1.0
    depth: float = 0.5
    centre_frequency_hz: float = 1300.0
    feedback: float = 0.0
    mix: float = 0.5

class DistortionParams(BaseModel):
    drive_db: float = 20.0

class ClippingParams(BaseModel):
    threshold_db: float = -6.0

class BitcrushParams(BaseModel):
    bit_depth: float = 8.0

class PitchShiftParams(BaseModel):
    semitones: float = 0.0

class PanParams(BaseModel):
    pan: float = 0.0

class InvertParams(BaseModel):
    pass

class ResampleParams(BaseModel):
    target_sample_rate: int = 44100

# Wrapper Models with Metadata (Existing)
class BaseEffect(BaseModel):
    start_time: Optional[float] = None
    end_time: Optional[float] = None

class CompressorEffect(BaseEffect):
    type: Literal["Compressor"]
    params: CompressorParams = Field(default_factory=CompressorParams)

class LimiterEffect(BaseEffect):
    type: Literal["Limiter"]
    params: LimiterParams = Field(default_factory=LimiterParams)

class GainEffect(BaseEffect):
    type: Literal["Gain"]
    params: GainParams = Field(default_factory=GainParams)

class NoiseGateEffect(BaseEffect):
    type: Literal["NoiseGate"]
    params: NoiseGateParams = Field(default_factory=NoiseGateParams)

class ReverbEffect(BaseEffect):
    type: Literal["Reverb"]
    params: ReverbParams = Field(default_factory=ReverbParams)

class DelayEffect(BaseEffect):
    type: Literal["Delay"]
    params: DelayParams = Field(default_factory=DelayParams)

class ConvolutionEffect(BaseEffect):
    type: Literal["Convolution"]
    params: ConvolutionParams

class LowpassFilterEffect(BaseEffect):
    type: Literal["LowpassFilter"]
    params: LowpassFilterParams = Field(default_factory=LowpassFilterParams)

class HighpassFilterEffect(BaseEffect):
    type: Literal["HighpassFilter"]
    params: HighpassFilterParams = Field(default_factory=HighpassFilterParams)

class BandpassFilterEffect(BaseEffect):
    type: Literal["BandpassFilter"]
    params: BandpassFilterParams = Field(default_factory=BandpassFilterParams)

class PeakFilterEffect(BaseEffect):
    type: Literal["PeakFilter"]
    params: PeakFilterParams = Field(default_factory=PeakFilterParams)

class NotchFilterEffect(BaseEffect):
    type: Literal["NotchFilter"]
    params: NotchFilterParams = Field(default_factory=NotchFilterParams)

class LowShelfFilterEffect(BaseEffect):
    type: Literal["LowShelfFilter"]
    params: LowShelfFilterParams = Field(default_factory=LowShelfFilterParams)

class HighShelfFilterEffect(BaseEffect):
    type: Literal["HighShelfFilter"]
    params: HighShelfFilterParams = Field(default_factory=HighShelfFilterParams)

class LadderFilterEffect(BaseEffect):
    type: Literal["LadderFilter"]
    params: LadderFilterParams = Field(default_factory=LadderFilterParams)

class ChorusEffect(BaseEffect):
    type: Literal["Chorus"]
    params: ChorusParams = Field(default_factory=ChorusParams)

class PhaserEffect(BaseEffect):
    type: Literal["Phaser"]
    params: PhaserParams = Field(default_factory=PhaserParams)

class DistortionEffect(BaseEffect):
    type: Literal["Distortion"]
    params: DistortionParams = Field(default_factory=DistortionParams)

class ClippingEffect(BaseEffect):
    type: Literal["Clipping"]
    params: ClippingParams = Field(default_factory=ClippingParams)

class BitcrushEffect(BaseEffect):
    type: Literal["Bitcrush"]
    params: BitcrushParams = Field(default_factory=BitcrushParams)

class PitchShiftEffect(BaseEffect):
    type: Literal["PitchShift"]
    params: PitchShiftParams = Field(default_factory=PitchShiftParams)

class PanEffect(BaseEffect):
    type: Literal["Pan"]
    params: PanParams = Field(default_factory=PanParams)

class InvertEffect(BaseEffect):
    type: Literal["Invert"]
    params: InvertParams = Field(default_factory=InvertParams)

class ResampleEffect(BaseEffect):
    type: Literal["Resample"]
    params: ResampleParams = Field(default_factory=ResampleParams)

EffectItem = Annotated[Union[
    CompressorEffect, LimiterEffect, GainEffect, NoiseGateEffect,
    ReverbEffect, DelayEffect, ConvolutionEffect,
    LowpassFilterEffect, HighpassFilterEffect, BandpassFilterEffect,
    PeakFilterEffect, NotchFilterEffect, LowShelfFilterEffect, HighShelfFilterEffect, LadderFilterEffect,
    ChorusEffect, PhaserEffect, DistortionEffect, ClippingEffect, BitcrushEffect,
    PitchShiftEffect, PanEffect, InvertEffect, ResampleEffect
], Field(discriminator="type")]


# --- NEW: FX Commit System Models ---

class Point(BaseModel):
    t: float = Field(..., description="Time in seconds")
    v: float = Field(..., description="Value at that time")

class AutomationLane(BaseModel):
    param: str = Field(..., description="Name of the parameter to automate, e.g. 'cutoff_hz'")
    curve: List[Point] = Field(..., description="List of automation points")

class FXRange(BaseModel):
    start: float = Field(0.0, description="Start time in seconds")
    end: Optional[float] = Field(None, description="End time in seconds (None = end of file)")

class FXCommitJob(BaseModel):
    fx: str = Field(..., description="The effect type name, e.g. 'LowpassFilter' or 'lowpass'")
    range: FXRange = Field(default_factory=FXRange)
    static_params: Dict[str, Any] = Field(default_factory=dict, description="Static parameter values")
    automation: List[AutomationLane] = Field(default_factory=list, description="List of automation curves (Primary + Optional Secondary)")

