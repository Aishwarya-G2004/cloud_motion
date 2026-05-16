import os
import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, random_split
from glob import glob
from tqdm import tqdm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import cv2
from torchmetrics.image import (
    StructuralSimilarityIndexMeasure,
    PeakSignalNoiseRatio
)

# Load environment variables from .env file (if it exists)
from dotenv import load_dotenv
load_dotenv()

# Import dynamic configuration
from config import (
    SEQUENCES_DIR,
    BEST_MODEL_DDPM_PATH,
    EVALUATION_DIR,
    CHECKPOINTS_DIR,
    NUM_CHANNELS,
    INPUT_FRAMES,
    IMG_SIZE,
    TIMESTEPS,
    CHANNEL_NAMES,
    DEVICE,
    ensure_dirs
)

# ── Config ─────────────────────────────────────────────────────────────
SEQUENCE_DIR = str(SEQUENCES_DIR)
CKPT_PATH = str(BEST_MODEL_DDPM_PATH)
EVAL_DIR = str(EVALUATION_DIR)
CHANNELS = NUM_CHANNELS
CH_NAMES = CHANNEL_NAMES

ensure_dirs()

# ── DDPM Scheduler ─────────────────────────────────────────────────────
class DDPMScheduler:
    def __init__(self, timesteps=1000):
        self.T         = timesteps
        self.betas     = torch.linspace(1e-4, 0.02, timesteps)
        self.alphas    = 1.0 - self.betas
        self.alpha_bar = torch.cumprod(self.alphas, dim=0)
        self.sqrt_alpha_bar    = torch.sqrt(self.alpha_bar)
        self.sqrt_one_minus_ab = torch.sqrt(1.0 - self.alpha_bar)
        self.alpha_bar_prev    = torch.cat(
            [torch.tensor([1.0]), self.alpha_bar[:-1]]
        )
        self.posterior_variance = (
            self.betas * (1 - self.alpha_bar_prev) /
            (1 - self.alpha_bar)
        )

    def sample_timesteps(self, batch_size):
        return torch.randint(0, self.T, (batch_size,)).long()

    def add_noise(self, x0, t, device):
        noise   = torch.randn_like(x0)
        sqrt_ab = self.sqrt_alpha_bar[t].view(-1,1,1,1).to(device)
        sqrt_om = self.sqrt_one_minus_ab[t].view(-1,1,1,1).to(device)
        return sqrt_ab * x0 + sqrt_om * noise, noise

# ── Model ──────────────────────────────────────────────────────────────
class ConvBlock(torch.nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Conv2d(in_ch, out_ch, 3, padding=1),
            torch.nn.BatchNorm2d(out_ch),
            torch.nn.ReLU(inplace=True),
            torch.nn.Conv2d(out_ch, out_ch, 3, padding=1),
            torch.nn.BatchNorm2d(out_ch),
            torch.nn.ReLU(inplace=True),
        )
    def forward(self, x): return self.net(x)

class TimeEmbedding(torch.nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim
        self.mlp = torch.nn.Sequential(
            torch.nn.Linear(dim, dim * 4),
            torch.nn.SiLU(),
            torch.nn.Linear(dim * 4, dim),
        )
    def forward(self, t):
        half  = self.dim // 2
        freqs = torch.exp(
            -torch.arange(half, device=t.device) *
            (torch.log(torch.tensor(10000.0)) / (half - 1))
        )
        args  = t[:, None].float() * freqs[None]
        embed = torch.cat([torch.sin(args), torch.cos(args)], dim=-1)
        return self.mlp(embed)

class DiffusionUNet(torch.nn.Module):
    def __init__(self, in_ch, out_ch, time_dim=128):
        super().__init__()
        self.time_mlp   = TimeEmbedding(time_dim)
        self.enc1       = ConvBlock(in_ch, 64)
        self.enc2       = ConvBlock(64, 128)
        self.enc3       = ConvBlock(128, 256)
        self.pool       = torch.nn.MaxPool2d(2)
        self.t_proj1    = torch.nn.Linear(time_dim, 64)
        self.t_proj2    = torch.nn.Linear(time_dim, 128)
        self.t_proj3    = torch.nn.Linear(time_dim, 256)
        self.bottleneck = ConvBlock(256, 512)
        self.t_proj_b   = torch.nn.Linear(time_dim, 512)
        self.up3        = torch.nn.ConvTranspose2d(512, 256, 2, stride=2)
        self.dec3       = ConvBlock(512, 256)
        self.up2        = torch.nn.ConvTranspose2d(256, 128, 2, stride=2)
        self.dec2       = ConvBlock(256, 128)
        self.up1        = torch.nn.ConvTranspose2d(128, 64,  2, stride=2)
        self.dec1       = ConvBlock(128, 64)
        self.out        = torch.nn.Conv2d(64, out_ch, 1)

    def forward(self, x, t):
        t_emb = self.time_mlp(t)
        e1    = self.enc1(x) + self.t_proj1(t_emb).view(-1,64,1,1)
        e2    = self.enc2(self.pool(e1)) + \
                self.t_proj2(t_emb).view(-1,128,1,1)
        e3    = self.enc3(self.pool(e2)) + \
                self.t_proj3(t_emb).view(-1,256,1,1)
        b     = self.bottleneck(self.pool(e3)) + \
                self.t_proj_b(t_emb).view(-1,512,1,1)
        d3    = self.dec3(torch.cat([self.up3(b),  e3], dim=1))
        d2    = self.dec2(torch.cat([self.up2(d3), e2], dim=1))
        d1    = self.dec1(torch.cat([self.up1(d2), e1], dim=1))
        return self.out(d1)

# ── DDIM inference ─────────────────────────────────────────────────────
@torch.no_grad()
def ddim_sample(model, cond, scheduler, steps=50):
    ddim_ts = torch.linspace(
        0, scheduler.T - 1, steps, dtype=torch.long
    ).flip(0)
    x = torch.randn(
        cond.shape[0], CHANNELS, IMG_SIZE, IMG_SIZE, device=DEVICE
    )
    for i, t_val in enumerate(ddim_ts):
        t_b        = torch.full(
            (cond.shape[0],), t_val, dtype=torch.long, device=DEVICE
        )
        x_in       = torch.cat([x, cond], dim=1)
        noise_pred = model(x_in, t_b)
        ab         = scheduler.alpha_bar[t_val].to(DEVICE)
        pred_x0    = (x - torch.sqrt(1-ab)*noise_pred) / torch.sqrt(ab)
        pred_x0    = pred_x0.clamp(0, 1)
        if i < len(ddim_ts) - 1:
            t_next  = ddim_ts[i+1]
            ab_next = scheduler.alpha_bar[t_next].to(DEVICE)
            x       = torch.sqrt(ab_next)*pred_x0 + \
                      torch.sqrt(1-ab_next)*noise_pred
        else:
            x = pred_x0
    return x.clamp(0, 1)

# ── Dataset ────────────────────────────────────────────────────────────
class INSATDataset(Dataset):
    def __init__(self, seq_dir):
        self.files = sorted(glob(os.path.join(seq_dir, "*.npy")))
    def __len__(self): return len(self.files)
    def __getitem__(self, idx):
        seq = torch.tensor(
            np.load(self.files[idx]), dtype=torch.float32
        )
        return seq[:INPUT_FRAMES], seq[INPUT_FRAMES]

# ── Load model ─────────────────────────────────────────────────────────
print("Loading DDPM model...")
model = DiffusionUNet(
    in_ch=CHANNELS + INPUT_FRAMES * CHANNELS,
    out_ch=CHANNELS, time_dim=128
).to(DEVICE)

# Find best Lightning checkpoint (lowest val_loss)
import os
from glob import glob
ckpt_files = sorted(glob(os.path.join(str(CHECKPOINTS_DIR), "lightning_*.ckpt")))
if ckpt_files:
    # Extract val_loss from filename: lightning_epoch=48_val_loss=0.0783.ckpt
    best_ckpt = min(ckpt_files, key=lambda x: float(x.split("val_loss=")[1].rstrip(".ckpt")))
    epoch = int(best_ckpt.split("epoch=")[1].split("_")[0])
    val_loss = float(best_ckpt.split("val_loss=")[1].rstrip(".ckpt"))
    print(f"Found best checkpoint: epoch={epoch}, val_loss={val_loss:.4f}")
    
    # Load Lightning checkpoint and strip "model." prefix
    ckpt = torch.load(best_ckpt, map_location=DEVICE)
    state_dict = ckpt['state_dict']
    
    # Remove "model." prefix from all keys (Lightning wraps models with this prefix)
    new_state_dict = {}
    for key, value in state_dict.items():
        if key.startswith("model."):
            new_key = key.replace("model.", "", 1)
            new_state_dict[new_key] = value
        else:
            new_state_dict[key] = value
    
    model.load_state_dict(new_state_dict)
    model.eval()
    scheduler = DDPMScheduler(TIMESTEPS)
    print(f"✓ Model loaded from: {os.path.basename(best_ckpt)}")
else:
    raise FileNotFoundError("No Lightning checkpoints found in checkpoints/ directory. Please run train.py first.")

# ── Test split ─────────────────────────────────────────────────────────
dataset    = INSATDataset(SEQUENCE_DIR)
train_size = int(0.8 * len(dataset))
val_size   = int(0.1 * len(dataset))
test_size  = len(dataset) - train_size - val_size

_, _, test_ds = random_split(
    dataset, [train_size, val_size, test_size],
    generator=torch.Generator().manual_seed(42)
)
test_loader = DataLoader(test_ds, batch_size=1, shuffle=False)
print(f"Test samples : {len(test_ds)}")

ssim_fn = StructuralSimilarityIndexMeasure(data_range=1.0).to(DEVICE)
psnr_fn = PeakSignalNoiseRatio(data_range=1.0).to(DEVICE)

# ── Evaluate ───────────────────────────────────────────────────────────
results = []
print("\nRunning DDPM evaluation (DDIM 50 steps)...")

with torch.no_grad():
    for i, (x, y) in enumerate(tqdm(test_loader, desc="Evaluating")):
        x, y   = x.to(DEVICE), y.to(DEVICE)
        B      = x.shape[0]
        cond   = x.reshape(B, INPUT_FRAMES*CHANNELS, IMG_SIZE, IMG_SIZE)
        pred   = ddim_sample(model, cond, scheduler, steps=50)

        ssim   = ssim_fn(pred, y).item()
        psnr   = psnr_fn(pred, y).item()
        mae    = F.l1_loss(pred, y).item()
        mse    = F.mse_loss(pred, y).item()

        results.append({
            'sample': i,
            'SSIM'  : round(ssim, 4),
            'PSNR'  : round(psnr, 2),
            'MAE'   : round(mae,  4),
            'MSE'   : round(mse,  6),
        })

        # Save comparison + difference map for first 10
        if i < 10:
            pred_np   = pred[0, 0].cpu().numpy()
            actual_np = y[0, 0].cpu().numpy()

            # Difference map
            diff       = np.abs(pred_np - actual_np)
            diff_big   = cv2.resize(
                (diff*255).astype(np.uint8),
                (256, 256), interpolation=cv2.INTER_LANCZOS4
            )
            diff_color = cv2.applyColorMap(diff_big, cv2.COLORMAP_JET)
            diff_rgb   = cv2.cvtColor(diff_color, cv2.COLOR_BGR2RGB)

            fig, axs = plt.subplots(1, 7, figsize=(24, 3))
            for t in range(4):
                axs[t].imshow(
                    x[0,t,0].cpu().numpy(),
                    cmap='gray', vmin=0, vmax=1
                )
                axs[t].set_title(f't-{4-t}', fontsize=9)
                axs[t].axis('off')

            axs[4].imshow(pred_np,   cmap='gray', vmin=0, vmax=1)
            axs[4].set_title(
                f'Predicted\nSSIM={ssim:.3f}',
                fontsize=9, color='blue'
            )
            axs[4].axis('off')

            axs[5].imshow(actual_np, cmap='gray', vmin=0, vmax=1)
            axs[5].set_title('Actual', fontsize=9, color='green')
            axs[5].axis('off')

            axs[6].imshow(diff_rgb)
            axs[6].set_title(
                'Error map\nBlue=low Red=high',
                fontsize=9, color='red'
            )
            axs[6].axis('off')

            plt.suptitle(
                f'Sample {i} | DDPM | '
                f'SSIM={ssim:.4f} | PSNR={psnr:.2f}dB | MAE={mae:.4f}',
                fontsize=9
            )
            plt.tight_layout()
            plt.savefig(
                os.path.join(EVAL_DIR, f'ddpm_sample_{i:03d}.png'),
                dpi=120, bbox_inches='tight'
            )
            plt.close()

# ── Save and print results ─────────────────────────────────────────────
df = pd.DataFrame(results)
df.to_csv(
    os.path.join(EVAL_DIR, 'ddpm_metrics.csv'), index=False
)

print(f"\n{'='*50}")
print(f"DDPM EVALUATION RESULTS")
print(f"{'='*50}")
print(f"Samples   : {len(results)}")
print(f"Mean SSIM : {df['SSIM'].mean():.4f}  (target > 0.6)")
print(f"Mean PSNR : {df['PSNR'].mean():.2f} dB  (target > 25)")
print(f"Mean MAE  : {df['MAE'].mean():.4f}")
print(f"Mean MSE  : {df['MSE'].mean():.6f}")
print(f"Best SSIM : {df['SSIM'].max():.4f}")
print(f"Worst SSIM: {df['SSIM'].min():.4f}")
print(f"\nSaved to  : {EVAL_DIR}")