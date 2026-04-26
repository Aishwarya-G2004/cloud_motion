# MOSDAC Data Download Setup Guide

## Overview

This project uses satellite data from India's INSAT3DR satellite, accessed through the MOSDAC (Meteorological and Oceanographic Satellite Data Archival Centre) portal.

## MOSDAC Account Setup

### Step 1: Create MOSDAC Account

1. Visit [MOSDAC Portal](https://www.mosdac.gov.in)
2. Click "Sign Up" and register with:
   - Email address
   - Password
   - Organization details
3. Verify your email
4. Log in to your account

### Step 2: Find Data Ordering Path

1. Log in to MOSDAC portal
2. Navigate to **Download → Order**
3. Select:
   - **Satellite**: INSAT-3DR
   - **Product**: 3RIMG (Full Disk Image)
   - **Date Range**: Your desired dates
   - **Channels**: TIR1, TIR2, WV (thermal + water vapor)
4. Place order and note the **Order Path** (e.g., `/Order/Apr26_178218`)

### Step 3: Configure Download Script

Edit `auto_download_mosdac.py`:

```python
USERNAME    = "your_email@example.com"      # Your MOSDAC login email
PASSWORD    = "your_password"               # Your MOSDAC password
SAVE_DIR    = r"D:\Insat_data\raw"         # Where to save .h5 files
FOLDER_PATH = "/Order/Apr26_178218"        # Your order path from Step 2
```

**Better: Use Environment Variables** (Recommended)

```bash
# Linux/macOS
export MOSDAC_USERNAME="your_email@example.com"
export MOSDAC_PASSWORD="your_password"

# Windows PowerShell
$env:MOSDAC_USERNAME="your_email@example.com"
$env:MOSDAC_PASSWORD="your_password"
```

Then update script:
```python
import os
USERNAME = os.getenv("MOSDAC_USERNAME")
PASSWORD = os.getenv("MOSDAC_PASSWORD")
```

## Downloading Data

### Option 1: Download via Script

```bash
python auto_download_mosdac.py
```

**What it does:**
1. Authenticates with MOSDAC
2. Browses the ordered data folder
3. Downloads all .h5 files to `raw/` directory
4. Shows download progress

### Option 2: Manual Download

1. Log in to MOSDAC portal
2. Navigate to your order
3. Right-click and download each file individually
4. Save to `raw/` directory

## Data Format

### File Structure

Downloaded files are named: `3RIMG_DDMMMYYYY_HHMM_L1C_SGP_V01R00.h5`

Example: `3RIMG_26APR2026_1230_L1C_SGP_V01R00.h5`

### Available Channels in H5 File

```
IMG_VIS    - Visible (black at night, 0.5-1.0 µm)
IMG_SWIR   - Short-wave IR (dim at night, 1.6-2.3 µm)
IMG_TIR1   - Thermal IR 1 (24/7, 10.2-11.2 µm) ✓ USED
IMG_TIR2   - Thermal IR 2 (24/7, 11.5-12.5 µm) ✓ USED
IMG_WV     - Water Vapor (24/7, 6.2-7.1 µm)   ✓ USED
```

This project uses **TIR1, TIR2, WV** channels as they work 24/7.

### Inspect Downloaded H5 Files

```bash
python inspect_all_h5.py
```

Shows:
- File size
- Available channels
- Data dimensions
- Value ranges
- Quality issues

## Data Preprocessing

After downloading:

```bash
python preprocessor/full_preprocessor.py
```

This will:
1. Extract TIR1, TIR2, WV channels
2. Normalize to 0-1 range
3. Resize to 64×64 pixels
4. Create 5-frame sequences (4 input + 1 target)
5. Save as NumPy arrays and pickle files

Output:
- `processed/`: Individual frames as .npy files
- `sequences/`: Sequence collections as .pkl files

## Data Statistics

Typical dataset characteristics:

```
Number of frames per day: ~288 (every 5 minutes)
Spatial resolution: 4 km at nadir (64×64 at 1 km²)
Temporal resolution: 5 minutes
Dynamic range: 0-65535 (16-bit)
Data type: uint16 (HDF5) → float32 (processed)
```

## Troubleshooting Download Issues

### Login Fails
- Verify credentials are correct
- Check internet connection
- Ensure account is active
- Try manual login at mosdac.gov.in first

### Slow Download Speed
- Check internet bandwidth
- Try downloading smaller date ranges first
- Consider scheduling downloads during off-peak hours

### Connection Timeouts
```python
# Edit auto_download_mosdac.py:
import requests
session = requests.Session()
session.timeout = 60  # Increase timeout to 60 seconds
```

### Corrupt H5 Files
Files with issues will be skipped during preprocessing:
```
Failed: 3RIMG_26APR2026_1230_L1C_SGP_V01R00.h5 — Missing IMG_TIR1
```

Check `failed_files.txt` after running `full_preprocessor.py`

## Disk Space Requirements

```
Typical sizes for 1 day of data:
- Raw (.h5 files):      ~15-20 GB (288 files × 50-70 MB)
- Processed (.npy):     ~3-4 GB   (288 files × 12 MB)
- Sequences (.pkl):     ~3-4 GB   (284 sequences × 12 MB)

Total for 30 days: ~1.5 TB
```

## Data Quality Notes

**Cloud Detection Performance**:
- TIR1 is best for cloud top temperature
- TIR2 provides surface temperature information
- WV captures atmospheric moisture patterns

**Challenges**:
- Thin clouds may appear transparent
- Nighttime observations lack visible channel info
- Sensor degradation over time
- Occasional data gaps due to satellite maintenance

## Data Privacy & Usage

- MOSDAC data is publicly available
- Proper attribution required in publications
- Follow [MOSDAC Terms of Service](https://www.mosdac.gov.in/about-us/terms-of-service)
- No commercial use without permission

## References

- [MOSDAC Data Portal](https://www.mosdac.gov.in)
- [INSAT3DR User Guide](https://mausam.imd.gov.in/about-us/about-imd-satellites)
- [INSAT3DR Technical Documentation](https://www.mausam.imd.gov.in/Satellite_insync/INSAT3DR_Intro.pdf)

## Next Steps

1. Create MOSDAC account
2. Order data for your date range
3. Run `auto_download_mosdac.py` to download
4. Run `preprocessor/full_preprocessor.py` to process
5. Train model with `train.py`

---

For issues with MOSDAC, contact: [MOSDAC Support](https://www.mosdac.gov.in/about-us/contact-us)
