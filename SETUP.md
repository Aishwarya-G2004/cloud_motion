# Project Setup Instructions

## Quick Start

This document provides detailed instructions for setting up the project locally.

### Prerequisites

- **Python**: 3.11 or higher
- **Git**: Latest version
- **Memory**: 8GB RAM minimum (16GB+ recommended)
- **GPU**: CUDA 11.8+ (optional, for accelerated training)

### Step-by-Step Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/insat-cloud-forecasting.git
cd insat-cloud-forecasting
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 3. Upgrade pip
```bash
python -m pip install --upgrade pip
```

#### 4. Install Requirements
```bash
pip install -r requirements.txt
```

#### 5. Download Pre-trained Models (Optional)
```bash
# Create checkpoints directory if it doesn't exist
mkdir -p checkpoints

# Download models (add download script or links)
# wget https://example.com/best_model_ddpm.pth -O checkpoints/best_model_ddpm.pth
```

### Configuration

#### Data Paths
Edit the following in each script:
- `auto_download_mosdac.py`: MOSDAC credentials and save paths
- `preprocessor/full_preprocessor.py`: Data directories
- `train.py`: Training output directories

#### MOSDAC Credentials
⚠️ **IMPORTANT**: Use environment variables instead of hardcoding:

```bash
# Linux/macOS
export MOSDAC_USERNAME="your_email@example.com"
export MOSDAC_PASSWORD="your_password"

# Windows PowerShell
$env:MOSDAC_USERNAME="your_email@example.com"
$env:MOSDAC_PASSWORD="your_password"
```

Then update `auto_download_mosdac.py`:
```python
USERNAME = os.getenv("MOSDAC_USERNAME")
PASSWORD = os.getenv("MOSDAC_PASSWORD")
```

### Verify Installation

```bash
# Check Python version
python --version

# Check PyTorch installation
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"

# Check other key packages
python -c "import tensorflow; import streamlit; import pandas; print('All packages installed!')"
```

### Optional: GPU Setup

#### Windows with NVIDIA GPU
```bash
# Install CUDA Toolkit (if not already installed)
# Download from: https://developer.nvidia.com/cuda-11-8-0-download-archive

# Install cuDNN
# Download from: https://developer.nvidia.com/cudnn

# Verify CUDA
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

#### Linux GPU Setup
```bash
# Ubuntu 22.04 example
sudo apt-get install nvidia-driver-535
sudo apt-get install nvidia-cuda-toolkit-11-8

# Verify
nvidia-smi
```

### Installing Optional Dependencies

#### GDAL (For Geospatial Operations)
```bash
# Windows (pre-built wheel provided)
pip install GDAL-3.11.1-cp311-cp311-win_amd64.whl

# Linux/macOS (via conda recommended)
conda install -c conda-forge gdal

# Or system package manager
# Ubuntu: sudo apt-get install gdal-bin
# macOS: brew install gdal
```

#### Jupyter for Development
```bash
pip install jupyter jupyterlab ipywidgets
```

### Project Initialization

#### Create Data Directories
```bash
mkdir -p raw processed sequences results evaluation checkpoints images/grids images/gifs geotiffs
```

#### Download Sample Data (Optional)
```bash
# Instructions for downloading sample data will be in MOSDAC_SETUP.md
python auto_download_mosdac.py --sample
```

### Testing the Setup

Run the diagnostic script:
```bash
python diagnostic.py
```

This will check:
- Python version
- Package versions
- GPU availability
- Data directories
- File access permissions

## Development Setup

### IDE Configuration

**VS Code** (recommended):
1. Install Python extension
2. Install Pylance for type checking
3. Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "ms-python.black-formatter"
    }
}
```

**PyCharm**:
1. Open project settings
2. Go to Project → Python Interpreter
3. Add new environment from the `venv` folder

### Code Quality Tools

```bash
# Install development dependencies
pip install black flake8 isort pytest

# Format code
black .

# Organize imports
isort .

# Lint code
flake8 .

# Run tests
pytest
```

## Troubleshooting

### Virtual Environment Issues
```bash
# Deactivate and reactivate
deactivate
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

### Package Installation Failures
```bash
# Clear pip cache
pip cache purge

# Install with no cache
pip install --no-cache-dir -r requirements.txt
```

### CUDA/GPU Issues
```bash
# Check PyTorch GPU support
python -c "import torch; print(torch.cuda.is_available())"

# Force CPU mode (in scripts)
os.environ['CUDA_VISIBLE_DEVICES'] = ''
```

### Permission Errors on Linux
```bash
# Add user to video group for GPU access
sudo usermod -a -G video $USER
# Log out and back in for changes to take effect
```

## Next Steps

1. Read [README.md](README.md) for project overview
2. Check [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
3. Explore the data pipeline in `preprocessor/`
4. Run training with `python train.py`
5. Launch dashboard with `streamlit run streamlit_app.py`

## Support

- GitHub Issues: For bug reports and feature requests
- Discussions: For questions and general help
- Email: Contact maintainers for sensitive issues

---

Happy coding! 🚀
