"""Minimal Phase 1 trading calendar (PRD-DATA-007).

This is a deliberately minimal stand-in for the full exchange-specific
``TradingCalendar`` entity described in DATABASE_ARCHITECTURE.md §7.1 — weekdays
plus an explicit holiday set, so gap detection (``phi.data.validation``) can tell
"expected non-trading day" apart from "missing data" without inventing a real
exchange calendar this project has not sourced yet. Tracked as a known
limitation, not a silent substitute for the real entity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

_SATURDAY = 5


@dataclass(frozen=True)
class SimpleTradingCalendar:
    """Weekday-based trading calendar with explicit holiday exceptions."""

    holidays: frozenset[date] = field(default_factory=frozenset)

    def is_trading_day(self, d: date) -> bool:
        return d.weekday() < _SATURDAY and d not in self.holidays

    def trading_days_between(self, start: date, end: date) -> list[date]:
        """Return trading days in ``[start, end]`` inclusive, in order."""
        if start > end:
            raise ValueError(f"start ({start}) must not be after end ({end})")
        days = []
        current = start
        while current <= end:
            if self.is_trading_day(current):
                days.append(current)
            current += timedelta(days=1)
        return days
