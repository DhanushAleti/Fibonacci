"""Tests for the synthetic (TEST-ONLY) market data provider.

Per the mission's DATA POLICY, synthetic data exists solely to validate the
engineering pipeline. These tests check determinism, calendar-awareness, and
that the data is unambiguously labeled synthetic — never that it resembles any
real market behavior, which would be a meaningless claim for fabricated data.
"""

from __future__ import annotations

from datetime import UTC, date, datetime

from hypothesis import given
from hypothesis import strategies as st

from phi.data.providers.synthetic import SyntheticMarketDataProvider, SyntheticProviderConfig

FIXED_NOW = datetime(2026, 2, 1, tzinfo=UTC)


def test_source_is_clearly_labeled_synthetic() -> None:
    provider = SyntheticMarketDataProvider()
    bars = provider.fetch("TEST", start=date(2026, 1, 5), end=date(2026, 1, 9), now=FIXED_NOW)
    assert bars
    for bar in bars:
        assert "synthetic" in bar.provenance.source.lower()


def test_same_seed_and_symbol_are_deterministic() -> None:
    cfg = SyntheticProviderConfig(seed=42)
    p1 = SyntheticMarketDataProvider(cfg)
    p2 = SyntheticMarketDataProvider(cfg)
    bars1 = p1.fetch("TEST", start=date(2026, 1, 5), end=date(2026, 1, 16), now=FIXED_NOW)
    bars2 = p2.fetch("TEST", start=date(2026, 1, 5), end=date(2026, 1, 16), now=FIXED_NOW)
    assert [b.close for b in bars1] == [b.close for b in bars2]
    assert bars1[0].provenance.content_hash == bars2[0].provenance.content_hash


def test_different_seed_gives_different_series() -> None:
    p1 = SyntheticMarketDataProvider(SyntheticProviderConfig(seed=1))
    p2 = SyntheticMarketDataProvider(SyntheticProviderConfig(seed=2))
    bars1 = p1.fetch("TEST", start=date(2026, 1, 5), end=date(2026, 1, 16), now=FIXED_NOW)
    bars2 = p2.fetch("TEST", start=date(2026, 1, 5), end=date(2026, 1, 16), now=FIXED_NOW)
    assert [b.close for b in bars1] != [b.close for b in bars2]


def test_only_produces_bars_on_trading_days() -> None:
    provider = SyntheticMarketDataProvider()
    # 2026-01-05 (Mon) .. 2026-01-11 (Sun): expect exactly the 5 weekdays.
    bars = provider.fetch("TEST", start=date(2026, 1, 5), end=date(2026, 1, 11), now=FIXED_NOW)
    assert [b.event_time.date() for b in bars] == [
        date(2026, 1, 5),
        date(2026, 1, 6),
        date(2026, 1, 7),
        date(2026, 1, 8),
        date(2026, 1, 9),
    ]


def test_all_bars_in_a_fetch_share_one_batch_provenance() -> None:
    provider = SyntheticMarketDataProvider()
    bars = provider.fetch("TEST", start=date(2026, 1, 5), end=date(2026, 1, 9), now=FIXED_NOW)
    hashes = {b.provenance.content_hash for b in bars}
    batch_ids = {b.provenance.provider_batch_id for b in bars}
    assert len(hashes) == 1
    assert len(batch_ids) == 1


def test_availability_time_never_precedes_event_time() -> None:
    provider = SyntheticMarketDataProvider()
    bars = provider.fetch("TEST", start=date(2026, 1, 5), end=date(2026, 1, 9), now=FIXED_NOW)
    for bar in bars:
        assert bar.availability_time >= bar.event_time


@given(seed=st.integers(min_value=0, max_value=10_000))
def test_generated_series_always_satisfies_ohlc_invariants_across_seeds(seed: int) -> None:
    # PriceBar's own constructor raises on an OHLC violation, so "does not raise"
    # across a wide range of seeds is itself the invariant under test.
    provider = SyntheticMarketDataProvider(SyntheticProviderConfig(seed=seed))
    bars = provider.fetch("TEST", start=date(2026, 1, 5), end=date(2026, 1, 30), now=FIXED_NOW)
    assert len(bars) > 0
