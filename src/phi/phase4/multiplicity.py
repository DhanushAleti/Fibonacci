"""Holm step-down family-wise error control (spec §XXXIX).

Holm (1979) controls the family-wise error rate without dependence assumptions
and is less conservative than plain Bonferroni. It is applied to the registered
confirmatory family; no unadjusted secondary result may be described as
confirmatory (spec §XXXIX). This is a pure function of the input p-values.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class HolmResult:
    """Per-hypothesis Holm outcome, in the caller's original order."""

    adjusted_p_values: tuple[float, ...]
    rejected: tuple[bool, ...]


def holm_step_down(p_values: Sequence[float], *, alpha: float = 0.05) -> HolmResult:
    """Holm step-down correction over ``p_values`` at level ``alpha`` (spec §XXXIX).

    Returns monotone adjusted p-values and rejection flags in original order. A
    hypothesis is rejected iff its adjusted p-value ``≤ alpha``. Once a hypothesis
    fails the step-down threshold, it and all larger p-values are retained
    (standard Holm short-circuit, expressed via the cumulative-max of adjusted p).
    """
    if not 0.0 < alpha < 1.0:
        raise ValueError(f"alpha must be in (0, 1); got {alpha!r}")
    for p in p_values:
        if not 0.0 <= p <= 1.0:
            raise ValueError(f"p-value {p!r} is outside [0, 1]")
    m = len(p_values)
    if m == 0:
        return HolmResult(adjusted_p_values=(), rejected=())
    order = sorted(range(m), key=lambda i: p_values[i])
    adjusted = [0.0] * m
    running_max = 0.0
    for rank, idx in enumerate(order):
        candidate = min((m - rank) * p_values[idx], 1.0)
        running_max = max(running_max, candidate)  # enforce monotonicity
        adjusted[idx] = running_max
    rejected = tuple(adjusted[i] <= alpha for i in range(m))
    return HolmResult(adjusted_p_values=tuple(adjusted), rejected=rejected)
