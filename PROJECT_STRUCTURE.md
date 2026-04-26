# Project Structure Documentation

## Directory Tree

```
insat-cloud-forecasting/
├── .github/
│   └── workflows/
│       └── tests.yml                    # GitHub Actions CI/CD pipeline
│
├── preprocessor/                        # Data processing module
│   ├── __init__.py
│   ├── full_preprocessor.py            # Main preprocessing script
│   │   ├── process_file()              # Convert HDF5 to NumPy
│   │   ├── preprocess_all_frames()     # Batch processing
│   │   └── create_sequences()          # Create sliding windows
│   └── visualize_data.py               # Data visualization utilities
│
├── checkpoints/                         # Model weights directory
│   ├── best_model_ddpm.pth             # Best DDPM checkpoint (primary)
│   ├── best_model.pth                  # Baseline model
│   ├── ddpm_epoch_*.pth                # Epoch checkpoints
│   ├── epoch_*.pth                     # Training checkpoints
│   └── lightning_logs/                 # PyTorch Lightning logs
│
├── processed/                           # Preprocessed frames
│   ├── frame_000.npy                   # Individual 3×64×64 frames
│   ├── frame_001.npy
│   └── ...
│
├── sequences/                           # Sequence collections
│   ├── sequence_0.pkl                  # 5-frame sequences
│   └── ...                             # (4 input + 1 target)
│
├── raw/                                 # Raw downloaded data
│   ├── 3RIMG_26APR2026_1000_L1C_SGP_V01R00.h5
│   └── ...
│
├── evaluation/                          # Evaluation results
│   ├── metrics.csv                     # Performance metrics
│   ├── ddpm_metrics.csv                # DDPM-specific metrics
│   └── visualizations/                 # Evaluation plots
│
├── results/                             # Training outputs
│   ├── predictions/                    # Model predictions
│   ├── losses/                         # Loss curves
│   └── logs/                           # Training logs
│
├── images/                              # Generated visualizations
│   ├── grids/                          # Prediction grids
│   │   ├── comparison_001.png          # Side-by-side predictions
│   │   └── ...
│   ├── sequences/                      # Frame sequences
│   │   ├── seq_001/
│   │   └── ...
│   └── gifs/                           # Animated predictions
│       ├── animation_001.gif
│       └── ...
│
├── geotiffs/                            # Geospatial outputs
│   ├── prediction_001.tif              # GeoTIFF format outputs
│   └── ...
│
├── latlon/                              # Geospatial metadata
│   └── latlon_insat3dr.nc              # Latitude/Longitude netCDF
│
├── .gitignore                           # Git ignore patterns
├── .env.example                         # Environment variables template
├── CONTRIBUTING.md                      # Contribution guidelines
├── MOSDAC_SETUP.md                     # Data download guide
├── README.md                            # Project overview
├── SETUP.md                             # Installation instructions
├── LICENSE                              # MIT License
├── pyproject.toml                       # Python package config
├── requirements.txt                     # Python dependencies
│
├── auto_download_mosdac.py             # Download satellite data
│   ├── login()                         # MOSDAC authentication
│   ├── download_files()                # File download logic
│   └── main()                          # Entry point
│
├── train.py                            # Training script
│   ├── DDPMScheduler                   # Diffusion scheduler
│   ├── UNet                            # Denoising network
│   ├── SatelliteDataset               # PyTorch Dataset
│   ├── DDPMModule                      # PyTorch Lightning Module
│   └── main()                          # Training loop
│
├── evaluate.py                         # Evaluation script
│   ├── DDPMScheduler                   # (same as train.py)
│   ├── UNet                            # (same as train.py)
│   ├── SatelliteDataset               # (same as train.py)
│   ├── compute_metrics()               # Metric calculation
│   └── main()                          # Evaluation loop
│
├── streamlit_app.py                    # Dashboard application
│   ├── load_model()                    # Load trained model
│   ├── render_sidebars()               # UI components
│   ├── tab_predictions()               # Predictions tab
│   ├── tab_metrics()                   # Metrics display
│   └── tab_comparison()                # Side-by-side comparison
│
├── plotly_viz.py                       # Interactive visualizations
│   ├── plot_predictions()
│   ├── plot_metrics()
│   └── plot_timeseries()
│
├── diagnostic.py                       # System diagnostics
│   ├── check_python_version()
│   ├── check_cuda()
│   ├── check_dependencies()
│   └── main()
│
├── inspect_all_h5.py                   # HDF5 file inspection
│   ├── inspect_file()
│   ├── get_statistics()
│   └── main()
│
├── failed_files.txt                    # Log of failed processing
│
└── latlon_insat3dr.nc                  # Coordinate reference file
```

## Module Descriptions

### Data Processing Pipeline

#### `preprocessor/full_preprocessor.py`
Converts raw MOSDAC HDF5 files to training sequences.

**Key Functions**:
- `normalize_band()`: Scale pixel values to [0, 1]
- `resize_band()`: Resize to 64×64 from native resolution
- `process_file()`: Extract 3 channels from single H5 file
- `preprocess_all_frames()`: Batch process all raw files
- `create_sequences()`: Create 5-frame sliding window sequences
- `save_sequences()`: Pickle sequences for fast loading

**Input**: `.h5` files (100-500 MB each)  
**Output**: `.npy` and `.pkl` files

---

### Training & Modeling

#### `train.py`
PyTorch Lightning training script for DDPM model.

**Key Classes**:
```
DDPMScheduler
├── __init__()           # Initialize noise schedules
├── add_noise()          # Forward diffusion
├── denoise()            # Backward diffusion
└── sample()             # Generate from noise

UNet
├── __init__()           # Residual blocks + attention
├── time_embedding()     # Timestep encoding
└── forward()            # Denoising prediction

SatelliteDataset
├── __init__()           # Load sequences
├── __len__()            # Dataset size
└── __getitem__()        # Load sequence + augmentation

DDPMModule (LightningModule)
├── __init__()           # Model initialization
├── training_step()      # MSE loss on noise prediction
├── validation_step()    # Validation metrics
└── configure_optimizers() # Adam optimizer
```

**Training Config**:
- Batch size: 4
- Learning rate: 1e-4
- Max epochs: 50
- Loss: MSE (predicted noise vs. actual noise)
- Scheduler: Linear warmup + cosine annealing

---

#### `evaluate.py`
Evaluation and metrics computation.

**Key Functions**:
```
compute_metrics()
├── ssim              # Structural Similarity Index
├── psnr              # Peak Signal-to-Noise Ratio
├── mae               # Mean Absolute Error
└── rmse              # Root Mean Squared Error

generate_predictions()
├── Load test sequence
├── Run diffusion loop
└── Save predictions

create_comparison_grid()
├── Input frame
├── Ground truth
└── Prediction
```

**Output**: `evaluation/ddpm_metrics.csv`

---

### Visualization & Dashboard

#### `streamlit_app.py`
Interactive web dashboard for model exploration.

**Features**:
- **Predictions Tab**: Browse generated outputs
- **Metrics Tab**: View performance metrics
- **Comparison Tab**: Side-by-side input/output
- **Heatmaps**: Per-channel analysis
- **Timeline**: Temporal sequence visualization

**Run**: `streamlit run streamlit_app.py`

#### `plotly_viz.py`
Plotly-based interactive visualizations.

**Visualizations**:
- Time series of metrics
- Spatial prediction heatmaps
- Channel comparison plots
- Error distribution histograms

---

### Utilities & Tools

#### `auto_download_mosdac.py`
Automated MOSDAC data download.

**Workflow**:
1. Login via MOSDAC credentials
2. Browse order folder path
3. List available files
4. Download with progress bar
5. Verify checksums
6. Organize by date

**Environment Variables**:
```
MOSDAC_USERNAME = "email@example.com"
MOSDAC_PASSWORD = "password"
```

#### `diagnostic.py`
System diagnostics and compatibility checking.

**Checks**:
- Python version (3.11+)
- GPU/CUDA availability
- Package versions
- Data directory permissions
- Available disk space
- Memory availability

#### `inspect_all_h5.py`
Inspect HDF5 file structure and metadata.

**Information**:
- File size
- Available datasets/groups
- Data shape and dtype
- Value ranges (min/max)
- Missing or corrupt channels
- Metadata attributes

---

## Data Formats

### Raw Data (.h5)
```
3RIMG_DDMMMYYYY_HHMM_L1C_SGP_V01R00.h5
├── IMG_VIS      → (2392, 2392) uint16
├── IMG_SWIR     → (2392, 2392) uint16
├── IMG_TIR1     → (2392, 2392) uint16  ✓ Used
├── IMG_TIR2     → (2392, 2392) uint16  ✓ Used
├── IMG_WV       → (2392, 2392) uint16  ✓ Used
└── Attributes:
    ├── acquisition_time
    ├── solar_zenith_angle
    └── satellite_geometry
```

### Processed Data (.npy)
```
frame_000.npy
├── Shape: (3, 64, 64)
├── dtype: float32
├── Values: [0.0, 1.0] normalized
└── Channels: [TIR1, TIR2, WV]
```

### Sequences (.pkl)
```
sequence_0.pkl
├── 'input': (4, 3, 64, 64)   → 4 frames, 3 channels
├── 'target': (1, 3, 64, 64)  → 1 frame (target)
└── 'metadata': dict
    ├── 'timestamp'
    ├── 'location'
    └── 'quality_score'
```

### Metrics (.csv)
```
metrics.csv
├── Columns: epoch, ssim, psnr, mae, rmse, val_loss
└── Rows: One per evaluation
```

---

## Key Configuration Parameters

| Parameter | Value | Location | Description |
|-----------|-------|----------|-------------|
| IMAGE_SIZE | 64 | All scripts | Model input resolution |
| CHANNELS | 3 | All scripts | RGB channels (TIR1, TIR2, WV) |
| INPUT_FRAMES | 4 | All scripts | Sequence input length |
| TARGET_FRAMES | 1 | All scripts | Sequence output length |
| BATCH_SIZE | 4 | `train.py` | Training batch size |
| LEARNING_RATE | 1e-4 | `train.py` | Optimizer learning rate |
| MAX_EPOCHS | 50 | `train.py` | Training duration |
| TIMESTEPS | 1000 | DDPM classes | Diffusion steps |

---

## File Dependencies

```
train.py
├── requires: sequences/
├── outputs: checkpoints/best_model_ddpm.pth
└── generates: results/training_logs/

evaluate.py
├── requires: checkpoints/best_model_ddpm.pth
├── requires: sequences/
└── outputs: evaluation/ddpm_metrics.csv

streamlit_app.py
├── requires: checkpoints/best_model_ddpm.pth
├── requires: images/grids/
└── requires: evaluation/ddpm_metrics.csv

preprocessor/full_preprocessor.py
├── requires: raw/*.h5
├── outputs: processed/frame_*.npy
└── outputs: sequences/*.pkl
```

---

## Size Estimates

| Directory | Files | Total Size | Notes |
|-----------|-------|-----------|-------|
| raw/ | 288 | 15-20 GB | MOSDAC downloaded |
| processed/ | 288 | 3-4 GB | Preprocessed frames |
| sequences/ | 284 | 3-4 GB | Training sequences |
| checkpoints/ | 15+ | 500 MB | Model weights |
| results/ | many | 1-2 GB | Logs, plots, outputs |
| evaluation/ | few | 50 MB | Metrics CSV files |
| images/ | many | 500 MB | PNG/GIF outputs |

**Total (full dataset)**: ~24-34 GB

---

## Development Workflow

```
1. Download data
   auto_download_mosdac.py → raw/

2. Preprocess
   preprocessor/full_preprocessor.py → processed/ & sequences/

3. Train
   train.py → checkpoints/best_model_ddpm.pth, results/

4. Evaluate
   evaluate.py → evaluation/ddpm_metrics.csv, images/

5. Visualize
   streamlit run streamlit_app.py → http://localhost:8501
```

---

## Adding New Modules

Place new code in appropriate locations:

**For new models**: Create `models/your_model.py`  
**For new preprocessing**: Add to `preprocessor/`  
**For new metrics**: Update `evaluate.py` or create `metrics/`  
**For new visualizations**: Update `streamlit_app.py` or `plotly_viz.py`  

---

For detailed setup instructions, see [SETUP.md](SETUP.md)  
For contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md)
