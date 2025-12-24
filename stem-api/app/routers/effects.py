from fastapi import APIRouter, UploadFile, File, Depends, Form, Query, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
from app.services.audio_processor import process_audio_chain
from app.schemas import (
    BaseEffect,
    CompressorEffect, CompressorParams,
    LimiterEffect, LimiterParams,
    GainEffect, GainParams,
    NoiseGateEffect, NoiseGateParams,
    ReverbEffect, ReverbParams,
    DelayEffect, DelayParams,
    ConvolutionEffect, ConvolutionParams,
    LowpassFilterEffect, LowpassFilterParams,
    HighpassFilterEffect, HighpassFilterParams,
    BandpassFilterEffect, BandpassFilterParams,
    PeakFilterEffect, PeakFilterParams,
    NotchFilterEffect, NotchFilterParams,
    LowShelfFilterEffect, LowShelfFilterParams,
    HighShelfFilterEffect, HighShelfFilterParams,
    LadderFilterEffect, LadderFilterParams,
    ChorusEffect, ChorusParams,
    PhaserEffect, PhaserParams,
    DistortionEffect, DistortionParams,
    ClippingEffect, ClippingParams,
    BitcrushEffect, BitcrushParams,
    PitchShiftEffect, PitchShiftParams,
    PanEffect, PanParams,
    InvertEffect, InvertParams,
    ResampleEffect, ResampleParams
)

router = APIRouter(
    prefix="/effects",
    tags=["Individual Effects"]
)

# Helper to process single effect
def process_single_effect(file: UploadFile, effect: BaseEffect, start: Optional[float] = None, end: Optional[float] = None):
    # Wrap in list
    effect.start_time = start
    effect.end_time = end
    
    try:
        audio_content = file.file.read()
        result = process_audio_chain(audio_content, [effect])
        return StreamingResponse(
            result, 
            media_type="audio/wav",
            headers={"Content-Disposition": f"attachment; filename=processed_{file.filename}.wav"}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

# --- Dynamic Processing ---

@router.post("/compressor")
def apply_compressor(
    file: UploadFile = File(...),
    params: CompressorParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = CompressorEffect(type="Compressor", params=params)
    return process_single_effect(file, effect, start_time, end_time)

@router.post("/limiter")
def apply_limiter(
    file: UploadFile = File(...),
    params: LimiterParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = LimiterEffect(type="Limiter", params=params)
    return process_single_effect(file, effect, start_time, end_time)

@router.post("/gain")
def apply_gain(
    file: UploadFile = File(...),
    params: GainParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = GainEffect(type="Gain", params=params)
    return process_single_effect(file, effect, start_time, end_time)

@router.post("/noisegate")
def apply_noisegate(
    file: UploadFile = File(...),
    params: NoiseGateParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = NoiseGateEffect(type="NoiseGate", params=params)
    return process_single_effect(file, effect, start_time, end_time)

# --- Time and Space ---

@router.post("/reverb")
def apply_reverb(
    file: UploadFile = File(...),
    params: ReverbParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = ReverbEffect(type="Reverb", params=params)
    return process_single_effect(file, effect, start_time, end_time)

@router.post("/delay")
def apply_delay(
    file: UploadFile = File(...),
    params: DelayParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = DelayEffect(type="Delay", params=params)
    return process_single_effect(file, effect, start_time, end_time)

@router.post("/convolution")
def apply_convolution(
    file: UploadFile = File(...),
    params: ConvolutionParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = ConvolutionEffect(type="Convolution", params=params)
    return process_single_effect(file, effect, start_time, end_time)

# --- Filters ---

@router.post("/lowpass")
def apply_lowpass(
    file: UploadFile = File(...),
    params: LowpassFilterParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = LowpassFilterEffect(type="LowpassFilter", params=params)
    return process_single_effect(file, effect, start_time, end_time)

@router.post("/highpass")
def apply_highpass(
    file: UploadFile = File(...),
    params: HighpassFilterParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = HighpassFilterEffect(type="HighpassFilter", params=params)
    return process_single_effect(file, effect, start_time, end_time)

@router.post("/bandpass")
def apply_bandpass(
    file: UploadFile = File(...),
    params: BandpassFilterParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = BandpassFilterEffect(type="BandpassFilter", params=params)
    return process_single_effect(file, effect, start_time, end_time)

@router.post("/peak")
def apply_peak(
    file: UploadFile = File(...),
    params: PeakFilterParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = PeakFilterEffect(type="PeakFilter", params=params)
    return process_single_effect(file, effect, start_time, end_time)

@router.post("/notch")
def apply_notch(
    file: UploadFile = File(...),
    params: NotchFilterParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = NotchFilterEffect(type="NotchFilter", params=params)
    return process_single_effect(file, effect, start_time, end_time)

@router.post("/lowshelf")
def apply_lowshelf(
    file: UploadFile = File(...),
    params: LowShelfFilterParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = LowShelfFilterEffect(type="LowShelfFilter", params=params)
    return process_single_effect(file, effect, start_time, end_time)

@router.post("/highshelf")
def apply_highshelf(
    file: UploadFile = File(...),
    params: HighShelfFilterParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = HighShelfFilterEffect(type="HighShelfFilter", params=params)
    return process_single_effect(file, effect, start_time, end_time)

@router.post("/ladder")
def apply_ladder(
    file: UploadFile = File(...),
    params: LadderFilterParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = LadderFilterEffect(type="LadderFilter", params=params)
    return process_single_effect(file, effect, start_time, end_time)

# --- Modulation ---

@router.post("/chorus")
def apply_chorus(
    file: UploadFile = File(...),
    params: ChorusParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = ChorusEffect(type="Chorus", params=params)
    return process_single_effect(file, effect, start_time, end_time)

@router.post("/phaser")
def apply_phaser(
    file: UploadFile = File(...),
    params: PhaserParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = PhaserEffect(type="Phaser", params=params)
    return process_single_effect(file, effect, start_time, end_time)

# --- Distortion ---

@router.post("/distortion")
def apply_distortion(
    file: UploadFile = File(...),
    params: DistortionParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = DistortionEffect(type="Distortion", params=params)
    return process_single_effect(file, effect, start_time, end_time)

@router.post("/clipping")
def apply_clipping(
    file: UploadFile = File(...),
    params: ClippingParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = ClippingEffect(type="Clipping", params=params)
    return process_single_effect(file, effect, start_time, end_time)

@router.post("/bitcrush")
def apply_bitcrush(
    file: UploadFile = File(...),
    params: BitcrushParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = BitcrushEffect(type="Bitcrush", params=params)
    return process_single_effect(file, effect, start_time, end_time)

# --- Pitch and Utility ---

@router.post("/pitchshift")
def apply_pitchshift(
    file: UploadFile = File(...),
    params: PitchShiftParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = PitchShiftEffect(type="PitchShift", params=params)
    return process_single_effect(file, effect, start_time, end_time)

@router.post("/pan")
def apply_pan(
    file: UploadFile = File(...),
    params: PanParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = PanEffect(type="Pan", params=params)
    return process_single_effect(file, effect, start_time, end_time)

@router.post("/invert")
def apply_invert(
    file: UploadFile = File(...),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    # No params
    effect = InvertEffect(type="Invert", params=InvertParams())
    return process_single_effect(file, effect, start_time, end_time)

@router.post("/resample")
def apply_resample(
    file: UploadFile = File(...),
    params: ResampleParams = Depends(),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None)
):
    effect = ResampleEffect(type="Resample", params=params)
    return process_single_effect(file, effect, start_time, end_time)
