"""Run a NanoVNA sweep and save its raw data and measurement metadata.

Usage: python scripts/bench_nanovna.py <label> <slot>
"""

import sys
from datetime import datetime
from pathlib import Path
from time import perf_counter

import numpy as np

from core.nanovna import NanoVNA, missing_cal_flags
from core.sweep_file import save_sweep

if len(sys.argv) != 3:
    raise SystemExit("Usage: python scripts/bench_nanovna.py <label> <slot>")

label, slot = sys.argv[1:3]

with NanoVNA("COM3") as vna:
    recall_reply = vna._query(f"recall {slot}")
    if recall_reply:
        raise SystemExit(f"Could not recall calibration slot {slot!r}: {recall_reply}")

    firmware_version = vna.identify()
    print(firmware_version)

    cal_status = vna._query("cal")
    missing_cals = missing_cal_flags(cal_status)
    if missing_cals:
        raise SystemExit(
            f"Missing calibration flags: {', '.join(sorted(missing_cals))}; "
            f"raw calibration status: {cal_status!r}"
        )
    start = perf_counter()
    result = vna.measure(50e3, 900e6, 101)
    end = perf_counter()
    print(f"Measurement took {end - start:.3f} seconds.")

    measurement_time = datetime.now().astimezone()
    repo_root = Path(__file__).resolve().parents[1]
    output_path = (
        repo_root
        / "data"
        / measurement_time.strftime("%Y-%m-%d")
        / f"{label}_{measurement_time.strftime('%H%M%S')}.csv"
    )
    save_sweep(
        output_path,
        result,
        {
            "label": label,
            "slot": slot,
            "cal_status": cal_status,
            "firmware_version": firmware_version,
            "time": measurement_time.isoformat(timespec="seconds"),
        },
    )
    print(f"Saved sweep to {output_path}")

    # Calculate S21 in dB (Insertion Loss / Attenuation)
    s21_db = 20 * np.log10(np.abs(result.s21))

    # Specify S21 in dB at 0.05 MHz, 450.025 MHz, and 900 MHz (given above, just isolated here)
    # Automatically pick 5 evenly-spaced sample points across the 101-point sweep
    num_samples = 5
    indices = np.linspace(0, len(result.frequency_hz) - 1, num_samples, dtype=int)
    s21_db_samples = s21_db[indices]

    # Calculate S11 in dB (Reflection / Return Loss)
    s11_db = 20 * np.log10(np.abs(result.s11))

    # Find the maximum (worst) S11 value across the sweep
    # (Since they are negative numbers, max() finds the number closest to 0 / least negative)
    worst_s11 = np.max(s11_db)

    print("S21 in dB:")
    for freq, db in zip(result.frequency_hz, s21_db):
        print(f"{freq / 1e6:8.3f} MHz: {db:.2f} dB")
    print("\nS21 samples at target frequencies:")
    for freq, val in zip(result.frequency_hz[indices], s21_db_samples):
        print(f"{freq / 1e6:8.3f} MHz: {val:.2f} dB")
    print(f"\nWorst S11 (Reflection):\n{worst_s11:.2f} dB")
    print("\nCalibration data:", cal_status)
    print("\nIF Bandwidth:", vna._query("bandwidth"))

    vna._query("resume")
