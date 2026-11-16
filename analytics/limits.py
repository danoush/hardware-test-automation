"""Pass/fail limits, read from config/limits.toml.

The limits file is the one place pass/fail numbers live. This module turns one
entry of the parsed file into a typed, checked object, so a typo in the file
fails loudly here instead of quietly changing a grade.

It never opens files itself: callers parse the file with tomllib and pass the
resulting dict in, the same split as parse_scan (pure) and measure() (I/O).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AttenuatorLimits:
    """Pass/fail limits for one attenuator.

    Attributes:
        nominal_db: The attenuation printed on the part, e.g. 3.0.
        tolerance_db: The allowed deviation either way, e.g. 0.1. Positive.
        band_hz: (low, high) in Hz, low < high: where the part is graded.
    """

    nominal_db: float
    tolerance_db: float
    band_hz: tuple[float, float]


def attenuator_limits(config: dict, part: str) -> AttenuatorLimits:
    """Return one attenuator's limits from a parsed limits file.

    `config` is what tomllib returns for config/limits.toml. Each attenuator
    is a table under [attenuators], named by the part:

        [attenuators.pad_3db]
        nominal_db = 3.0
        tolerance_db = 0.1          # where the number comes from
        band_hz = [50e3, 675e6]

    Other keys in the table (a description, say) are allowed and ignored.

    Args:
        config: The parsed limits file.
        part: The table name, e.g. "pad_3db".

    Returns:
        The part's limits, every number a float and band_hz a tuple.

    Raises:
        ValueError: if the part isn't in the file, one of the three keys is
            missing, tolerance_db isn't positive, or band_hz isn't a list of
            two numbers with low < high. The message names the part and the
            problem: whoever reads it is about to edit the file.
    """
    attenuators = config.get("attenuators")
    if not isinstance(attenuators, dict) or not attenuators:
        raise ValueError(f"{part} is not found: config has no attenuators.")
    if part not in attenuators:
        available = "\n".join(attenuators)
        raise ValueError(
            f"{part} is not found in part database. Please select from:\n{available}"
        )

    pad_data = attenuators[part]
    if not isinstance(pad_data, dict):
        raise TypeError(f"{part} must be a table.")

    for key in ("nominal_db", "tolerance_db", "band_hz"):
        if key not in pad_data:
            raise ValueError(f"{part} is missing {key}.")

    band_hz = pad_data["band_hz"]
    if not isinstance(band_hz, list) or len(band_hz) != 2:
        raise ValueError(f"{part} band_hz must contain exactly two numbers.")

    values = (pad_data["nominal_db"], pad_data["tolerance_db"], *band_hz)
    if any(
        isinstance(value, bool) or not isinstance(value, (int, float))
        for value in values
    ):
        raise ValueError(f"{part} limits must be numbers.")

    nominal_db, tolerance_db, low_hz, high_hz = (float(value) for value in values)
    if not tolerance_db > 0:
        raise ValueError(f"{part} tolerance_db must be positive.")
    if not low_hz < high_hz:
        raise ValueError(f"{part} band_hz low edge must be less than high edge.")

    return AttenuatorLimits(
        nominal_db=nominal_db,
        tolerance_db=tolerance_db,
        band_hz=(low_hz, high_hz),
    )
