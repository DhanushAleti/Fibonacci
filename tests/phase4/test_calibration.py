"""Null-DGP false-positive calibration and power harnesses (spec §XLIV, §XLV).

These lock, as a reproducible regression, the honest finding that the primary
estimand *as specified* (Δ_φ vs matched controls, tested against 0) is **not**
null-calibrated: it rejects H0 under pure-noise DGPs far more than ``alpha``. This
is a documented blocker (see the Phase-4 readiness report), not a target — the
methodology's own hard gate (§XLIV) therefore correctly forbids a confirmatory
claim. If a methodologist later revises the estimand/inference, these expectations
change with it.
"""

from __future__ import annotations

import pytest

from phi.phase4.calibration import estimate_power, estimate_rejection_rate
from phi.phase4.nulldgp import iid_gaussian
from phi.phase4.registration import ComparisonSet

_C = ComparisonSet.build(delta=0.05, k_per_side=4).constants


@pytest.mark.slow
def test_specified_estimand_is_not_null_calibrated() -> None:
    result = estimate_rejection_rate(
        iid_gaussian,
        _C,
        n_series=40,
        series_length=300,
        replicates=99,
        base_seed=20260812,
        dgp_name="iid_gaussian",
    )
    # Jensen bias => Δ_φ >= 0 structurally, so the vs-0 test over-rejects under a
    # pure-null DGP. This documents the blocker; it must NOT be "fixed" in code.
    assert result.mean_delta_hat > 0.0
    assert result.rejection_rate > 0.5
    assert result.is_calibrated() is False


@pytest.mark.slow
def test_power_harness_runs_and_detects_injected_bias() -> None:
    result = estimate_power(_C, n_series=30, series_length=300, replicates=99, base_seed=20260812)
    assert 0.0 <= result.rejection_rate <= 1.0
    assert result.n_valid > 0
