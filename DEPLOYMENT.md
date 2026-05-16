# 🚀 INSAT Cloud Forecasting - Team Deployment Guide

This guide explains how to set up, configure, and deploy the INSAT cloud forecasting project for team collaboration.

---

## 📋 Prerequisites

- **Python 3.11+** (Check with `python --version`)
- **Git** installed (Check with `git --version`)
- **NVIDIA GPU** (Optional but recommended for faster training)
- **MOSDAC Account** (For downloading satellite data) - Register at https://www.mosdac.gov.in

---

## 🔧 Step 1: Clone the Repository

```bash
# Clone from GitHub
git clone https://github.com/your-org/insat-cloud-forecasting.git
cd insat-cloud-forecasting

# OR if you have SSH keys configured
git clone git@github.com:your-org/insat-cloud-forecasting.git
cd insat-cloud-forecasting
```

---

## 🐍 Step 2: Set Up Python Environment

### Option A: Using venv (Recommended for simplicity)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Option B: Using Conda (If you prefer Conda)

```bash
# Create conda environment
conda create -n insat python=3.11 -y
conda activate insat

# Install dependencies
pip install -r requirements.txt
```

---

## 🔐 Step 3: Configure Environment Variables

### Create `.env` file from template

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file with your credentials
# Windows - use your preferred editor (VS Code, Notepad++, etc.)
# macOS/Linux
nano .env
```

### Configure `.env` file

```env
# ── MOSDAC DOWNLOAD CREDENTIALS ────────────────────────────────────────
# Get credentials by registering at https://www.mosdac.gov.in

MOSDAC_USERNAME=your_email@example.com
MOSDAC_PASSWORD=your_secure_password
MOSDAC_FOLDER_PATH=/Order/Apr26_178218

# ── DATA DIRECTORIES ───────────────────────────────────────────────────
# Default is project root. Adjust if needed.

INSAT_RAW_DIR=./raw
INSAT_PROCESSED_DIR=./processed
INSAT_SEQUENCES_DIR=./sequences
INSAT_RESULTS_DIR=./results
INSAT_EVALUATION_DIR=./evaluation
INSAT_CHECKPOINTS_DIR=./checkpoints

# ── FLEXIBLE DATA SUBSET CONFIGURATION ────────────────────────────────
# Set to 50 if working on initial 50 files (team task)
# Set to 163 for full dataset processing

NUM_FILES_TO_PROCESS=50

# ── TRAINING CONFIGURATION ────────────────────────────────────────────
# Adjust BATCH_SIZE based on your GPU memory:
#   - 4GB GPU  : BATCH_SIZE=2
#   - 8GB GPU  : BATCH_SIZE=4
#   - 16GB GPU : BATCH_SIZE=8

BATCH_SIZE=4
LEARNING_RATE=1e-4
MAX_EPOCHS=50
TRAIN_TEST_SPLIT=0.8
RANDOM_SEED=42
```

### 🔒 IMPORTANT: Keep `.env` Secure!

**NEVER commit `.env` to GitHub!** It's in `.gitignore` for security.

```bash
# Verify .env is ignored
git status    # Should NOT show .env
```

---

## 📊 Step 4: Download Data

### If starting fresh:

```bash
# Download 163 .h5 files from MOSDAC
python auto_download_mosdac.py

# This saves ~50GB of data to ./raw/
# Note: Make sure you have disk space!
```

### If data already exists:

Skip to next step. The preprocessor will use existing data.

---

## 🔄 Step 5: Preprocess Data

### Process 50 files (team task):

```bash
# Uses NUM_FILES_TO_PROCESS=50 from .env
python preprocessor/full_preprocessor.py
```

**Output structure created:**
```
processed/           # ~500 MB (individual frames)
sequences/           # ~2 GB (sliding window sequences)
```

**What it does:**
1. Reads 50 .h5 files from `raw/`
2. Extracts 3 thermal channels (TIR1, TIR2, WV)
3. Normalizes and resizes to 64×64
4. Creates sliding window sequences (5 frames each)

---

## 🤖 Step 6: Train Model

### Start training:

```bash
python train.py

# Model will:
# - Use PyTorch Lightning for distributed training
# - Save checkpoints to ./checkpoints/
# - Save training curve to ./results/
# - Show GPU utilization
```

### Monitor training:

```bash
# In another terminal, watch training curve
# (saved after every 10 epochs)
```

---

## 📈 Step 7: Evaluate Model

### Run evaluation metrics:

```bash
python evaluate.py

# Computes SSIM, PSNR, MAE, MSE on test set
# Saves metrics to ./evaluation/ddpm_metrics.csv
# Saves sample predictions to ./evaluation/
```

---

## 🎨 Step 8: Run Interactive Dashboard

### Launch Streamlit app:

```bash
streamlit run streamlit_app.py

# Opens at http://localhost:8501
# Features:
# - Load trained model
# - Visualize predictions
# - Interactive sequence explorer
# - Metrics dashboard
```

---

## 📁 Project Structure

```
insat-cloud-forecasting/
├── config.py                    ← Configuration (DO NOT EDIT - use .env)
├── requirements.txt             ← Python dependencies
├── .env.example                 ← Template for credentials (.env from this)
├── .gitignore                   ← Excludes large files and .env
│
├── DEPLOYMENT.md                ← This file
├── README.md                    ← Project overview
├── SETUP.md                     ← Initial setup instructions
│
├── train.py                     ← DDPM model training
├── evaluate.py                  ← Evaluation metrics
├── auto_download_mosdac.py      ← Download satellite data
├── streamlit_app.py             ← Interactive dashboard
│
├── preprocessor/
│   └── full_preprocessor.py     ← Data preprocessing pipeline
│
├── checkpoints/                 ← Model weights (GITIGNORED)
│   └── .gitkeep                 ← Placeholder (keep directory)
│
├── raw/                         ← Raw .h5 files (GITIGNORED)
│   └── .gitkeep
│
├── processed/                   ← Preprocessed frames (GITIGNORED)
│   └── .gitkeep
│
├── sequences/                   ← Training sequences (GITIGNORED)
│   └── .gitkeep
│
├── results/                     ← Training results (GITIGNORED)
│   └── .gitkeep
│
└── evaluation/                  ← Evaluation outputs (GITIGNORED)
    └── .gitkeep
```

---

## 🎯 Quick Start (Team Member Workflow)

Assuming data and models are shared via network drive:

```bash
# 1. Clone repo
git clone <repo-url>
cd insat-cloud-forecasting

# 2. Setup environment
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env with:
#   - MOSDAC credentials (if downloading)
#   - Path to shared data location
#   - NUM_FILES_TO_PROCESS=50

# 4. Process data (if not preprocessed)
python preprocessor/full_preprocessor.py

# 5. Train
python train.py

# 6. Evaluate
python evaluate.py

# 7. Visualize
streamlit run streamlit_app.py
```

---

## 🔄 Flexibility: Processing Different Data Subsets

### Scenario 1: Team A processes first 50 files

```env
NUM_FILES_TO_PROCESS=50
```

### Scenario 2: Team B processes next 50 files (files 50-100)

```bash
# Rename raw files to process only 50-100
# Or modify config.py to slice the file list

# Then preprocess
python preprocessor/full_preprocessor.py
```

### Scenario 3: Full dataset processing

```env
NUM_FILES_TO_PROCESS=163
```

---

## ⚠️ Common Issues & Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'config'`

**Solution:** Make sure you're in the project root directory:
```bash
cd insat-cloud-forecasting
python train.py
```

### Issue: `KeyError: 'MOSDAC_USERNAME'`

**Solution:** Create `.env` file and fill in credentials:
```bash
cp .env.example .env
# Edit .env with your MOSDAC credentials
```

### Issue: `CUDA out of memory`

**Solution:** Reduce `BATCH_SIZE` in `.env`:
```env
BATCH_SIZE=2    # Instead of 4
```

### Issue: Data preprocessing stops at raw file 50

**Solution:** This is expected if `NUM_FILES_TO_PROCESS=50`. To process more:
```env
NUM_FILES_TO_PROCESS=163
```

Then rerun preprocessor.

---

## 📤 Git Workflow for Team

### Before pushing code:

```bash
# Check what will be committed
git status

# Verify .env is NOT included
git check-ignore .env     # Should output: .env

# Stage and commit
git add .
git commit -m "Feature: Add distributed training"
git push origin feature-branch
```

### Large files are automatically excluded:

- ✅ Code files pushed
- ❌ `.env` excluded (security)
- ❌ `.h5` files excluded (data)
- ❌ Model weights excluded (too large)
- ❌ Results excluded (can be regenerated)

---

## 💾 Data Management Strategy

### Local Development:
- Store raw data in `./raw/` (excluded from git)
- Process locally with `full_preprocessor.py`

### Team Collaboration:
- Share preprocessed sequences via:
  - Network drive
  - Google Drive / OneDrive
  - S3 bucket
  - Internal git LFS

### Production:
- Host data on dedicated server
- Set `INSAT_SEQUENCES_DIR` to remote path
- Use network mounts or cloud APIs

---

## 🔐 Security Best Practices

| ✅ DO | ❌ DON'T |
|------|---------|
| Store credentials in `.env` | Hardcode passwords in Python |
| Use `.env.example` as template | Commit `.env` to GitHub |
| Run `git check-ignore .env` | Trust that `.gitignore` works |
| Use environment variables | Print credentials in logs |
| Review `.gitignore` before push | Push large binary files |

---

## 📞 Support & Questions

For issues or questions:
1. Check [Troubleshooting](#-common-issues--troubleshooting) section
2. Review [README.md](README.md) for project background
3. Check [SETUP.md](SETUP.md) for installation details
4. Open an issue on GitHub

---

## 📝 Quick Reference

| Command | Purpose |
|---------|---------|
| `python config.py` | Print current configuration |
| `python preprocessor/full_preprocessor.py` | Preprocess raw data |
| `python train.py` | Train DDPM model |
| `python evaluate.py` | Evaluate on test set |
| `streamlit run streamlit_app.py` | Launch dashboard |
| `python auto_download_mosdac.py` | Download satellite data |

---

**Last Updated:** 2025-04-27  
**Version:** 1.0.0  
**Status:** Production Ready
