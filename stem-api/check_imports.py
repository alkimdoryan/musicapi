import sys
print(f"Testing imports with Python {sys.version}")

try:
    print("Importing fastapi...")
    import fastapi
    print("Importing torch...")
    import torch
    print("Importing torchaudio...")
    import torchaudio
    print("Importing demucs...")
    import demucs
    print("Importing spleeter...")
    import spleeter
    print("Importing tensorflow...")
    import tensorflow
    print("Importing librosa...")
    import librosa
    
    print("\nSUCCESS: All critical packages imported successfully!")
except Exception as e:
    print(f"\nFAILURE: {e}")
    sys.exit(1)
