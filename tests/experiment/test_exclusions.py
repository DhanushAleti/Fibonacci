"""Exclusion accounting ledger (external contract §7, §35)."""

from __future__ import annotations

import dataclasses

import pytest

from phi.experiment.exclusions import (
    ExclusionAccountant,
    ExclusionReason,
    ExclusionSummary,
)


class TestBasicAccounting:
    def test_valid_equals_raw_minus_excluded(self) -> None:
        acc = ExclusionAccountant(raw_count=1000)
        acc.record(ExclusionReason.ZERO_EXCURSION, 12)
        acc.record(ExclusionReason.INSUFFICIENT_HISTORY, 20)
        summary = acc.summary()
        assert summary.raw_count == 1000
        assert summary.excluded_total == 32
        assert summary.valid_count == 968

    def test_missingness_rate(self) -> None:
        acc = ExclusionAccountant(raw_count=200)
        acc.record(ExclusionReason.MISSING_DATA, 50)
        assert acc.summary().missingness_rate == pytest.approx(0.25)

    def test_running_valid_count_and_excluded_total(self) -> None:
        acc = ExclusionAccountant(raw_count=100)
        assert acc.excluded_total() == 0
        assert acc.valid_count() == 100
        acc.record(ExclusionReason.ZERO_EXCURSION, 7)
        assert acc.excluded_total() == 7
        assert acc.valid_count() == 93

    def test_accumulates_same_reason(self) -> None:
        acc = ExclusionAccountant(raw_count=100)
        acc.record(ExclusionReason.MISSING_DATA, 3)
        acc.record(ExclusionReason.MISSING_DATA, 4)
        summary = acc.summary()
        assert dict(summary.per_reason) == {"missing_data": 7}

    def test_per_reason_is_sorted_and_stable(self) -> None:
        acc = ExclusionAccountant(raw_count=100)
        acc.record(ExclusionReason.ZERO_EXCURSION, 1)
        acc.record(ExclusionReason.DOMAIN_ERROR, 2)
        acc.record(ExclusionReason.MISSING_DATA, 3)
        reasons = [name for name, _ in acc.summary().per_reason]
        assert reasons == sorted(reasons)

    def test_zero_raw_count_has_zero_missingness(self) -> None:
        assert ExclusionAccountant(raw_count=0).summary().missingness_rate == 0.0

    def test_no_exclusions_all_valid(self) -> None:
        summary = ExclusionAccountant(raw_count=500).summary()
        assert summary.valid_count == 500
        assert summary.per_reason == ()


class TestFailureModes:
    def test_negative_raw_count_rejected(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            ExclusionAccountant(raw_count=-1)

    def test_negative_record_rejected(self) -> None:
        acc = ExclusionAccountant(raw_count=10)
        with pytest.raises(ValueError, match="non-negative"):
            acc.record(ExclusionReason.MISSING_DATA, -1)

    def test_over_exclusion_raises_not_silent(self) -> None:
        acc = ExclusionAccountant(raw_count=10)
        acc.record(ExclusionReason.MISSING_DATA, 11)
        with pytest.raises(ValueError, match="exceed raw_count"):
            acc.summary()


class TestSummaryIsImmutable:
    def test_summary_is_frozen(self) -> None:
        summary = ExclusionAccountant(raw_count=1).summary()
        assert isinstance(summary, ExclusionSummary)
        with pytest.raises(dataclasses.FrozenInstanceError):
            summary.raw_count = 5  # type: ignore[misc]
