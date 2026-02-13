
import torch
print(f"Torch version: {torch.__version__}")
try:
    x = torch.rand(5, 3)
    print("Torch tensor created successfully.")
except Exception as e:
    print(f"Torch error: {e}")
