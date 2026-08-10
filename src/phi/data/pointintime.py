"""Point-in-time query helper tying time semantics to concrete PriceBar data.

Deliberately kept separate from ``phi.data.time`` (which stays free of any
dependency on concrete schemas, so it can be reused for non-price data later)
and from ``phi.data.storage`` (persistence and range queries, not decision-time
filtering). This is the module where PRD-ACCEPT-002's "point-in-time
correctness demonstrated on a worked example" requirement has one clear,
reusable, testable entry point.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from phi.data.schemas import PriceBar
from phi.data.time import is_available_at


def as_of(bars: Sequence[PriceBar], decision_time: datetime) -> list[PriceBar]:
    """Return only the bars knowable at ``decision_time`` (SYSTEM_ARCHITECTURE §12).

    Bars are returned in their input order; callers that need chronological
    order should sort separately (this function makes no assumption about
    input ordering).
    """
    return [b for b in bars if is_available_at(b.availability_time, decision_time=decision_time)]
