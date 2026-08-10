"""Time semantics — the architectural backbone against look-ahead bias.

Implements SYSTEM_ARCHITECTURE.md §12: event time, availability time, decision
time, and the T-1 / information-barrier rule. Every module that touches market
data (feature engineering, backtesting) is bound by this rule; this module is
where it is enforced, not merely documented.

Nothing here decides *what* data exists — only whether a piece of data with a
given availability time may be used at a given decision time.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


class LookaheadViolationError(ValueError):
    """Raised when code attempts to use data not yet available at decision time.

    This is a scientific-integrity error, not an ordinary validation error — it
    signals a potential leakage bug (PRD-BIAS-007) and must never be silently
    caught and ignored by calling code.
    """


def is_available_at(availability_time: datetime, *, decision_time: datetime) -> bool:
    """Whether data with ``availability_time`` may be used at ``decision_time``.

    Per SYSTEM_ARCHITECTURE §12: "A decision may only use data whose availability
    time is <= decision time." Equality is intentionally permitted — data whose
    availability time coincides exactly with decision time is, by definition,
    knowable at that instant.
    """
    return availability_time <= decision_time


def enforce_information_barrier(
    *, availability_time: datetime, decision_time: datetime, description: str = "data"
) -> None:
    """Raise ``LookaheadViolationError`` if this would cross the T-1 barrier.

    Args:
        availability_time: when the data was actually knowable to a real
            participant (not the event time it describes).
        decision_time: the simulated "now" the caller wants to use the data at.
        description: human-readable identifier of what would have leaked,
            included in the raised error so a violation is traceable.
    """
    if not is_available_at(availability_time, decision_time=decision_time):
        raise LookaheadViolationError(
            f"{description} has availability_time={availability_time.isoformat()} "
            f"which is after decision_time={decision_time.isoformat()}; using it "
            "would violate the T-1 / information-barrier rule "
            "(SYSTEM_ARCHITECTURE §12)."
        )


@dataclass(frozen=True)
class ObservationWindow:
    """The historical span of data a feature/model may look backward over.

    Per PRD-FEATENG-002, an observation window must end no later than the
    decision time it will be used at. Construction only validates internal
    consistency (start <= end); whether a given window is *usable* at a specific
    decision time is a separate question answered by :meth:`ends_by`, because the
    same window definition may be legitimately reused across many decision times
    as a backtest advances.
    """

    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise ValueError(
                f"ObservationWindow start ({self.start.isoformat()}) must not be "
                f"after end ({self.end.isoformat()})"
            )

    def ends_by(self, decision_time: datetime) -> bool:
        """Whether this window respects the T-1 barrier at ``decision_time``."""
        return self.end <= decision_time

    def require_valid_at(self, decision_time: datetime, *, description: str = "feature") -> None:
        """Raise ``LookaheadViolationError`` if this window leaks past decision_time."""
        enforce_information_barrier(
            availability_time=self.end, decision_time=decision_time, description=description
        )
