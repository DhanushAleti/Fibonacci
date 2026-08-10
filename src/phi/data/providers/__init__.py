"""Data Ingestion providers (SYSTEM_ARCHITECTURE §9.1, module 1).

A provider acquires raw OHLCV data and tags it with provenance; it does not
validate, clean, or interpret data (that is Data Validation's job, module 2).
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Protocol

from phi.data.schemas import PriceBar


class MarketDataProvider(Protocol):
    """Acquires raw OHLCV bars for a symbol over an inclusive date range."""

    def fetch(
        self, symbol: str, *, start: date, end: date, now: datetime | None = None
    ) -> list[PriceBar]: ...
