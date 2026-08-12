"""Determinism of the Phase-4 analysis, in-process and across process restarts (spec §XXXV)."""

from __future__ import annotations

import os
import subprocess
import sys

import numpy as np
import pytest

from phi.phase4.analysis import analyze_series
from phi.phase4.registration import ComparisonSet

_C = ComparisonSet.build(delta=0.05, k_per_side=4).constants


def _series() -> np.ndarray:
    return np.cumsum(np.random.default_rng(12345).standard_normal(500))


@pytest.mark.reproducibility
def test_in_process_determinism() -> None:
    a = analyze_series(_series(), _C, replicates=300, seed=20260812)
    b = analyze_series(_series(), _C, replicates=300, seed=20260812)
    assert a.delta_hat == b.delta_hat
    assert a.bootstrap is not None and b.bootstrap is not None
    assert a.bootstrap.p_value == b.bootstrap.p_value
    assert (a.bootstrap.ci_low, a.bootstrap.ci_high) == (b.bootstrap.ci_low, b.bootstrap.ci_high)


_CHILD = """
import numpy as np
from phi.phase4.analysis import analyze_series
from phi.phase4.registration import ComparisonSet
c = ComparisonSet.build(delta=0.05, k_per_side=4).constants
s = np.cumsum(np.random.default_rng(12345).standard_normal(500))
a = analyze_series(s, c, replicates=300, seed=20260812)
b = a.bootstrap
print(f"{a.delta_hat!r}|{b.p_value!r}|{b.ci_low!r}|{b.ci_high!r}")
"""


@pytest.mark.reproducibility
def test_cross_process_determinism() -> None:
    # A fresh interpreter with an unpinned hash seed must reproduce the exact result.
    out = subprocess.run(
        [sys.executable, "-c", _CHILD],
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "PYTHONHASHSEED": "random"},
    ).stdout.strip()
    a = analyze_series(_series(), _C, replicates=300, seed=20260812)
    boot = a.bootstrap
    assert boot is not None
    expected = f"{a.delta_hat!r}|{boot.p_value!r}|{boot.ci_low!r}|{boot.ci_high!r}"
    assert out == expected
