import os
import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, random_split
from glob import glob
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ── Config ─────────────────────────────────────────────────────────────
SEQUENCE_DIR = r"D:\Insat_data\sequences"
RESULTS_DIR  = r"D:\Insat_data\results"
CKPT_DIR     = r"D:\Insat_data\checkpoints"
CHANNELS     = 3
INPUT_FRAMES = 4
IMG_SIZE     = 64
BATCH_SIZE   = 4
LR           = 1e-4
MAX_EPOCHS   = 50
TIMESTEPS    = 1000

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(CKPT_DIR,    exist_ok=True)

print(f"GPU: {torch.cuda.is_available()}")

# ── DDPM Scheduler ─────────────────────────────────────────────────────
class DDPMScheduler:
    def __init__(self, timesteps=1000):
        self.T             = timesteps
        self.betas         = torch.linspace(1e-4, 0.02, timesteps)
        self.alphas        = 1.0 - self.betas
        self.alpha_bar     = torch.cumprod(self.alphas, dim=0)
        self.sqrt_ab       = torch.sqrt(self.alpha_bar)
        self.sqrt_one_m_ab = torch.sqrt(1.0 - self.alpha_bar)
        self.alpha_bar_prev = torch.cat(
            [torch.tensor([1.0]), self.alpha_bar[:-1]]
        )
        self.posterior_var = (
            self.betas *
            (1 - self.alpha_bar_prev) /
            (1 - self.alpha_bar)
        )

    def add_noise(self, x0, t, device):
        noise   = torch.randn_like(x0)
        sqrt_ab = self.sqrt_ab[t].view(-1,1,1,1).to(device)
        sqrt_om = self.sqrt_one_m_ab[t].view(-1,1,1,1).to(device)
        return sqrt_ab * x0 + sqrt_om * noise, noise

    def sample_timesteps(self, B):
        return torch.randint(0, self.T, (B,)).long()

# ── UNet components ────────────────────────────────────────────────────
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
        e1 = self.enc1(x) + \
             self.t_proj1(t_emb).view(-1, 64,  1, 1)
        e2 = self.enc2(self.pool(e1)) + \
             self.t_proj2(t_emb).view(-1, 128, 1, 1)
        e3 = self.enc3(self.pool(e2)) + \
             self.t_proj3(t_emb).view(-1, 256, 1, 1)
        b  = self.bottleneck(self.pool(e3)) + \
             self.t_proj_b(t_emb).view(-1, 512, 1, 1)
        d3 = self.dec3(torch.cat([self.up3(b),  e3], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d3), e2], dim=1))
        d1 = self.dec1(torch.cat([self.up1(d2), e1], dim=1))
        return self.out(d1)

# ── Dataset ────────────────────────────────────────────────────────────
class INSATDataset(Dataset):
    def __init__(self, seq_dir):
        self.files = sorted(glob(os.path.join(seq_dir, "*.npy")))
        print(f"Loaded {len(self.files)} sequences")

    def __len__(self): return len(self.files)

    def __getitem__(self, idx):
        seq = torch.tensor(
            np.load(self.files[idx]), dtype=torch.float32
        )
        return seq[:INPUT_FRAMES], seq[INPUT_FRAMES]

# ── Lightning Module ───────────────────────────────────────────────────
class CloudDiffusionLightning(pl.LightningModule):
    def __init__(self):
        super().__init__()
        self.model = DiffusionUNet(
            in_ch    = CHANNELS + INPUT_FRAMES * CHANNELS,
            out_ch   = CHANNELS,
            time_dim = 128
        )
        self.scheduler = DDPMScheduler(TIMESTEPS)
        self.train_losses = []
        self.val_losses   = []
        self.save_hyperparameters()

    def forward(self, x, t):
        return self.model(x, t)

    def training_step(self, batch, batch_idx):
        x, y = batch
        B    = x.shape[0]
        cond = x.reshape(
            B, INPUT_FRAMES * CHANNELS, IMG_SIZE, IMG_SIZE
        )
        t              = self.scheduler.sample_timesteps(B).to(self.device)
        noisy_y, noise = self.scheduler.add_noise(y, t, self.device)
        x_in           = torch.cat([noisy_y, cond], dim=1)
        noise_pred     = self.model(x_in, t)
        mse  = F.mse_loss(noise_pred, noise)
        mae  = F.l1_loss(noise_pred, noise)
        loss = mse + 0.5 * mae
        self.log("train_loss", loss, prog_bar=True, on_epoch=True)
        self.log("train_mae",  mae,  prog_bar=True, on_epoch=True)
        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        B    = x.shape[0]
        cond = x.reshape(
            B, INPUT_FRAMES * CHANNELS, IMG_SIZE, IMG_SIZE
        )
        t              = self.scheduler.sample_timesteps(B).to(self.device)
        noisy_y, noise = self.scheduler.add_noise(y, t, self.device)
        x_in           = torch.cat([noisy_y, cond], dim=1)
        noise_pred     = self.model(x_in, t)
        loss = F.mse_loss(noise_pred, noise) + \
               0.5 * F.l1_loss(noise_pred, noise)
        self.log("val_loss", loss, prog_bar=True, on_epoch=True)
        return loss

    def on_train_epoch_end(self):
        train_loss = self.trainer.callback_metrics.get("train_loss")
        val_loss   = self.trainer.callback_metrics.get("val_loss")
        if train_loss: self.train_losses.append(float(train_loss))
        if val_loss:   self.val_losses.append(float(val_loss))

        # Save training curve every 10 epochs
        if (self.current_epoch + 1) % 10 == 0:
            self._save_training_curve()

    def _save_training_curve(self):
        if len(self.train_losses) < 2:
            return
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(self.train_losses, label='Train Loss', color='blue')
        ax.plot(self.val_losses,   label='Val Loss',   color='orange')
        ax.set_title('DDPM Training — PyTorch Lightning')
        ax.set_xlabel('Epoch')
        ax.set_ylabel('Loss')
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        plt.savefig(
            os.path.join(RESULTS_DIR, 'lightning_training_curve.png'),
            dpi=120
        )
        plt.close()

    def configure_optimizers(self):
        opt   = torch.optim.AdamW(
            self.parameters(),
            lr=LR, weight_decay=1e-4
        )
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(
            opt, T_max=MAX_EPOCHS
        )
        return {
            "optimizer"   : opt,
            "lr_scheduler": {
                "scheduler": sched,
                "interval" : "epoch"
            }
        }

# ── Main ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    dataset    = INSATDataset(SEQUENCE_DIR)
    train_size = int(0.8 * len(dataset))
    val_size   = int(0.1 * len(dataset))
    test_size  = len(dataset) - train_size - val_size

    train_ds, val_ds, _ = random_split(
        dataset,
        [train_size, val_size, test_size],
        generator=torch.Generator().manual_seed(42)
    )

    train_loader = DataLoader(
        train_ds, batch_size=BATCH_SIZE,
        shuffle=True, num_workers=0, pin_memory=True
    )
    val_loader = DataLoader(
        val_ds, batch_size=BATCH_SIZE,
        shuffle=False, num_workers=0
    )

    model = CloudDiffusionLightning()
    params = sum(
        p.numel() for p in model.parameters()
    ) / 1e6
    print(f"Model parameters : {params:.1f}M")

    checkpoint_cb = ModelCheckpoint(
        dirpath   = CKPT_DIR,
        filename  = "lightning_{epoch:02d}_{val_loss:.4f}",
        monitor   = "val_loss",
        mode      = "min",
        save_top_k= 3,
        verbose   = True
    )

    early_stop_cb = EarlyStopping(
        monitor  = "val_loss",
        patience = 10,
        mode     = "min",
        verbose  = True
    )

    trainer = pl.Trainer(
        max_epochs        = MAX_EPOCHS,
        accelerator       = "gpu" if torch.cuda.is_available() else "cpu",
        devices           = 1,
        callbacks         = [checkpoint_cb, early_stop_cb],
        log_every_n_steps = 5,
        default_root_dir  = CKPT_DIR,
    )

    print(f"\nTrain:{len(train_ds)} | Val:{len(val_ds)} | Test:{test_size}")
    print("Starting PyTorch Lightning DDPM training...\n")
    trainer.fit(model, train_loader, val_loader)

    print(f"\nBest checkpoint : {checkpoint_cb.best_model_path}")
    print(f"Training curve  : {RESULTS_DIR}\\lightning_training_curve.png")