"""Six-category control set: C1, C2, D, E, F correctness (contract §7, §11 item 1)."""

from __future__ import annotations

import math

import pytest

from phi.features.constants import G_HALF, G_SQRT2
from phi.features.controls import _ols_slope, f_C1, f_C2, f_D, f_E_series, f_F
from phi.features.pipeline import compute_window, compute_windows
from tests.features.conftest import make_bar, make_flat_bars, make_ramp_bars


class TestC1FixedRoundNumberBenchmark:
    def test_matches_manual_formula(self) -> None:
        bars = [
            make_bar(0, open_=100, high=101, low=99, close=100),
            make_bar(1, open_=100, high=101, low=99, close=100),
            make_bar(2, open_=100, high=101, low=99, close=100),
            make_bar(3, open_=100, high=101, low=99, close=100.5),  # p=0.75
        ]
        window = compute_window(bars, 3, window=3)
        assert window.p == pytest.approx(0.75)
        assert f_C1(window) == pytest.approx(abs(0.75 - G_HALF))

    def test_null_propagates(self) -> None:
        bars = make_ramp_bars(2)
        window = compute_window(bars, 1, window=3)
        assert f_C1(window) is None


class TestC2NonPhiIrrationalBenchmark:
    def test_matches_manual_formula(self) -> None:
        bars = [
            make_bar(0, open_=100, high=101, low=99, close=100),
            make_bar(1, open_=100, high=101, low=99, close=100),
            make_bar(2, open_=100, high=101, low=99, close=100),
            make_bar(3, open_=100, high=101, low=99, close=100.5),
        ]
        window = compute_window(bars, 3, window=3)
        assert f_C2(window) == pytest.approx(abs(0.75 - G_SQRT2))
        assert pytest.approx(1.0 / math.sqrt(2)) == G_SQRT2

    def test_null_propagates(self) -> None:
        bars = make_ramp_bars(2)
        window = compute_window(bars, 1, window=3)
        assert f_C2(window) is None


class TestDRollingRangePositionBaseline:
    def test_equals_p(self) -> None:
        bars = [
            make_bar(0, open_=100, high=101, low=99, close=100),
            make_bar(1, open_=100, high=101, low=99, close=100),
            make_bar(2, open_=100, high=101, low=99, close=100),
            make_bar(3, open_=100, high=101, low=99, close=100.5),
        ]
        window = compute_window(bars, 3, window=3)
        assert f_D(window) == window.p == pytest.approx(0.75)

    def test_null_propagates(self) -> None:
        bars = make_ramp_bars(2)
        window = compute_window(bars, 1, window=3)
        assert f_D(window) is None


class TestENaiveBaseline:
    def test_index_zero_is_null(self) -> None:
        p_values = [0.5, 0.6, 0.7]
        result = f_E_series(p_values)
        assert result[0] is None

    def test_shifts_by_exactly_one(self) -> None:
        p_values = [0.1, 0.2, None, 0.4, 0.5]
        result = f_E_series(p_values)
        assert result == [None, 0.1, 0.2, None, 0.4]

    def test_empty_series(self) -> None:
        assert f_E_series([]) == []

    def test_full_series_worked_example(self) -> None:
        bars = make_ramp_bars(6, start=100, step=1, half_width=0.5)
        windows = compute_windows(bars, window=3)
        p_values = [w.p for w in windows]
        e_values = f_E_series(p_values)
        for t in range(1, len(bars)):
            assert e_values[t] == p_values[t - 1]
        assert e_values[0] is None


class TestFSimpleStatisticalBaseline:
    def test_ols_slope_of_perfectly_linear_series(self) -> None:
        # closes 0,1,2,...,19 -> slope must be exactly 1.0 (x_k IS the close).
        closes = list(range(20))
        slope = _ols_slope([float(c) for c in closes])
        assert slope == pytest.approx(1.0)

    def test_ols_slope_of_constant_series_is_zero(self) -> None:
        slope = _ols_slope([100.0] * 20)
        assert slope == pytest.approx(0.0)

    def test_denominator_matches_closed_form_for_l_equals_20(self) -> None:
        # contract §7.2: sum((x_k - x_mean)^2) = L(L^2-1)/12 = 665 for L=20.
        n = 20
        x_mean = (n - 1) / 2.0
        denom = sum((k - x_mean) ** 2 for k in range(n))
        assert denom == pytest.approx(665.0)

    def test_matches_manual_worked_example_window3(self) -> None:
        # window=3 prior closes [100, 101, 103] (not perfectly linear).
        bars = [
            make_bar(0, open_=100, high=101, low=99, close=100),
            make_bar(1, open_=101, high=102, low=100, close=101),
            make_bar(2, open_=103, high=104, low=102, close=103),
            make_bar(3, open_=100, high=101, low=99, close=100),
        ]
        window = compute_window(bars, 3, window=3)
        closes = [100.0, 101.0, 103.0]
        x_mean = 1.0  # (3-1)/2
        y_mean = sum(closes) / 3.0
        numerator = sum((k - x_mean) * (y - y_mean) for k, y in enumerate(closes))
        denominator = 3 * (3**2 - 1) / 12.0
        expected_slope = numerator / denominator
        expected_range = window.high - window.low  # type: ignore[operator]
        assert f_F(window) == pytest.approx(expected_slope / expected_range)

    def test_sign_is_retained_for_declining_window(self) -> None:
        bars = [
            make_bar(0, open_=103, high=104, low=102, close=103),
            make_bar(1, open_=102, high=103, low=101, close=102),
            make_bar(2, open_=101, high=102, low=100, close=101),
            make_bar(3, open_=100, high=101, low=99, close=100),
        ]
        window = compute_window(bars, 3, window=3)
        value = f_F(window)
        assert value is not None
        assert value < 0.0

    def test_null_on_flat_window(self) -> None:
        bars = make_flat_bars(4, price=100.0)
        window = compute_window(bars, 3, window=3)
        assert f_F(window) is None

    def test_null_on_insufficient_history(self) -> None:
        bars = make_ramp_bars(2)
        window = compute_window(bars, 1, window=3)
        assert f_F(window) is None

    def test_current_bar_close_not_used(self) -> None:
        # F must not consume close_t at all — changing it must not change f_F.
        base = [
            make_bar(0, open_=100, high=101, low=99, close=100),
            make_bar(1, open_=101, high=102, low=100, close=101),
            make_bar(2, open_=103, high=104, low=102, close=103),
        ]
        bars_a = [*base, make_bar(3, open_=100, high=101, low=99, close=100)]
        bars_b = [*base, make_bar(3, open_=100, high=200, low=50, close=150)]
        window_a = compute_window(bars_a, 3, window=3)
        window_b = compute_window(bars_b, 3, window=3)
        assert f_F(window_a) == f_F(window_b)
