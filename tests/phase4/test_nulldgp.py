"""Null-DGP suite: finiteness, length, determinism, coarse-tick grid (spec §XLIII)."""

from __future__ import annotations

import numpy as np
import pytest

from phi.phase4.nulldgp import NULL_DGPS, coarse_tick, phi_biased_positive_control


class TestDgpSuite:
    @pytest.mark.parametrize("name", list(NULL_DGPS))
    def test_produces_finite_series_of_requested_length(self, name: str) -> None:
        series = NULL_DGPS[name](np.random.default_rng(0), 200)
        assert series.shape == (200,)
        assert np.all(np.isfinite(series))

    @pytest.mark.parametrize("name", list(NULL_DGPS))
    def test_is_deterministic_given_seed(self, name: str) -> None:
        a = NULL_DGPS[name](np.random.default_rng(20260812), 100)
        b = NULL_DGPS[name](np.random.default_rng(20260812), 100)
        assert np.array_equal(a, b)

    def test_suite_has_the_ten_plus_microstructure_dgps(self) -> None:
        # Spec §XLIII: 10 DGPs + the red-team coarse-tick microstructure null.
        assert len(NULL_DGPS) >= 11
        assert "coarse_tick" in NULL_DGPS


class TestCoarseTick:
    def test_values_lie_on_the_tick_grid(self) -> None:
        tick = 0.25
        series = coarse_tick(np.random.default_rng(1), 500, tick=tick)
        # Every value is an integer multiple of the tick.
        assert np.allclose(series / tick, np.round(series / tick))


class TestPositiveControl:
    def test_finite_and_correct_length(self) -> None:
        series = phi_biased_positive_control(np.random.default_rng(2), 300)
        assert series.shape == (300,) and np.all(np.isfinite(series))
