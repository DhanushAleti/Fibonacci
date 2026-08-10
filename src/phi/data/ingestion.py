"""Ingestion orchestration: provider -> validation -> storage.

Wires together Data Ingestion (module 1, a ``MarketDataProvider``), Data
Validation (module 2, ``validate_price_bars``), and Market Data Storage
(module 3, a ``PriceBarRepository``) into the single entry point Phase 1
exposes. Only validated bars are persisted; every flag raised during
validation is returned to the caller rather than logged-and-discarded, so a
research run always has visibility into what was quarantined and why
(PRD-BIAS-001).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime

from phi.data.calendar import SimpleTradingCalendar
from phi.data.providers import MarketDataProvider
from phi.data.schemas import DataQualityFlag
from phi.data.storage import PriceBarRepository
from phi.data.validation import validate_price_bars


@dataclass(frozen=True)
class IngestionResult:
    """Summary of a single ingestion run, sufficient for a research log entry."""

    symbol: str
    fetched: int
    valid: int
    flags: tuple[DataQualityFlag, ...]


def ingest(
    provider: MarketDataProvider,
    repository: PriceBarRepository,
    *,
    symbol: str,
    start: date,
    end: date,
    calendar: SimpleTradingCalendar | None = None,
    now: datetime | None = None,
) -> IngestionResult:
    """Fetch, validate, and persist bars for ``symbol`` over ``[start, end]``."""
    cal = calendar or SimpleTradingCalendar()
    fetch_time = now or datetime.now(UTC)

    raw_bars = provider.fetch(symbol, start=start, end=end, now=fetch_time)
    result = validate_price_bars(raw_bars, calendar=cal, now=fetch_time)
    repository.append(result.valid_bars)

    return IngestionResult(
        symbol=symbol,
        fetched=len(raw_bars),
        valid=len(result.valid_bars),
        flags=result.flags,
    )
