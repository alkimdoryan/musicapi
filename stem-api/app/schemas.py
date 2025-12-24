from typing import List, Optional, Literal, Union, Annotated
from pydantic import BaseModel, Field

# Params Models remain the same
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

# Wrapper Models with Metadata
class BaseEffect(BaseModel):
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    # category and description are defined in subclasses

class CompressorEffect(BaseEffect):
    type: Literal["Compressor"]
    category: Literal["Dinamik İşlem"] = "Dinamik İşlem"
    description: Literal["Sesin dinamik aralığını daraltır."] = "Sesin dinamik aralığını daraltır."
    params: CompressorParams = Field(default_factory=CompressorParams)

class LimiterEffect(BaseEffect):
    type: Literal["Limiter"]
    category: Literal["Dinamik İşlem"] = "Dinamik İşlem"
    description: Literal["Sesin belirlenen eşiği aşmasını engeller."] = "Sesin belirlenen eşiği aşmasını engeller."
    params: LimiterParams = Field(default_factory=LimiterParams)

class GainEffect(BaseEffect):
    type: Literal["Gain"]
    category: Literal["Dinamik İşlem"] = "Dinamik İşlem"
    description: Literal["Ses seviyesini artırır veya azaltır."] = "Ses seviyesini artırır veya azaltır."
    params: GainParams = Field(default_factory=GainParams)

class NoiseGateEffect(BaseEffect):
    type: Literal["NoiseGate"]
    category: Literal["Dinamik İşlem"] = "Dinamik İşlem"
    description: Literal["Belirli eşik altındaki sesleri keser."] = "Belirli eşik altındaki sesleri keser."
    params: NoiseGateParams = Field(default_factory=NoiseGateParams)

class ReverbEffect(BaseEffect):
    type: Literal["Reverb"]
    category: Literal["Zaman ve Mekan"] = "Zaman ve Mekan"
    description: Literal["Yankı ve mekan simülasyonu ekler."] = "Yankı ve mekan simülasyonu ekler."
    params: ReverbParams = Field(default_factory=ReverbParams)

class DelayEffect(BaseEffect):
    type: Literal["Delay"]
    category: Literal["Zaman ve Mekan"] = "Zaman ve Mekan"
    description: Literal["Sesi geciktirerek eko oluşturur."] = "Sesi geciktirerek eko oluşturur."
    params: DelayParams = Field(default_factory=DelayParams)

class ConvolutionEffect(BaseEffect):
    type: Literal["Convolution"]
    category: Literal["Zaman ve Mekan"] = "Zaman ve Mekan"
    description: Literal["IR dosyası ile gerçek mekan akustiği sağlar."] = "IR dosyası ile gerçek mekan akustiği sağlar."
    params: ConvolutionParams

class LowpassFilterEffect(BaseEffect):
    type: Literal["LowpassFilter"]
    category: Literal["Filtreler (EQ)"] = "Filtreler (EQ)"
    description: Literal["Belirlenen frekansın üstünü keser."] = "Belirlenen frekansın üstünü keser."
    params: LowpassFilterParams = Field(default_factory=LowpassFilterParams)

class HighpassFilterEffect(BaseEffect):
    type: Literal["HighpassFilter"]
    category: Literal["Filtreler (EQ)"] = "Filtreler (EQ)"
    description: Literal["Belirlenen frekansın altını keser."] = "Belirlenen frekansın altını keser."
    params: HighpassFilterParams = Field(default_factory=HighpassFilterParams)

class BandpassFilterEffect(BaseEffect):
    type: Literal["BandpassFilter"]
    category: Literal["Filtreler (EQ)"] = "Filtreler (EQ)"
    description: Literal["Belirli bir frekans aralığını geçirir."] = "Belirli bir frekans aralığını geçirir."
    params: BandpassFilterParams = Field(default_factory=BandpassFilterParams)

class PeakFilterEffect(BaseEffect):
    type: Literal["PeakFilter"]
    category: Literal["Filtreler (EQ)"] = "Filtreler (EQ)"
    description: Literal["Belirli frekans bölgesini artırır/azaltır."] = "Belirli frekans bölgesini artırır/azaltır."
    params: PeakFilterParams = Field(default_factory=PeakFilterParams)

class NotchFilterEffect(BaseEffect):
    type: Literal["NotchFilter"]
    category: Literal["Filtreler (EQ)"] = "Filtreler (EQ)"
    description: Literal["Belirli frekansı dar bir şekilde keser."] = "Belirli frekansı dar bir şekilde keser."
    params: NotchFilterParams = Field(default_factory=NotchFilterParams)

class LowShelfFilterEffect(BaseEffect):
    type: Literal["LowShelfFilter"]
    category: Literal["Filtreler (EQ)"] = "Filtreler (EQ)"
    description: Literal["Alçak frekansları raf şeklinde yönetir."] = "Alçak frekansları raf şeklinde yönetir."
    params: LowShelfFilterParams = Field(default_factory=LowShelfFilterParams)

class HighShelfFilterEffect(BaseEffect):
    type: Literal["HighShelfFilter"]
    category: Literal["Filtreler (EQ)"] = "Filtreler (EQ)"
    description: Literal["Yüksek frekansları raf şeklinde yönetir."] = "Yüksek frekansları raf şeklinde yönetir."
    params: HighShelfFilterParams = Field(default_factory=HighShelfFilterParams)

class LadderFilterEffect(BaseEffect):
    type: Literal["LadderFilter"]
    category: Literal["Filtreler (EQ)"] = "Filtreler (EQ)"
    description: Literal["Moog tipi analog filtre."] = "Moog tipi analog filtre."
    params: LadderFilterParams = Field(default_factory=LadderFilterParams)

class ChorusEffect(BaseEffect):
    type: Literal["Chorus"]
    category: Literal["Modülasyon"] = "Modülasyon"
    description: Literal["Sese derinlik ve koro etkisi verir."] = "Sese derinlik ve koro etkisi verir."
    params: ChorusParams = Field(default_factory=ChorusParams)

class PhaserEffect(BaseEffect):
    type: Literal["Phaser"]
    category: Literal["Modülasyon"] = "Modülasyon"
    description: Literal["Faz kaydırmalı dalgalanma yaratır."] = "Faz kaydırmalı dalgalanma yaratır."
    params: PhaserParams = Field(default_factory=PhaserParams)

class DistortionEffect(BaseEffect):
    type: Literal["Distortion"]
    category: Literal["Distorsiyon"] = "Distorsiyon"
    description: Literal["Sesi kirleterek harmonik zenginlik katar."] = "Sesi kirleterek harmonik zenginlik katar."
    params: DistortionParams = Field(default_factory=DistortionParams)

class ClippingEffect(BaseEffect):
    type: Literal["Clipping"]
    category: Literal["Distorsiyon"] = "Distorsiyon"
    description: Literal["Dalga formunu tepeden keserek sert ses yaratır."] = "Dalga formunu tepeden keserek sert ses yaratır."
    params: ClippingParams = Field(default_factory=ClippingParams)

class BitcrushEffect(BaseEffect):
    type: Literal["Bitcrush"]
    category: Literal["Distorsiyon"] = "Distorsiyon"
    description: Literal["Dijital çözünürlüğü düşürerek retro ses verir."] = "Dijital çözünürlüğü düşürerek retro ses verir."
    params: BitcrushParams = Field(default_factory=BitcrushParams)

class PitchShiftEffect(BaseEffect):
    type: Literal["PitchShift"]
    category: Literal["Ses Kalınlığı"] = "Ses Kalınlığı"
    description: Literal["Perdeyi (nota) tempo değişmeden değiştirir."] = "Perdeyi (nota) tempo değişmeden değiştirir."
    params: PitchShiftParams = Field(default_factory=PitchShiftParams)

class PanEffect(BaseEffect):
    type: Literal["Pan"]
    category: Literal["Utility"] = "Utility"
    description: Literal["Sesi sağ/sol kanala yönlendirir."] = "Sesi sağ/sol kanala yönlendirir."
    params: PanParams = Field(default_factory=PanParams)

class InvertEffect(BaseEffect):
    type: Literal["Invert"]
    category: Literal["Utility"] = "Utility"
    description: Literal["Ses dalgasının fazını ters çevirir."] = "Ses dalgasının fazını ters çevirir."
    params: InvertParams = Field(default_factory=InvertParams)

class ResampleEffect(BaseEffect):
    type: Literal["Resample"]
    category: Literal["Utility"] = "Utility"
    description: Literal["Örnekleme hızını çalışma anında değiştirir."] = "Örnekleme hızını çalışma anında değiştirir."
    params: ResampleParams = Field(default_factory=ResampleParams)

# Union Type for the list
EffectItem = Annotated[Union[
    CompressorEffect, LimiterEffect, GainEffect, NoiseGateEffect,
    ReverbEffect, DelayEffect, ConvolutionEffect,
    LowpassFilterEffect, HighpassFilterEffect, BandpassFilterEffect,
    PeakFilterEffect, NotchFilterEffect, LowShelfFilterEffect, HighShelfFilterEffect, LadderFilterEffect,
    ChorusEffect, PhaserEffect, DistortionEffect, ClippingEffect, BitcrushEffect,
    PitchShiftEffect, PanEffect, InvertEffect, ResampleEffect
], Field(discriminator="type")]
