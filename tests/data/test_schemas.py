"""Tests for Phase 1 domain schemas (DATABASE_ARCHITECTURE.md §7)."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pytest
from pydantic import ValidationError

from phi.data.schemas import (
    AssetClass,
    DataProvenance,
    DataQualityFlag,
    Instrument,
    InstrumentStatus,
    PriceBar,
    QualityFlagType,
)

EVENT_TIME = datetime(2026, 1, 5, 21, 0, tzinfo=UTC)


def _provenance(**overrides: object) -> DataProvenance:
    defaults: dict[str, object] = {
        "source": "synthetic-test-fixture",
        "fetch_timestamp": EVENT_TIME + timedelta(minutes=1),
        "provider_batch_id": "batch-1",
        "content_hash": "deadbeef",
    }
    defaults.update(overrides)
    return DataProvenance(**defaults)  # type: ignore[arg-type]


def _bar(**overrides: object) -> PriceBar:
    defaults: dict[str, object] = {
        "symbol": "TEST",
        "event_time": EVENT_TIME,
        "availability_time": EVENT_TIME,
        "open": 100.0,
        "high": 101.0,
        "low": 99.0,
        "close": 100.5,
        "volume": 1000.0,
        "adjusted": False,
        "provenance": _provenance(),
    }
    defaults.update(overrides)
    return PriceBar(**defaults)  # type: ignore[arg-type]


class TestInstrument:
    def test_valid_active_instrument(self) -> None:
        inst = Instrument(
            symbol="TEST",
            exchange="XTST",
            asset_class=AssetClass.EQUITY,
            currency="USD",
            listing_date=date(2000, 1, 1),
        )
        assert inst.status is InstrumentStatus.ACTIVE
        assert inst.delisting_date is None

    def test_inactive_instrument_requires_delisting_date(self) -> None:
        with pytest.raises(ValidationError, match="delisting_date"):
            Instrument(
                symbol="TEST",
                exchange="XTST",
                asset_class=AssetClass.EQUITY,
                currency="USD",
                listing_date=date(2000, 1, 1),
                status=InstrumentStatus.INACTIVE,
            )

    def test_delisting_before_listing_rejected(self) -> None:
        with pytest.raises(ValidationError, match="delisting_date"):
            Instrument(
                symbol="TEST",
                exchange="XTST",
                asset_class=AssetClass.EQUITY,
                currency="USD",
                listing_date=date(2010, 1, 1),
                delisting_date=date(2000, 1, 1),
                status=InstrumentStatus.INACTIVE,
            )

    def test_instrument_is_frozen(self) -> None:
        inst = Instrument(
            symbol="TEST",
            exchange="XTST",
            asset_class=AssetClass.EQUITY,
            currency="USD",
            listing_date=date(2000, 1, 1),
        )
        with pytest.raises(ValidationError):
            inst.symbol = "OTHER"  # type: ignore[misc]


class TestDataProvenance:
    @pytest.mark.leakage
    def test_naive_fetch_timestamp_rejected(self) -> None:
        with pytest.raises(ValidationError, match="timezone"):
            _provenance(fetch_timestamp=datetime(2026, 1, 5))  # no tzinfo


class TestPriceBar:
    def test_valid_bar(self) -> None:
        bar = _bar()
        assert bar.symbol == "TEST"

    @pytest.mark.leakage
    def test_naive_timestamp_rejected(self) -> None:
        with pytest.raises(ValidationError, match="timezone"):
            _bar(event_time=datetime(2026, 1, 5, 21, 0))  # no tzinfo

    @pytest.mark.leakage
    def test_availability_before_event_time_rejected(self) -> None:
        with pytest.raises(ValidationError, match="availability_time"):
            _bar(availability_time=EVENT_TIME - timedelta(minutes=1))

    def test_availability_after_event_time_is_valid(self) -> None:
        # Restated data: availability may genuinely be later than event time.
        bar = _bar(availability_time=EVENT_TIME + timedelta(days=2))
        assert bar.availability_time > bar.event_time

    def test_ohlc_high_below_low_rejected(self) -> None:
        with pytest.raises(ValidationError, match="low"):
            _bar(low=105.0, high=95.0)

    def test_open_outside_high_low_range_rejected(self) -> None:
        with pytest.raises(ValidationError):
            _bar(open=200.0)

    def test_close_outside_high_low_range_rejected(self) -> None:
        with pytest.raises(ValidationError, match="close"):
            _bar(close=200.0)

    def test_negative_volume_rejected(self) -> None:
        with pytest.raises(ValidationError):
            _bar(volume=-1.0)

    def test_bar_is_frozen(self) -> None:
        bar = _bar()
        with pytest.raises(ValidationError):
            bar.close = 999.0  # type: ignore[misc]


class TestDataQualityFlag:
    def test_construct_gap_flag(self) -> None:
        flag = DataQualityFlag(
            flag_type=QualityFlagType.GAP,
            symbol="TEST",
            event_time=EVENT_TIME,
            detail="missing bar for 2026-01-06",
            raised_at=EVENT_TIME + timedelta(days=1),
        )
        assert flag.flag_type is QualityFlagType.GAP

    def test_construct_flag_with_no_event_time(self) -> None:
        # GAP flags may not have a single associated event_time (see validation.py).
        flag = DataQualityFlag(
            flag_type=QualityFlagType.GAP,
            symbol="TEST",
            event_time=None,
            detail="missing bar",
            raised_at=EVENT_TIME,
        )
        assert flag.event_time is None

    @pytest.mark.leakage
    def test_naive_raised_at_rejected(self) -> None:
        with pytest.raises(ValidationError, match="timezone"):
            DataQualityFlag(
                flag_type=QualityFlagType.GAP,
                symbol="TEST",
                event_time=EVENT_TIME,
                detail="missing bar",
                raised_at=datetime(2026, 1, 6),  # no tzinfo
            )
