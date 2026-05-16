# 🚀 INSAT Cloud Forecasting - Complete Execution Guide

## ✅ Prerequisites Completed
- Python 3.11 installed ✓
- Virtual environment configured ✓
- Dependencies installed ✓
- .env file created ✓

---

## 📊 **PROJECT WORKFLOW**

This project has 4 main phases:

```
┌─────────────────────────────────────────────────────────────┐
│                   INSAT Cloud Forecasting                    │
│                      Project Pipeline                        │
└─────────────────────────────────────────────────────────────┘

Phase 1: DATA DOWNLOAD (Optional - if you have raw .h5 files)
         └─→ auto_download_mosdac.py
             Downloads 163 .h5 satellite files (50GB+)

Phase 2: DATA PREPROCESSING (Essential)
         └─→ preprocessor/full_preprocessor.py
             Converts .h5 → frames → sequences
             Configurable: Process 50 or 163 files

Phase 3: MODEL TRAINING (Optional but recommended)
         └─→ train.py
             Trains DDPM model on sequences
             Uses PyTorch Lightning
             
Phase 4: EVALUATION & VISUALIZATION
         ├─→ evaluate.py
         │   Metrics: SSIM, PSNR, MAE, MSE
         └─→ streamlit_app.py
             Interactive dashboard
```

---

## 🔧 STEP 1: Configure Your `.env` File

The `.env` file has been created. Now customize it:

**Open: `d:\Insat_data\.env`**

Key settings to check/modify:

```env
# ── DATA CONFIGURATION ────────────────────────────────────────
# Where your raw satellite data is stored
INSAT_RAW_DIR=./raw

# Where processed frames will be saved (~500MB)
INSAT_PROCESSED_DIR=./processed

# Where training sequences will be saved (~2GB)
INSAT_SEQUENCES_DIR=./sequences

# Results and evaluation outputs
INSAT_RESULTS_DIR=./results
INSAT_EVALUATION_DIR=./evaluation

# Model checkpoints
INSAT_CHECKPOINTS_DIR=./checkpoints

# ── DATA PROCESSING FLEXIBILITY ────────────────────────────────
# How many files to process:
#   - 50   = Process initial 50 files (team task)
#   - 163  = Full dataset
NUM_FILES_TO_PROCESS=50

# ── TRAINING SETTINGS ──────────────────────────────────────────
# Batch size (reduce if GPU memory is limited)
#   - 2  = Very limited GPU (4GB)
#   - 4  = Standard (8GB GPU)
#   - 8  = Better GPU (16GB)
BATCH_SIZE=4

LEARNING_RATE=1e-4
MAX_EPOCHS=50
TRAIN_TEST_SPLIT=0.8
```

**Optional: MOSDAC Credentials** (only if downloading data)
```env
MOSDAC_USERNAME=your_email@example.com
MOSDAC_PASSWORD=your_password
```

---

## 📥 STEP 2: Data Availability Check

### Option A: You already have raw .h5 files

```
If you have .h5 files in: d:\Insat_data\raw\
→ Skip Phase 1 (auto_download_mosdac.py)
→ Go directly to Phase 2 (preprocessing)
```

### Option B: You need to download satellite data

```
Run this ONCE (takes many hours):
$ python auto_download_mosdac.py

This requires:
- MOSDAC account (register at https://www.mosdac.gov.in)
- Internet connection (downloads 50GB+)
- Disk space (at least 60GB)
- MOSDAC credentials in .env
```

### Option C: Demo mode (limited data)

```
If you don't have full data yet:
→ Set NUM_FILES_TO_PROCESS=50
→ Work with the 50 files you have
→ Full pipeline still works
```

---

## 🔄 STEP 3: Preprocess Data (Required)

**Run once to convert raw data into training sequences:**

### Command:
```bash
python preprocessor/full_preprocessor.py
```

### What it does:
```
raw/*.h5 (163+ files, 50GB)
    ↓
    [Extract 3 thermal channels: TIR1, TIR2, WV]
    [Normalize to 0-1 range]
    [Resize to 64×64]
    ↓
processed/*.npy (~500 MB)
    ↓
    [Create 5-frame sliding windows]
    [Each sequence: (5, 3, 64, 64)]
    ↓
sequences/*.npy (~2 GB)
```

### Expected output:
```
Found 50 raw files to process
Channels: ['IMG_TIR1', 'IMG_TIR2', 'IMG_WV']

Processing frames: 100% |████████| 50/50
Saved   : 50
Skipped : 0
Failed  : 0

Creating sequences: 100% |████████| 246/246
Saved   : 246
Skipped : 0

=== Final Verification ===
Frames    : 50
Sequences : 246
GOOD — 246 sequences. Ready for training.
```

### Time estimate:
- 50 files: ~5 minutes
- 163 files: ~15 minutes

---

## 🤖 STEP 4: Train Model (Optional but Recommended)

**Train DDPM model on sequences:**

### Command:
```bash
python train.py
```

### What it does:
```
sequences/*.npy (training data)
    ↓
    [Split: 80% train, 10% val, 10% test]
    [Batch size: from .env]
    [DDPM: Add noise → Predict noise]
    ↓
    Every epoch:
      - Train loss: decreases
      - Val loss: monitored
      - Training curve saved every 10 epochs
    ↓
checkpoints/ (model weights)
results/ (training curves)
```

### Configuration (in .env):
```env
BATCH_SIZE=4              # Adjust for your GPU
LEARNING_RATE=1e-4
MAX_EPOCHS=50
TRAIN_TEST_SPLIT=0.8
```

### GPU Memory requirements:
```
BATCH_SIZE=2  → ~4 GB (minimum)
BATCH_SIZE=4  → ~8 GB (recommended)
BATCH_SIZE=8  → ~16 GB
```

### If you see CUDA out of memory:
```
Edit .env:
BATCH_SIZE=2    # Reduce batch size
```

### Expected output:
```
Model parameters : 15.3M
Train:246 | Val:31 | Test:31

Epoch 1/50  [████████░░] train_loss=0.5432  val_loss=0.4821
Epoch 2/50  [████████░░] train_loss=0.4156  val_loss=0.3945
...
Epoch 50/50 [██████████] train_loss=0.0856  val_loss=0.0796

Best checkpoint: checkpoints/lightning_epoch=44_val_loss=0.0796.ckpt
Training curve: results/lightning_training_curve.png
```

### Time estimate:
- GPU (8GB): ~2-4 hours for 50 epochs
- GPU (16GB): ~1-2 hours
- CPU only: ~20+ hours (not recommended)

---

## 📈 STEP 5: Evaluate Model

**Test model performance on unseen test data:**

### Command:
```bash
python evaluate.py
```

### What it does:
```
Loads trained model checkpoint
For each test sequence:
  - Input: 4 frames (context)
  - Predict: Next frame
  - Compute metrics:
    * SSIM (Structural Similarity)
    * PSNR (Peak Signal-to-Noise Ratio)
    * MAE (Mean Absolute Error)
    * MSE (Mean Squared Error)

Saves:
  - evaluation/ddpm_metrics.csv (metrics)
  - evaluation/ddpm_sample_*.png (visualizations)
```

### Output:
```
Evaluating: 100% |██████████| 31/31

==================================================
DDPM EVALUATION RESULTS
==================================================
Samples   : 31
Mean SSIM : 0.7234  (target > 0.6) ✓
Mean PSNR : 28.45 dB  (target > 25) ✓
Mean MAE  : 0.0342
Mean MSE  : 0.001234

Best SSIM : 0.8901
Worst SSIM: 0.5432

Saved to  : evaluation/
```

### Time estimate:
- ~2-5 minutes

---

## 🎨 STEP 6: Interactive Dashboard

**Visualize predictions in a web interface:**

### Command:
```bash
streamlit run streamlit_app.py
```

### What it opens:
```
Browser: http://localhost:8501

Features:
✓ Load trained model
✓ Select test sequences
✓ Visualize 4 input frames + prediction
✓ Compare with actual next frame
✓ Show difference maps
✓ Optical flow visualization
✓ Performance metrics
✓ Weather analysis
✓ Interactive parameter controls
```

### Features in detail:
- **Sequence Explorer**: Select and view any sequence
- **Predictions**: See model's forecasted frame
- **Metrics**: SSIM, PSNR, MAE, MSE for each sample
- **Visualizations**: Input→Prediction→Actual→Difference
- **Flow Analysis**: Motion vectors between frames
- **Weather Labels**: Cloud severity assessment

### Time to launch:
- First run: ~10 seconds (loads model)
- Subsequent runs: <1 second

---

## 📋 QUICK START CHECKLIST

```
Your Step-by-Step Plan:

Phase 1: SETUP (Right Now)
  ☐ Edit .env file with your settings
  ☐ Verify raw data location (or plan to download)
  
Phase 2: PREPROCESSING (30 min)
  ☐ python preprocessor/full_preprocessor.py
  ☐ Wait for completion
  ☐ Check: sequences/ folder has .npy files
  
Phase 3: TRAINING (2-4 hours with GPU)
  ☐ python train.py
  ☐ Monitor training in terminal
  ☐ Check: checkpoints/ has model files
  
Phase 4: EVALUATION (5 min)
  ☐ python evaluate.py
  ☐ Check: evaluation/ has metrics.csv
  
Phase 5: VISUALIZATION (Ongoing)
  ☐ streamlit run streamlit_app.py
  ☐ Open browser to http://localhost:8501
  ☐ Explore results!
```

---

## 🔧 RUNNING EACH PHASE

### **Phase 1: Optional - Download Data** (Skip if you have data)

```bash
python auto_download_mosdac.py

# Downloads to: d:\Insat_data\raw\
# Size: ~50GB
# Time: 12-24 hours
# Requires: MOSDAC account + .env credentials
```

### **Phase 2: REQUIRED - Preprocess Data**

```bash
python preprocessor/full_preprocessor.py

# Progress: Shows percentage
# Saves to: processed/ and sequences/
# Configurable: NUM_FILES_TO_PROCESS from .env
```

### **Phase 3: OPTIONAL - Train Model**

```bash
python train.py

# Shows live metrics
# Saves checkpoints every epoch
# Can stop anytime with Ctrl+C
# Can resume from checkpoint
```

### **Phase 4: OPTIONAL - Evaluate**

```bash
python evaluate.py

# Requires: Trained model checkpoint
# Outputs: Metrics + visualizations
# Check: evaluation/ folder
```

### **Phase 5: INTERACTIVE - Dashboard**

```bash
streamlit run streamlit_app.py

# Opens in browser (http://localhost:8501)
# Requires: Trained model + sequences
# Press Ctrl+C to stop
```

---

## 🎯 RECOMMENDED WORKFLOW

### For First-Time Testing:

```powershell
# Terminal 1: Preprocessing
python preprocessor/full_preprocessor.py

# Wait for completion...

# Terminal 2: Training (while above runs, or after)
python train.py

# After training completes...

# Terminal 3: Evaluation
python evaluate.py

# Finally: Visualization
streamlit run streamlit_app.py
```

### For Quick Demo (Skip Training):

```powershell
# Just preprocess and visualize
python preprocessor/full_preprocessor.py
streamlit run streamlit_app.py
```

### For Production:

```powershell
# Full pipeline with all 163 files
# 1. Edit .env: NUM_FILES_TO_PROCESS=163
# 2. Run all phases in order
python preprocessor/full_preprocessor.py
python train.py
python evaluate.py
streamlit run streamlit_app.py
```

---

## ⚠️ COMMON ISSUES & SOLUTIONS

### Issue: "ModuleNotFoundError: No module named 'config'"
**Solution:**
```bash
cd d:\Insat_data
python config.py    # Should print configuration
```

### Issue: "CUDA out of memory"
**Solution:**
```
Edit .env:
BATCH_SIZE=2    # Instead of 4

Then retry:
python train.py
```

### Issue: "No sequences found in sequences/ folder"
**Solution:**
```
Run preprocessing first:
python preprocessor/full_preprocessor.py
```

### Issue: "Streamlit app won't load"
**Solution:**
```bash
# Reinstall streamlit
pip install --upgrade streamlit

# Then retry
streamlit run streamlit_app.py
```

### Issue: "Checkpoint file not found"
**Solution:**
```
Make sure you've run:
python train.py    # Generates checkpoints

Check checkpoints/ folder exists
```

---

## 📊 DISK SPACE REQUIREMENTS

```
raw/           50 GB   (raw satellite files - .h5)
processed/    0.5 GB   (individual frames - .npy)
sequences/      2 GB   (training sequences - .npy)
checkpoints/    2 GB   (model weights - .pth)
results/      0.5 GB   (training curves - .png)
evaluation/   0.5 GB   (evaluation results - .png/.csv)
──────────────────────
Total:       ~55 GB    (with all 163 files)

For 50 files:
raw/           15 GB   
processed/    0.2 GB   
sequences/    0.7 GB   
checkpoints/    2 GB   
──────────────────────
Total:       ~18 GB    (much smaller!)
```

---

## 💾 SAVING YOUR WORK

### Important files to backup:
```
checkpoints/lightning_epoch=XX_val_loss=XXX.ckpt
results/lightning_training_curve.png
evaluation/ddpm_metrics.csv
evaluation/ddpm_sample_*.png
```

### Files you can delete (regenerate if needed):
```
processed/*.npy    (regenerate with preprocessor)
sequences/*.npy    (regenerate with preprocessor)
```

---

## 🎓 UNDERSTANDING THE OUTPUT

### Training Metrics:
- **train_loss**: Decreases → Model learning
- **val_loss**: Should also decrease (avoid overfitting)
- **mae**: Mean absolute error between predictions

### Evaluation Metrics:
- **SSIM > 0.7**: Excellent similarity
- **SSIM 0.6-0.7**: Good
- **SSIM < 0.6**: Needs improvement
- **PSNR > 25 dB**: Good image quality

### Dashboard shows:
- Input frames (4 most recent)
- Predicted frame (model output)
- Actual frame (ground truth)
- Difference map (where model is wrong)
- Performance metrics

---

## ✅ YOU'RE READY!

Your project is fully configured. Choose your starting point:

1. **Have raw data?** → Start with Phase 2 (Preprocessing)
2. **Don't have data?** → Start with Phase 1 (Download)
3. **Want quick demo?** → Just run Phases 2 & 5 (Preprocess + Dashboard)
4. **Full experiment?** → Run all Phases 1-5

**Next command to run:**
```bash
python preprocessor/full_preprocessor.py
```

---

**Questions?** Check the documentation:
- README.md - Project overview
- DEPLOYMENT.md - Team deployment
- PRODUCTION_CHECKLIST.md - Changes made
- config.py - Configuration reference
