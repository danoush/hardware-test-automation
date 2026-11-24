# Hardware Test Automation Framework

[![tests](https://github.com/danoush/pic-test-automation-framework/actions/workflows/tests.yml/badge.svg)](https://github.com/danoush/pic-test-automation-framework/actions/workflows/tests.yml)

Python test automation built around a real instrument: a NanoVNA-H vector network analyzer driven over USB serial. A bench script recalls a calibration slot, refuses to measure unless the analyzer reports a complete calibration, sweeps, saves the raw data and, given a part name, grades it PASS or FAIL against limits kept in a config file. A pytest suite runs on every push without hardware, using a fake serial port that replays output captured from the analyzer.

I'm building this toward test and validation work in RF, optical transceivers and silicon photonics. Everything outside `prototypes/` runs against the real NanoVNA-H.

## What's in it

| Path | What it does |
|---|---|
| `core/vna.py` | The `VNA` interface every driver implements, and `SweepResult`: frequencies plus complex S11 and S21. A `SweepResult` can't be built with fewer than two points or with frequencies that aren't strictly ascending. |
| `core/nanovna.py` | The NanoVNA-H driver. It talks to the firmware's serial shell and runs `scan` for fresh data. Timeouts, malformed lines and a lost command echo raise exceptions instead of being skipped. `missing_cal_flags()` reads the analyzer's calibration status. |
| `core/sweep_file.py` | Saves a sweep and its metadata to CSV at full precision, never overwriting an existing file, and reads it back. |
| `analytics/grading.py` | `grade_attenuation()`: pass/fail of measured attenuation against nominal ± tolerance across a band. It reports the worst error and its frequency, and refuses a band the sweep doesn't fully cover. |
| `analytics/limits.py`, `config/limits.toml` | Pass/fail limits for each part (the six pads and a thru), kept in a TOML file. `load_limits()` reads the file; `attenuator_limits()` checks one part's entry (missing keys, non-positive tolerance, bad bands) and lists the valid part names when it's given an unknown one. |
| `scripts/bench_nanovna.py` | Bench run: `python scripts/bench_nanovna.py <label> <slot> [part]`. It looks up the part's limits before touching the analyzer, recalls the calibration slot, stops unless the analyzer reports a complete calibration with correction on, sweeps 50 kHz–900 MHz (101 points) and saves the sweep under `data/<date>/`. Given a part, it prints PASS or FAIL with the worst error and its frequency. It sends `resume` in a `finally` block, so the analyzer's own live sweep restarts even after an error. |
| `data/` | Raw sweeps from bench sessions, with a notes file per session describing the setup. |
| `tests/` | pytest suite: driver tests against real captured output, plus sweep-validation, grading, limits, calibration-flag and file round-trip tests. |
| `prototypes/` | Earlier simulated-data practice code: a wafer-test pipeline into SQLite, Gage R&R and laser L-I analysis. See its README. |

## Design rules

- Drivers return raw data: frequencies and complex S-parameters. dB conversion and pass/fail decisions happen in analysis code.
- Never pass a part that wasn't measured. Bad instrument output, timeouts and lost sync raise exceptions, and grading raises on a band with no measured points.
- Limits live in `config/limits.toml`, not in code.
- Check inputs before touching hardware: a slot number outside 0–4 or an unknown part name stops the run before the serial port opens.
- Measurement files are evidence: they're saved at full precision and never overwritten.

## Bench results (Nov 19, 2026)

Setup: NanoVNA-H (firmware 1.2.50) with two SMA cables, SOLT and isolation calibration at the cable ends, 50 kHz–900 MHz, 101 points. Parts: a Nooelec SMA attenuator kit (1, 2, 3, 6, 10 and 20 dB, specified ±0.1 dB to 3 GHz) and a Mini-Circuits VLF-120+ low-pass filter. The raw sweeps are in [`data/2026-11-19/`](data/2026-11-19/), with [NOTES.md](data/2026-11-19/NOTES.md) describing each file. Every number below uses all 101 points of each sweep.

- **Thru checks:** five checks over five hours stayed within 0.09 dB of 0 dB from 50 kHz to 676 MHz, and within 0.12 dB up to 900 MHz. One point, 315 MHz, is about five times noisier than its neighbors (±0.09 dB from run to run).
- **Wrong calibration slot:** the factory calibration (slot 0), which the analyzer loads at power-on, reports the same six calibration flags as the bench calibration but reads the thru up to +0.29 dB mid-band and −0.31 dB at 900 MHz. The flag check can't see this; a thru check can. Graded in code against the thru limit in `config/limits.toml` (0 ± 0.15 dB from 50 kHz to 676 MHz, set from this session's data), all six thru checks taken on bench calibrations pass (the five above plus the first one, on the previous week's calibration). Both factory-calibration runs fail (worst point 0.29 dB off, at 405 MHz), as do the run with the thru disconnected and the slot 3 mix-up described in NOTES.md.
- **Every attenuator fails ±0.1 dB on this station.** Graded from 50 kHz to 676 MHz, each pad reads light somewhere by 0.21–0.41 dB, worst between 520 and 590 MHz. Loosening and retightening a pad between its two runs changed the reading by at most 0.11 dB.
- **Port mismatch is a large part of the error.** With a 10 dB attenuator left on port 2 and calibrated out, the pads read 0.07–0.14 dB more loss on average (closer to nominal), and the drop from 675 to 900 MHz shrinks for the 3, 6 and 20 dB pads (0.27 → 0.12, 0.37 → 0.14 and 0.52 → 0.23 dB, averaging 630–676 MHz against 855–900 MHz). That is what uncorrected port-2 mismatch predicts. The 1 dB pad's 0.15 dB drop doesn't change, so another effect remains (the pads' own roll-off or a residual calibration error). The cost is 10 dB less signal: the 20 dB pad's two padded runs differ by up to 0.38 dB.
- **At 50 kHz, where mismatch matters least,** the pads still read 0.09–0.28 dB light in both setups, the 3 and 6 dB pads most. That points at the pads themselves; a DC resistance check would confirm it.
- **Conclusion:** this station's errors (about 0.1–0.4 dB) are as large as the pads' ±0.1 dB tolerance, so it can't verify that spec. Its test uncertainty ratio is about 1:1, against the usual 4:1 target.
- **VLF-120+ low-pass filter: passes its spec.** At most 0.75 dB loss up to 120 MHz (spec: 1 dB maximum) and at least 33.4 dB rejection from 300 to 900 MHz (spec: 20 dB minimum). The 3 dB point is 201 MHz (datasheet: 195 MHz nominal). Rejection near 500 MHz is 33.7 dB against 46.5 dB typical on the datasheet. The deepest stopband readings (54–71 dB) vary between runs because they reach the analyzer's noise floor.

## Running it

```powershell
pip install -r requirements.txt
pip install -e .
pytest
python scripts/bench_nanovna.py thru_check 2 thru         # needs a NanoVNA-H on COM3
python scripts/bench_nanovna.py pad_3db_run1 2 pad_3db
```

The arguments are a label for the file name, the calibration slot to recall (0–4) and, optionally, a part from `config/limits.toml` to grade. Each session starts with a graded thru check.

## Next

- A second instrument: a PyVISA/SCPI driver for a bench multimeter (an OWON XDM1041), and a DC resistance check of the pads as an independent measurement.
- Grade the VLF-120+ in code against its datasheet limits.
- A plot of the Nov 19 results in this README.
