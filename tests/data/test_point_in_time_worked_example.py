"""PRD-ACCEPT-002 worked example: point-in-time correctness, end to end.

"For Phase 1: a reference dataset has passed validation with logged
data-quality results, and point-in-time correctness (availability time vs.
decision time) is demonstrated on at least one worked example."

Scenario: a 2026-01-05 daily bar is first reported with close=100.0, available
at its own bar close. Three days later, a correction restates the same trading
day's close as 101.5, available only once the correction lands. This is the
single most direct demonstration in this codebase that SYSTEM_ARCHITECTURE
§12's T-1 / information-barrier rule is load-bearing, not decorative: a
decision made before the correction exists literally cannot see it, and the
storage layer never silently overwrites the original with the correction
(PRD-DATA-002).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from phi.data.pointintime import as_of
from phi.data.schemas import DataProvenance, PriceBar
from phi.data.storage import ParquetPriceBarRepository
from phi.data.time import LookaheadViolationError, enforce_information_barrier

EVENT_TIME = datetime(2026, 1, 5, 21, 0, tzinfo=UTC)


def _bar(*, availability_time: datetime, close: float, content_hash: str) -> PriceBar:
    return PriceBar(
        symbol="TEST",
        event_time=EVENT_TIME,
        availability_time=availability_time,
        open=100.0,
        high=max(close, 102.0),
        low=min(close, 99.0),
        close=close,
        volume=1000.0,
        adjusted=False,
        provenance=DataProvenance(
            source="synthetic:test",
            fetch_timestamp=availability_time,
            provider_batch_id=content_hash,
            content_hash=content_hash,
        ),
    )


@pytest.mark.leakage
def test_point_in_time_worked_example(tmp_path: Path) -> None:
    original = _bar(availability_time=EVENT_TIME, close=100.0, content_hash="original")
    correction_availability = EVENT_TIME + timedelta(days=3)
    corrected = _bar(
        availability_time=correction_availability, close=101.5, content_hash="corrected"
    )

    repo = ParquetPriceBarRepository(tmp_path)
    repo.append([original])
    repo.append([corrected])

    stored = repo.query(
        "TEST", start=EVENT_TIME - timedelta(days=1), end=EVENT_TIME + timedelta(days=10)
    )
    # Both versions are retained side by side — the correction never
    # destructively overwrote the original record (PRD-DATA-002).
    assert len(stored) == 2

    decision_before_correction = EVENT_TIME + timedelta(days=1)
    visible_before = as_of(stored, decision_before_correction)
    assert [b.close for b in visible_before] == [100.0]

    decision_after_correction = EVENT_TIME + timedelta(days=4)
    visible_after = as_of(stored, decision_after_correction)
    assert {b.close for b in visible_after} == {100.0, 101.5}

    # The barrier is enforced, not just descriptive: a direct attempt to use
    # the not-yet-existing correction at the earlier decision time is rejected.
    with pytest.raises(LookaheadViolationError):
        enforce_information_barrier(
            availability_time=corrected.availability_time,
            decision_time=decision_before_correction,
            description="corrected 2026-01-05 close",
        )
