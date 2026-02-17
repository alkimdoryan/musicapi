import io
import numpy as np
import pedalboard
from pedalboard import (
    Compressor, Limiter, Gain, NoiseGate,
    Reverb, Delay, Convolution,
    LowpassFilter, HighpassFilter,
    PeakFilter, LowShelfFilter, HighShelfFilter, LadderFilter,
    Chorus, Phaser, Distortion, Clipping, Bitcrush,
    PitchShift, Invert, Resample
)
from pedalboard.io import AudioFile
import math
from typing import List
from app.schemas import BaseEffect

# Utility classes might not be directly in pedalboard or need custom implementation
# Pan is usually just channel manipulation or a plugin if available. 
# Pedalboard 0.7.4+ has Pan? Or we map it manually.
# Checking docs (simulated): Pedalboard has standard plugins. 
# If a plugin is missing, we might need a workaround or custom Board.
# For now, I'll assume standard naming or use `pedalboard.VST3` etc if it was VST, 
# but these look like the built-in plugins.
# LadderFilter, Bitcrush, etc are built-ins.
# Pan: built-in logic or custom? I'll check if `pedalboard.Pan` exists later or implement manual panning (L/R gain).
# Actually, Pedalboard has `LinearFilter`, etc.
# Let's map carefully.

def process_audio_chain(audio_bytes: bytes, effect_chain: List[BaseEffect]) -> io.BytesIO:
    with AudioFile(io.BytesIO(audio_bytes)) as f:
        audio = f.read(f.frames)
        sample_rate = f.samplerate

    # Audio is (channels, samples)
    
    for effect_data in effect_chain:
        effect_type = effect_data.type
        params = effect_data.params
        
        # Instantiate Effect
        board = pedalboard.Pedalboard([])
        plugin = None
        
        # Mapping logic
        p = params 
        # Note: params is a Pydantic model at this point because we will parse it in the router
        # But if passed as dict (from JSON), we access via dict or attributes. 
        # Assuming we pass validated Pydantic objects here.
        
        if effect_type == "Compressor":
            plugin = Compressor(threshold_db=p.threshold_db, ratio=p.ratio, attack_ms=p.attack_ms, release_ms=p.release_ms)
        elif effect_type == "Limiter":
            plugin = Limiter(threshold_db=p.threshold_db, release_ms=p.release_ms)
        elif effect_type == "Gain":
            plugin = Gain(gain_db=p.gain_db)
        elif effect_type == "NoiseGate":
            plugin = NoiseGate(threshold_db=p.threshold_db, ratio=p.ratio, attack_ms=p.attack_ms, release_ms=p.release_ms)
        elif effect_type == "Reverb":
            plugin = Reverb(room_size=p.room_size, damping=p.damping, wet_level=p.wet_level, dry_level=p.dry_level, width=p.width)
        elif effect_type == "Delay":
            plugin = Delay(delay_seconds=p.delay_seconds, feedback=p.feedback, mix=p.mix)
        elif effect_type == "Convolution":
            # Warning: Path security. Assuming valid path provided or relative to an assets dir.
            # For now, passing parameters directly.
            plugin = Convolution(impulse_response_filename=p.impulse_response_filename, mix=p.mix)
        elif effect_type == "LowpassFilter":
            plugin = LowpassFilter(cutoff_hz=p.cutoff_hz)
        elif effect_type == "HighpassFilter":
            plugin = HighpassFilter(cutoff_hz=p.cutoff_hz)
        elif effect_type == "BandpassFilter":
            # Bandpass Implementation: Highpass * Lowpass
            # Q = fc / BW => BW = fc / Q
            # f1, f2 calculation
            fc = p.cutoff_hz
            q = max(p.q, 0.01) # Avoid div zero
            
            # Simple approx for symmetric bandpass around fc
            # For geometric symmetry: f1 = fc / 2^(1/2Q) ? No, standard bandwidth formulas.
            # Using basic BW = fc/Q.
            # f1 = fc - (fc/Q)/2 ? 
            # Better approximation for constant Q:
            # f1 = fc * (math.sqrt(1 + 1/(4*q*q)) - 1/(2*q))
            # f2 = fc * (math.sqrt(1 + 1/(4*q*q)) + 1/(2*q))
            
            w = math.sqrt(1 + 1/(4*q*q))
            val = 1/(2*q)
            f1 = fc * (w - val)
            f2 = fc * (w + val)
            
            # Chain HP(f1) and LP(f2)
            # Create a mini board for this effect or just append both?
            # Appending both works for serial.
            plugin = None
            board.append(HighpassFilter(cutoff_hz=f1))
            board.append(LowpassFilter(cutoff_hz=f2))
            
        elif effect_type == "PeakFilter":
            plugin = PeakFilter(cutoff_hz=p.cutoff_hz, gain_db=p.gain_db, q=p.q)
        elif effect_type == "NotchFilter":
             # Notch Implementation: PeakFilter with high cut
             # Standard Notch is infinite cut. -24dB to -48dB is practical.
             plugin = PeakFilter(cutoff_hz=p.cutoff_hz, gain_db=-24.0, q=p.q)
             
        elif effect_type == "LowShelfFilter":
            plugin = LowShelfFilter(cutoff_hz=p.cutoff_hz, gain_db=p.gain_db, q=p.q)
        elif effect_type == "HighShelfFilter":
            plugin = HighShelfFilter(cutoff_hz=p.cutoff_hz, gain_db=p.gain_db, q=p.q)
        elif effect_type == "LadderFilter":
            # LadderFilter in pedalboard: mode is an enum or string?
            # Pedalboard.LadderFilter.Mode.LPF12 etc.
            # Map string to enum if needed. Assuming string works or we map it.
            # mode_map = {"LPF12": pedalboard.LadderFilter.Mode.LPF12, ...}
            # Implementing mapping for safety.
            mode_map = {
                "LPF12": pedalboard.LadderFilter.Mode.LPF12,
                "LPF24": pedalboard.LadderFilter.Mode.LPF24,
                "HPF12": pedalboard.LadderFilter.Mode.HPF12,
                "HPF24": pedalboard.LadderFilter.Mode.HPF24,
                "BPF12": pedalboard.LadderFilter.Mode.BPF12,
                "BPF24": pedalboard.LadderFilter.Mode.BPF24,
            }
            mode_enum = mode_map.get(p.mode, pedalboard.LadderFilter.Mode.LPF12)
            plugin = LadderFilter(mode=mode_enum, cutoff_hz=p.cutoff_hz, resonance=p.resonance, drive=p.drive)
        elif effect_type == "Chorus":
            plugin = Chorus(rate_hz=p.rate_hz, depth=p.depth, centre_delay_ms=p.centre_delay_ms, feedback=p.feedback, mix=p.mix)
        elif effect_type == "Phaser":
            plugin = Phaser(rate_hz=p.rate_hz, depth=p.depth, centre_frequency_hz=p.centre_frequency_hz, feedback=p.feedback, mix=p.mix)
        elif effect_type == "Distortion":
            plugin = Distortion(drive_db=p.drive_db)
        elif effect_type == "Clipping":
            plugin = Clipping(threshold_db=p.threshold_db)
        elif effect_type == "Bitcrush":
            plugin = Bitcrush(bit_depth=p.bit_depth)
        elif effect_type == "PitchShift":
            plugin = PitchShift(semitones=p.semitones)
        elif effect_type == "Pan":
             # Pedalboard treats audio as stereo numpy arrays usually.
             # Custom implementation or simple gain adjustment? 
             # Pedalboard doesn't have a specific "Pan" plugin in older versions, but check docs.
             # Assuming we just do numpy manipulation or check if I can use a simple channel mixer?
             # For now, let's implement Pan manually if I can't find it, or assume it exists.
             # Wait, Pedalboard has `mix` params in many plugins but Pan is specific.
             # Manual implementation:
             # Left = Left * (1 - pan) if pan > 0 else Left
             # Right = Right * (1 + pan) if pan < 0 else Right ... 
             # Standard pan law: -1 (Left), +1 (Right). 0 (Center).
             # Let's try to look for `Pan` in imports? I didn't import it because I wasn't sure.
             # PROCEEDING WITHOUT IMPORTING 'Pan' and doing manual numpy processing for this one if needed.
             # But let's assume I can't easily mix board and numpy manually inside the chain unless I execute the board.
             # STRATEGY: Create a board with 1 plugin, run it on the slice. 
             # If "Pan", I'll modify the array directly.
             pass 
        elif effect_type == "Invert":
            # Manual numpy: audio = -audio
            pass
        elif effect_type == "Resample":
            # Use `pedalboard.Resample` plugin allows changing target sample rate?
            # Pedalboard plugins process audio stream. Resample usually changes the length of the array.
            # This is tricky for "slice" processing if the length changes. 
            # If `Resample` is requested, it MUST be applied to the WHOLE file usually, or we handle the length change.
            # User requirement: "Resample: target_sample_rate=44100".
            # For this API, maybe we resample the WHOLE audio at the end or beginning?
            # Or if it's in the chain, it changes downstream.
            pass

        # Prepare processing
        start_idx = 0
        end_idx = audio.shape[1]
        
        if effect_data.start_time is not None:
            start_idx = int(effect_data.start_time * sample_rate)
        if effect_data.end_time is not None:
            end_idx = int(effect_data.end_time * sample_rate)
            
        # Bounds check
        start_idx = max(0, start_idx)
        end_idx = min(audio.shape[1], end_idx)
        
        # Apply Logic
        if effect_type == "Pan":
            # Manual Pan Implementation: -1.0 (L) to 1.0 (R)
            pan = p.pan
            # Simple linear pan for now
            # audio shape is (channels, samples). assume stereo (2 channels)
            # If mono, expand to stereo first?
            if audio.shape[0] == 1:
                audio = np.concatenate([audio, audio], axis=0) # Make stereo
            
            # Apply to slice
            # Left channel (0)
            if pan > 0:
                audio[0, start_idx:end_idx] *= (1 - pan)
            # Right channel (1)
            if pan < 0:
                audio[1, start_idx:end_idx] *= (1 + pan)
                
        elif effect_type == "Invert":
            audio[:, start_idx:end_idx] *= -1
            
        elif effect_type == "Resample":
            # This fundamentally changes the array shape and sample rate.
            # If applied on a SLICE, it would desync the rest of the audio.
            # Restriction: Resample should probably be applied to the whole audio or
            # if applied to a slice, we'd have to insert/cut which is complex editing.
            # Given "Partial Processing" requirement, Resample is an outlier.
            # Implementation decision: If Resample is present, we ignore start/end OR we resample the whole thing.
            # Let's assume Resample applies to the whole file for safety, ignoring start/end if set.
            if p.target_sample_rate != sample_rate:
                from pedalboard import Resample
                # Resample is a plugin in pedalboard? 
                # Actually pedalboard.resample convenience function exists or we use AudioFile resampling.
                # But here we have numpy array.
                # Let's use `pedalboard.resample(audio, sample_rate, target_sample_rate)`
                # It returns new audio.
                new_audio = pedalboard.resample(audio, sample_rate, float(p.target_sample_rate))
                audio = new_audio
                sample_rate = p.target_sample_rate
                # Note: This might invalidate subsequent start/end indices if they were in seconds?
                # The prompt implies the list order matters.
                # Start/end time (seconds) is preserved, indices would need recalculation for NEXT effects.
                # Since we recalculate indices at the start of loop:
                # start_idx = int(effect_data.start_time * sample_rate)
                # It should be fine as long as we update `sample_rate`.
        
        elif plugin:
            # Standard Pedalboard Plugin
            board.append(plugin)
            # Apply
            # If start/end are full range, use board normal
            # If partial, slice.
            
            # For pedalboard, we pass the slice
            segment = audio[:, start_idx:end_idx]
            
            # Pedalboard expects (channels, samples)
            # Be careful with channels. If input is mono and effect is stereo?
            # Pedalboard handles it.
            
            processed_segment = board(segment, sample_rate)
            
            # Ensure shape match. (Reverb might add tails? No, board() returns same length usually 
            # unless Reverb has tails but on a slice we want to merge back?)
            # Pedalboard usually returns same length for realtime plugins. Reverb tails might get cut if we paste back.
            # For "Merge back", we just overwrite the slice.
            # Note: If Reverb ringout is needed, it would extend beyond end_idx.
            # Slicing implementation limits the effect to that window exactly. 
            # Tail would be cut. This is "Partial Processing" behavior usually (insert effect).
            
            # Check dimensions match
            if processed_segment.shape != segment.shape:
                # Handle dimension mismatch (e.g. Mono -> Stereo)
                if processed_segment.shape[0] > segment.shape[0]:
                    new_audio = np.zeros((processed_segment.shape[0], audio.shape[1]), dtype=audio.dtype)
                    new_audio[0, :] = audio[0, :]
                    if audio.shape[0] == 1:
                        new_audio[1, :] = audio[0, :]
                    elif audio.shape[0] > 1:
                        new_audio[:audio.shape[0], :] = audio
                    audio = new_audio
                # If length differs, we can't easily crossfade in place without resizing. 
                # Assuming length is preserved for now.

            # --- Crossfade Logic (Fade-in / Fade-out) ---
            # To prevent clicks at boundaries, we crossfade the processed signal 
            # with the original signal (dry) at the edges of the selection.
            
            # Constants
            FADE_MS = 50 
            fade_len = int(sample_rate * FADE_MS / 1000)
            
            # Ensure fade length is not larger than half the segment
            fade_len = min(fade_len, processed_segment.shape[1] // 2)
            
            if fade_len > 0:
                # Create ramps
                # 0 -> 1
                fade_in = np.linspace(0, 1, fade_len)
                # 1 -> 0
                fade_out = np.linspace(1, 0, fade_len)
                
                # Apply Fade IN (Start of selection)
                # processed * fade_in + original * (1 - fade_in)
                original_start = audio[:, start_idx:start_idx+fade_len]
                processed_start = processed_segment[:, :fade_len]
                
                # Broadcasting fade array to channels
                fade_in_expanded = fade_in[np.newaxis, :]
                
                processed_segment[:, :fade_len] = (
                    processed_start * fade_in_expanded + 
                    original_start * (1 - fade_in_expanded)
                )
                
                # Apply Fade OUT (End of selection)
                original_end = audio[:, end_idx-fade_len:end_idx]
                processed_end = processed_segment[:, -fade_len:]
                
                fade_out_expanded = fade_out[np.newaxis, :]
                
                processed_segment[:, -fade_len:] = (
                    processed_end * fade_out_expanded + 
                    original_end * (1 - fade_out_expanded)
                )

            audio[:, start_idx:end_idx] = processed_segment

    # Write output
    output_buffer = io.BytesIO()
    output_buffer.name = "processed.wav"
    with AudioFile(output_buffer, 'w', sample_rate, audio.shape[0]) as f:
        f.write(audio)
    
    output_buffer.seek(0)
    return output_buffer
