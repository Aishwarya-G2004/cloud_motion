import requests
import os
import re
import time
import base64
from pathlib import Path

# Load environment variables from .env file (if it exists)
from dotenv import load_dotenv
load_dotenv()

# Import dynamic configuration
from config import (
    RAW_DIR,
    MOSDAC_USERNAME,
    MOSDAC_PASSWORD,
    MOSDAC_FOLDER_PATH,
    MOSDAC_BASE_URL,
    ensure_dirs
)

# ── Configuration ──────────────────────────────────────────────────────
USERNAME    = MOSDAC_USERNAME
PASSWORD    = MOSDAC_PASSWORD
SAVE_DIR    = str(RAW_DIR)
FOLDER_PATH = MOSDAC_FOLDER_PATH
BASE_URL    = MOSDAC_BASE_URL

# Validate credentials
if not USERNAME or not PASSWORD:
    print("❌ ERROR: MOSDAC credentials not found!")
    print("   Please set MOSDAC_USERNAME and MOSDAC_PASSWORD in .env file")
    print("   Copy .env.example to .env and fill in your credentials")
    exit(1)

ensure_dirs()

Path(SAVE_DIR).mkdir(parents=True, exist_ok=True)
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

print("="*70)
print("INSAT-3DR MOSDAC Automated Downloader")
print("="*70)
print(f"Username : {USERNAME}")
print(f"Save Dir : {SAVE_DIR}\n")

# ── Step 1: Login ──────────────────────────────────────────────────────
print("Logging in...")
resp       = session.get(f"{BASE_URL}/download/", allow_redirects=True)
action_url = re.search(r'action="([^"]+)"', resp.text).group(1).replace("&amp;","&")
session.post(action_url, data={
    "username": USERNAME,
    "password": PASSWORD,
    "credentialId": ""
}, allow_redirects=True)
print("Login done.")

# ── Step 2: Generate all 750 filenames ────────────────────────────────
# Files are named: 3RIMG_DDMMMYYYY_HHMM_L1C_SGP_V01R00.h5
# Every 30 mins from 0015 to 2345, July 1-15 2025
from datetime import datetime, timedelta

def generate_filenames():
    filenames = []
    start = datetime(2025, 7, 1, 0, 15)
    end   = datetime(2025, 7, 15, 23, 45)
    current = start
    months = ["JAN","FEB","MAR","APR","MAY","JUN",
              "JUL","AUG","SEP","OCT","NOV","DEC"]
    while current <= end:
        dd  = current.strftime("%d")
        mmm = months[current.month - 1]
        yyyy = current.strftime("%Y")
        hhmm = current.strftime("%H%M")
        fname = f"3RIMG_{dd}{mmm}{yyyy}_{hhmm}_L1C_SGP_V01R00.h5"
        filenames.append(fname)
        current += timedelta(minutes=30)
    return filenames

h5_files = generate_filenames()
print(f"Generated {len(h5_files)} filenames to download.")

# ── Step 3: Download each file ─────────────────────────────────────────
def make_url(filename):
    full_path = f"{FOLDER_PATH}/{filename}"
    encoded   = base64.b64encode(full_path.encode()).decode()
    return f"{BASE_URL}/download/?r=/download&path={encoded}"

failed  = []
skipped = 0

for i, filename in enumerate(h5_files):
    save_path = os.path.join(SAVE_DIR, filename)

    if os.path.exists(save_path) and os.path.getsize(save_path) > 1024*1024:
        skipped += 1
        print(f"[{i+1}/{len(h5_files)}] Skipping (exists): {filename}")
        continue

    url = make_url(filename)
    print(f"[{i+1}/{len(h5_files)}] Downloading: {filename} ...", end=" ", flush=True)

    try:
        r = session.get(url, stream=True, timeout=300)
        content_type = r.headers.get("content-type", "")

        if r.status_code == 200 and "html" not in content_type:
            with open(save_path, "wb") as fh:
                for chunk in r.iter_content(1024 * 1024):
                    fh.write(chunk)
            size = os.path.getsize(save_path) / 1024 / 1024
            print(f"OK ({size:.1f} MB)")
        elif r.status_code == 404:
            print(f"NOT FOUND (file may not exist for this timestamp)")
            failed.append(filename)
        else:
            print(f"FAILED ({r.status_code}) {content_type}")
            failed.append(filename)

    except Exception as e:
        print(f"ERROR: {e}")
        failed.append(filename)

    time.sleep(0.5)

# ── Summary ────────────────────────────────────────────────────────────
total     = len(h5_files)
succeeded = total - len(failed) - skipped
print(f"\n{'='*70}")
print(f"DOWNLOAD SUMMARY")
print(f"{'='*70}")
print(f"Total files:     {total}")
print(f"Downloaded:      {succeeded}")
print(f"Skipped:         {skipped}")
print(f"Failed/Missing:  {len(failed)}")
print(f"Saved to:        {SAVE_DIR}")
if failed:
    print(f"\nFailed files saved to: failed_files.txt")
    with open("failed_files.txt", "w") as f:
        f.write("\n".join(failed))
    print("Re-run script to retry.")

# ── Step 2: Generate all 750 filenames ────────────────────────────────
# Files are named: 3RIMG_DDMMMYYYY_HHMM_L1C_SGP_V01R00.h5
# Every 30 mins from 0015 to 2345, July 1-15 2025
from datetime import datetime, timedelta

def generate_filenames():
    filenames = []
    start = datetime(2025, 7, 1, 0, 15)
    end   = datetime(2025, 7, 15, 23, 45)
    current = start
    months = ["JAN","FEB","MAR","APR","MAY","JUN",
              "JUL","AUG","SEP","OCT","NOV","DEC"]
    while current <= end:
        dd  = current.strftime("%d")
        mmm = months[current.month - 1]
        yyyy = current.strftime("%Y")
        hhmm = current.strftime("%H%M")
        fname = f"3RIMG_{dd}{mmm}{yyyy}_{hhmm}_L1C_SGP_V01R00.h5"
        filenames.append(fname)
        current += timedelta(minutes=30)
    return filenames

h5_files = generate_filenames()
print(f"Generated {len(h5_files)} filenames to download.")

# ── Step 3: Download each file ─────────────────────────────────────────
def make_url(filename):
    full_path = f"{FOLDER_PATH}/{filename}"
    encoded   = base64.b64encode(full_path.encode()).decode()
    return f"{BASE_URL}/download/?r=/download&path={encoded}"

failed  = []
skipped = 0

for i, filename in enumerate(h5_files):
    save_path = os.path.join(SAVE_DIR, filename)

    if os.path.exists(save_path) and os.path.getsize(save_path) > 1024*1024:
        skipped += 1
        print(f"[{i+1}/{len(h5_files)}] Skipping (exists): {filename}")
        continue

    url = make_url(filename)
    print(f"[{i+1}/{len(h5_files)}] Downloading: {filename} ...", end=" ", flush=True)

    try:
        r = session.get(url, stream=True, timeout=300)
        content_type = r.headers.get("content-type", "")

        if r.status_code == 200 and "html" not in content_type:
            with open(save_path, "wb") as fh:
                for chunk in r.iter_content(1024 * 1024):
                    fh.write(chunk)
            size = os.path.getsize(save_path) / 1024 / 1024
            print(f"OK ({size:.1f} MB)")
        elif r.status_code == 404:
            print(f"NOT FOUND (file may not exist for this timestamp)")
            failed.append(filename)
        else:
            print(f"FAILED ({r.status_code}) {content_type}")
            failed.append(filename)

    except Exception as e:
        print(f"ERROR: {e}")
        failed.append(filename)

    time.sleep(0.5)

# ── Summary ────────────────────────────────────────────────────────────
total     = len(h5_files)
succeeded = total - len(failed) - skipped
print(f"\n{'='*50}")
print(f"Total files:     {total}")
print(f"Downloaded:      {succeeded}")
print(f"Skipped:         {skipped}")
print(f"Failed/Missing:  {len(failed)}")
print(f"Saved to:        {SAVE_DIR}")
if failed:
    print(f"\nFailed files saved to: failed_files.txt")
    with open("failed_files.txt", "w") as f:
        f.write("\n".join(failed))
    print("Re-run script to retry.")
    