import pedalboard
try:
    f = pedalboard.IIRFilter(cutoff_hz=440, gain_db=0)
    print("IIRFilter properties:", dir(f))
except Exception as e:
    print("IIRFilter init error:", e) # It might require 'type' or similar
