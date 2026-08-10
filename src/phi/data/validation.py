"""Data Validation (SYSTEM_ARCHITECTURE §9.2, module 2).

Rejects or flags malformed/suspicious data before it reaches storage. This
module never silently "fixes" data: a bar is only ever dropped from the valid
set when keeping it would require guessing (an unresolvable conflicting
duplicate) or when it is a bit-identical redundant copy of another retained
record. Every anomaly — including ones that don't remove anything — is recorded
as a ``DataQualityFlag`` so the failure is visible, not hidden (PRD-BIAS-001).

Scope for this increment: daily-bar gap detection (via a weekday-based
calendar), exact/conflicting duplicate detection, arrival-order monotonicity,
and a simple z-score volume-plausibility check. Cross-provider disagreement
flags and corporate-action detection are not yet implemented (tracked as a
known limitation — see ``phi/data/schemas.py`` module docstring).
"""

from __future__ import annotations

import statistics
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from phi.data.calendar import SimpleTradingCalendar
from phi.data.schemas import DataQualityFlag, PriceBar, QualityFlagType

_MIN_BARS_FOR_VOLUME_CHECK = 3


@dataclass(frozen=True)
class ValidationResult:
    """Validated bars plus every flag raised while producing them."""

    valid_bars: tuple[PriceBar, ...]
    flags: tuple[DataQualityFlag, ...]


def validate_price_bars(
    bars: list[PriceBar],
    *,
    calendar: SimpleTradingCalendar,
    now: datetime,
    volume_z_threshold: float = 5.0,
) -> ValidationResult:
    """Validate bars as received (order matters — see monotonicity check below).

    Bars for different symbols are validated independently; nothing about one
    symbol's data affects another's flags or valid set.
    """
    by_symbol: dict[str, list[PriceBar]] = defaultdict(list)
    for bar in bars:
        by_symbol[bar.symbol].append(bar)

    all_valid: list[PriceBar] = []
    all_flags: list[DataQualityFlag] = []
    for symbol, symbol_bars in by_symbol.items():
        valid, flags = _validate_one_symbol(
            symbol, symbol_bars, calendar=calendar, now=now, volume_z_threshold=volume_z_threshold
        )
        all_valid.extend(valid)
        all_flags.extend(flags)

    return ValidationResult(valid_bars=tuple(all_valid), flags=tuple(all_flags))


def _validate_one_symbol(
    symbol: str,
    bars: list[PriceBar],
    *,
    calendar: SimpleTradingCalendar,
    now: datetime,
    volume_z_threshold: float,
) -> tuple[list[PriceBar], list[DataQualityFlag]]:
    flags: list[DataQualityFlag] = []

    flags.extend(_check_monotonicity(symbol, bars, now=now))

    sorted_bars = sorted(bars, key=lambda b: b.event_time)
    deduped, dup_flags = _dedupe(symbol, sorted_bars, now=now)
    flags.extend(dup_flags)

    flags.extend(_check_gaps(symbol, deduped, calendar=calendar, now=now))
    flags.extend(_check_volume(symbol, deduped, now=now, z_threshold=volume_z_threshold))

    return deduped, flags


def _check_monotonicity(
    symbol: str, bars: list[PriceBar], *, now: datetime
) -> list[DataQualityFlag]:
    flags = []
    previous: PriceBar | None = None
    for bar in bars:
        if previous is not None and bar.event_time < previous.event_time:
            flags.append(
                DataQualityFlag(
                    flag_type=QualityFlagType.NON_MONOTONIC_TIMESTAMP,
                    symbol=symbol,
                    event_time=bar.event_time,
                    detail=(
                        f"bar at {bar.event_time.isoformat()} arrived after "
                        f"{previous.event_time.isoformat()} out of chronological order"
                    ),
                    raised_at=now,
                )
            )
        previous = bar
    return flags


def _dedupe(
    symbol: str, sorted_bars: list[PriceBar], *, now: datetime
) -> tuple[list[PriceBar], list[DataQualityFlag]]:
    groups: dict[datetime, list[PriceBar]] = defaultdict(list)
    for bar in sorted_bars:
        groups[bar.event_time].append(bar)

    valid: list[PriceBar] = []
    flags: list[DataQualityFlag] = []
    for event_time, group in groups.items():
        if len(group) == 1:
            valid.append(group[0])
            continue
        if all(b == group[0] for b in group):
            # Bit-identical redundant copies: keep exactly one, flag the rest.
            valid.append(group[0])
            flags.append(
                DataQualityFlag(
                    flag_type=QualityFlagType.DUPLICATE,
                    symbol=symbol,
                    event_time=event_time,
                    detail=f"{len(group)} identical duplicate records for {event_time.isoformat()}",
                    raised_at=now,
                )
            )
        else:
            # Conflicting values at the same timestamp: cannot silently pick one.
            flags.append(
                DataQualityFlag(
                    flag_type=QualityFlagType.DUPLICATE,
                    symbol=symbol,
                    event_time=event_time,
                    detail=(
                        f"{len(group)} conflicting duplicate records for "
                        f"{event_time.isoformat()}; quarantined, none retained as valid"
                    ),
                    raised_at=now,
                )
            )
    return valid, flags


def _check_gaps(
    symbol: str, sorted_bars: list[PriceBar], *, calendar: SimpleTradingCalendar, now: datetime
) -> list[DataQualityFlag]:
    if len(sorted_bars) < 2:
        return []
    present_dates = {b.event_time.date() for b in sorted_bars}
    expected = calendar.trading_days_between(
        sorted_bars[0].event_time.date(), sorted_bars[-1].event_time.date()
    )
    flags = []
    for expected_date in expected:
        if expected_date not in present_dates:
            flags.append(
                DataQualityFlag(
                    flag_type=QualityFlagType.GAP,
                    symbol=symbol,
                    event_time=None,
                    detail=f"missing expected trading-day bar for {expected_date.isoformat()}",
                    raised_at=now,
                )
            )
    return flags


def _check_volume(
    symbol: str, bars: list[PriceBar], *, now: datetime, z_threshold: float
) -> list[DataQualityFlag]:
    """Flag statistically implausible volume using a leave-one-out z-score.

    Leave-one-out (excluding the candidate bar from its own reference
    statistics) avoids the classic outlier-masking effect where a single huge
    spike inflates the series mean/stdev enough to hide itself.
    """
    if len(bars) < _MIN_BARS_FOR_VOLUME_CHECK:
        return []
    volumes = [b.volume for b in bars]
    flags = []
    for i, bar in enumerate(bars):
        others = volumes[:i] + volumes[i + 1 :]
        mean_others = statistics.fmean(others)
        stdev_others = statistics.pstdev(others)
        if stdev_others == 0:
            is_outlier = bar.volume != mean_others
            detail = (
                f"volume {bar.volume} differs from a constant reference series "
                f"(all other bars = {mean_others:.2f})"
            )
        else:
            z = (bar.volume - mean_others) / stdev_others
            is_outlier = abs(z) > z_threshold
            detail = (
                f"volume {bar.volume} has |leave-one-out z-score|={abs(z):.2f} "
                f"exceeding threshold {z_threshold} (reference mean={mean_others:.2f})"
            )
        if is_outlier:
            flags.append(
                DataQualityFlag(
                    flag_type=QualityFlagType.IMPLAUSIBLE_VOLUME,
                    symbol=symbol,
                    event_time=bar.event_time,
                    detail=detail,
                    raised_at=now,
                )
            )
    return flags
