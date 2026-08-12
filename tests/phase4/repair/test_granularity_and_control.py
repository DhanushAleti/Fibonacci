"""Granularity audit + phi-attractor positive control (Repair Parts 6-7)."""

from __future__ import annotations

import numpy as np
import pytest

from phi.phase4.repair.granularity import (
    coarse_tick_fbm_null,
    discretize,
    fbm,
    granularity_audit,
    phi_vs_five_eighths_distance,
)
from phi.phase4.repair.positive_control import phi_attractor_garch


class TestFbmAndDiscretize:
    def test_fbm_shape_and_finite(self) -> None:
        x = fbm(np.random.default_rng(0), 400, hurst=0.7)
        assert x.shape == (400,) and np.all(np.isfinite(x))

    def test_discretize_lands_on_grid(self) -> None:
        x = fbm(np.random.default_rng(1), 400)
        d = discretize(x, n_levels=10)
        assert len(np.unique(np.round(d, 8))) <= 12  # ~10 distinct tick levels

    def test_coarse_tick_null_shape(self) -> None:
        s = coarse_tick_fbm_null(np.random.default_rng(2), 300, n_levels=50)
        assert s.shape == (300,) and np.all(np.isfinite(s))

    def test_phi_vs_five_eighths_distance_returns_two_means(self) -> None:
        r = np.random.default_rng(3).uniform(0, 1, 100)
        d_phi, d_58 = phi_vs_five_eighths_distance(r)
        assert d_phi >= 0.0 and d_58 >= 0.0


class TestPhiAttractorControl:
    def test_shape_finite_and_deterministic(self) -> None:
        a = phi_attractor_garch(np.random.default_rng(5), 600, inject_prob=0.15)
        b = phi_attractor_garch(np.random.default_rng(5), 600, inject_prob=0.15)
        assert np.all(np.isfinite(a)) and np.array_equal(a, b)


class TestGranularityAuditRuns:
    @pytest.mark.slow
    def test_audit_reports_per_resolution_fpr(self) -> None:
        audit = granularity_audit(
            tick_levels=(100, 10), n=250, n_series=15, n_surrogates=39, base_seed=1
        )
        assert set(audit.phi_fpr_by_level) == {100, 10}
        assert isinstance(audit.passes, bool)
