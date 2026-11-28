"""
Usage: python scripts/regrade.py <part> <folder> <pattern>.

Use argparse with three positional arguments: part, folder, pattern.
Look up the limits first, with load_limits() and attenuator_limits(), so a misspelled part fails before any file is read.
Build the file list with sorted(Path(folder).glob(pattern)). If it's empty, raise SystemExit(f"No files match {pattern!r} in {folder}").
For each file, run load_sweep and then grade_attenuation, and print one line: the file name, PASS or FAIL, and the worst error. Use two spaces between the parts, and the same number formats as the bench script.
End with a count line like 6 PASS, 4 FAIL.

The expected output is your test.
"""

import argparse
from collections.abc import Sequence
from pathlib import Path

from analytics.grading import grade_attenuation
from analytics.limits import attenuator_limits, load_limits
from core.sweep_file import load_sweep


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Regrade NanoVNA bench sweep.")
    parser.add_argument("part", help="Part found in database")
    parser.add_argument("folder", help="Input to Path function")
    parser.add_argument("pattern", help="Input to glob function")

    args = parser.parse_args(argv)
    part = args.part
    folder = args.folder
    pattern = args.pattern
    config = load_limits()
    limits = attenuator_limits(config, part)
    file_list = sorted(Path(folder).glob(pattern))
    if not file_list:
        raise SystemExit(f"No files match {pattern!r} in {folder}")
    pass_count = 0
    fail_count = 0

    for file in file_list:
        sweep, _ = load_sweep(file)
        grade = grade_attenuation(
            sweep, limits.nominal_db, limits.tolerance_db, limits.band_hz
        )
        grade_outcome = "PASS" if grade.passed else "FAIL"
        pass_count += grade.passed
        fail_count += not grade.passed
        print(
            f"{file.name}  {grade_outcome}  "
            f"worst error {grade.worst_error_db:+.3f} dB "
            f"at {grade.worst_frequency_hz / 1e6:.3f} MHz"
        )

    print(f"{pass_count} PASS, {fail_count} FAIL")


if __name__ == "__main__":
    main()
