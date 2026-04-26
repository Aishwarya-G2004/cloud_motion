import h5py
import numpy as np
import os
from glob import glob

RAW_DIR  = r"D:\Insat_data\raw"

# Only thermal channels — VIS and SWIR are black at night
CHANNELS = ['IMG_TIR1', 'IMG_TIR2', 'IMG_WV']

def inspect_all_h5_files():
    files = sorted(glob(os.path.join(RAW_DIR, "*.h5")))
    print(f"Found {len(files)} HDF5 files\n")

    passed = []
    failed = []

    for file in files:
        fname  = os.path.basename(file)
        all_ok = True
        print(f"File: {fname}")
        try:
            with h5py.File(file, 'r') as f:
                for ch in CHANNELS:
                    if ch not in f:
                        print(f"  MISSING  : {ch}")
                        all_ok = False
                    else:
                        data = f[ch][:]
                        nans = int(np.isnan(data).sum())
                        mx   = float(np.nanmax(data))
                        mn   = float(np.nanmin(data))
                        print(f"  OK  {ch}: shape={data.shape}  "
                              f"min={mn:.1f}  max={mx:.1f}  NaNs={nans}")
                        if mx == 0:
                            print(f"  WARNING: {ch} is all zeros")
                            all_ok = False
                        if nans > data.size * 0.5:
                            print(f"  WARNING: {ch} has >50% NaNs")
                            all_ok = False
        except Exception as e:
            print(f"  FAILED to open: {e}")
            all_ok = False

        if all_ok:
            passed.append(fname)
        else:
            failed.append(fname)
        print("-" * 60)

    print(f"\n=== SUMMARY ===")
    print(f"Total   : {len(files)}")
    print(f"Passed  : {len(passed)}")
    print(f"Failed  : {len(failed)}")
    if failed:
        print("\nFailed files:")
        for f in failed:
            print(f"  {f}")

if __name__ == "__main__":
    inspect_all_h5_files()