"""Dependence-aware inference: block length, determinism, dependence-robust SE (spec §XXXII)."""

from __future__ import annotations

import numpy as np
import pytest

from phi.phase4.inference import (
    bootstrap_delta_phi,
    politis_white_block_length,
    stationary_bootstrap_indices,
)


def _ar1(n: int, rho: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    x = np.empty(n, dtype=np.float64)
    eps = rng.standard_normal(n)
    x[0] = eps[0]
    for t in range(1, n):
        x[t] = rho * x[t - 1] + eps[t]
    return x


class TestBlockLength:
    def test_iid_gives_short_block(self) -> None:
        x = np.random.default_rng(0).standard_normal(1000)
        assert politis_white_block_length(x) <= 3.0

    def test_stronger_dependence_gives_longer_block(self) -> None:
        # Monotone dependence -> monotone (at least non-decreasing) block length.
        b_iid = politis_white_block_length(_ar1(2000, 0.0, 1))
        b_mid = politis_white_block_length(_ar1(2000, 0.6, 1))
        b_high = politis_white_block_length(_ar1(2000, 0.9, 1))
        assert b_high > b_mid > b_iid


class TestDeterminism:
    def test_same_seed_same_indices(self) -> None:
        a = stationary_bootstrap_indices(
            50, expected_block_length=5.0, rng=np.random.default_rng(7)
        )
        b = stationary_bootstrap_indices(
            50, expected_block_length=5.0, rng=np.random.default_rng(7)
        )
        assert np.array_equal(a, b)

    def test_bootstrap_result_is_reproducible(self) -> None:
        z = np.random.default_rng(0).standard_normal(300)
        r1 = bootstrap_delta_phi(z, replicates=500, seed=20260812, block_length=4.0)
        r2 = bootstrap_delta_phi(z, replicates=500, seed=20260812, block_length=4.0)
        assert r1.delta_hat == r2.delta_hat
        assert r1.ci_low == r2.ci_low and r1.ci_high == r2.ci_high
        assert r1.p_value == r2.p_value

    def test_needs_at_least_two_observations(self) -> None:
        with pytest.raises(ValueError, match=">= 2"):
            bootstrap_delta_phi(np.array([0.3]), replicates=10, seed=1)


class TestDependenceRobustSE:
    """A longer block (dependence-aware) widens the CI on autocorrelated data (Gemini dim 6)."""

    def test_dependence_widens_ci_vs_iid(self) -> None:
        z = _ar1(600, 0.9, 3)  # strongly positively autocorrelated advantage series
        iid = bootstrap_delta_phi(z, replicates=1000, seed=5, block_length=1.0)
        dep = bootstrap_delta_phi(z, replicates=1000, seed=5, block_length=40.0)
        width_iid = iid.ci_high - iid.ci_low
        width_dep = dep.ci_high - dep.ci_low
        assert width_dep > width_iid
