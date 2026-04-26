# Quick Reference Guide

## 🚀 Quick Start (5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/insat-cloud-forecasting.git
cd insat-cloud-forecasting

# 2. Setup environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure MOSDAC credentials
cp .env.example .env
# Edit .env with your MOSDAC email and password

# 5. Run training
python train.py

# 6. View results
streamlit run streamlit_app.py
```

Access dashboard at: **http://localhost:8501**

---

## 📋 Common Commands

### Data Management
```bash
# Download satellite data
python auto_download_mosdac.py

# Preprocess raw data
python preprocessor/full_preprocessor.py

# Inspect HDF5 files
python inspect_all_h5.py

# Visualize processed data
python preprocessor/visualize_data.py
```

### Training & Evaluation
```bash
# Train DDPM model
python train.py

# Evaluate trained model
python evaluate.py

# System diagnostics
python diagnostic.py
```

### Visualization & Dashboard
```bash
# Launch Streamlit dashboard
streamlit run streamlit_app.py

# View Plotly visualizations
python plotly_viz.py
```

### Code Quality
```bash
# Format code
black .

# Check imports
isort .

# Lint code
flake8 .

# Run tests
pytest tests/
```

---

## 📁 Important Directories

| Path | Purpose | Size |
|------|---------|------|
| `raw/` | Raw MOSDAC .h5 files | ~20 GB |
| `processed/` | Preprocessed .npy frames | ~4 GB |
| `sequences/` | Training sequences | ~4 GB |
| `checkpoints/` | Model weights | ~500 MB |
| `results/` | Training outputs | ~2 GB |
| `evaluation/` | Metrics and results | ~50 MB |
| `images/` | Visualizations | ~500 MB |

---

## ⚙️ Key Configuration

All main scripts use these constants:

```python
IMG_SIZE = 64           # Model input size
CHANNELS = 3            # Number of channels (TIR1, TIR2, WV)
INPUT_FRAMES = 4        # Frames in input sequence
BATCH_SIZE = 4          # Training batch size
LEARNING_RATE = 1e-4    # Optimizer LR
MAX_EPOCHS = 50         # Training epochs
TIMESTEPS = 1000        # Diffusion timesteps
```

Edit in each script or use `.env` file.

---

## 🔧 Troubleshooting

### GPU Not Available
```python
# In scripts, add:
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Force CPU
```

### Out of Memory (OOM)
```python
# In train.py:
BATCH_SIZE = 2  # Reduce batch size
NUM_WORKERS = 0  # Disable parallel loading
```

### MOSDAC Login Issues
```bash
# Verify credentials
python -c "import requests; print(requests.Session().post('https://www.mosdac.gov.in/login'))"
```

### Missing Data Files
```bash
# Check what files exist
ls -la raw/      # Linux/macOS
dir raw/         # Windows

# Preprocess if needed
python preprocessor/full_preprocessor.py
```

---

## 📊 Model Architecture

```
Input (4 frames, 3 channels)
    ↓
Time Embedding → Sin/Cos positional encoding
    ↓
UNet Encoder → Multiple residual blocks
    ↓
UNet Decoder → Up-sampling + Attention
    ↓
Output (Predicted noise for denoising)
```

---

## 📈 Training Pipeline

```
1. Load sequences from sequences/
2. Create DataLoader with batch_size=4
3. Forward diffusion: Add noise to images
4. Predict noise with UNet
5. Compute MSE loss
6. Backward pass + optimizer step
7. Save checkpoint if validation improves
8. Repeat for MAX_EPOCHS
```

---

## 🎯 Evaluation Metrics

| Metric | Formula | Range | Better |
|--------|---------|-------|--------|
| SSIM | Structure similarity | [-1, 1] | ↑ Higher |
| PSNR | Peak signal-to-noise ratio (dB) | [0, ∞] | ↑ Higher |
| MAE | Mean absolute error | [0, ∞] | ↓ Lower |
| RMSE | Root mean squared error | [0, ∞] | ↓ Lower |

Check results in: `evaluation/ddpm_metrics.csv`

---

## 🔐 Security Checklist

- [ ] Remove credentials from `auto_download_mosdac.py`
- [ ] Use `.env` file for sensitive data
- [ ] Add `.env` to `.gitignore` (already done)
- [ ] Never commit model weights containing sensitive info
- [ ] Use SSH keys for GitHub instead of HTTPS
- [ ] Regularly rotate MOSDAC password

---

## 📝 File Editing Locations

**Model hyperparameters**: Edit `BATCH_SIZE`, `LR`, etc. in scripts or `.env`

**Data paths**: Update paths in each script (search for `*_DIR` constants)

**Network architecture**: Modify `UNet` class in `train.py` and `evaluate.py`

**Loss function**: Change in `DDPMModule.training_step()`

**Metrics**: Add to `compute_metrics()` in `evaluate.py`

---

## 🌐 Dashboard Features

### Streamlit App (`streamlit_app.py`)

**Sidebar Controls**:
- Select frame to display
- Choose visualization type
- Adjust color scale
- Filter by date range

**Tabs**:
1. **Predictions** - View model outputs
2. **Metrics** - Performance visualization
3. **Comparison** - Input vs. output
4. **Analysis** - Per-channel breakdown

---

## 📦 Package Management

```bash
# Add new package
pip install package_name
pip freeze > requirements.txt

# Update all packages
pip install --upgrade -r requirements.txt

# Remove unused packages
pip uninstall unused_package
```

---

## 🐛 Debugging Tips

Enable verbose logging:
```python
# In scripts:
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

Add breakpoints (PyCharm/VS Code):
```python
breakpoint()  # Python 3.7+
```

Profile code:
```python
import cProfile
cProfile.run('train()')
```

---

## 📚 Useful Resources

- [PyTorch Docs](https://pytorch.org/docs/)
- [PyTorch Lightning](https://lightning.ai/docs/)
- [DDPM Paper](https://arxiv.org/abs/2006.11239)
- [Streamlit Docs](https://docs.streamlit.io/)
- [MOSDAC Portal](https://www.mosdac.gov.in)

---

## 🎓 Learning Resources

**For beginners**:
1. Read [README.md](README.md)
2. Follow [SETUP.md](SETUP.md)
3. Check [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

**For contributors**:
1. Review [CONTRIBUTING.md](CONTRIBUTING.md)
2. Study [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
3. Explore existing code

**For data scientists**:
1. See [MOSDAC_SETUP.md](MOSDAC_SETUP.md)
2. Check `preprocessor/full_preprocessor.py`
3. Review `evaluate.py` for metrics

---

## ⚡ Performance Tips

1. **Use GPU**: `torch.cuda.is_available()` returns True
2. **Increase workers**: Set `NUM_WORKERS=4` in config
3. **Pin memory**: Use `pin_memory=True` in DataLoader
4. **Mixed precision**: Enable AMP in PyTorch Lightning
5. **Batch size**: Try 8-16 with sufficient VRAM

---

## 📞 Getting Help

1. Check [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines
2. Search existing GitHub Issues
3. Create a new Issue with:
   - System info (OS, Python, CUDA version)
   - Error traceback
   - Minimal reproducible example
4. Contact maintainers on email

---

## 🎯 Next Steps After Setup

1. ✅ Install dependencies
2. ✅ Download sample data
3. ✅ Preprocess data
4. ✅ Train model
5. ✅ Evaluate results
6. ✅ Deploy dashboard
7. 🚀 Make improvements!

---

**Happy coding!** 🌩️🚀
