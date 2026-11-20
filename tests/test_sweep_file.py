"""Tests for core/sweep_file.py.

Every test writes into `tmp_path`, a pytest built-in fixture: name it as an
argument and pytest hands the test a fresh, empty folder (a pathlib.Path)
that nothing else uses. Your repo never gets test files in it.
Run with:  pytest tests/test_sweep_file.py -x
"""

import numpy as np
import pytest

from core.sweep_file import COLUMNS, load_sweep, save_sweep
from core.vna import SweepResult

# Awkward values on purpose: negative parts, a tiny one, and one that only
# survives a round trip if every digit is written out.
THREE_POINTS = SweepResult(
    frequency_hz=np.array([50e3, 450.025e6, 900e6]),
    s11=np.array([0.998 - 0.001j, -0.012 + 0.0034j, 1e-5 - 2e-6j]),
    s21=np.array([0.7079 + 0j, 0.1 / 3 - 0.68j, -0.69 + 0.11j]),
)

FREQS = np.linspace(50e3, 900e6, 101)
ONE_HUNDRED_ONE_POINTS = SweepResult(
    frequency_hz=FREQS,
    s11=0.05 * np.exp(-2j * np.pi * FREQS / 3e8),
    s21=0.7 * np.exp(-1j * np.pi * FREQS / 1e8),
)


@pytest.mark.parametrize("result", [THREE_POINTS, ONE_HUNDRED_ONE_POINTS])
def test_round_trip_keeps_every_digit(tmp_path, result):
    path = tmp_path / "sweep.csv"
    save_sweep(path, result, {"part": "pad_3db", "cal_slot": "2"})
    loaded, metadata = load_sweep(path)
    # Raw data means full precision: exactly equal, not approximately.
    np.testing.assert_array_equal(loaded.frequency_hz, result.frequency_hz)
    np.testing.assert_array_equal(loaded.s11, result.s11)
    np.testing.assert_array_equal(loaded.s21, result.s21)
    assert np.iscomplexobj(loaded.s11) and np.iscomplexobj(loaded.s21)
    assert metadata == {"part": "pad_3db", "cal_slot": "2"}


def test_metadata_values_may_contain_colons(tmp_path):
    path = tmp_path / "sweep.csv"
    metadata = {
        "time": "2026-11-18 14:05:09",
        "note": "port 2: 10 dB pad on cable 2",
        "cal_status": "load isoln Es Er Et cal'ed",
    }
    save_sweep(path, THREE_POINTS, metadata)
    _, loaded = load_sweep(path)
    assert loaded == metadata


def test_file_is_plain_text_with_metadata_then_column_names(tmp_path):
    path = tmp_path / "sweep.csv"
    save_sweep(path, THREE_POINTS, {"part": "thru"})
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "# part: thru"
    assert lines[1] == "# " + ",".join(COLUMNS)
    assert len(lines) == 2 + 3  # two comment lines, then one row per point
    assert len(lines[2].split(",")) == 5


def test_refuses_to_overwrite_and_leaves_the_old_file_alone(tmp_path):
    path = tmp_path / "sweep.csv"
    save_sweep(path, THREE_POINTS, {"run": "1"})
    before = path.read_bytes()
    with pytest.raises(FileExistsError):
        save_sweep(path, ONE_HUNDRED_ONE_POINTS, {"run": "2"})
    assert path.read_bytes() == before


def test_creates_missing_folders(tmp_path):
    path = tmp_path / "data" / "2026-11-18" / "thru.csv"
    save_sweep(path, THREE_POINTS, {"part": "thru"})
    assert path.exists()


def test_load_rejects_rows_without_five_columns(tmp_path):
    path = tmp_path / "four_columns.csv"
    path.write_text(
        "# part: pad_3db\n50000,0.9,0.0,0.7\n450025000,0.9,0.0,0.7\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="column"):
        load_sweep(path)
