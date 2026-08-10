"""Phase 1 domain schemas (DATABASE_ARCHITECTURE.md §7).

Pydantic models enforce structural/schema-level invariants at construction —
a malformed record cannot exist as an object at all (e.g. a naive timestamp, or
availability_time preceding event_time). This is deliberately stricter than the
architecture's module split between "Data Ingestion" (tags, does not validate)
and "Data Validation" (module 2): schema-shape invariants are cheapest and safest
to enforce at the type boundary itself, while cross-record checks that need a
whole batch (duplicates, gaps, monotonicity) belong to ``phi.data.validation``.

Not yet modeled in this increment (tracked as a known limitation, not a silent
omission): ``InstrumentAlias``, ``CorporateAction``, and a full exchange-specific
``TradingCalendar`` (see ``phi.data.calendar.SimpleTradingCalendar`` for the
minimal weekday-based stand-in used for gap detection in Phase 1).
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AssetClass(StrEnum):
    EQUITY = "equity"
    ETF = "etf"
    INDEX = "index"
    FX = "fx"
    CRYPTO = "crypto"
    FUTURE = "future"


class InstrumentStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Instrument(BaseModel):
    """A tradable security. Never hard-deleted on delisting (PRD-DATA-009)."""

    model_config = ConfigDict(frozen=True)

    symbol: str = Field(min_length=1)
    exchange: str = Field(min_length=1)
    asset_class: AssetClass
    currency: str = Field(min_length=3, max_length=3)
    listing_date: date
    delisting_date: date | None = None
    status: InstrumentStatus = InstrumentStatus.ACTIVE

    @model_validator(mode="after")
    def _delisting_consistent_with_status(self) -> Instrument:
        if self.delisting_date is not None and self.delisting_date < self.listing_date:
            raise ValueError("delisting_date must not precede listing_date")
        if self.status is InstrumentStatus.INACTIVE and self.delisting_date is None:
            raise ValueError("an inactive instrument must record a delisting_date")
        return self


class DataProvenance(BaseModel):
    """Source, fetch time, and content identity of an ingested batch (PRD-DATA-010)."""

    model_config = ConfigDict(frozen=True)

    source: str = Field(min_length=1)
    fetch_timestamp: datetime
    provider_batch_id: str = Field(min_length=1)
    content_hash: str = Field(min_length=1)

    @field_validator("fetch_timestamp")
    @classmethod
    def _tz_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("fetch_timestamp must be timezone-aware (SYSTEM_ARCHITECTURE §12)")
        return v


class QualityFlagType(StrEnum):
    DUPLICATE = "duplicate"
    GAP = "gap"
    NON_MONOTONIC_TIMESTAMP = "non_monotonic_timestamp"
    IMPLAUSIBLE_VOLUME = "implausible_volume"
    SCHEMA_INVALID = "schema_invalid"


class DataQualityFlag(BaseModel):
    """A validation failure or anomaly, routed to quarantine rather than dropped.

    Per SYSTEM_ARCHITECTURE §9.2, Data Validation must not silently "fix" data —
    every flag raised here must remain visible, never silently discarded.
    """

    model_config = ConfigDict(frozen=True)

    flag_type: QualityFlagType
    symbol: str = Field(min_length=1)
    event_time: datetime | None
    detail: str = Field(min_length=1)
    raised_at: datetime

    @field_validator("event_time", "raised_at")
    @classmethod
    def _tz_aware(cls, v: datetime | None) -> datetime | None:
        if v is not None and v.tzinfo is None:
            raise ValueError("timestamps must be timezone-aware (SYSTEM_ARCHITECTURE §12)")
        return v


class PriceBar(BaseModel):
    """The canonical OHLCV time series entity (DATABASE_ARCHITECTURE §7.2).

    ``event_time`` is what the bar is *about*; ``availability_time`` is when it
    was actually knowable (SYSTEM_ARCHITECTURE §12). They are tracked separately
    because the two can diverge (e.g. restated data) and collapsing them would
    make look-ahead bias structurally undetectable.
    """

    model_config = ConfigDict(frozen=True)

    symbol: str = Field(min_length=1)
    event_time: datetime
    availability_time: datetime
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: float = Field(ge=0)
    adjusted: bool
    provenance: DataProvenance

    @field_validator("event_time", "availability_time")
    @classmethod
    def _tz_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("timestamps must be timezone-aware (SYSTEM_ARCHITECTURE §12)")
        return v

    @model_validator(mode="after")
    def _consistent(self) -> PriceBar:
        if self.availability_time < self.event_time:
            raise ValueError(
                "availability_time must not precede event_time "
                "(SYSTEM_ARCHITECTURE §12 information barrier)"
            )
        if self.low > self.high:
            raise ValueError("low must not exceed high")
        if not (self.low <= self.open <= self.high):
            raise ValueError("open must satisfy low <= open <= high")
        if not (self.low <= self.close <= self.high):
            raise ValueError("close must satisfy low <= close <= high")
        return self
