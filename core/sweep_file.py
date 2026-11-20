"""Save sweeps to CSV files and read them back.

One sweep per file. Metadata comes first as comment lines ("# key: value"),
then a comment line naming the columns, then one row per frequency point
holding the raw data at full precision:

    # part: pad_3db
    # cal_slot: 2
    # frequency_hz,s11_re,s11_im,s21_re,s21_im
    5.000000000000000000e+04,9.98...e-01,...

Saved files are measurement evidence, so save_sweep never overwrites one.
"""

from pathlib import Path

import numpy as np

from core.vna import SweepResult

COLUMNS = ("frequency_hz", "s11_re", "s11_im", "s21_re", "s21_im")


def save_sweep(path: Path, result: SweepResult, metadata: dict[str, str]) -> None:
    """Write one sweep and its metadata to a new CSV file.

    Creates any missing parent folders, so a path like
    data/2026-11-18/pad_3db.csv works on the first save of the day.

    Args:
        path: The file to create.
        result: The sweep to save.
        metadata: Short facts about the measurement, e.g.
            {"part": "pad_3db", "cal_slot": "2"}. Keys must not contain
            ": ". Values may (a timestamp like "2026-11-18 14:05:09" does).

    Raises:
        FileExistsError: if `path` already exists. The old file is left
            untouched.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    data = np.column_stack(
        (
            result.frequency_hz,
            result.s11.real,
            result.s11.imag,
            result.s21.real,
            result.s21.imag,
        )
    )

    with path.open("x", encoding="utf-8") as file:
        for key, value in metadata.items():
            file.write(f"# {key}: {value}\n")
        np.savetxt(
            file,
            data,
            delimiter=",",
            header=",".join(COLUMNS),
            fmt="%.18e",
        )


def load_sweep(path: Path) -> tuple[SweepResult, dict[str, str]]:
    """Read a file written by save_sweep.

    Returns:
        The sweep (s11 and s21 complex again) and the metadata dict.

    Raises:
        ValueError: if the data rows don't have exactly five columns. The
            message says how many columns it found.
    """
    metadata: dict[str, str] = {}
    with path.open(encoding="utf-8") as file:
        for line in file:
            if not line.startswith("# "):
                continue
            comment = line[2:].rstrip("\r\n")
            if ": " in comment:
                key, value = comment.split(": ", 1)
                metadata[key] = value
            else:
                break

    data = np.loadtxt(path, delimiter=",", comments="#", ndmin=2)
    if data.shape[1] != len(COLUMNS):
        raise ValueError(f"Expected {len(COLUMNS)} columns, found {data.shape[1]}")

    result = SweepResult(
        frequency_hz=data[:, 0],
        s11=data[:, 1] + 1j * data[:, 2],
        s21=data[:, 3] + 1j * data[:, 4],
    )
    return result, metadata
