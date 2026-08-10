"""Tests for Data Validation (module 2): gaps, duplicates, monotonicity, volume.

Per SYSTEM_ARCHITECTURE §9.2, validation must never silently "fix" data — every
test here checks both that a problem is *flagged* and that the flagging does not
quietly mutate values it hasn't earned the right to change.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pytest

from phi.data.calendar import SimpleTradingCalendar
from phi.data.schemas import DataProvenance, PriceBar, QualityFlagType
from phi.data.validation import validate_price_bars

CAL = SimpleTradingCalendar()


def _provenance() -> DataProvenance:
    return DataProvenance(
        source="synthetic-test-fixture",
        fetch_timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        provider_batch_id="batch-1",
        content_hash="deadbeef",
    )


def _bar(symbol: str, d: date, *, close: float = 100.0, volume: float = 1000.0) -> PriceBar:
    et = datetime(d.year, d.month, d.day, 21, 0, tzinfo=UTC)
    return PriceBar(
        symbol=symbol,
        event_time=et,
        availability_time=et,
        open=close,
        high=close + 1,
        low=close - 1,
        close=close,
        volume=volume,
        adjusted=False,
        provenance=_provenance(),
    )


NOW = datetime(2026, 2, 1, tzinfo=UTC)


@pytest.mark.unit
def test_empty_input_returns_empty_result() -> None:
    result = validate_price_bars([], calendar=CAL, now=NOW)
    assert result.valid_bars == ()
    assert result.flags == ()


@pytest.mark.unit
def test_clean_consecutive_weekday_series_has_no_flags() -> None:
    bars = [_bar("TEST", date(2026, 1, 5) + timedelta(days=i)) for i in range(5)]  # Mon-Fri
    result = validate_price_bars(bars, calendar=CAL, now=NOW)
    assert len(result.valid_bars) == 5
    assert result.flags == ()


@pytest.mark.unit
def test_weekend_gap_is_not_flagged() -> None:
    # Friday then the following Monday — no weekday missing in between.
    bars = [_bar("TEST", date(2026, 1, 9)), _bar("TEST", date(2026, 1, 12))]
    result = validate_price_bars(bars, calendar=CAL, now=NOW)
    assert result.flags == ()


@pytest.mark.unit
def test_missing_weekday_is_flagged_as_gap() -> None:
    # Monday, then Wednesday — Tuesday 2026-01-06 is missing.
    bars = [_bar("TEST", date(2026, 1, 5)), _bar("TEST", date(2026, 1, 7))]
    result = validate_price_bars(bars, calendar=CAL, now=NOW)
    gap_flags = [f for f in result.flags if f.flag_type is QualityFlagType.GAP]
    assert len(gap_flags) == 1
    assert "2026-01-06" in gap_flags[0].detail
    # A gap doesn't invalidate the bars that *do* exist.
    assert len(result.valid_bars) == 2


@pytest.mark.unit
def test_exact_duplicate_is_deduped_and_flagged() -> None:
    d = date(2026, 1, 5)
    bars = [_bar("TEST", d), _bar("TEST", d)]  # bit-identical
    result = validate_price_bars(bars, calendar=CAL, now=NOW)
    assert len(result.valid_bars) == 1
    dup_flags = [f for f in result.flags if f.flag_type is QualityFlagType.DUPLICATE]
    assert len(dup_flags) == 1


@pytest.mark.unit
def test_conflicting_duplicate_is_quarantined_not_silently_resolved() -> None:
    d = date(2026, 1, 5)
    bars = [_bar("TEST", d, close=100.0), _bar("TEST", d, close=105.0)]
    result = validate_price_bars(bars, calendar=CAL, now=NOW)
    # Neither conflicting record is silently picked as "the" valid one.
    assert len(result.valid_bars) == 0
    dup_flags = [f for f in result.flags if f.flag_type is QualityFlagType.DUPLICATE]
    assert len(dup_flags) == 1
    assert "conflict" in dup_flags[0].detail.lower()


@pytest.mark.unit
def test_out_of_order_arrival_flagged_as_non_monotonic() -> None:
    bars = [_bar("TEST", date(2026, 1, 6)), _bar("TEST", date(2026, 1, 5))]  # reversed
    result = validate_price_bars(bars, calendar=CAL, now=NOW)
    mono_flags = [f for f in result.flags if f.flag_type is QualityFlagType.NON_MONOTONIC_TIMESTAMP]
    assert len(mono_flags) == 1
    # Both underlying bars are still structurally valid and retained.
    assert len(result.valid_bars) == 2


@pytest.mark.unit
def test_implausible_volume_is_flagged_but_bar_is_retained() -> None:
    normal = [_bar("TEST", date(2026, 1, 5) + timedelta(days=i), volume=1000.0) for i in range(4)]
    spike = _bar("TEST", date(2026, 1, 9), volume=1_000_000.0)
    result = validate_price_bars([*normal, spike], calendar=CAL, now=NOW)
    vol_flags = [f for f in result.flags if f.flag_type is QualityFlagType.IMPLAUSIBLE_VOLUME]
    assert len(vol_flags) == 1
    # Flagged, not silently dropped (PRD-DATA-011: flag, don't discard).
    assert len(result.valid_bars) == 5


@pytest.mark.unit
def test_multiple_symbols_validated_independently() -> None:
    a = [_bar("AAA", date(2026, 1, 5)), _bar("AAA", date(2026, 1, 7))]  # gap
    b = [_bar("BBB", date(2026, 1, 5)), _bar("BBB", date(2026, 1, 6))]  # clean
    result = validate_price_bars([*a, *b], calendar=CAL, now=NOW)
    gap_flags = [f for f in result.flags if f.flag_type is QualityFlagType.GAP]
    assert len(gap_flags) == 1
    assert gap_flags[0].symbol == "AAA"
    assert len(result.valid_bars) == 4
