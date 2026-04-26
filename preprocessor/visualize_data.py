import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from glob import glob
from tqdm import tqdm

# ── Paths ──────────────────────────────────────────────────────────────
PROCESSED_DIR = r"D:\Insat_data\processed"
SEQUENCE_DIR  = r"D:\Insat_data\sequences"
GRID_DIR      = r"D:\Insat_data\images\grids"
GIF_DIR       = r"D:\Insat_data\images\gifs"
SEQ_IMG_DIR   = r"D:\Insat_data\images\sequences"

# 3 channels only — thermal bands
CHANNELS = ['TIR1', 'TIR2', 'WV']

os.makedirs(GRID_DIR,    exist_ok=True)
os.makedirs(GIF_DIR,     exist_ok=True)
os.makedirs(SEQ_IMG_DIR, exist_ok=True)

# ── 1. Channel grids from processed frames ────────────────────────────
def save_grids(max_files=10):
    files = sorted(glob(os.path.join(PROCESSED_DIR, "*.npy")))[:max_files]
    print(f"Saving grids for {len(files)} frames...")

    for file in tqdm(files, desc="Grids"):
        data = np.load(file)   # (3, 64, 64)
        C    = data.shape[0]

        fig, axs = plt.subplots(1, C, figsize=(12, 4))
        for i in range(C):
            axs[i].imshow(data[i], cmap='gray', vmin=0, vmax=1)
            axs[i].set_title(CHANNELS[i], fontsize=11)
            axs[i].axis('off')

        plt.suptitle(os.path.basename(file), fontsize=9)
        plt.tight_layout()
        out = os.path.join(
            GRID_DIR,
            os.path.basename(file).replace('.npy', '_grid.png')
        )
        plt.savefig(out, dpi=120, bbox_inches='tight')
        plt.close()

    print(f"Grids saved → {GRID_DIR}")

# ── 2. Sequence comparison images ─────────────────────────────────────
def save_sequence_images(max_seqs=5):
    seq_files = sorted(
        glob(os.path.join(SEQUENCE_DIR, "*.npy"))
    )[:max_seqs]
    print(f"Saving sequence images for {len(seq_files)} sequences...")

    for seq_file in tqdm(seq_files, desc="Sequence images"):
        # Shape: (5, 3, 64, 64) = (T_total, C, H, W)
        seq     = np.load(seq_file)
        T_total = seq.shape[0]   # 5
        C       = seq.shape[1]   # 3

        for ch in range(C):
            fig, axs = plt.subplots(1, T_total, figsize=(15, 3))

            for t in range(T_total):
                axs[t].imshow(seq[t, ch], cmap='gray', vmin=0, vmax=1)
                if t < T_total - 1:
                    label = f"t-{T_total - 1 - t}"
                    color = 'black'
                else:
                    label = "TARGET"
                    color = 'red'
                axs[t].set_title(label, fontsize=10, color=color)
                axs[t].axis('off')

            plt.suptitle(
                f"{os.path.basename(seq_file)} | "
                f"Channel: {CHANNELS[ch]}",
                fontsize=9
            )
            plt.tight_layout()
            seq_idx = os.path.basename(seq_file).replace('.npy', '')
            out = os.path.join(
                SEQ_IMG_DIR,
                f"{seq_idx}_ch{ch}_{CHANNELS[ch]}.png"
            )
            plt.savefig(out, dpi=120, bbox_inches='tight')
            plt.close()

    print(f"Sequence images saved → {SEQ_IMG_DIR}")

# ── 3. GIF for one sequence ───────────────────────────────────────────
def save_gif(seq_idx=0, channel=0):
    seq_path = os.path.join(SEQUENCE_DIR, f"seq_{seq_idx:03d}.npy")
    if not os.path.exists(seq_path):
        print(f"Not found: {seq_path}")
        return

    # Shape: (5, 3, 64, 64)
    seq    = np.load(seq_path)
    T      = seq.shape[0]
    frames = []

    for t in range(T):
        frame = seq[t, channel]                        # (64, 64)
        img   = (frame * 255).astype(np.uint8)
        img   = Image.fromarray(img).resize(
            (256, 256), Image.NEAREST
        ).convert("L")
        draw  = ImageDraw.Draw(img)
        if t < T - 1:
            label = f"{CHANNELS[channel]} | t-{T-1-t}"
        else:
            label = f"{CHANNELS[channel]} | TARGET"
        draw.text((8, 8), label, fill=255)
        frames.append(img)

    out = os.path.join(
        GIF_DIR,
        f"seq_{seq_idx:03d}_ch{channel}_{CHANNELS[channel]}.gif"
    )
    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=500,
        loop=0
    )
    print(f"GIF saved → {out}")

# ── 4. GIFs for all sequences ─────────────────────────────────────────
def save_all_gifs(max_seqs=10):
    seq_files = sorted(
        glob(os.path.join(SEQUENCE_DIR, "*.npy"))
    )[:max_seqs]
    print(f"Generating GIFs for {len(seq_files)} sequences...")

    for seq_file in tqdm(seq_files, desc="GIFs"):
        idx = int(
            os.path.basename(seq_file).split('_')[1].split('.')[0]
        )
        for ch in range(len(CHANNELS)):
            save_gif(seq_idx=idx, channel=ch)

    print(f"All GIFs saved → {GIF_DIR}")

# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("INSAT-3DR Cloud Motion — Visualizer")
    print(f"Channels: {CHANNELS}")
    print("=" * 50)

    print("\n=== Step 1: Channel grids ===")
    save_grids(max_files=10)

    print("\n=== Step 2: Sequence images ===")
    save_sequence_images(max_seqs=5)

    print("\n=== Step 3: GIF animations ===")
    save_all_gifs(max_seqs=10)

    print("\nDone. Check D:\\Insat_data\\images\\")