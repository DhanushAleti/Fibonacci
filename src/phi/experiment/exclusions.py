"""Exclusion accounting ledger (external contract §7, §35; Gemini Attack Vector 5).

The contract requires every analysis to report the number of raw observations,
the number excluded, the reasons, the number of valid observations, and the
missingness rate — and forbids silent dropping or curated "survivor pools."
This module provides a small, explicit accountant for exactly that: every
exclusion must be recorded against a named :class:`ExclusionReason`, and the
:class:`ExclusionSummary` it produces is an immutable, fully reconciled record
(``valid = raw - excluded``).

It makes no scientific decision. It counts. A downstream analysis may set a
pre-registered exclusion ceiling and abort as ``INVALID_EXPERIMENT`` if it is
exceeded (contract §31; Attack Vector 5), but that policy lives with the
experiment, not here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ExclusionReason(StrEnum):
    """The closed set of reasons an observation/excursion may be excluded.

    Every value corresponds to a contract-defined invalidation condition, so
    an exclusion can never be attributed to an unnamed developer heuristic
    (contract §28 researcher-degrees-of-freedom control).
    """

    MISSING_DATA = "missing_data"  # §7: any missing required input
    ZERO_EXCURSION = "zero_excursion"  # §8: |X_e - X_a| == 0 -> NA
    INSUFFICIENT_HISTORY = "insufficient_history"  # warmup / < window eligible bars
    INELIGIBLE_AVAILABILITY = "ineligible_availability"  # §16: availability_time > T
    UNORDERABLE_DUPLICATE = "unorderable_duplicate"  # §10: duplicate, not uniquely ordered
    DOMAIN_ERROR = "domain_error"  # dataset-contract domain violation


@dataclass(frozen=True)
class ExclusionSummary:
    """Immutable, reconciled exclusion counts for one analysis run (§7, §35)."""

    raw_count: int
    valid_count: int
    excluded_total: int
    per_reason: tuple[tuple[str, int], ...]
    missingness_rate: float


class ExclusionAccountant:
    """Mutable accumulator that produces an immutable :class:`ExclusionSummary`.

    Usage::

        acc = ExclusionAccountant(raw_count=1000)
        acc.record(ExclusionReason.ZERO_EXCURSION, 12)
        acc.record(ExclusionReason.INSUFFICIENT_HISTORY, 20)
        summary = acc.summary()   # valid_count == 968

    The accountant never silently drops: every excluded item must be recorded
    against a named reason, and :meth:`summary` fails loudly if the recorded
    exclusions exceed the raw count (an accounting bug, surfaced not hidden).
    """

    def __init__(self, raw_count: int) -> None:
        if raw_count < 0:
            raise ValueError(f"raw_count must be non-negative; got {raw_count!r}")
        self._raw_count = raw_count
        self._counts: dict[ExclusionReason, int] = {}

    def record(self, reason: ExclusionReason, count: int = 1) -> None:
        """Record ``count`` exclusions attributed to ``reason`` (count must be >= 0)."""
        if count < 0:
            raise ValueError(f"count must be non-negative; got {count!r}")
        self._counts[reason] = self._counts.get(reason, 0) + count

    def excluded_total(self) -> int:
        return sum(self._counts.values())

    def valid_count(self) -> int:
        return self._raw_count - self.excluded_total()

    def summary(self) -> ExclusionSummary:
        """Produce the reconciled, immutable summary (raises if over-excluded)."""
        excluded_total = self.excluded_total()
        if excluded_total > self._raw_count:
            raise ValueError(
                f"recorded exclusions ({excluded_total}) exceed raw_count "
                f"({self._raw_count}); exclusion accounting is inconsistent"
            )
        per_reason = tuple(
            (reason.value, self._counts[reason])
            for reason in sorted(self._counts, key=lambda r: r.value)
        )
        missingness_rate = excluded_total / self._raw_count if self._raw_count > 0 else 0.0
        return ExclusionSummary(
            raw_count=self._raw_count,
            valid_count=self._raw_count - excluded_total,
            excluded_total=excluded_total,
            per_reason=per_reason,
            missingness_rate=missingness_rate,
        )
