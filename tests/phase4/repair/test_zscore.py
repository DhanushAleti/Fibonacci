"""Standardized null score Z_phi: math, null behaviour, injection detection (Repair Part 2)."""

from __future__ import annotations

import numpy as np
import pytest

from phi.phase4.repair.positive_control import phi_attractor_garch
from phi.phase4.repair.rational import Q_PHI, RATIONAL_CONSTANTS
from phi.phase4.repair.zscore import eligible_retracements, phi_advantage, standardized_null_score

_C = tuple(RATIONAL_CONSTANTS.values())


class TestPhiAdvantage:
    def test_zero_when_all_r_on_focal(self) -> None:
        # If every R == focal, E|R-focal| = 0 and the advantage is the mean control distance.
        r = np.full(50, Q_PHI)
        expected = float(np.mean([np.mean(np.abs(r - c)) for c in _C]))
        assert phi_advantage(r, focal=Q_PHI, constants=_C) == pytest.approx(expected)


class TestNullBehaviour:
    def test_null_series_does_not_show_phi_excess(self) -> None:
        # A pure random walk (no phi mechanism): Z_phi should not be significantly > 0.
        series = np.cumsum(np.random.default_rng(0).standard_normal(600))
        score = standardized_null_score(series, constants=_C, n_surrogates=99, seed=20260812)
        assert score is not None
        assert score.surrogate_p >= 0.05  # not a false positive
        assert score.z_phi <= 3.0

    def test_determinism(self) -> None:
        series = np.cumsum(np.random.default_rng(1).standard_normal(400))
        a = standardized_null_score(series, constants=_C, n_surrogates=50, seed=7)
        b = standardized_null_score(series, constants=_C, n_surrogates=50, seed=7)
        assert a is not None and b is not None
        assert (a.z_phi, a.surrogate_p, a.delta_obs) == (b.z_phi, b.surrogate_p, b.delta_obs)

    def test_too_few_retracements_returns_none(self) -> None:
        assert (
            standardized_null_score(list(range(40)), constants=_C, n_surrogates=50, seed=1) is None
        )


class TestInjectionDetection:
    def test_strong_phi_injection_lifts_z(self) -> None:
        # Large-signal positive control: Z_phi should be positive vs a null of the same length.
        rng = np.random.default_rng(4)
        injected = phi_attractor_garch(rng, 900, inject_prob=0.30)
        score = standardized_null_score(injected, constants=_C, n_surrogates=99, seed=20260812)
        assert score is not None
        assert score.z_phi > 0.0


class TestEligibleRetracements:
    def test_returns_values_in_unit_interval(self) -> None:
        series = np.cumsum(np.random.default_rng(2).standard_normal(400))
        r = eligible_retracements(series)
        assert r.size > 0 and np.all((r >= 0.0) & (r <= 1.0))
