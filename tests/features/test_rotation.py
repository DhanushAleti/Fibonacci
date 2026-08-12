"""Category B: deterministic temporal-alignment placebo (contract §7.1)."""

from __future__ import annotations

import random

import pytest

from phi.features.controls import InsufficientSupportForRotationError, rotate_series

SEED = 1618
WINDOW = 3


class TestRotationCorrectness:
    def test_matches_manual_construction_for_known_seed(self) -> None:
        # 10 non-NULL values, window=3 -> n=10 >= 2*window=6.
        candidate_values: list[float | None] = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        result = rotate_series(candidate_values, seed=SEED, window=WINDOW)

        support_positions = list(range(len(candidate_values)))
        n = len(candidate_values)
        expected_offset = random.Random(SEED).randrange(WINDOW, n - WINDOW + 1)
        expected = [
            candidate_values[support_positions[(k + expected_offset) % n]] for k in range(n)
        ]
        assert result == expected

    def test_null_positions_remain_null(self) -> None:
        candidate_values: list[float | None] = [
            None,
            0.2,
            0.3,
            None,
            0.5,
            0.6,
            0.7,
            0.8,
            None,
            1.0,
        ]
        result = rotate_series(candidate_values, seed=SEED, window=WINDOW)
        null_positions = {i for i, v in enumerate(candidate_values) if v is None}
        for i in null_positions:
            assert result[i] is None
        for i in range(len(candidate_values)):
            if i not in null_positions:
                assert result[i] is not None

    def test_preserves_multiset_of_realized_values(self) -> None:
        candidate_values: list[float | None] = [None, 0.11, 0.22, 0.33, 0.44, 0.55, 0.66, 0.77]
        result = rotate_series(candidate_values, seed=SEED, window=2)
        original_realized = sorted(v for v in candidate_values if v is not None)
        rotated_realized = sorted(v for v in result if v is not None)
        assert original_realized == pytest.approx(rotated_realized)


class TestRotationDeterminism:
    def test_same_seed_same_input_gives_identical_output(self) -> None:
        candidate_values: list[float | None] = [0.1 * i for i in range(12)]
        first = rotate_series(candidate_values, seed=SEED, window=WINDOW)
        second = rotate_series(candidate_values, seed=SEED, window=WINDOW)
        assert first == second

    def test_different_seed_can_give_different_offset(self) -> None:
        candidate_values: list[float | None] = [0.1 * i for i in range(12)]
        a = rotate_series(candidate_values, seed=1, window=WINDOW)
        b = rotate_series(candidate_values, seed=2, window=WINDOW)
        # Not a strict requirement that they differ (small support spaces
        # could coincide), but for this fixture size they must, and this
        # guards against an implementation that ignores the seed entirely.
        assert a != b


class TestRotationFixtureSizing:
    def test_raises_when_support_too_small(self) -> None:
        # n=5 < 2*window=6 -> must raise, not silently return all-NULL.
        candidate_values: list[float | None] = [0.1, 0.2, 0.3, 0.4, 0.5]
        with pytest.raises(InsufficientSupportForRotationError):
            rotate_series(candidate_values, seed=SEED, window=WINDOW)

    def test_exactly_at_boundary_does_not_raise(self) -> None:
        # n=6 == 2*window=6 -> randrange(3, 6-3+1) = randrange(3,4) -> offset=3 always.
        candidate_values: list[float | None] = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        result = rotate_series(candidate_values, seed=SEED, window=WINDOW)
        assert all(v is not None for v in result)

    def test_all_null_input_is_below_threshold_and_raises(self) -> None:
        candidate_values: list[float | None] = [None] * 10
        with pytest.raises(InsufficientSupportForRotationError):
            rotate_series(candidate_values, seed=SEED, window=WINDOW)
