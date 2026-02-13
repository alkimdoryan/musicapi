from pedalboard import Pedalboard, Reverb
import numpy as np
import soundfile as sf

def check_state():
    # Create a simple Reverb
    board = Pedalboard([Reverb(room_size=0.5, wet_level=1.0, dry_level=0.0)])
    
    # Create an impulse: a click followed by silence
    sr = 44100
    chunk_size = 1024
    
    # Chunk 1: The click
    chunk1 = np.zeros(chunk_size, dtype=np.float32)
    chunk1[0] = 1.0 
    
    # Chunk 2: Silence (should contain reverb tail from chunk 1)
    chunk2 = np.zeros(chunk_size, dtype=np.float32)
    
    print("Processing Chunk 1...")
    out1 = board.process(chunk1, sample_rate=sr)
    
    print("Processing Chunk 2 (Silence)...")
    out2 = board.process(chunk2, sample_rate=sr)
    
    # Analyze Output 2
    max_amp_2 = np.max(np.abs(out2))
    print(f"Max amplitude in Chunk 2: {max_amp_2}")
    
    if max_amp_2 > 0.0001:
        print("SUCCESS: Tail detected in Chunk 2. Pedalboard preserves state.")
    else:
        print("FAIL: Chunk 2 is silent. Pedalboard resets state on each call.")
        
    # Check if there is a way to preserve state?
    # Usually standard plugins do. But Pedalboard.process might wrap it with reset.
    # Let's check reset method.
    
if __name__ == "__main__":
    check_state()
