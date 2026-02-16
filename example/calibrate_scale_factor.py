# calibrate_scale_factor.py
#
# Usage:
#   python calibrate_scale_factor.py --force force.csv --touch touch.csv
#
# Output:
#   force_baseline_g
#   k_g_per_countsum (scale factor)
#   R^2
#
# Notes:
# - Assumes force.csv third value (col index 2) is middle finger FORCE_ACT in gram-force (g).
# - Fits delta_force_g ≈ k * S, where S = sum(max(touch - touch_baseline, 0))

import argparse
import numpy as np


def load_csv_numeric(path: str) -> np.ndarray:
    """
    Loads a CSV into a float numpy array.
    Tries to handle optional headers by ignoring non-numeric rows.
    """
    # Try genfromtxt which can handle missing/header better than loadtxt
    arr = np.genfromtxt(path, delimiter=",", dtype=float)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)

    # Drop rows that are all NaN (often headers)
    mask_valid = ~np.all(np.isnan(arr), axis=1)
    arr = arr[mask_valid]

    # If still has NaNs in some columns, drop those rows (conservative)
    mask_row = ~np.any(np.isnan(arr), axis=1)
    arr = arr[mask_row]

    if arr.size == 0:
        raise ValueError(f"No valid numeric data found in {path}")
    return arr


def compute_r2(y: np.ndarray, yhat: np.ndarray) -> float:
    ss_res = np.sum((y - yhat) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    return float(1.0 - ss_res / ss_tot) if ss_tot > 1e-12 else float("nan")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", default="force.csv", help="Path to force.csv")
    parser.add_argument("--touch", default="touch.csv", help="Path to touch.csv")
    parser.add_argument("--baseline_frac", type=float, default=0.2,
                        help="Fraction (0-1) of lowest-force frames used to estimate baselines (default 0.2)")
    parser.add_argument("--touch_thresh", type=float, default=0.0,
                        help="Extra threshold after baseline subtraction; values <= thresh are treated as 0 (default 0.0)")
    args = parser.parse_args()

    force = load_csv_numeric(args.force)
    touch = load_csv_numeric(args.touch)

    n = min(force.shape[0], touch.shape[0])
    force = force[:n]
    touch = touch[:n]

    if force.shape[1] < 3:
        raise ValueError("force.csv must have at least 3 columns (need the 3rd for middle finger).")

    # Middle finger force in gram-force (g)
    Fg = force[:, 2].astype(float)

    # Choose baseline frames = lowest force fraction (more robust than "first N")
    frac = np.clip(args.baseline_frac, 0.05, 0.8)
    k0 = max(5, int(frac * n))
    idx_sorted = np.argsort(Fg)
    idx_base = idx_sorted[:k0]

    # Force baseline (offset) and delta force
    F0 = float(np.median(Fg[idx_base]))
    dF = np.clip(Fg - F0, 0.0, None)  # only consider positive load

    # Touch baseline per pixel (vector)
    T0 = np.median(touch[idx_base, :], axis=0)

    # Baseline-subtracted touch, clamp to >=0
    dT = touch - T0
    dT = np.where(dT > args.touch_thresh, dT, 0.0)

    # Feature S: sum over pixels
    S = np.sum(dT, axis=1)

    # Fit delta force vs S through origin: dF ≈ k * S
    # (This gives a clean "scale factor" in g per count-sum)
    denom = float(np.dot(S, S))
    if denom < 1e-12:
        raise ValueError("Touch feature S has near-zero energy; check your touch.csv or baseline selection.")
    k_scale = float(np.dot(S, dF) / denom)

    # Evaluate fit
    dF_hat = k_scale * S
    r2 = compute_r2(dF, dF_hat)

    print("=== Calibration Result ===")
    print(f"samples_used: {n}")
    print(f"baseline_frames: {k0} (lowest {frac*100:.1f}% by force)")
    print(f"force_baseline_g (F0): {F0:.4f}")
    print(f"k_g_per_countsum (scale factor): {k_scale:.8f}")
    print(f"R2 (delta force vs S): {r2:.4f}")

    # Convenience: function form you can paste elsewhere
    print("\nEquation:")
    print("Let S = sum(max(touch - touch_baseline, 0))")
    print(f"delta_force_g ≈ {k_scale:.8f} * S")
    print(f"force_g ≈ {F0:.4f} + delta_force_g")
    print("force_N ≈ force_g * 0.00981")


if __name__ == "__main__":
    main()