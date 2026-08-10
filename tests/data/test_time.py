"""Tests for the time-semantics backbone (SYSTEM_ARCHITECTURE §12).

These are scientific-invariant tests, not incidental unit tests: they exist to
prove the T-1 / information-barrier rule is enforced, not merely documented.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from phi.data.time import (
    LookaheadViolationError,
    ObservationWindow,
    enforce_information_barrier,
    is_available_at,
)

T0 = datetime(2026, 1, 5, 16, 0, tzinfo=UTC)  # a decision time, e.g. bar close


@pytest.mark.leakage
def test_data_available_before_decision_time_is_usable() -> None:
    availability = T0 - timedelta(minutes=1)
    assert is_available_at(availability, decision_time=T0) is True


@pytest.mark.leakage
def test_data_available_exactly_at_decision_time_is_usable() -> None:
    # SYSTEM_ARCHITECTURE §12: availability time <= decision time is the rule.
    assert is_available_at(T0, decision_time=T0) is True


@pytest.mark.leakage
def test_data_available_after_decision_time_is_not_usable() -> None:
    availability = T0 + timedelta(minutes=1)
    assert is_available_at(availability, decision_time=T0) is False


@pytest.mark.leakage
def test_enforce_information_barrier_allows_past_data() -> None:
    enforce_information_barrier(
        availability_time=T0 - timedelta(days=1), decision_time=T0
    )  # must not raise


@pytest.mark.leakage
def test_enforce_information_barrier_rejects_future_data() -> None:
    with pytest.raises(LookaheadViolationError) as exc:
        enforce_information_barrier(
            availability_time=T0 + timedelta(minutes=1),
            decision_time=T0,
            description="restated Q3 earnings",
        )
    # The error must name what leaked, not just that something did.
    assert "restated Q3 earnings" in str(exc.value)


@pytest.mark.leakage
def test_observation_window_rejects_start_after_end() -> None:
    with pytest.raises(ValueError, match=r"start.*end"):
        ObservationWindow(start=T0, end=T0 - timedelta(days=1))


@pytest.mark.leakage
def test_observation_window_ends_by_decision_time() -> None:
    window = ObservationWindow(start=T0 - timedelta(days=30), end=T0)
    assert window.ends_by(T0) is True
    assert window.ends_by(T0 - timedelta(seconds=1)) is False


@pytest.mark.leakage
def test_observation_window_require_valid_at_allows_compliant_window() -> None:
    window = ObservationWindow(start=T0 - timedelta(days=30), end=T0)
    window.require_valid_at(T0)  # must not raise


@pytest.mark.leakage
def test_observation_window_require_valid_at_rejects_leaking_window() -> None:
    window = ObservationWindow(start=T0 - timedelta(days=30), end=T0 + timedelta(days=1))
    with pytest.raises(LookaheadViolationError, match="golden-ratio-feature"):
        window.require_valid_at(T0, description="golden-ratio-feature")


@pytest.mark.leakage
def test_observation_window_spanning_into_the_future_is_rejected_at_use_time() -> None:
    # A feature whose window extends past decision time is exactly PRD-FEATENG-002's
    # violation; the window itself is constructible (it may be built ahead of time)
    # but must be rejected when checked against a decision time it doesn't respect.
    window = ObservationWindow(start=T0 - timedelta(days=30), end=T0 + timedelta(days=1))
    assert window.ends_by(T0) is False
