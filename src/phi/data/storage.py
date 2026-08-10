"""Market Data Storage (SYSTEM_ARCHITECTURE §9.3, module 3).

See docs/18-decisions/0001-phase1-local-storage-implementation.md for why this
Phase 1 implementation is a local, content-hashed Parquet store behind a
repository interface rather than PostgreSQL/TimescaleDB (the architecture's
committed long-term storage engine): no database server is available in this
environment, and standing one up is its own deliberate infrastructure decision,
not a side effect of writing Phase 1 code. A future TimescaleDB-backed
implementation of ``PriceBarRepository`` is a boundary swap, not a rewrite.

Storage never destructively overwrites (PRD-DATA-002): every ingested batch is
persisted as its own content-addressed file, so restated/corrected data sits
alongside the original rather than replacing it. Reconciling multiple versions
of the same event is left to the caller — Market Data Storage's job is to
retain, not to decide which version is "correct".
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol

import polars as pl

from phi.data.schemas import DataProvenance, PriceBar

_COLUMNS = [
    "symbol",
    "event_time",
    "availability_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "adjusted",
    "provenance_source",
    "provenance_fetch_timestamp",
    "provenance_provider_batch_id",
    "provenance_content_hash",
]


class PriceBarRepository(Protocol):
    """The storage contract module 3 must satisfy, regardless of backend."""

    def append(self, bars: Sequence[PriceBar]) -> None: ...

    def query(self, symbol: str, *, start: datetime, end: datetime) -> list[PriceBar]: ...


class ParquetPriceBarRepository:
    """Local-first, content-hashed, append-only ``PriceBar`` store."""

    def __init__(self, root: Path) -> None:
        self._root = root
        self._root.mkdir(parents=True, exist_ok=True)

    def append(self, bars: Sequence[PriceBar]) -> None:
        if not bars:
            return
        groups: dict[tuple[str, str], list[PriceBar]] = defaultdict(list)
        for bar in bars:
            groups[(bar.symbol, bar.provenance.content_hash)].append(bar)

        for (symbol, content_hash), group in groups.items():
            symbol_dir = self._root / symbol
            symbol_dir.mkdir(parents=True, exist_ok=True)
            path = symbol_dir / f"{content_hash}.parquet"
            if path.exists():
                # Content-addressed: an identical hash means identical content is
                # already persisted — re-appending is a safe no-op, never a
                # destructive overwrite (PRD-DATA-002).
                continue
            rows = [_bar_to_row(b) for b in group]
            df = pl.DataFrame(rows, schema=_COLUMNS, orient="row")
            df.write_parquet(path)

    def query(self, symbol: str, *, start: datetime, end: datetime) -> list[PriceBar]:
        symbol_dir = self._root / symbol
        if not symbol_dir.exists():
            return []
        paths = sorted(symbol_dir.glob("*.parquet"))
        if not paths:
            return []
        combined = pl.concat([pl.read_parquet(p) for p in paths])
        bars = [_row_to_bar(row) for row in combined.iter_rows(named=True)]
        in_range = [b for b in bars if start <= b.event_time <= end]
        return sorted(in_range, key=lambda b: (b.event_time, b.availability_time))


def _bar_to_row(bar: PriceBar) -> tuple[object, ...]:
    return (
        bar.symbol,
        bar.event_time.isoformat(),
        bar.availability_time.isoformat(),
        bar.open,
        bar.high,
        bar.low,
        bar.close,
        bar.volume,
        bar.adjusted,
        bar.provenance.source,
        bar.provenance.fetch_timestamp.isoformat(),
        bar.provenance.provider_batch_id,
        bar.provenance.content_hash,
    )


def _row_to_bar(row: dict[str, Any]) -> PriceBar:
    return PriceBar(
        symbol=row["symbol"],
        event_time=datetime.fromisoformat(row["event_time"]),
        availability_time=datetime.fromisoformat(row["availability_time"]),
        open=row["open"],
        high=row["high"],
        low=row["low"],
        close=row["close"],
        volume=row["volume"],
        adjusted=row["adjusted"],
        provenance=DataProvenance(
            source=row["provenance_source"],
            fetch_timestamp=datetime.fromisoformat(row["provenance_fetch_timestamp"]),
            provider_batch_id=row["provenance_provider_batch_id"],
            content_hash=row["provenance_content_hash"],
        ),
    )
