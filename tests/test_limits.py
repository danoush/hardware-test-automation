"""Tests for analytics/limits.py.

Most tests parse a small TOML snippet written right here, so each test shows
the file contents it depends on. The last test reads your real
config/limits.toml, so a typo in that file fails CI instead of a grade.
Run with:  pytest tests/test_limits.py -x
"""

import tomllib

import pytest

from analytics.limits import AttenuatorLimits, attenuator_limits, load_limits

# Two parts with different numbers everywhere, so a value copied from one
# part to the other, or typed into the code, gets caught.
TWO_PADS = """
[attenuators.pad_3db]
nominal_db = 3.0
tolerance_db = 0.1
band_hz = [50e3, 675e6]

[attenuators.pad_10db]
description = "extra keys are allowed"
nominal_db = 10.0
tolerance_db = 0.25
band_hz = [1e6, 450e6]
"""


def two_pads():
    """A fresh parsed copy for each test, so one test's edits can't leak."""
    return tomllib.loads(TWO_PADS)


def test_returns_the_requested_parts_limits():
    config = two_pads()
    assert attenuator_limits(config, "pad_3db") == AttenuatorLimits(
        nominal_db=3.0, tolerance_db=0.1, band_hz=(50e3, 675e6)
    )
    assert attenuator_limits(config, "pad_10db") == AttenuatorLimits(
        nominal_db=10.0, tolerance_db=0.25, band_hz=(1e6, 450e6)
    )


def test_numbers_come_back_as_floats_even_when_written_as_integers():
    # TOML keeps 3 and 3.0 apart (int vs float); the limits object shouldn't.
    config = tomllib.loads("""
[attenuators.pad_1db]
nominal_db = 1
tolerance_db = 0.1  
band_hz = [50_000, 675_000_000]
""")
    limits = attenuator_limits(config, "pad_1db")
    assert isinstance(limits.nominal_db, float)
    assert isinstance(limits.tolerance_db, float)
    assert isinstance(limits.band_hz, tuple)
    assert all(isinstance(edge, float) for edge in limits.band_hz)
    assert limits.band_hz == (50e3, 675e6)


def test_unknown_part_raises_and_says_what_the_file_has():
    config = two_pads()
    # `as excinfo` keeps the exception so you can inspect it after the block.
    with pytest.raises(ValueError) as excinfo:
        attenuator_limits(config, "pad_6db")
    message = str(excinfo.value)
    assert "pad_6db" in message  # what was asked for
    assert "pad_3db" in message  # what the file does have: typos get obvious


def test_empty_file_raises_value_error_not_key_error():
    # An empty file parses to {}: there's no [attenuators] table at all.
    with pytest.raises(ValueError, match="pad_3db"):
        attenuator_limits({}, "pad_3db")


@pytest.mark.parametrize(
    ("part", "contents", "expected"),
    [
        (
            "pad_3db",
            """
[attenuators.pad_3db]
nominal_db = 3.0
tolerance_db = 0.1
band_hz = [50e3, 675e6]
""",
            AttenuatorLimits(3.0, 0.1, (50e3, 675e6)),
        ),
        (
            "pad_10db",
            """
[attenuators.pad_10db]
nominal_db = 10.0
tolerance_db = 0.25
band_hz = [1e6, 450e6]
""",
            AttenuatorLimits(10.0, 0.25, (1e6, 450e6)),
        ),
    ],
)
def test_load_limits_reads_a_toml_file(tmp_path, part, contents, expected):
    path = tmp_path / "limits.toml"
    path.write_text(contents, encoding="utf-8")

    assert attenuator_limits(load_limits(path), part) == expected


def test_load_limits_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_limits(tmp_path / "missing.toml")


def test_default_limits_include_thru_tolerance():
    assert attenuator_limits(load_limits(), "thru").tolerance_db == 0.15


@pytest.mark.parametrize("key", ["nominal_db", "tolerance_db", "band_hz"])
def test_missing_key_raises_and_names_it(key):
    config = two_pads()
    del config["attenuators"]["pad_3db"][key]
    # match= is a regular expression searched for in the message, so this
    # pins *your* ValueError, not one that happens to come from deeper down.
    with pytest.raises(ValueError, match=key):
        attenuator_limits(config, "pad_3db")


@pytest.mark.parametrize("tolerance", [0, 0.0, -0.1])
def test_tolerance_must_be_positive(tolerance):
    config = two_pads()
    config["attenuators"]["pad_3db"]["tolerance_db"] = tolerance
    with pytest.raises(ValueError, match="tolerance_db"):
        attenuator_limits(config, "pad_3db")


@pytest.mark.parametrize(
    "band",
    [
        [675e6, 50e3],  # reversed
        [50e3, 50e3],  # zero width
        [50e3],  # one number
        [50e3, 450e6, 675e6],  # three numbers
        675e6,  # not a list at all
    ],
)
def test_bad_band_raises(band):
    config = two_pads()
    config["attenuators"]["pad_3db"]["band_hz"] = band
    with pytest.raises(ValueError, match="band_hz"):
        attenuator_limits(config, "pad_3db")


def test_your_limits_file_is_valid():
    # Every attenuator in config/limits.toml must produce valid limits.
    config = load_limits()
    parts = config["attenuators"]
    assert parts, "config/limits.toml has no [attenuators.<part>] tables"
    for part in parts:
        attenuator_limits(config, part)  # raises if anything is wrong
