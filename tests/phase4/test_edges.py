"""Edge-case and secondary-path behavior across the Phase-4 modules."""

from __future__ import annotations

import numpy as np
import pytest

from phi.phase4.analysis import analyze_series
from phi.phase4.calibration import all_nulls_calibrated, null_calibration
from phi.phase4.estimand import (
    delta_phi,
    dense_grid,
    mean_phi_distance,
    median_phi_distance,
    paired_z,
)
from phi.phase4.inference import BootstrapResult, politis_white_block_length
from phi.phase4.multiplicity import holm_step_down
from phi.phase4.registration import ComparisonSet, ComparisonSetError

_C = ComparisonSet.build(delta=0.05, k_per_side=4).constants


class TestEstimandGuardsAndSecondaries:
    def test_paired_z_empty_sample_returns_empty(self) -> None:
        assert paired_z([], _C).size == 0

    def test_paired_z_requires_controls(self) -> None:
        with pytest.raises(ValueError, match="comparison_set is empty"):
            paired_z([0.5], ())

    def test_delta_phi_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="undefined"):
            delta_phi([], _C)

    def test_mean_and_median_phi_distance(self) -> None:
        r = [0.6180339887498949]  # exactly q_phi
        assert mean_phi_distance(r) == pytest.approx(0.0, abs=1e-12)
        assert median_phi_distance(r) == pytest.approx(0.0, abs=1e-12)

    def test_dense_grid_spans_the_registered_domain(self) -> None:
        grid = dense_grid(lo=0.05, hi=0.95, step=0.001)
        assert grid[0] == pytest.approx(0.05)
        assert grid[-1] == pytest.approx(0.95)
        assert grid.size == 901


class TestBlockLengthEdges:
    def test_tiny_series_returns_unit_block(self) -> None:
        assert politis_white_block_length(np.array([1.0, 2.0, 3.0])) == 1.0

    def test_constant_series_returns_unit_block(self) -> None:
        assert politis_white_block_length(np.ones(100)) == 1.0


class TestCiExcludesZero:
    def _r(self, lo: float, hi: float) -> BootstrapResult:
        return BootstrapResult(0.0, lo, hi, 0.1, 0.0, 1.0, 10, 1, 10)

    def test_excludes_when_entirely_positive(self) -> None:
        assert self._r(0.01, 0.02).ci_excludes_zero is True

    def test_includes_when_spanning_zero(self) -> None:
        assert self._r(-0.01, 0.02).ci_excludes_zero is False


class TestMultiplicityGuard:
    def test_alpha_must_be_in_unit_interval(self) -> None:
        with pytest.raises(ValueError, match="alpha"):
            holm_step_down([0.01], alpha=1.5)


class TestComparisonSetBuildErrors:
    @pytest.mark.parametrize("delta", [0.0, -0.05])
    def test_nonpositive_delta_rejected(self, delta: float) -> None:
        with pytest.raises(ComparisonSetError, match="delta"):
            ComparisonSet.build(delta=delta, k_per_side=3)

    def test_zero_controls_rejected(self) -> None:
        with pytest.raises(ComparisonSetError, match="k_per_side"):
            ComparisonSet.build(delta=0.05, k_per_side=0)


class TestAnalysisTooFewExcursions:
    def test_monotone_series_yields_no_inference(self) -> None:
        analysis = analyze_series(list(range(50)), _C, replicates=50, seed=1)
        assert analysis.n_excursions == 0
        assert analysis.n_eligible == 0
        assert analysis.bootstrap is None
        assert analysis.delta_hat is None
        assert analysis.rejected_h0 is False


class TestNullCalibrationHarness:
    @pytest.mark.slow
    def test_full_suite_runs_and_reports_per_dgp(self) -> None:
        results = null_calibration(_C, n_series=3, series_length=120, replicates=39, base_seed=1)
        assert set(results) == {
            "iid_gaussian",
            "iid_heavy_tailed",
            "random_walk",
            "ar1",
            "heteroskedastic",
            "garch11",
            "regime_switching",
            "trend_plus_noise",
            "seasonality",
            "market_like",
            "coarse_tick",
        }
        assert isinstance(all_nulls_calibrated(results), bool)
