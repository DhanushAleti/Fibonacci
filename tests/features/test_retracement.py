"""Frozen excursion-retracement math (external contract §4, §8, §9, §43).

These tests pin the *frozen* arithmetic exactly. They deliberately do NOT test
any anchor-selection algorithm (Blocker 1) or any epsilon_phi value (Blocker 2)
— those are unfrozen and unimplemented by design (ADR 0003).
"""

from __future__ import annotations

import math

import pytest
from hypothesis import given
from hypothesis import strategies as st

from phi import PHI
from phi.features.retracement import (
    Q_PHI,
    NonFiniteRetracementError,
    is_phi_hit,
    phi_distance,
    retracement_ratio,
)


class TestQPhi:
    def test_q_phi_is_reciprocal_of_phi(self) -> None:
        assert pytest.approx(1.0 / PHI) == Q_PHI
        # Algebraic identity 1/phi == phi - 1 (contract §3).
        assert pytest.approx(PHI - 1.0) == Q_PHI
        assert pytest.approx(0.6180339887498949) == Q_PHI


class TestRetracementRatioWorkedExamples:
    def test_exactly_on_golden_level(self) -> None:
        # Excursion 100 -> 200 (magnitude 100). X_t at 138.196 gives
        # |X_t - X_e| = |138.196 - 200| = 61.804 -> R_t = 0.61804 ~ q_phi.
        x_a, x_e = 100.0, 200.0
        x_t = x_e - Q_PHI * (x_e - x_a)  # lands exactly on q_phi from X_e
        r = retracement_ratio(x_a, x_e, x_t)
        assert r == pytest.approx(Q_PHI)

    def test_full_retracement_is_one(self) -> None:
        # X_t returns exactly to the anchor -> |X_t - X_e| = |X_e - X_a| -> R=1.
        assert retracement_ratio(100.0, 200.0, 100.0) == pytest.approx(1.0)

    def test_no_retracement_is_zero(self) -> None:
        # X_t sits at the endpoint -> numerator 0 -> R=0.
        assert retracement_ratio(100.0, 200.0, 200.0) == pytest.approx(0.0)

    def test_downward_excursion_symmetric(self) -> None:
        # Direction does not matter: magnitudes only (200 -> 100).
        assert retracement_ratio(200.0, 100.0, 161.803) == pytest.approx(
            abs(161.803 - 100.0) / 100.0
        )

    def test_overshoot_beyond_one_not_clamped(self) -> None:
        # X_t past the anchor -> R > 1, returned unclamped (Attack Vector 8).
        r = retracement_ratio(100.0, 200.0, 50.0)
        assert r == pytest.approx(1.5)
        assert r > 1.0


class TestRetracementRatioEdgeCases:
    def test_zero_excursion_returns_na_not_epsilon(self) -> None:
        # Contract §8: |X_e - X_a| == 0 -> NA (None). No epsilon substitution,
        # no division error.
        assert retracement_ratio(100.0, 100.0, 137.0) is None

    def test_negative_values_allowed(self) -> None:
        # Contract §9: negatives are valid; the ratio uses absolute magnitudes.
        r = retracement_ratio(-50.0, -10.0, -30.0)
        # excursion magnitude = 40; |X_t - X_e| = |-30 - (-10)| = 20 -> 0.5
        assert r == pytest.approx(0.5)

    def test_overflow_raises_not_silent_inf(self) -> None:
        # Nonzero-but-subnormal excursion with a huge numerator overflows to inf;
        # must raise, never return a silent non-finite value.
        with pytest.raises(NonFiniteRetracementError):
            retracement_ratio(0.0, 5e-324, 1e308)

    def test_result_is_always_non_negative(self) -> None:
        assert retracement_ratio(100.0, 200.0, 175.0) >= 0.0  # type: ignore[operator]


class TestPhiDistance:
    def test_zero_on_level(self) -> None:
        assert phi_distance(Q_PHI) == pytest.approx(0.0, abs=1e-15)

    def test_matches_absolute_difference(self) -> None:
        assert phi_distance(0.5) == pytest.approx(abs(0.5 - Q_PHI))

    def test_never_negative(self) -> None:
        for r in (-2.0, 0.0, 0.5, Q_PHI, 1.0, 5.0):
            assert phi_distance(r) >= 0.0


class TestIsPhiHit:
    def test_hit_when_within_epsilon(self) -> None:
        assert is_phi_hit(Q_PHI + 0.005, epsilon=0.01) is True

    def test_miss_when_outside_epsilon(self) -> None:
        assert is_phi_hit(Q_PHI + 0.05, epsilon=0.01) is False

    def test_boundary_is_inclusive(self) -> None:
        # Use an exact distance so float rounding cannot push it over: the hit
        # rule is `<=`, so distance == epsilon must count as a hit.
        r = 0.5
        eps = phi_distance(r)
        assert is_phi_hit(r, epsilon=eps) is True  # distance == epsilon (inclusive)
        assert is_phi_hit(r, epsilon=eps - 1e-12) is False  # just below -> miss

    def test_epsilon_is_required_keyword_only(self) -> None:
        # Anti-threshold-fishing: no positional epsilon, no default.
        with pytest.raises(TypeError):
            is_phi_hit(Q_PHI, 0.01)  # type: ignore[misc]
        with pytest.raises(TypeError):
            is_phi_hit(Q_PHI)  # type: ignore[call-arg]

    def test_negative_epsilon_rejected(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            is_phi_hit(Q_PHI, epsilon=-0.01)


class TestScaleInvarianceProperty:
    @given(
        scale=st.floats(min_value=1e-3, max_value=1e6, allow_nan=False, allow_infinity=False),
        x_a=st.floats(min_value=-1e4, max_value=1e4, allow_nan=False),
        gap=st.floats(min_value=1.0, max_value=1e4, allow_nan=False),
        x_t=st.floats(min_value=-1e4, max_value=1e4, allow_nan=False),
    )
    def test_ratio_invariant_under_common_positive_scaling(
        self, scale: float, x_a: float, gap: float, x_t: float
    ) -> None:
        # R_t is a ratio of differences, so multiplying every price by a common
        # positive constant leaves it unchanged.
        x_e = x_a + gap  # guarantees nonzero excursion
        base = retracement_ratio(x_a, x_e, x_t)
        scaled = retracement_ratio(x_a * scale, x_e * scale, x_t * scale)
        assert base is not None and scaled is not None
        if math.isfinite(base) and math.isfinite(scaled):
            assert scaled == pytest.approx(base, rel=1e-9, abs=1e-12)
