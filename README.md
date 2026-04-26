# Chase the Cloud: INSAT3DR Cloud Forecasting using DDPM

A deep learning project for cloud detection and short-term forecasting using satellite imagery from INSAT3DR and Denoising Diffusion Probabilistic Models (DDPM).

## 📋 Project Overview

This project leverages satellite thermal imagery data from India's INSAT3DR satellite to predict cloud patterns using diffusion-based generative models. The system processes thermal infrared bands (TIR1, TIR2) and water vapor (WV) channels to forecast future cloud states.

### Key Features

- **Data Source**: INSAT3DR satellite thermal imagery from MOSDAC
- **Input**: 4-frame sequences of 3-channel satellite data (64×64 resolution)
- **Output**: Predicted future cloud frames using DDPM
- **Channels Used**:
  - **TIR1**: Thermal IR Band 1 — Cloud top temperature (best for cloud detection)
  - **TIR2**: Thermal IR Band 2 — Surface temperature proxy
  - **WV**: Water Vapor — Atmospheric moisture content

## 📁 Project Structure

```
Insat_data/
├── auto_download_mosdac.py          # Download satellite data from MOSDAC
├── preprocessor/
│   ├── full_preprocessor.py          # Convert .h5 files to sequences
│   └── visualize_data.py             # Data visualization utilities
├── train.py                          # Training script for DDPM model
├── evaluate.py                       # Model evaluation & metrics
├── streamlit_app.py                  # Interactive visualization dashboard
├── plotly_viz.py                     # Plotly-based visualizations
├── diagnostic.py                     # System diagnostics
├── inspect_all_h5.py                 # H5 file inspection utilities
├── checkpoints/                      # Model checkpoints
│   ├── best_model_ddpm.pth          # Best DDPM model
│   ├── best_model.pth               # Best baseline model
│   └── ddpm_epoch_*.pth             # DDPM epoch checkpoints
├── processed/                        # Preprocessed .npy frames
│   └── frame_*.npy
├── sequences/                        # 5-frame sliding window sequences
├── raw/                              # Raw .h5 files from MOSDAC
├── evaluation/                       # Evaluation metrics & results
│   ├── metrics.csv                  # Performance metrics
│   └── ddpm_metrics.csv
├── results/                          # Training results & logs
├── images/                           # Generated outputs
│   ├── grids/                       # Visualization grids
│   ├── sequences/                   # Sequence outputs
│   └── gifs/                        # Animated GIFs
├── latlon/                           # Geospatial coordinate data
└── geotiffs/                         # GeoTIFF format outputs
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- CUDA 11.8+ (for GPU acceleration, optional)
- 8GB+ RAM recommended

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/insat-cloud-forecasting.git
cd insat-cloud-forecasting
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
# or
source venv/bin/activate      # Linux/macOS
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install GDAL (optional, for geospatial operations)**
```bash
# Windows: Install from pre-built wheel
pip install GDAL-3.11.1-cp311-cp311-win_amd64.whl

# Linux/macOS: Use conda or apt-get
# conda install -c conda-forge gdal
# apt-get install gdal-bin
```

## 📊 Workflow

### 1. Data Download
Download satellite data from MOSDAC:
```bash
python auto_download_mosdac.py
```
**Note**: Requires MOSDAC credentials. Register at [MOSDAC Portal](https://www.mosdac.gov.in)

### 2. Data Preprocessing
Convert HDF5 files to processed NumPy arrays and create sequences:
```bash
python preprocessor/full_preprocessor.py
```
This generates:
- `processed/`: Individual 3×64×64 frames
- `sequences/`: 5-frame (4-input + 1-target) sequences

### 3. Model Training
Train the DDPM model:
```bash
python train.py
```

**Training Configuration**:
- Batch size: 4
- Learning rate: 1e-4
- Max epochs: 50
- Timesteps: 1000
- Image size: 64×64
- Channels: 3 (TIR1, TIR2, WV)

### 4. Model Evaluation
Evaluate the trained model:
```bash
python evaluate.py
```

**Metrics Computed**:
- SSIM (Structural Similarity Index)
- PSNR (Peak Signal-to-Noise Ratio)
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)

### 5. Interactive Dashboard
Launch the Streamlit visualization app:
```bash
streamlit run streamlit_app.py
```

Access at: `http://localhost:8501`

## 🏗️ Architecture

### DDPM Model
The project implements a Denoising Diffusion Probabilistic Model with:
- **Forward diffusion**: Gradually add noise to satellite images
- **Reverse diffusion**: Learned denoising to reconstruct cloud patterns
- **Conditioning**: Optional temporal and spatial conditioning
- **Loss**: MSE between predicted and actual noise

### Key Components

**Scheduler** (`DDPMScheduler`):
- Beta schedule: Linear from 1e-4 to 0.02
- Alpha bar computation for noise scaling
- Posterior variance calculation

**UNet Architecture**:
- Input: 3-channel satellite images
- Embeddings: Time and spatial position
- Blocks: Residual + Attention layers
- Output: Predicted noise

## 📈 Model Checkpoints

Available pre-trained models:
- `best_model_ddpm.pth`: Best DDPM model (recommended)
- `best_model.pth`: Baseline model checkpoint
- `ddpm_epoch_*.pth`: Intermediate epoch checkpoints (5-50)

## 📝 Configuration

Edit constants in respective scripts:

**Data paths** (all scripts):
```python
SEQUENCE_DIR = r"D:\Insat_data\sequences"
CKPT_DIR     = r"D:\Insat_data\checkpoints"
RESULTS_DIR  = r"D:\Insat_data\results"
```

**Model parameters** (`train.py`):
```python
BATCH_SIZE   = 4
LR           = 1e-4
MAX_EPOCHS   = 50
TIMESTEPS    = 1000
IMG_SIZE     = 64
CHANNELS     = 3
INPUT_FRAMES = 4
```

## 📊 Results

### Evaluation Metrics

Available in `evaluation/`:
- `metrics.csv`: Baseline model metrics
- `ddpm_metrics.csv`: DDPM model metrics

### Sample Outputs

- Predicted cloud frames in `images/grids/`
- Animated sequences in `images/gifs/`
- Difference maps and visualizations
- Per-channel predictions

## 🔧 Utilities

### Visualization
```bash
python preprocessor/visualize_data.py  # Visualize preprocessed data
python plotly_viz.py                   # Interactive Plotly visualizations
```

### Data Inspection
```bash
python inspect_all_h5.py  # Inspect raw H5 file metadata
python diagnostic.py      # System diagnostics & compatibility checks
```

## 📚 Dependencies

See [requirements.txt](requirements.txt) for complete list. Key packages:
- **PyTorch**: Deep learning framework
- **PyTorch Lightning**: Training loop abstraction
- **NumPy/Pandas**: Data manipulation
- **Matplotlib/Plotly**: Visualization
- **Streamlit**: Interactive dashboard
- **OpenCV**: Image processing
- **h5py**: HDF5 file handling
- **torchmetrics**: Model evaluation
- **tqdm**: Progress bars

## 🐛 Troubleshooting

### GPU Not Available
```python
# Check GPU availability
import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))

# Force CPU
DEVICE = torch.device("cpu")
```

### GDAL Installation Issues
```bash
# If GDAL wheel fails, try conda:
conda install -c conda-forge gdal

# Or use system package manager:
# Ubuntu: sudo apt-get install gdal-bin
# macOS: brew install gdal
```

### MOSDAC Login Failures
- Verify credentials in `auto_download_mosdac.py`
- Check network connectivity
- Ensure account is active at [MOSDAC](https://www.mosdac.gov.in)

## 🔐 Security Notes

⚠️ **IMPORTANT**: 
- Remove MOSDAC credentials from `auto_download_mosdac.py` before committing
- Use environment variables for sensitive data:
```bash
export MOSDAC_USERNAME="your_email@example.com"
export MOSDAC_PASSWORD="your_password"
```

## 📖 References

- [INSAT3DR Satellite Documentation](https://mausam.imd.gov.in/about-us/about-imd-satellites)
- [MOSDAC Data Portal](https://www.mosdac.gov.in)
- [DDPM Paper](https://arxiv.org/abs/2006.11239)
- [PyTorch Lightning](https://lightning.ai/)
- [Streamlit Documentation](https://docs.streamlit.io/)

## 👥 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## ✉️ Contact

For questions or suggestions:
- Open an issue on GitHub
- Email: your-email@example.com

## 🙏 Acknowledgments

- MOSDAC for providing satellite data
- PyTorch and PyTorch Lightning teams
- Open-source community contributions

---

**Last Updated**: April 2026  
**Version**: 1.0.0  
**Status**: Active Development
