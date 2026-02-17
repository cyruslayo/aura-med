import os
import torch

# --- Environment Detection ---
IS_KAGGLE = os.environ.get("KAGGLE_KERNEL_RUN_TYPE") is not None
IS_COLAB = "COLAB_RELEASE_TAG" in os.environ or os.path.exists("/content")
HAS_GPU = torch.cuda.is_available()

# --- Resource Constraints ---
MAX_RAM_GB = 4.0
MAX_INFERENCE_TIME_SEC = 10.0

# --- Model Paths ---
MEDGEMMA_MODEL_PATH = "google/medgemma-4b-it"

# --- Dataset Paths ---
if IS_COLAB:
    ICBHI_DATA_DIR = "/content/drive/MyDrive/aura-med/data/icbhi"
else:
    ICBHI_DATA_DIR = os.path.join("data", "icbhi")

# --- HeAR Audio Encoder Settings ---
HEAR_EMBEDDING_DIM = 512             # Real HeAR output dimension
HEAR_CHUNK_DURATION_SEC = 2.0        # HeAR processes 2-second segments

# --- Projection Layer Settings ---
PROJECTION_INPUT_DIM = HEAR_EMBEDDING_DIM  # Match HeAR output

# --- Audio Settings ---
SAMPLE_RATE = 16000
MAX_AUDIO_DURATION_SEC = 10
MIN_AUDIO_DURATION_SEC = 1.0

# --- Noise Gate Settings (RMS thresholds) ---
NOISE_RMS_UPPER_THRESHOLD = 0.8
NOISE_RMS_LOWER_THRESHOLD = 0.001

# --- Demo / Fallback Mode ---
# Only use mock mode if no GPU is available (e.g., local dev without GPU)
IS_DEMO_MODE = not HAS_GPU
