"""Tests for the minimal Phase 1 trading calendar (PRD-DATA-007)."""

from __future__ import annotations

from datetime import date

import pytest

from phi.data.calendar import SimpleTradingCalendar


@pytest.mark.unit
def test_weekday_is_trading_day() -> None:
    cal = SimpleTradingCalendar()
    assert cal.is_trading_day(date(2026, 1, 5)) is True  # Monday


@pytest.mark.unit
def test_weekend_is_not_trading_day() -> None:
    cal = SimpleTradingCalendar()
    assert cal.is_trading_day(date(2026, 1, 3)) is False  # Saturday
    assert cal.is_trading_day(date(2026, 1, 4)) is False  # Sunday


@pytest.mark.unit
def test_explicit_holiday_is_not_trading_day() -> None:
    cal = SimpleTradingCalendar(holidays=frozenset({date(2026, 1, 5)}))
    assert cal.is_trading_day(date(2026, 1, 5)) is False


@pytest.mark.unit
def test_trading_days_between_excludes_weekends_and_holidays() -> None:
    # 2026-01-05 (Mon) .. 2026-01-09 (Fri), with Wednesday as a holiday.
    cal = SimpleTradingCalendar(holidays=frozenset({date(2026, 1, 7)}))
    days = cal.trading_days_between(date(2026, 1, 5), date(2026, 1, 11))
    assert days == [
        date(2026, 1, 5),
        date(2026, 1, 6),
        date(2026, 1, 8),
        date(2026, 1, 9),
    ]


@pytest.mark.unit
def test_trading_days_between_rejects_start_after_end() -> None:
    cal = SimpleTradingCalendar()
    with pytest.raises(ValueError, match="start"):
        cal.trading_days_between(date(2026, 1, 10), date(2026, 1, 1))
