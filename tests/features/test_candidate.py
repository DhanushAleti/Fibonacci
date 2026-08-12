"""Category A mathematical correctness (contract §3, §11 item 1)."""

from __future__ import annotations

import pytest

from phi.features.candidate import f_A
from phi.features.constants import G_PHI
from phi.features.pipeline import compute_window
from tests.features.conftest import make_bar, make_ramp_bars


class TestCandidateWorkedExamples:
    def test_close_exactly_on_golden_level_gives_zero(self) -> None:
        # window=3, bars 0-2 form a range [low=99, high=101] -> R=2.
        # A close at low + g_phi*R sits exactly on the level -> f_A = 0.
        bars = [
            make_bar(0, open_=100, high=101, low=99, close=100),
            make_bar(1, open_=100, high=101, low=99, close=100),
            make_bar(2, open_=100, high=101, low=99, close=100),
        ]
        target_close = 99.0 + G_PHI * 2.0
        bars.append(make_bar(3, open_=100, high=101, low=99, close=target_close))

        window = compute_window(bars, 3, window=3)
        assert window.p == pytest.approx(G_PHI)
        assert f_A(window) == pytest.approx(0.0, abs=1e-12)

    def test_close_at_prior_high_gives_known_value(self) -> None:
        bars = [
            make_bar(0, open_=100, high=101, low=99, close=100),
            make_bar(1, open_=100, high=101, low=99, close=100),
            make_bar(2, open_=100, high=101, low=99, close=100),
            make_bar(3, open_=100, high=101, low=99, close=101.0),  # close = H_t
        ]
        window = compute_window(bars, 3, window=3)
        assert window.p == pytest.approx(1.0)  # (101-99)/(101-99) = 1
        assert f_A(window) == pytest.approx(abs(1.0 - G_PHI))

    def test_close_at_prior_low_gives_known_value(self) -> None:
        bars = [
            make_bar(0, open_=100, high=101, low=99, close=100),
            make_bar(1, open_=100, high=101, low=99, close=100),
            make_bar(2, open_=100, high=101, low=99, close=100),
            make_bar(3, open_=100, high=101, low=99, close=99.0),  # close = Lo_t
        ]
        window = compute_window(bars, 3, window=3)
        assert window.p == pytest.approx(0.0)
        assert f_A(window) == pytest.approx(G_PHI)

    def test_null_window_propagates_to_null_feature(self) -> None:
        bars = make_ramp_bars(2)
        window = compute_window(bars, 1, window=3)
        assert window.is_null
        assert f_A(window) is None


class TestCandidateInvariants:
    def test_never_negative(self) -> None:
        bars = make_ramp_bars(10, start=100, step=0.37, half_width=0.5)
        for t in range(3, len(bars)):
            window = compute_window(bars, t, window=3)
            value = f_A(window)
            if value is not None:
                assert value >= 0.0

    def test_breakout_above_range_not_clipped(self) -> None:
        bars = [
            make_bar(0, open_=100, high=101, low=99, close=100),
            make_bar(1, open_=100, high=101, low=99, close=100),
            make_bar(2, open_=100, high=101, low=99, close=100),
            make_bar(3, open_=100, high=111, low=99, close=110.0),  # far above prior H_t=101
        ]
        window = compute_window(bars, 3, window=3)
        assert window.p is not None
        assert window.p > 1.0
        assert f_A(window) == pytest.approx(abs(window.p - G_PHI))
