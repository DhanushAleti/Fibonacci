"""Deterministic synthetic OHLCV provider — TEST/SYNTHETIC ONLY.

Per the mission's DATA POLICY: this generator exists exclusively to validate
the ingestion → validation → storage pipeline end-to-end without a real data
provider (none is selected yet — PRD-OPEN-001). Its output must never be
presented as market evidence; every record it produces is labeled with a
``synthetic:`` source so this cannot happen silently downstream.

Determinism (PRD-FEATENG-003 applies equally to test fixtures): the same
``(seed, symbol, date range)`` always produces the same series, using a
symbol-namespaced ``random.Random`` instance rather than the shared global RNG.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from datetime import UTC, date, datetime

from phi.data.calendar import SimpleTradingCalendar
from phi.data.schemas import DataProvenance, PriceBar

_EOD_HOUR = 21  # UTC proxy for "end of trading session" on a daily bar
_MIN_PRICE = 0.01


@dataclass(frozen=True)
class SyntheticProviderConfig:
    """Parameters of the synthetic random walk. Not a market model — a fixture."""

    seed: int = 1618
    start_price: float = 100.0
    daily_return_stdev: float = 0.01
    drift: float = 0.0
    base_volume: float = 1_000_000.0
    volume_stdev_fraction: float = 0.2


class SyntheticMarketDataProvider:
    """Generates a deterministic synthetic daily OHLCV series. NOT REAL DATA."""

    SOURCE_NAME = "synthetic:phi-engineering-fixture"

    def __init__(
        self,
        config: SyntheticProviderConfig | None = None,
        *,
        calendar: SimpleTradingCalendar | None = None,
    ) -> None:
        self._config = config or SyntheticProviderConfig()
        self._calendar = calendar or SimpleTradingCalendar()

    def fetch(
        self, symbol: str, *, start: date, end: date, now: datetime | None = None
    ) -> list[PriceBar]:
        fetch_time = now or datetime.now(UTC)
        cfg = self._config
        rng = random.Random(f"{cfg.seed}:{symbol}")

        trading_days = self._calendar.trading_days_between(start, end)
        raw_rows: list[tuple[date, float, float, float, float, float]] = []
        price = cfg.start_price
        for d in trading_days:
            daily_return = rng.gauss(cfg.drift, cfg.daily_return_stdev)
            new_close = max(price * (1 + daily_return), _MIN_PRICE)
            open_ = price
            wick = abs(rng.gauss(0, cfg.daily_return_stdev / 2))
            high = max(open_, new_close) * (1 + wick)
            low = max(min(open_, new_close) * (1 - wick), _MIN_PRICE)
            volume = max(cfg.base_volume * (1 + rng.gauss(0, cfg.volume_stdev_fraction)), 1.0)
            raw_rows.append((d, open_, high, low, new_close, volume))
            price = new_close

        batch_id = f"{symbol}:{start.isoformat()}:{end.isoformat()}:seed{cfg.seed}"
        content = "|".join(
            f"{symbol},{d.isoformat()},{o:.6f},{h:.6f},{lo:.6f},{c:.6f},{v:.6f}"
            for d, o, h, lo, c, v in raw_rows
        )
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        provenance = DataProvenance(
            source=self.SOURCE_NAME,
            fetch_timestamp=fetch_time,
            provider_batch_id=batch_id,
            content_hash=content_hash,
        )

        bars = []
        for d, o, h, lo, c, v in raw_rows:
            event_time = datetime(d.year, d.month, d.day, _EOD_HOUR, tzinfo=UTC)
            bars.append(
                PriceBar(
                    symbol=symbol,
                    event_time=event_time,
                    # A daily bar's EOD data is treated as available at its own
                    # close for this synthetic fixture (no restatement modeled).
                    availability_time=event_time,
                    open=o,
                    high=h,
                    low=lo,
                    close=c,
                    volume=v,
                    adjusted=True,
                    provenance=provenance,
                )
            )
        return bars
