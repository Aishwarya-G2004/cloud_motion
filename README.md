# INSAT3DR Cloud Forecasting with DDPM

A satellite cloud forecasting project using INSAT3DR imagery and Denoising Diffusion Probabilistic Models (DDPM).

## 📋 Project Overview

This repository processes INSAT3DR satellite data and trains a diffusion-based model to forecast cloud patterns from thermal infrared and water vapor channels.

## 📁 Project Structure

```
Insat_data/
├── auto_download_mosdac.py          # Download satellite data from MOSDAC
├── config.py                       # Project configuration values
├── diagnostic.py                   # System diagnostics and checks
├── evaluate.py                     # Model evaluation and metrics
├── inspect_all_h5.py               # HDF5 inspection utilities
├── plotly_viz.py                   # Plotly visualization utilities
├── preprocessor/
│   ├── full_preprocessor.py        # Convert raw .h5 to processed frames and sequences
│   └── visualize_data.py           # Visualize preprocessed data
├── pyproject.toml                  # Python package metadata
├── README.md                       # Project overview and usage
├── requirements.txt                # Python dependencies
├── SETUP.md                        # Installation instructions
├── streamlit_app.py                # Interactive dashboard
├── train.py                        # Training script for the DDPM model
├── checkpoints/                    # Model checkpoint artifacts
│   ├── lightning_epoch=*.ckpt
│   └── lightning_logs/
├── processed/                      # Preprocessed frames
│   └── frame_*.npy
├── sequences/                      # Generated training sequences
├── raw/                            # Raw downloaded satellite HDF5 files
├── evaluation/                     # Evaluation metrics and reports
├── results/                        # Output logs and generated results
├── images/                         # Generated visualization images
│   ├── grids/
│   ├── sequences/
│   └── gifs/
├── geotiffs/                       # GeoTIFF export files
└── latlon/                         # Latitude/longitude reference data
    └── latlon_insat3dr.nc
```

> Large generated artifacts and raw satellite files are not tracked by Git and are excluded by `.gitignore`.

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- CUDA 11.8+ for GPU acceleration (optional)
- 8 GB+ RAM recommended

### Install

1. Clone the repository:
```bash
git clone https://github.com/<yourusername>/<your-repo>.git
cd Insat_data
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate      # Windows PowerShell
# or
.venv\Scripts\activate.bat  # Windows CMD
# Linux/macOS
# source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install GDAL if needed:
```bash
pip install GDAL-3.11.1-cp311-cp311-win_amd64.whl
```

## 🧠 Main Workflow

### Download data
```bash
python auto_download_mosdac.py
```

### Preprocess raw files
```bash
python preprocessor/full_preprocessor.py
```

### Train model
```bash
python train.py
```

### Evaluate model
```bash
python evaluate.py
```

### Launch dashboard
```bash
streamlit run streamlit_app.py
```

## 📌 Directory Purpose

- `raw/` — Raw HDF5 satellite files from MOSDAC.
- `processed/` — Per-frame `.npy` outputs generated from raw data.
- `sequences/` — Sliding-window training sequences used for model input.
- `checkpoints/` — Model weights and checkpoint files.
- `evaluation/` — Metrics and evaluation output.
- `results/` — Generated results, logs, and plots.
- `images/` — Visualization images, grids, GIFs, and sequence outputs.
- `geotiffs/` — GeoTIFF export files.
- `latlon/` — Geospatial latitude/longitude reference data.

## 🔧 Push to GitHub

If your repository already has a remote configured:
```bash
git add .
git commit -m "Update README and .gitignore"
git push origin main
```

If you need to add the remote first:
```bash
git remote add origin https://github.com/<yourusername>/<your-repo>.git
git push --set-upstream origin main
```

> Replace `<yourusername>` and `<your-repo>` with your GitHub account and repository name.
