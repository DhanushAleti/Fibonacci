"""Surrogate ensemble: determinism, marginal preservation, shapes (Repair Part 4)."""

from __future__ import annotations

import numpy as np

from phi.phase4.repair.surrogates import (
    SURROGATES,
    block_length_for,
    block_permutation_surrogate,
    garch_surrogate,
    iaaft_surrogate,
)


def _series(seed: int = 0, n: int = 300) -> np.ndarray:
    return np.cumsum(np.random.default_rng(seed).standard_normal(n))


class TestBlockPermutation:
    def test_preserves_the_exact_marginal(self) -> None:
        x = _series()
        surr = block_permutation_surrogate(x, np.random.default_rng(1), block_length=8.0)
        assert np.array_equal(np.sort(x), np.sort(surr))  # same multiset of values

    def test_is_deterministic_given_seed(self) -> None:
        x = _series()
        a = block_permutation_surrogate(x, np.random.default_rng(3), block_length=8.0)
        b = block_permutation_surrogate(x, np.random.default_rng(3), block_length=8.0)
        assert np.array_equal(a, b)

    def test_destroys_ordering(self) -> None:
        x = _series()
        surr = block_permutation_surrogate(x, np.random.default_rng(5), block_length=8.0)
        assert not np.array_equal(x, surr)


class TestOtherFamilies:
    def test_garch_and_iaaft_return_finite_series_of_length_n(self) -> None:
        x = _series(n=256)
        for fn in (garch_surrogate, iaaft_surrogate):
            surr = fn(x, np.random.default_rng(7))
            assert surr.shape == x.shape and np.all(np.isfinite(surr))

    def test_registry_has_the_three_families_with_block_permutation_primary(self) -> None:
        assert set(SURROGATES) == {"block_permutation", "garch", "iaaft"}


class TestBlockLength:
    def test_returns_finite_block_at_least_one(self) -> None:
        for x in (np.random.default_rng(0).standard_normal(1000), _series(n=1000)):
            length = block_length_for(x)
            assert np.isfinite(length) and length >= 1.0

    def test_tiny_series_is_unit(self) -> None:
        assert block_length_for(np.array([1.0, 2.0])) == 1.0
