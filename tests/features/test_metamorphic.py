"""Metamorphic / invariant properties (contract §11 item 11)."""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from phi.features.candidate import f_A
from phi.features.constants import G_HALF, G_PHI, G_SQRT2
from phi.features.controls import f_C1, f_C2, f_D
from phi.features.pipeline import compute_windows
from tests.features.conftest import make_ramp_bars, scale_bars, translate_bars


class TestNonNegativity:
    @given(st.floats(min_value=1.0, max_value=1000.0, allow_nan=False))
    def test_f_a_never_negative(self, step: float) -> None:
        bars = make_ramp_bars(30, start=100_000.0, step=step, half_width=0.4)
        for window in compute_windows(bars, window=5):
            value = f_A(window)
            if value is not None:
                assert value >= 0.0


class TestScaleInvariance:
    """p_t (hence f_A, C1, C2, D) is a ratio within the prior range — scaling
    all prices by a positive constant must leave it unchanged (contract §5:
    "already dimensionless and scale-invariant").
    """

    @given(st.floats(min_value=0.01, max_value=1000.0, allow_nan=False, allow_infinity=False))
    def test_p_unchanged_under_positive_price_scaling(self, factor: float) -> None:
        bars = make_ramp_bars(10, start=100.0, step=1.0, half_width=0.5)
        scaled = scale_bars(bars, factor)

        windows_original = compute_windows(bars, window=3)
        windows_scaled = compute_windows(scaled, window=3)

        for original, scaled_result in zip(windows_original, windows_scaled, strict=True):
            if original.p is None:
                assert scaled_result.p is None
            else:
                assert scaled_result.p is not None
                assert scaled_result.p == pytest.approx(original.p, rel=1e-9, abs=1e-12)


class TestTranslationPredictability:
    """Translating all prices by an additive constant changes p_t
    predictably: since p_t = (c - Lo) / (H - Lo), a uniform additive shift
    to every price leaves p_t exactly unchanged too (unlike scaling, a
    constant shift cancels in both numerator and denominator).
    """

    def test_p_unchanged_under_uniform_additive_shift(self) -> None:
        bars = make_ramp_bars(10, start=100.0, step=1.0, half_width=0.5)
        shifted = translate_bars(bars, 500.0)

        windows_original = compute_windows(bars, window=3)
        windows_shifted = compute_windows(shifted, window=3)

        for original, shifted_result in zip(windows_original, windows_shifted, strict=True):
            if original.p is None:
                assert shifted_result.p is None
            else:
                assert shifted_result.p == pytest.approx(original.p, rel=1e-9, abs=1e-12)


class TestSwapConstantIdentities:
    """A, C1, C2 are literally the same function with one constant swapped —
    verified directly against the frozen constants, not just against each
    other (contract §8.1).
    """

    def test_identities_hold_across_a_synthetic_window_sweep(self) -> None:
        bars = make_ramp_bars(30, start=50.0, step=3.0, half_width=1.0)
        for window in compute_windows(bars, window=5):
            if window.p is None:
                continue
            assert f_A(window) == pytest.approx(abs(window.p - G_PHI))
            assert f_C1(window) == pytest.approx(abs(window.p - G_HALF))
            assert f_C2(window) == pytest.approx(abs(window.p - G_SQRT2))
            assert f_D(window) == window.p
