# Hardware Test Automation Framework

[![tests](https://github.com/danoush/pic-test-automation-framework/actions/workflows/tests.yml/badge.svg)](https://github.com/danoush/pic-test-automation-framework/actions/workflows/tests.yml)

Python test automation built around a real instrument: a NanoVNA-H vector network analyzer driven over USB serial. A bench script refuses to measure unless the analyzer reports a complete calibration, then runs a sweep, and a grading module checks attenuation against pass/fail limits kept in a config file. A pytest suite runs on every push without hardware, using a fake serial port that replays output captured from the analyzer.

I'm building this toward test and validation work in RF, optical transceivers and silicon photonics. Everything outside `prototypes/` runs against the real NanoVNA-H.

## What's in it

| Path | What it does |
|---|---|
| `core/vna.py` | The `VNA` interface every driver implements, and `SweepResult`: frequencies plus complex S11 and S21. |
| `core/nanovna.py` | The NanoVNA-H driver. It talks to the firmware's serial shell and runs `scan` for fresh data. Timeouts, malformed lines and a lost command echo raise exceptions instead of being skipped. `missing_cal_flags()` reads the analyzer's calibration status. |
| `analytics/grading.py` | `grade_attenuation()`: pass/fail of measured attenuation against nominal ± tolerance across a band. It reports the worst error and its frequency, and refuses a band the sweep doesn't fully cover. |
| `analytics/limits.py`, `config/limits.toml` | Pass/fail limits per part, kept in a TOML file and checked on load (missing keys, non-positive tolerance, bad bands). |
| `scripts/bench_nanovna.py` | Bench run: stops unless the analyzer reports a complete calibration with correction on, then sweeps 50 kHz–900 MHz (101 points) and prints S21 and the worst S11. |
| `tests/` | pytest suite: driver tests against real captured output, plus grading, limits and calibration-flag tests. |
| `prototypes/` | Earlier simulated-data practice code: a wafer-test pipeline into SQLite, Gage R&R and laser L-I analysis. See its README. |

## Design rules

- Drivers return raw data: frequencies and complex S-parameters. dB conversion and pass/fail decisions happen in analysis code.
- Never pass a part that wasn't measured. Bad instrument output, timeouts and lost sync raise exceptions, and grading raises on a band with no measured points.
- Limits live in `config/limits.toml`, not in code.

## Bench results so far

Setup: NanoVNA-H (firmware 1.2.50) with two SMA cables, SOLT and isolation calibration at the cable ends, 50 kHz–900 MHz, 101 points. Parts: a Nooelec SMA attenuator kit (1, 2, 3, 6, 10 and 20 dB, specified ±0.1 dB to 3 GHz). The numbers come from five sample frequencies per sweep (50 kHz and 225, 450, 675 and 900 MHz), logged in November 2026.

- **Thru after calibration:** within 0.03 dB of 0 dB.
- **3 dB pad, 12 runs over four calibrations:** 2.74–2.84 dB from 50 kHz to 675 MHz, against a spec of 2.9–3.1 dB. Each frequency repeats within 0.06 dB. The highest reading is only 0.06 dB inside the limit, so calling the part out of spec at that frequency needs a measurement-uncertainty estimate first.
- **10 dB and 20 dB pads in cascade:** within 0.14 dB of 30 dB up to 675 MHz.
- **900 MHz:** every pad reads light, and the drop from 675 to 900 MHz grows roughly with attenuation, from 0.24 dB on the 1 dB pad to 0.52 dB on the 20 dB pad. That pattern fits uncorrected port mismatch (the NanoVNA's calibration doesn't correct port 2's match), but it isn't confirmed, so grading stops at 676 MHz for now.
- **Wrong calibration slot:** the analyzer loads its factory calibration at power-on. That calibration reports the same six status flags as the bench calibration but reads the thru at +0.11 to +0.20 dB mid-band and −0.39 to −0.44 dB at 900 MHz. The flag check can't tell the two apart, so a thru check against limits comes next.

## Running it

```powershell
pip install -r requirements.txt
pip install -e .
pytest
python scripts/bench_nanovna.py    # needs a NanoVNA-H on COM3 with the bench calibration loaded
```

## Next

- Save every sweep (raw complex data) and recompute the numbers above from all 101 points.
- Pick the part on the command line, grade it against `config/limits.toml`, and print PASS or FAIL.
- Read the calibration slot from config, and gate each session on a thru check.
- Test the 900 MHz mismatch explanation with a 10 dB pad on port 2.
- Measure a Mini-Circuits VLF-120+ low-pass filter against its datasheet.
