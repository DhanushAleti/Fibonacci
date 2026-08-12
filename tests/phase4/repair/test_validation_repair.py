"""Repair validation harness at tiny scale (Repair Part 8). Marked slow."""

from __future__ import annotations

import pytest

from phi.phase4.nulldgp import iid_gaussian
from phi.phase4.repair.validation import (
    RepairValidation,
    constant_sweep_symmetry,
    positive_control_power,
    run_repair_validation,
    surrogate_fpr,
)


@pytest.mark.slow
class TestHarness:
    def test_surrogate_fpr_low_on_iid_gaussian(self) -> None:
        rate, valid = surrogate_fpr(
            iid_gaussian, n_series=40, series_length=300, n_surrogates=49, base_seed=1
        )
        assert valid > 0
        assert rate <= 0.15  # neutralized geometric bias (not 1.0); small-scale tolerance

    def test_constant_sweep_returns_per_focal(self) -> None:
        fpr, _symmetric = constant_sweep_symmetry(
            n_series=20, series_length=300, n_surrogates=39, base_seed=2
        )
        assert len(fpr) == 3

    def test_positive_control_power_in_unit_interval(self) -> None:
        p = positive_control_power(
            inject_prob=0.3, n_series=20, series_length=300, n_surrogates=39, base_seed=3
        )
        assert 0.0 <= p <= 1.0

    def test_full_gate_returns_all_fields(self) -> None:
        v = run_repair_validation(n_series=10, series_length=250, n_surrogates=29, base_seed=4)
        assert isinstance(v, RepairValidation)
        assert isinstance(v.passes, bool)
        assert 0.0 <= v.aggregate_fpr <= 1.0
        assert len(v.per_dgp_fpr) == 13
