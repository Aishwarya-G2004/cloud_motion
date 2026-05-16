"""
Configuration module for INSAT Cloud Forecasting project.
Supports dynamic paths via environment variables for team deployment.
"""

import os
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────
# PROJECT ROOT
# ──────────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.absolute()

# ──────────────────────────────────────────────────────────────────────────
# DATA PATHS (Dynamic - set via environment variables)
# ──────────────────────────────────────────────────────────────────────────
RAW_DIR = Path(os.getenv("INSAT_RAW_DIR", PROJECT_ROOT / "raw"))
PROCESSED_DIR = Path(os.getenv("INSAT_PROCESSED_DIR", PROJECT_ROOT / "processed"))
SEQUENCES_DIR = Path(os.getenv("INSAT_SEQUENCES_DIR", PROJECT_ROOT / "sequences"))
RESULTS_DIR = Path(os.getenv("INSAT_RESULTS_DIR", PROJECT_ROOT / "results"))
EVALUATION_DIR = Path(os.getenv("INSAT_EVALUATION_DIR", PROJECT_ROOT / "evaluation"))
GEOTIFFS_DIR = Path(os.getenv("INSAT_GEOTIFFS_DIR", PROJECT_ROOT / "geotiffs"))

# ──────────────────────────────────────────────────────────────────────────
# CHECKPOINT PATHS
# ──────────────────────────────────────────────────────────────────────────
CHECKPOINTS_DIR = Path(os.getenv("INSAT_CHECKPOINTS_DIR", PROJECT_ROOT / "checkpoints"))
BEST_MODEL_PATH = CHECKPOINTS_DIR / "best_model.pth"
BEST_MODEL_DDPM_PATH = CHECKPOINTS_DIR / "best_model_ddpm.pth"

# ──────────────────────────────────────────────────────────────────────────
# MOSDAC CREDENTIALS & SETTINGS (Never hardcode - use .env)
# ──────────────────────────────────────────────────────────────────────────
MOSDAC_USERNAME = os.getenv("MOSDAC_USERNAME", "")
MOSDAC_PASSWORD = os.getenv("MOSDAC_PASSWORD", "")
MOSDAC_FOLDER_PATH = os.getenv("MOSDAC_FOLDER_PATH", "/Order/Apr26_178218")
MOSDAC_BASE_URL = "https://www.mosdac.gov.in"

# ──────────────────────────────────────────────────────────────────────────
# DATA PROCESSING CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────
# Number of files to process (for team flexibility - process 50 out of 163)
NUM_FILES_TO_PROCESS = int(os.getenv("NUM_FILES_TO_PROCESS", "163"))

# Channel configuration
CHANNELS = ["IMG_TIR1", "IMG_TIR2", "IMG_WV"]
CHANNEL_NAMES = ["TIR1", "TIR2", "WV"]
NUM_CHANNELS = len(CHANNELS)

# Image processing
IMG_SIZE = 64
RESIZE_SHAPE = (IMG_SIZE, IMG_SIZE)

# Sequence configuration
INPUT_FRAMES = 4
TARGET_FRAMES = 1
TOTAL_WINDOW = INPUT_FRAMES + TARGET_FRAMES

# ──────────────────────────────────────────────────────────────────────────
# MODEL CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "4"))
LEARNING_RATE = float(os.getenv("LEARNING_RATE", "1e-4"))
MAX_EPOCHS = int(os.getenv("MAX_EPOCHS", "50"))
TIMESTEPS = 1000

# ──────────────────────────────────────────────────────────────────────────
# TRAINING CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────
TRAIN_TEST_SPLIT = float(os.getenv("TRAIN_TEST_SPLIT", "0.8"))
RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))

# ──────────────────────────────────────────────────────────────────────────
# DEVICE CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────
import torch
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ──────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────
def ensure_dirs():
    """Create all necessary directories if they don't exist."""
    dirs = [
        RAW_DIR,
        PROCESSED_DIR,
        SEQUENCES_DIR,
        RESULTS_DIR,
        EVALUATION_DIR,
        CHECKPOINTS_DIR,
        GEOTIFFS_DIR,
    ]
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)


def print_config():
    """Print current configuration (useful for debugging)."""
    print("\n" + "="*70)
    print("INSAT CLOUD FORECASTING - CONFIGURATION")
    print("="*70)
    print(f"\n📁 DATA DIRECTORIES:")
    print(f"  Project Root    : {PROJECT_ROOT}")
    print(f"  Raw Data        : {RAW_DIR}")
    print(f"  Processed Data  : {PROCESSED_DIR}")
    print(f"  Sequences       : {SEQUENCES_DIR}")
    print(f"  Results         : {RESULTS_DIR}")
    print(f"  Evaluation      : {EVALUATION_DIR}")
    print(f"  Checkpoints     : {CHECKPOINTS_DIR}")
    
    print(f"\n⚙️  PROCESSING CONFIG:")
    print(f"  Files to Process: {NUM_FILES_TO_PROCESS}")
    print(f"  Channels        : {CHANNEL_NAMES}")
    print(f"  Image Size      : {IMG_SIZE}x{IMG_SIZE}")
    print(f"  Input Frames    : {INPUT_FRAMES}")
    print(f"  Window Size     : {TOTAL_WINDOW}")
    
    print(f"\n🤖 MODEL CONFIG:")
    print(f"  Batch Size      : {BATCH_SIZE}")
    print(f"  Learning Rate   : {LEARNING_RATE}")
    print(f"  Max Epochs      : {MAX_EPOCHS}")
    print(f"  Device          : {DEVICE}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    ensure_dirs()
    print_config()
