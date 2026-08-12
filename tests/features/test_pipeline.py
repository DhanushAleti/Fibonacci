"""§2 shared pipeline: eligibility, window boundary, leakage, edge cases (contract §6 cases 1-5)."""

from __future__ import annotations

from datetime import timedelta

import pytest

from phi.features.engine import compute_phi_retracement_features
from phi.features.pipeline import (
    DuplicateEventTimeError,
    MixedSymbolError,
    NonMonotonicBarSequenceError,
    compute_window,
    compute_windows,
    validate_bar_sequence,
)
from tests.features.conftest import make_bar, make_flat_bars, make_ramp_bars


class TestWindowGuard:
    """The primitive rejects an out-of-contract window (< 2), making the
    Category F zero-denominator / degenerate-range state unrepresentable."""

    def test_window_one_raises_valueerror(self) -> None:
        bars = make_ramp_bars(5)
        with pytest.raises(ValueError, match="window must be >= 2"):
            compute_window(bars, 3, window=1)

    def test_window_zero_raises_valueerror(self) -> None:
        bars = make_ramp_bars(5)
        with pytest.raises(ValueError, match="window must be >= 2"):
            compute_windows(bars, window=0)

    def test_window_two_is_accepted(self) -> None:
        # The boundary value is valid: f_F's OLS denominator n(n^2-1)/12 = 0.5 > 0.
        rows = compute_phi_retracement_features(make_ramp_bars(6), window=2, seed=1618)
        assert any(row.f_f is not None for row in rows)


class TestInsufficientHistory:
    """Contract §6 case 1: fewer than ``window`` eligible prior bars."""

    def test_first_bar_is_null(self) -> None:
        bars = make_ramp_bars(5)
        result = compute_window(bars, 0, window=3)
        assert result.is_null
        assert result.p is None
        assert result.prior_window == ()

    def test_below_window_is_null(self) -> None:
        bars = make_ramp_bars(5)
        result = compute_window(bars, 2, window=3)  # only 2 prior bars exist
        assert result.is_null

    def test_exactly_at_window_is_not_null(self) -> None:
        bars = make_ramp_bars(5)
        result = compute_window(bars, 3, window=3)  # exactly 3 prior bars
        assert not result.is_null
        assert len(result.prior_window) == 3


class TestLateAvailabilityFiltering:
    """Contract §6 case 2 / §2.1: eligibility filter, not raw index alone."""

    def test_late_arriving_bar_excluded_from_window(self) -> None:
        # Bar 2 is "restated" long after the fact; by t=5 it has NOT yet
        # arrived (its availability_time is after bar 5's).
        bars = [
            make_bar(0, open_=100, high=101, low=99, close=100),
            make_bar(1, open_=100, high=101, low=99, close=100),
            make_bar(
                2,
                open_=100,
                high=101,
                low=99,
                close=100,
                availability_offset=timedelta(days=30),
            ),
            make_bar(3, open_=100, high=101, low=99, close=100),
            make_bar(4, open_=100, high=101, low=99, close=100),
            make_bar(5, open_=100, high=101, low=99, close=100),
        ]
        result = compute_window(bars, 5, window=3)
        # Eligible = [0,1,3,4] (bar 2 excluded); window is last 3 -> [1,3,4].
        assert [b.close for b in result.prior_window] == [100, 100, 100]
        indices_in_window = [bars.index(b) for b in result.prior_window]
        assert indices_in_window == [1, 3, 4]
        assert 2 not in indices_in_window

    def test_post_filter_insufficient_history_is_null(self) -> None:
        # 3 prior bars exist by index (0,1,2), but bar 1 is late-arriving
        # (available only after bar 3), leaving only 2 eligible for
        # window=3 -> NULL (case 2, not case 1: there ARE 3 prior-index
        # bars, but the eligibility filter reduces them below window).
        bars = [
            make_bar(0, open_=100, high=101, low=99, close=100),
            make_bar(
                1,
                open_=100,
                high=101,
                low=99,
                close=100,
                availability_offset=timedelta(days=30),
            ),
            make_bar(2, open_=100, high=101, low=99, close=100),
            make_bar(3, open_=100, high=101, low=99, close=100),
        ]
        result = compute_window(bars, 3, window=3)
        assert result.is_null


@pytest.mark.leakage
class TestLeakageInvariant:
    """Every eligible bar must satisfy availability_time <= decision bar's (contract §4)."""

    def test_no_window_member_is_later_available_than_decision_bar(self) -> None:
        bars = [
            make_bar(0, open_=100, high=101, low=99, close=100),
            make_bar(1, open_=100, high=101, low=99, close=100),
            make_bar(
                2,
                open_=100,
                high=101,
                low=99,
                close=100,
                availability_offset=timedelta(days=30),
            ),
            make_bar(3, open_=100, high=101, low=99, close=100),
            make_bar(4, open_=100, high=101, low=99, close=100),
            make_bar(5, open_=100, high=101, low=99, close=100),
        ]
        decision_bar = bars[5]
        result = compute_window(bars, 5, window=3)
        for w_bar in result.prior_window:
            assert w_bar.availability_time <= decision_bar.availability_time

    def test_feature_value_invariant_to_appending_future_bars(self) -> None:
        base_bars = make_ramp_bars(6)
        extended_bars = make_ramp_bars(10)
        assert extended_bars[:6] == base_bars

        result_short = compute_window(base_bars, 5, window=3)
        result_long = compute_window(extended_bars, 5, window=3)

        assert result_short.p == result_long.p
        assert result_short.prior_window == result_long.prior_window


@pytest.mark.leakage
class TestAdversarialFutureInjection:
    """Mandatory scientific invariant (external contract §16, §37; Gemini red-team dim 26).

    "Inject a spectacularly predictive T+1 value and prove the feature at T
    cannot change." This is a hard leakage invariant, not an optional unit
    test: it must hold for whatever Phase-2 feature is authoritative. It is
    exercised here against the currently-implemented rolling-window feature,
    which is feature-agnostic in spirit — the barrier lives in the shared
    §2 pipeline, not in the candidate transform.
    """

    def test_injecting_1e10_future_bar_does_not_change_feature_at_t(self) -> None:
        bars = make_ramp_bars(6, start=100.0, step=1.0, half_width=0.5)
        t = 5

        p_before = compute_window(bars, t, window=3).p
        assert p_before is not None  # guard: the test must exercise a real value

        # A spectacularly predictive future observation at T+1: schema-valid
        # (all prices > 0, low <= open,close <= high), astronomically large.
        adversarial = make_bar(6, open_=1e10, high=1e10, low=1e10, close=1e10)
        bars_with_future = [*bars, adversarial]

        p_after = compute_window(bars_with_future, t, window=3).p

        # Bit-for-bit identical: the future bar is invisible to the decision at T.
        assert p_after == p_before

    def test_engine_row_at_t_is_bitwise_identical_after_future_injection(self) -> None:
        # Whole-engine version: every emitted control on the row for the last
        # pre-injection bar must be unchanged when a future bar is appended.
        bars = make_ramp_bars(30, start=100.0, step=0.7, half_width=0.4)
        rows_before = compute_phi_retracement_features(bars, window=5, seed=1618)

        adversarial = make_bar(30, open_=1e10, high=1e10, low=1e10, close=1e10)
        rows_after = compute_phi_retracement_features([*bars, adversarial], window=5, seed=1618)

        # Category B is a global rotation over the realized support set, whose
        # size changes when a new supported bar is appended; so B is expected
        # to differ and is excluded from this per-row leakage assertion. Every
        # per-bar transform (A, C1, C2, D, E, F, p) must be identical at each
        # pre-injection index.
        for i in range(len(bars)):
            before, after = rows_before[i], rows_after[i]
            assert before.event_time == after.event_time
            assert before.p == after.p
            assert before.f_a == after.f_a
            assert before.f_c1 == after.f_c1
            assert before.f_c2 == after.f_c2
            assert before.f_d == after.f_d
            assert before.f_e == after.f_e
            assert before.f_f == after.f_f


class TestWindowBoundary:
    """Left-closed/right-open [t-window, t) semantics (contract §2.2, §4)."""

    def test_boundary_and_correctness_worked_example(self) -> None:
        # window=3, t=5: eligible bars are indices 0..4; prior window is the
        # 3 highest-indexed, i.e. indices 2,3,4. Bar 1 (=t-window-1) must be
        # absent; bar 2 (=t-window) must be present; bar 5 (=t) must be absent.
        bars = make_ramp_bars(10, start=100, step=1, half_width=0.5)
        result = compute_window(bars, 5, window=3)

        window_indices = [bars.index(b) for b in result.prior_window]
        assert window_indices == [2, 3, 4]
        assert 1 not in window_indices
        assert 5 not in window_indices

        # Hand-computed: bar i has low=99.5+i, high=100.5+i, close=100+i.
        # H_5 = max(high[2..4]) = 104.5, Lo_5 = min(low[2..4]) = 101.5.
        assert result.high == pytest.approx(104.5)
        assert result.low == pytest.approx(101.5)
        assert result.range_ == pytest.approx(3.0)
        # close_5 = 105 -> p_5 = (105 - 101.5) / 3.0
        assert result.p == pytest.approx((105.0 - 101.5) / 3.0)

    def test_current_bar_high_low_excluded_from_range(self) -> None:
        # Give the decision bar itself an extreme high/low; it must not
        # affect H_t/Lo_t (contract §2.3: "current bar excluded from range").
        bars = make_ramp_bars(4, start=100, step=1, half_width=0.5)
        extreme_current = make_bar(3, open_=100, high=999.0, low=0.01, close=103.0)
        bars_with_extreme = [*bars[:3], extreme_current]
        result = compute_window(bars_with_extreme, 3, window=3)
        assert result.high == pytest.approx(102.5)  # from bars[2], not 999
        assert result.low == pytest.approx(99.5)  # from bars[0], not -999


class TestFlatWindow:
    """Contract §6 case 3: R_t = 0 (degenerate flat window) -> NULL, never divide-by-zero."""

    def test_flat_window_is_null(self) -> None:
        bars = make_flat_bars(5, price=100.0)
        result = compute_window(bars, 3, window=3)
        assert result.is_null
        assert result.range_ == 0.0
        assert result.high == 100.0
        assert result.low == 100.0


class TestNonFiniteOutputGuard:
    """Contract §6 case 8: a non-finite p_t despite range_ > 0 must RAISE.

    This is constructible for real: R_t comes only from the *prior* window,
    while close_t is unconstrained relative to it, so an extreme breakout
    against a tiny prior range can overflow float64 division. This is a
    genuine implementation-bug guard, not decoration — it is exercised here
    with real (schema-valid) inputs, not a mocked internal.
    """

    def test_extreme_breakout_against_tiny_range_raises(self) -> None:
        tiny = 1e-300
        bars = [
            make_bar(0, open_=tiny, high=2 * tiny, low=tiny, close=1.5 * tiny),
            make_bar(1, open_=tiny, high=2 * tiny, low=tiny, close=1.5 * tiny),
            make_bar(2, open_=tiny, high=2 * tiny, low=tiny, close=1.5 * tiny),
            make_bar(3, open_=1e308, high=1e308, low=1e308, close=1e308),
        ]
        with pytest.raises(AssertionError, match="non-finite"):
            compute_window(bars, 3, window=3)


class TestIndexBounds:
    def test_negative_index_raises(self) -> None:
        bars = make_ramp_bars(5)
        with pytest.raises(IndexError):
            compute_window(bars, -1, window=3)

    def test_out_of_range_index_raises(self) -> None:
        bars = make_ramp_bars(5)
        with pytest.raises(IndexError):
            compute_window(bars, 5, window=3)


class TestValidateBarSequence:
    """Contract §6 case 5 and §1's ordering precondition."""

    def test_empty_sequence_is_valid(self) -> None:
        validate_bar_sequence([])  # must not raise

    def test_valid_sequence_does_not_raise(self) -> None:
        validate_bar_sequence(make_ramp_bars(5))

    def test_duplicate_event_time_rejected(self) -> None:
        bars = make_ramp_bars(3)
        # index=1 reproduces bars[1]'s event_time exactly (see make_bar).
        duplicate = make_bar(1, open_=105, high=106, low=104, close=105)
        with pytest.raises(DuplicateEventTimeError):
            validate_bar_sequence([bars[0], bars[1], duplicate])

    def test_non_monotonic_sequence_rejected(self) -> None:
        bars = make_ramp_bars(3)
        with pytest.raises(NonMonotonicBarSequenceError):
            validate_bar_sequence([bars[1], bars[0], bars[2]])

    def test_mixed_symbols_rejected(self) -> None:
        bars_a = make_ramp_bars(2, symbol="AAA")
        bars_b = make_ramp_bars(2, symbol="BBB")
        with pytest.raises(MixedSymbolError):
            validate_bar_sequence([*bars_a, *bars_b])

    def test_compute_windows_validates_once(self) -> None:
        bars = make_ramp_bars(3)
        duplicate = make_bar(0, open_=105, high=106, low=104, close=105)
        with pytest.raises(DuplicateEventTimeError):
            compute_windows([duplicate, bars[0], bars[2]], window=1)
