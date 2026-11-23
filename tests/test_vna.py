"""Tests for the measurement contract in core/vna.py."""

import numpy as np
import pytest

from core.vna import VNA, SweepResult


def test_sweep_result_rejects_mismatched_lengths():
    with pytest.raises(ValueError):
        SweepResult(
            frequency_hz=np.array([1e6, 2e6, 3e6]),
            s11=np.array([1 + 0j, 1 + 0j, 1 + 0j]),
            s21=np.array([0j, 0j]),  # one value short
        )


def test_vna_cannot_be_used_without_implementing_the_contract():
    class HalfDone(VNA):
        def connect(self):
            pass

    with pytest.raises(TypeError):
        HalfDone()  # close, identify and measure are still abstract


@pytest.mark.parametrize("frequencies", [[], [50e3]])
def test_sweep_with_fewer_than_two_points_raises(frequencies):
    with pytest.raises(ValueError, match="at least two points"):
        SweepResult(
            frequency_hz=np.array(frequencies),
            s11=np.zeros(len(frequencies), dtype=complex),
            s21=np.zeros(len(frequencies), dtype=complex),
        )


@pytest.mark.parametrize(
    "frequencies",
    [
        [50e3, 450e6, 400e6, 900e6],
        [50e3, 450e6, 450e6, 900e6],
    ],
)
def test_non_ascending_sweep_raises(frequencies):
    with pytest.raises(ValueError, match="strictly ascending"):
        SweepResult(
            frequency_hz=np.array(frequencies),
            s11=np.zeros(len(frequencies), dtype=complex),
            s21=np.zeros(len(frequencies), dtype=complex),
        )


def test_valid_two_point_sweep_builds():
    sweep = SweepResult(
        frequency_hz=np.array([50e3, 900e6]),
        s11=np.zeros(2, dtype=complex),
        s21=np.zeros(2, dtype=complex),
    )
    np.testing.assert_array_equal(sweep.frequency_hz, [50e3, 900e6])


@pytest.mark.parametrize(
    "frequencies",
    [
        [50e3, 450e6, 400e6, 900e6],
        [50e3, 450e6, 450e6],
    ],
)
def test_non_ascending_plain_list_raises(frequencies):
    # A plain list, not np.array(...): list > list compares like words in a dictionary.
    with pytest.raises(ValueError, match="strictly ascending"):
        SweepResult(
            frequency_hz=frequencies,
            s11=np.zeros(len(frequencies), dtype=complex),
            s21=np.zeros(len(frequencies), dtype=complex),
        )
