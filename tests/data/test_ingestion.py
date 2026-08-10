"""Tests for ingestion orchestration (provider -> validation -> storage)."""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

from phi.data.ingestion import ingest
from phi.data.providers.synthetic import SyntheticMarketDataProvider, SyntheticProviderConfig
from phi.data.schemas import DataProvenance, PriceBar, QualityFlagType
from phi.data.storage import ParquetPriceBarRepository

FIXED_NOW = datetime(2026, 2, 1, tzinfo=UTC)
FAR_PAST = datetime(2020, 1, 1, tzinfo=UTC)
FAR_FUTURE = datetime(2030, 1, 1, tzinfo=UTC)


def test_ingest_happy_path_stores_all_clean_bars(tmp_path: Path) -> None:
    provider = SyntheticMarketDataProvider(SyntheticProviderConfig(seed=7))
    repo = ParquetPriceBarRepository(tmp_path)

    result = ingest(
        provider, repo, symbol="TEST", start=date(2026, 1, 5), end=date(2026, 1, 9), now=FIXED_NOW
    )

    assert result.fetched == 5
    assert result.valid == 5
    assert result.flags == ()
    stored = repo.query("TEST", start=FAR_PAST, end=FAR_FUTURE)
    assert len(stored) == 5


class _FakeProvider:
    """A minimal provider stand-in for exercising orchestration without RNG."""

    def __init__(self, bars: list[PriceBar]) -> None:
        self._bars = bars

    def fetch(
        self, symbol: str, *, start: date, end: date, now: datetime | None = None
    ) -> list[PriceBar]:
        return self._bars


def test_ingest_flags_duplicates_and_does_not_store_redundant_copies(tmp_path: Path) -> None:
    bar = PriceBar(
        symbol="TEST",
        event_time=datetime(2026, 1, 5, 21, 0, tzinfo=UTC),
        availability_time=datetime(2026, 1, 5, 21, 0, tzinfo=UTC),
        open=100.0,
        high=101.0,
        low=99.0,
        close=100.0,
        volume=1000.0,
        adjusted=False,
        provenance=DataProvenance(
            source="synthetic:test",
            fetch_timestamp=FIXED_NOW,
            provider_batch_id="batch",
            content_hash="dup-hash",
        ),
    )
    provider = _FakeProvider([bar, bar])
    repo = ParquetPriceBarRepository(tmp_path)

    result = ingest(
        provider, repo, symbol="TEST", start=date(2026, 1, 5), end=date(2026, 1, 5), now=FIXED_NOW
    )

    assert result.fetched == 2
    assert result.valid == 1
    assert any(f.flag_type is QualityFlagType.DUPLICATE for f in result.flags)
    stored = repo.query("TEST", start=FAR_PAST, end=FAR_FUTURE)
    assert len(stored) == 1
