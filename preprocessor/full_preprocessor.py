import os
import numpy as np
import h5py
import cv2
from glob import glob
from tqdm import tqdm

# Load environment variables from .env file (if it exists)
from dotenv import load_dotenv
load_dotenv()

# Import dynamic configuration
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    CHANNELS,
    RESIZE_SHAPE,
    INPUT_FRAMES,
    TARGET_FRAMES,
    TOTAL_WINDOW,
    RAW_DIR,
    PROCESSED_DIR,
    SEQUENCES_DIR,
    NUM_FILES_TO_PROCESS,
    ensure_dirs
)

# ── Configuration ──────────────────────────────────────────────────────
# Using only thermal channels — TIR1, TIR2, WV work 24/7
# VIS and SWIR removed — completely black at night (UTC 0000-0600)

ensure_dirs()

# ── Normalize band to 0-1 ─────────────────────────────────────────────
def normalize_band(band):
    band = band.astype(np.float32)
    mn   = np.nanmin(band)
    mx   = np.nanmax(band)
    if mx - mn < 1e-5:
        return np.zeros_like(band)
    return (band - mn) / (mx - mn)

# ── Resize to 64x64 ───────────────────────────────────────────────────
def resize_band(band):
    if band.ndim == 3:
        band = band[0]
    band = band.astype(np.float32)
    return cv2.resize(band, RESIZE_SHAPE, interpolation=cv2.INTER_AREA)

# ── Process one .h5 file → (3, 64, 64) ───────────────────────────────
def process_file(file_path):
    try:
        with h5py.File(file_path, 'r') as f:
            bands = []
            for ch in CHANNELS:
                if ch not in f:
                    print(f"  Missing {ch} in {os.path.basename(file_path)}")
                    return None
                band = f[ch][:]
                if band.size == 0 or np.nanmax(band) == 0:
                    print(f"  Empty {ch} in {os.path.basename(file_path)}")
                    return None
                norm    = normalize_band(band)
                resized = resize_band(norm)
                bands.append(resized)
            frame = np.stack(bands, axis=0)   # (3, 64, 64)
            return frame
    except Exception as e:
        print(f"  Failed: {os.path.basename(file_path)} — {e}")
        return None

# ── Step 1: Preprocess all .h5 → .npy frames ─────────────────────────
def preprocess_all_frames():
    raw_files = sorted(glob(os.path.join(str(RAW_DIR), "*.h5")))
    
    # Limit to NUM_FILES_TO_PROCESS (supports flexible team workload)
    if NUM_FILES_TO_PROCESS < len(raw_files):
        raw_files = raw_files[:NUM_FILES_TO_PROCESS]
        print(f"Processing limited set: {NUM_FILES_TO_PROCESS} files (out of {len(sorted(glob(os.path.join(str(RAW_DIR), '*.h5'))))} available)")
    
    print(f"Found {len(raw_files)} raw files to process")
    print(f"Channels: {CHANNELS}")
    print(f"Output shape per frame: ({len(CHANNELS)}, {RESIZE_SHAPE[0]}, {RESIZE_SHAPE[1]})\n")

    saved   = 0
    skipped = 0
    failed  = 0

    for i, file in enumerate(tqdm(raw_files, desc="Processing frames")):
        out_path = os.path.join(str(PROCESSED_DIR), f"frame_{i:03d}.npy")

        if os.path.exists(out_path):
            skipped += 1
            continue

        frame = process_file(file)
        if frame is not None:
            np.save(out_path, frame)
            saved += 1
        else:
            failed += 1

    print(f"\nSaved   : {saved}")
    print(f"Skipped : {skipped} (already existed)")
    print(f"Failed  : {failed} (corrupt or missing channels)")
    print(f"Total frames in processed/ : {saved + skipped}")
    return saved + skipped

# ── Step 2: Create sliding window sequences ───────────────────────────
def create_sequences():
    frame_files = sorted(glob(os.path.join(str(PROCESSED_DIR), "*.npy")))
    n_frames    = len(frame_files)
    total_seqs  = n_frames - TOTAL_WINDOW + 1

    if total_seqs <= 0:
        print(f"Not enough frames ({n_frames}). Need at least {TOTAL_WINDOW}.")
        return 0

    print(f"Frames available : {n_frames}")
    print(f"Sequences to create : {total_seqs}")
    print(f"Each sequence shape : ({TOTAL_WINDOW}, {len(CHANNELS)}, {RESIZE_SHAPE[0]}, {RESIZE_SHAPE[1]})\n")

    saved   = 0
    skipped = 0

    for i in tqdm(range(total_seqs), desc="Creating sequences"):
        out_path = os.path.join(str(SEQUENCES_DIR), f"seq_{i:03d}.npy")

        if os.path.exists(out_path):
            skipped += 1
            continue

        frames = []
        valid  = True

        for j in range(TOTAL_WINDOW):
            frame = np.load(frame_files[i + j])
            if frame.shape != (len(CHANNELS), RESIZE_SHAPE[0], RESIZE_SHAPE[1]):
                print(f"\n  Wrong shape {frame.shape} at index {i+j} — skipping")
                valid = False
                break
            frames.append(frame)

        if not valid:
            continue

        # Stack into (T_total, C, H, W) = (5, 3, 64, 64)
        # seq[0] = oldest frame (t-4)
        # seq[1] = t-3
        # seq[2] = t-2
        # seq[3] = t-1  (most recent input)
        # seq[4] = TARGET frame model must predict
        seq = np.stack(frames, axis=0)
        np.save(out_path, seq)
        saved += 1

    print(f"\nSaved   : {saved}")
    print(f"Skipped : {skipped} (already existed)")
    return saved + skipped

# ── Step 3: Verify output ─────────────────────────────────────────────
def verify_output():
    frames = sorted(glob(os.path.join(str(PROCESSED_DIR), "*.npy")))
    seqs   = sorted(glob(os.path.join(str(SEQUENCES_DIR),  "*.npy")))

    print(f"\n=== Final Verification ===")
    print(f"Frames    : {len(frames)}")
    print(f"Sequences : {len(seqs)}")

    if frames:
        f      = np.load(frames[0])
        ok     = f.shape == (len(CHANNELS), RESIZE_SHAPE[0], RESIZE_SHAPE[1])
        status = "OK" if ok else "ERROR"
        print(f"\nFrame shape    : {f.shape}")
        print(f"Expected       : ({len(CHANNELS)}, {RESIZE_SHAPE[0]}, {RESIZE_SHAPE[1]})  [{status}]")
        print(f"Value range    : min={f.min():.3f}  max={f.max():.3f}")

    if seqs:
        s      = np.load(seqs[0])
        ok     = s.shape == (TOTAL_WINDOW, len(CHANNELS), RESIZE_SHAPE[0], RESIZE_SHAPE[1])
        status = "OK" if ok else "ERROR"
        print(f"\nSequence shape : {s.shape}")
        print(f"Expected       : ({TOTAL_WINDOW}, {len(CHANNELS)}, {RESIZE_SHAPE[0]}, {RESIZE_SHAPE[1]})  [{status}]")
        print(f"  seq[0:4]     : input frames fed to model")
        print(f"  seq[4]       : target frame model must predict")
        print(f"Value range    : min={s.min():.3f}  max={s.max():.3f}")

    print()
    if len(seqs) == 0:
        print("ERROR — No sequences created. Check processed folder.")
    elif len(seqs) < 20:
        print(f"WARNING — Only {len(seqs)} sequences. Need more data.")
    elif len(seqs) < 50:
        print(f"OK — {len(seqs)} sequences. Acceptable for prototype.")
    else:
        print(f"GOOD — {len(seqs)} sequences. Ready for training.")

# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 70)
    print("INSAT-3DR Cloud Motion — Data Preprocessor")
    print("=" * 70)
    print(f"Configuration: Process up to {NUM_FILES_TO_PROCESS} files\n")

    print("=== STEP 1: Preprocessing raw .h5 files ===")
    preprocess_all_frames()

    print("\n=== STEP 2: Creating sequences ===")
    create_sequences()

    print("\n=== STEP 3: Verifying output ===")
    verify_output()

# ── Process one .h5 file → (3, 64, 64) ───────────────────────────────
def process_file(file_path):
    try:
        with h5py.File(file_path, 'r') as f:
            bands = []
            for ch in CHANNELS:
                if ch not in f:
                    print(f"  Missing {ch} in {os.path.basename(file_path)}")
                    return None
                band = f[ch][:]
                if band.size == 0 or np.nanmax(band) == 0:
                    print(f"  Empty {ch} in {os.path.basename(file_path)}")
                    return None
                norm    = normalize_band(band)
                resized = resize_band(norm)
                bands.append(resized)
            frame = np.stack(bands, axis=0)   # (3, 64, 64)
            return frame
    except Exception as e:
        print(f"  Failed: {os.path.basename(file_path)} — {e}")
        return None

# ── Step 1: Preprocess all .h5 → .npy frames ─────────────────────────
def preprocess_all_frames():
    raw_files = sorted(glob(os.path.join(RAW_DIR, "*.h5")))
    print(f"Found {len(raw_files)} raw files")
    print(f"Channels: {CHANNELS}")
    print(f"Output shape per frame: ({len(CHANNELS)}, 64, 64)\n")

    saved   = 0
    skipped = 0
    failed  = 0

    for i, file in enumerate(tqdm(raw_files, desc="Processing frames")):
        out_path = os.path.join(PROCESSED_DIR, f"frame_{i:03d}.npy")

        if os.path.exists(out_path):
            skipped += 1
            continue

        frame = process_file(file)
        if frame is not None:
            np.save(out_path, frame)
            saved += 1
        else:
            failed += 1

    print(f"\nSaved   : {saved}")
    print(f"Skipped : {skipped} (already existed)")
    print(f"Failed  : {failed} (corrupt or missing channels)")
    print(f"Total frames in processed/ : {saved + skipped}")
    return saved + skipped

# ── Step 2: Create sliding window sequences ───────────────────────────
def create_sequences():
    frame_files = sorted(glob(os.path.join(PROCESSED_DIR, "*.npy")))
    n_frames    = len(frame_files)
    total_seqs  = n_frames - TOTAL_WINDOW + 1

    if total_seqs <= 0:
        print(f"Not enough frames ({n_frames}). Need at least {TOTAL_WINDOW}.")
        return 0

    print(f"Frames available : {n_frames}")
    print(f"Sequences to create : {total_seqs}")
    print(f"Each sequence shape : ({TOTAL_WINDOW}, {len(CHANNELS)}, 64, 64)\n")

    saved   = 0
    skipped = 0

    for i in tqdm(range(total_seqs), desc="Creating sequences"):
        out_path = os.path.join(str(SEQUENCES_DIR), f"seq_{i:03d}.npy")

        if os.path.exists(out_path):
            skipped += 1
            continue

        frames = []
        valid  = True

        for j in range(TOTAL_WINDOW):
            frame = np.load(frame_files[i + j])
            if frame.shape != (len(CHANNELS), 64, 64):
                print(f"\n  Wrong shape {frame.shape} at index {i+j} — skipping")
                valid = False
                break
            frames.append(frame)

        if not valid:
            continue

        # Stack into (T_total, C, H, W) = (5, 3, 64, 64)
        # seq[0] = oldest frame (t-4)
        # seq[1] = t-3
        # seq[2] = t-2
        # seq[3] = t-1  (most recent input)
        # seq[4] = TARGET frame model must predict
        seq = np.stack(frames, axis=0)
        np.save(out_path, seq)
        saved += 1

    print(f"\nSaved   : {saved}")
    print(f"Skipped : {skipped} (already existed)")
    return saved + skipped

# ── Step 3: Verify output ─────────────────────────────────────────────
def verify_output():
    frames = sorted(glob(os.path.join(PROCESSED_DIR, "*.npy")))
    seqs   = sorted(glob(os.path.join(str(SEQUENCES_DIR),  "*.npy")))

    print(f"\n=== Final Verification ===")
    print(f"Frames    : {len(frames)}")
    print(f"Sequences : {len(seqs)}")

    if frames:
        f      = np.load(frames[0])
        ok     = f.shape == (len(CHANNELS), 64, 64)
        status = "OK" if ok else "ERROR"
        print(f"\nFrame shape    : {f.shape}")
        print(f"Expected       : ({len(CHANNELS)}, 64, 64)  [{status}]")
        print(f"Value range    : min={f.min():.3f}  max={f.max():.3f}")

    if seqs:
        s      = np.load(seqs[0])
        ok     = s.shape == (TOTAL_WINDOW, len(CHANNELS), 64, 64)
        status = "OK" if ok else "ERROR"
        print(f"\nSequence shape : {s.shape}")
        print(f"Expected       : ({TOTAL_WINDOW}, {len(CHANNELS)}, 64, 64)  [{status}]")
        print(f"  seq[0:4]     : input frames fed to model")
        print(f"  seq[4]       : target frame model must predict")
        print(f"Value range    : min={s.min():.3f}  max={s.max():.3f}")

    print()
    if len(seqs) == 0:
        print("ERROR — No sequences created. Check processed folder.")
    elif len(seqs) < 20:
        print(f"WARNING — Only {len(seqs)} sequences. Need more data.")
    elif len(seqs) < 50:
        print(f"OK — {len(seqs)} sequences. Acceptable for prototype.")
    else:
        print(f"GOOD — {len(seqs)} sequences. Ready for training.")

# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("INSAT-3DR Cloud Motion — Data Preprocessor")
    print("=" * 50)

    print("\n=== STEP 1: Preprocessing raw .h5 files ===")
    preprocess_all_frames()

    print("\n=== STEP 2: Creating sequences ===")
    create_sequences()

    print("\n=== STEP 3: Verifying output ===")
    verify_output()