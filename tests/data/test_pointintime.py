"""Unit tests for the point-in-time query helper (ties phi.data.time to PriceBar)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from phi.data.pointintime import as_of
from phi.data.schemas import DataProvenance, PriceBar

EVENT_TIME = datetime(2026, 1, 5, 21, 0, tzinfo=UTC)


def _bar(availability_time: datetime, *, content_hash: str) -> PriceBar:
    return PriceBar(
        symbol="TEST",
        event_time=EVENT_TIME,
        availability_time=availability_time,
        open=100.0,
        high=101.0,
        low=99.0,
        close=100.0,
        volume=1000.0,
        adjusted=False,
        provenance=DataProvenance(
            source="synthetic:test",
            fetch_timestamp=availability_time,
            provider_batch_id="batch",
            content_hash=content_hash,
        ),
    )


@pytest.mark.leakage
def test_as_of_excludes_bars_not_yet_available() -> None:
    early = _bar(EVENT_TIME, content_hash="a")
    late = _bar(EVENT_TIME + timedelta(days=3), content_hash="b")
    result = as_of([early, late], EVENT_TIME + timedelta(days=1))
    assert result == [early]


@pytest.mark.leakage
def test_as_of_includes_everything_available_by_decision_time() -> None:
    early = _bar(EVENT_TIME, content_hash="a")
    late = _bar(EVENT_TIME + timedelta(days=3), content_hash="b")
    result = as_of([early, late], EVENT_TIME + timedelta(days=5))
    assert result == [early, late]


@pytest.mark.leakage
def test_as_of_empty_input_returns_empty() -> None:
    assert as_of([], EVENT_TIME) == []
