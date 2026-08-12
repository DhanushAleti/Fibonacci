"""Shared §2 computation — identical code path for the candidate and every control.

Implements ``docs/05-mathematics/phi-retracement-feature-contract.md`` §2
(eligibility filter, prior window, prior range, position-in-range) and the
parts of §6 (edge-case contract) that are the pipeline's responsibility:
insufficient history (cases 1-2) and a degenerate flat window (case 3).

Cases 6-7 of the edge-case contract (OHLC inconsistency, non-finite prices)
are **not** re-checked here: they are structurally impossible for a
constructed ``PriceBar`` (``phi.data.schemas`` enforces both at the type
boundary, see ``tests/data/test_schemas.py``), so re-validating them in this
module would be dead defensive code for a condition the type system already
forbids.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from phi.data.schemas import PriceBar
from phi.features.constants import DEFAULT_WINDOW


class DuplicateEventTimeError(ValueError):
    """Two or more input bars share an ``event_time`` (contract §6 case 5).

    Phase 1 (``phi.data.validation``) must dedupe/quarantine before bars
    reach the feature layer; a duplicate surviving to here is an upstream
    contract violation, not a data condition to silently tolerate.
    """


class NonMonotonicBarSequenceError(ValueError):
    """Input bars are not strictly ascending by ``event_time`` (contract §1).

    ``B`` is defined as "ordered by ``event_time`` ascending, exactly as
    produced by Phase 1." The feature layer treats a violation as a defect
    to surface, not something to silently re-sort — silent re-sorting would
    hide exactly the kind of upstream bug this check exists to catch.
    """


class MixedSymbolError(ValueError):
    """Input bars span more than one instrument ``symbol``.

    The shared pipeline operates on one instrument's validated series;
    silently mixing symbols would compute a prior range across unrelated
    instruments.
    """


def validate_bar_sequence(bars: Sequence[PriceBar]) -> None:
    """Validate that ``bars`` satisfies the §1 precondition for ``B``.

    Raises on the first violation found, scanning in sequence order. Callers
    that will make many :func:`compute_window` calls over the same series
    should call this once up front (as :func:`compute_windows` does) rather
    than re-validating per call.
    """
    if not bars:
        return
    symbol = bars[0].symbol
    previous_event_time = bars[0].event_time
    for bar in bars[1:]:
        if bar.symbol != symbol:
            raise MixedSymbolError(
                f"bar sequence mixes symbols {symbol!r} and {bar.symbol!r}; the "
                "shared pipeline requires a single instrument's validated series "
                "(contract §1)"
            )
        if bar.event_time == previous_event_time:
            raise DuplicateEventTimeError(
                f"duplicate event_time {bar.event_time.isoformat()!r} in bar "
                "sequence; Phase 1 must dedupe/quarantine before the feature "
                "layer (contract §6 case 5)"
            )
        if bar.event_time < previous_event_time:
            raise NonMonotonicBarSequenceError(
                f"bar at event_time {bar.event_time.isoformat()!r} precedes the "
                f"prior bar at {previous_event_time.isoformat()!r}; B must be "
                "ordered by event_time ascending (contract §1)"
            )
        previous_event_time = bar.event_time


@dataclass(frozen=True)
class WindowResult:
    """Result of the shared §2 computation for one decision index ``t``.

    ``p`` (and hence :attr:`is_null`) is the single source of truth for NULL
    propagation: the candidate and every control derive their own NULL from
    this one flag, so NULL masks cannot diverge between them by construction
    (contract §8's matching requirement that they share "the same NULL /
    support policy").
    """

    t: int
    close: float
    prior_window: tuple[PriceBar, ...]
    high: float | None
    low: float | None
    range_: float | None
    p: float | None

    @property
    def is_null(self) -> bool:
        return self.p is None


def compute_window(
    bars: Sequence[PriceBar], t: int, *, window: int = DEFAULT_WINDOW
) -> WindowResult:
    """Compute the §2 shared window/position result for decision index ``t``.

    Assumes ``bars`` already satisfies the §1 precondition (validated,
    ordered by ``event_time`` ascending, one instrument) — this function does
    not re-validate it; call :func:`validate_bar_sequence` once beforehand
    (or use :func:`compute_windows`, which does).

    Implements the §2.1 eligibility filter (``i < t`` and
    ``availability_time_i <= availability_time_t``),
    §2.2 prior window (the ``window`` highest-indexed eligible bars), §2.3
    prior range (excluding bar ``t`` itself), and §2.4 position-in-range.
    Returns a NULL result (``p is None``) for edge cases 1-3 of §6:
    insufficient eligible history, or a degenerate flat window
    (``range_ == 0``).
    """
    if window < 2:
        # Make the impossible state unrepresentable rather than relying on the
        # frozen L=20 default: a length-1 window gives Category F's OLS slope a
        # zero denominator (``n(n^2-1)/12 = 0`` at ``n=1``, see controls._ols_slope)
        # and a degenerate single-bar range. The contract fixes ``L=20`` (§1);
        # this guard defends the primitive itself against an out-of-contract call.
        raise ValueError(f"window must be >= 2 (got {window}); see contract §1 (L=20)")
    if t < 0 or t >= len(bars):
        raise IndexError(f"decision index t={t} out of range for {len(bars)} bars")

    decision_bar = bars[t]
    eligible = [bar for bar in bars[:t] if bar.availability_time <= decision_bar.availability_time]

    if len(eligible) < window:
        return WindowResult(
            t=t,
            close=decision_bar.close,
            prior_window=(),
            high=None,
            low=None,
            range_=None,
            p=None,
        )

    prior_window = tuple(eligible[-window:])
    high = max(bar.high for bar in prior_window)
    low = min(bar.low for bar in prior_window)
    range_ = high - low

    if range_ == 0.0:
        return WindowResult(
            t=t,
            close=decision_bar.close,
            prior_window=prior_window,
            high=high,
            low=low,
            range_=0.0,
            p=None,
        )

    p = (decision_bar.close - low) / range_
    if not math.isfinite(p):
        # Contract §6 case 8: a non-finite result despite range_ > 0 is an
        # implementation bug, never a silently-tolerated NaN/inf output.
        raise AssertionError(
            f"non-finite p_t={p!r} at t={t} despite range_={range_!r} > 0; this "
            "indicates an implementation bug (contract §6 case 8)"
        )

    return WindowResult(
        t=t,
        close=decision_bar.close,
        prior_window=prior_window,
        high=high,
        low=low,
        range_=range_,
        p=p,
    )


def compute_windows(
    bars: Sequence[PriceBar], *, window: int = DEFAULT_WINDOW
) -> list[WindowResult]:
    """Compute :func:`compute_window` for every index in ``bars``.

    Validates the §1 precondition once up front via
    :func:`validate_bar_sequence`.
    """
    validate_bar_sequence(bars)
    return [compute_window(bars, t, window=window) for t in range(len(bars))]
