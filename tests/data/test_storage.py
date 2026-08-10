"""Tests for the Phase 1 Parquet-backed PriceBarRepository (module 3).

See docs/18-decisions/0001-phase1-local-storage-implementation.md for why this
is Parquet rather than PostgreSQL/TimescaleDB in this environment.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

from phi.data.providers.synthetic import SyntheticMarketDataProvider, SyntheticProviderConfig
from phi.data.schemas import DataProvenance, PriceBar
from phi.data.storage import ParquetPriceBarRepository

FIXED_NOW = datetime(2026, 2, 1, tzinfo=UTC)
FAR_PAST = datetime(2020, 1, 1, tzinfo=UTC)
FAR_FUTURE = datetime(2030, 1, 1, tzinfo=UTC)


def _provider(seed: int = 1) -> SyntheticMarketDataProvider:
    return SyntheticMarketDataProvider(SyntheticProviderConfig(seed=seed))


def test_append_empty_list_is_a_no_op(tmp_path: Path) -> None:
    repo = ParquetPriceBarRepository(tmp_path)
    repo.append([])  # must not raise or create anything
    assert repo.query("TEST", start=FAR_PAST, end=FAR_FUTURE) == []


def test_query_symbol_directory_with_no_files_returns_empty(tmp_path: Path) -> None:
    repo = ParquetPriceBarRepository(tmp_path)
    (tmp_path / "EMPTY").mkdir()  # directory exists, but no batches ingested
    assert repo.query("EMPTY", start=FAR_PAST, end=FAR_FUTURE) == []


def test_query_unknown_symbol_returns_empty(tmp_path: Path) -> None:
    repo = ParquetPriceBarRepository(tmp_path)
    result = repo.query("NOPE", start=FAR_PAST, end=FAR_FUTURE)
    assert result == []


def test_append_and_query_roundtrip(tmp_path: Path) -> None:
    repo = ParquetPriceBarRepository(tmp_path)
    bars = _provider().fetch("TEST", start=date(2026, 1, 5), end=date(2026, 1, 9), now=FIXED_NOW)
    repo.append(bars)

    result = repo.query("TEST", start=FAR_PAST, end=FAR_FUTURE)

    assert len(result) == len(bars)
    by_time = {b.event_time: b for b in result}
    for original in bars:
        stored = by_time[original.event_time]
        assert stored.close == original.close
        assert stored.provenance.content_hash == original.provenance.content_hash
        assert stored.availability_time == original.availability_time


def test_query_filters_by_time_range(tmp_path: Path) -> None:
    repo = ParquetPriceBarRepository(tmp_path)
    bars = _provider().fetch("TEST", start=date(2026, 1, 5), end=date(2026, 1, 16), now=FIXED_NOW)
    repo.append(bars)

    result = repo.query(
        "TEST",
        start=datetime(2026, 1, 5, tzinfo=UTC),
        end=datetime(2026, 1, 7, 23, 59, tzinfo=UTC),
    )
    expected_dates = {date(2026, 1, 5), date(2026, 1, 6), date(2026, 1, 7)}
    assert {b.event_time.date() for b in result} == expected_dates


def test_append_of_identical_batch_is_idempotent(tmp_path: Path) -> None:
    repo = ParquetPriceBarRepository(tmp_path)
    bars = _provider().fetch("TEST", start=date(2026, 1, 5), end=date(2026, 1, 9), now=FIXED_NOW)
    repo.append(bars)
    repo.append(bars)  # same content_hash — must not duplicate

    result = repo.query("TEST", start=FAR_PAST, end=FAR_FUTURE)
    assert len(result) == len(bars)


def test_append_never_destructively_overwrites_prior_batch(tmp_path: Path) -> None:
    # PRD-DATA-002: corrected/restated data is tracked *alongside* the original.
    repo = ParquetPriceBarRepository(tmp_path)
    single_day = date(2026, 1, 5)
    original = _provider(seed=1).fetch("TEST", start=single_day, end=single_day, now=FIXED_NOW)
    restated = _provider(seed=2).fetch("TEST", start=single_day, end=single_day, now=FIXED_NOW)
    assert original[0].provenance.content_hash != restated[0].provenance.content_hash

    repo.append(original)
    repo.append(restated)

    result = repo.query("TEST", start=FAR_PAST, end=FAR_FUTURE)
    assert len(result) == 2  # both versions retained, neither silently dropped
    hashes = {b.provenance.content_hash for b in result}
    assert hashes == {original[0].provenance.content_hash, restated[0].provenance.content_hash}


def test_repository_persists_across_instances(tmp_path: Path) -> None:
    bars = _provider().fetch("TEST", start=date(2026, 1, 5), end=date(2026, 1, 9), now=FIXED_NOW)
    ParquetPriceBarRepository(tmp_path).append(bars)

    # A fresh repository instance pointed at the same root must see prior data.
    reopened = ParquetPriceBarRepository(tmp_path)
    result = reopened.query("TEST", start=FAR_PAST, end=FAR_FUTURE)
    assert len(result) == len(bars)


def test_query_results_are_sorted_by_event_time(tmp_path: Path) -> None:
    repo = ParquetPriceBarRepository(tmp_path)
    bars = _provider().fetch("TEST", start=date(2026, 1, 5), end=date(2026, 1, 16), now=FIXED_NOW)
    repo.append(bars)

    result = repo.query("TEST", start=FAR_PAST, end=FAR_FUTURE)
    assert [b.event_time for b in result] == sorted(b.event_time for b in result)


def test_symbols_are_stored_independently(tmp_path: Path) -> None:
    repo = ParquetPriceBarRepository(tmp_path)
    aaa = PriceBar(
        symbol="AAA",
        event_time=datetime(2026, 1, 5, 21, 0, tzinfo=UTC),
        availability_time=datetime(2026, 1, 5, 21, 0, tzinfo=UTC),
        open=10.0, high=11.0, low=9.0, close=10.5, volume=100.0, adjusted=False,
        provenance=DataProvenance(
            source="synthetic:test", fetch_timestamp=FIXED_NOW,
            provider_batch_id="b1", content_hash="hash-aaa",
        ),
    )
    bbb = PriceBar(
        symbol="BBB",
        event_time=datetime(2026, 1, 5, 21, 0, tzinfo=UTC),
        availability_time=datetime(2026, 1, 5, 21, 0, tzinfo=UTC),
        open=20.0, high=21.0, low=19.0, close=20.5, volume=200.0, adjusted=False,
        provenance=DataProvenance(
            source="synthetic:test", fetch_timestamp=FIXED_NOW,
            provider_batch_id="b2", content_hash="hash-bbb",
        ),
    )
    repo.append([aaa, bbb])

    result_a = repo.query("AAA", start=FAR_PAST, end=FAR_FUTURE)
    result_b = repo.query("BBB", start=FAR_PAST, end=FAR_FUTURE)
    assert len(result_a) == 1 and result_a[0].symbol == "AAA"
    assert len(result_b) == 1 and result_b[0].symbol == "BBB"
