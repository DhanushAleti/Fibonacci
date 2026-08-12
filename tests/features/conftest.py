"""Bar-construction helpers shared by the Phase 2 feature-contract tests.

Each helper builds fully schema-valid, deterministic ``PriceBar`` sequences
so tests can hand-verify expected values against
``docs/05-mathematics/phi-retracement-feature-contract.md`` rather than
relying on the synthetic random-walk provider (whose exact values are not
meant to be hand-derivable).
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from phi.data.providers.synthetic import SyntheticMarketDataProvider, SyntheticProviderConfig
from phi.data.schemas import DataProvenance, PriceBar

BASE_TIME = datetime(2026, 1, 1, 21, 0, tzinfo=UTC)


def make_bar(
    index: int,
    *,
    open_: float,
    high: float,
    low: float,
    close: float,
    volume: float = 1_000_000.0,
    availability_offset: timedelta = timedelta(0),
    symbol: str = "TEST",
) -> PriceBar:
    """Build one deterministic, schema-valid ``PriceBar`` at sequence position ``index``."""
    event_time = BASE_TIME + timedelta(days=index)
    availability_time = event_time + availability_offset
    return PriceBar(
        symbol=symbol,
        event_time=event_time,
        availability_time=availability_time,
        open=open_,
        high=high,
        low=low,
        close=close,
        volume=volume,
        adjusted=True,
        provenance=DataProvenance(
            source="synthetic:test",
            fetch_timestamp=availability_time,
            provider_batch_id=f"{symbol}:{index}",
            content_hash=f"hash-{symbol}-{index}",
        ),
    )


def make_flat_bars(n: int, *, price: float = 100.0, symbol: str = "TEST") -> list[PriceBar]:
    """``n`` bars with identical OHLC — a degenerate flat window (``R_t = 0``)."""
    return [
        make_bar(i, open_=price, high=price, low=price, close=price, symbol=symbol)
        for i in range(n)
    ]


def make_ramp_bars(
    n: int,
    *,
    start: float = 100.0,
    step: float = 1.0,
    half_width: float = 0.5,
    symbol: str = "TEST",
) -> list[PriceBar]:
    """``n`` bars with strictly increasing close prices, for hand-verifiable OLS/range tests.

    Bar ``i`` has ``close = open = start + i*step``, ``high = close +
    half_width``, ``low = close - half_width``.
    """
    return [
        make_bar(
            i,
            open_=start + i * step,
            high=start + i * step + half_width,
            low=start + i * step - half_width,
            close=start + i * step,
            symbol=symbol,
        )
        for i in range(n)
    ]


def scale_bars(bars: list[PriceBar], factor: float) -> list[PriceBar]:
    """Return a copy of ``bars`` with every price multiplied by ``factor`` (scale-invariance)."""
    return [
        make_bar(
            i,
            open_=b.open * factor,
            high=b.high * factor,
            low=b.low * factor,
            close=b.close * factor,
            volume=b.volume,
            availability_offset=b.availability_time - b.event_time,
            symbol=b.symbol,
        )
        for i, b in enumerate(bars)
    ]


def make_synthetic_bars(
    *,
    seed: int = 1618,
    symbol: str = "SYN",
    start: date = date(2020, 1, 1),
    end: date = date(2020, 8, 1),
) -> list[PriceBar]:
    """A realistic, deterministic bar series, via the project's own synthetic
    provider (NOT hand-crafted), long enough to exercise the default window
    (20) and Category B's rotation (needs >= 2*window realized values).
    """
    provider = SyntheticMarketDataProvider(SyntheticProviderConfig(seed=seed))
    return provider.fetch(symbol, start=start, end=end)


def translate_bars(bars: list[PriceBar], shift: float) -> list[PriceBar]:
    """Return a copy of ``bars`` with every price shifted by an additive constant."""
    return [
        make_bar(
            i,
            open_=b.open + shift,
            high=b.high + shift,
            low=b.low + shift,
            close=b.close + shift,
            volume=b.volume,
            availability_offset=b.availability_time - b.event_time,
            symbol=b.symbol,
        )
        for i, b in enumerate(bars)
    ]
