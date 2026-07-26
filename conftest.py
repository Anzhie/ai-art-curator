import os

# Force single-thread execution for PyTorch/OpenMP BEFORE importing libraries
# (Fixes Windows 'access violation' crashes during parallel model loading)
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"

# Force Hugging Face Hub and Transformers into offline mode
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"