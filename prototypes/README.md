# Prototypes

Early practice code from before the NanoVNA-H driver existed. Most of it runs on simulated data. The exceptions are `old_nanovna_driver.py`, `run_desk_bench.py` and `debug_raw_serial.py`, which were first attempts at talking to the real analyzer. The real driver, grading and limits live in `core/`, `analytics/` and `config/`. This folder is kept for reference and isn't developed further.

| File | What it is |
|---|---|
| `execution_engine.py`, `data_logger.py` | A simulated wafer-probe line: sweeps five dies on a simulated VNA, grades them against `factory_settings.json` and logs the results to SQLite. |
| `simulated_vnas.py`, `base_instrument.py` | Two simulated VNAs (Keysight and Anritsu stand-ins) behind an abstract interface. They print the SCPI a real driver would send and return fixed data. |
| `spc_failure_analysis.py` | A rolling-average yield alert over the SQLite results. |
| `statistical_qc.py` | An average-and-range Gage R&R on simulated data. |
| `laser_characterization.py` | Threshold current and slope efficiency from a simulated laser L-I curve. |
| `yield_reporter.py` | Filters simulated wafer data and exports it to CSV. |
| `old_nanovna_driver.py`, `run_desk_bench.py`, `debug_raw_serial.py` | First attempts at the real NanoVNA-H, superseded by `core/nanovna.py`. The old driver skips lines it can't parse; the current one rejects them. |
| `tests/` | Tests for the simulated VNAs and the old driver. |

Run any of them from the repository root, for example:

```powershell
python -m prototypes.execution_engine
```
