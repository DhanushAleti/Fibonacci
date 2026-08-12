"""Frozen excursion-retracement math primitives (external contract §4, §8, §9, §43).

This module implements the **frozen arithmetic core** of the external
"Authoritative Scientific Contract" excursion-retracement feature:

    R_t      = |X_t - X_e| / |X_e - X_a|        (retracement ratio, §4)
    D_phi,t  = |R_t - q_phi|,   q_phi = 1/phi    (phi-distance, §4)
    phi-hit  <=> D_phi,t <= epsilon_phi          (§4, threshold registered)

Scope boundary — what is frozen vs. what is NOT (see ADR 0003):

* FROZEN and implemented here: the ratio arithmetic, zero-excursion -> NA
  (§8, no epsilon substitution), negative input values allowed (§9), and the
  phi-distance / phi-hit definitions. These take the anchors (X_a, X_e) and
  the threshold epsilon as **explicit inputs**.
* NOT frozen and deliberately NOT implemented (would be inventing methodology):
  - the causal anchor/excursion **selection** algorithm (Blocker 1) — only a
    typing ``Protocol`` boundary is declared below, with no concrete selector;
  - the value of ``epsilon_phi`` (Blocker 2) — ``is_phi_hit`` requires it to be
    passed explicitly and supplies **no default**, structurally preventing a
    silent threshold and threshold-fishing (Gemini dim 14 / Attack Vector 7).

This module is anchor-agnostic: it computes the frozen feature *given* anchors.
The feature-authority question is **decided** (ADR 0003, 2026-08-12, Option B):
the rolling-window feature in ``phi.features.candidate`` is the authoritative
Phase-2 feature; this excursion arithmetic is retained as **Phase-4 statistical
guidance only** and is deliberately not wired into the compute path. It remains
NO-GO for any confirmatory use until Blockers 1-4 are frozen by a human.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Protocol

from phi.features.constants import G_PHI

#: q_phi = 1/phi, the canonical golden-ratio retracement level (contract §3).
#: Reuses the single frozen source of truth in ``phi.features.constants``.
Q_PHI: float = G_PHI


class NonFiniteRetracementError(ValueError):
    """A retracement ratio overflowed to a non-finite value despite a nonzero excursion.

    Contract §8 maps only an **exact** zero excursion to NA; a finite-but-large
    overshoot (``R_t > 1``) is a valid structural value and must never be
    clamped (Gemini Attack Vector 8). This error is reserved for the distinct
    pathological case where finite inputs produce ``inf``/``nan`` via float
    overflow — surfaced explicitly rather than returned as a silent ``inf``.
    """


def retracement_ratio(x_a: float, x_e: float, x_t: float) -> float | None:
    """Canonical excursion retracement ratio ``R_t = |X_t - X_e| / |X_e - X_a|`` (§4).

    Args:
        x_a: excursion anchor (start). Selected by a frozen causal algorithm
            (Blocker 1) — this function does not select it.
        x_e: excursion endpoint (extremum). Likewise anchor-algorithm supplied.
        x_t: the subsequent eligible observation being measured.

    Returns:
        ``R_t >= 0``, or ``None`` (NA) when the excursion is exactly zero
        (``x_e == x_a``), per §8 — **no epsilon denominator substitution**.

    Negative input values are permitted (§9): the ratio is built from absolute
    magnitudes of differences, so it does not require positivity of the inputs.
    Values ``R_t > 1`` (overshoot / trend reversal) are returned unclamped.

    Raises:
        NonFiniteRetracementError: if finite inputs overflow to a non-finite
            ratio (numerical pathology; never silently returned as ``inf``).
    """
    excursion = x_e - x_a
    if excursion == 0.0:
        return None  # §8: undefined -> NA, no epsilon fudge
    ratio = abs(x_t - x_e) / abs(excursion)
    if not math.isfinite(ratio):
        raise NonFiniteRetracementError(
            f"retracement ratio is non-finite ({ratio!r}) for "
            f"x_a={x_a!r}, x_e={x_e!r}, x_t={x_t!r} despite a nonzero excursion; "
            "this is a numerical pathology, not a valid feature value"
        )
    return ratio


def phi_distance(r: float) -> float:
    """Canonical phi-distance ``D_phi = |R_t - q_phi|`` (§4). Always ``>= 0``."""
    return abs(r - Q_PHI)


def is_phi_hit(r: float, *, epsilon: float) -> bool:
    """Whether ratio ``r`` is a phi-hit: ``|R_t - q_phi| <= epsilon`` (§4).

    ``epsilon`` is a **required keyword argument with no default** by design:
    ``epsilon_phi`` is an unfrozen scientific parameter (Blocker 2) that MUST be
    registered in an immutable experiment manifest before confirmatory analysis
    and MUST NOT be chosen from observed data. Refusing a default makes a silent
    or data-driven threshold structurally impossible at the call site.

    Raises:
        ValueError: if ``epsilon`` is negative.
    """
    if epsilon < 0.0:
        raise ValueError(f"epsilon must be non-negative; got {epsilon!r}")
    return phi_distance(r) <= epsilon


class ExcursionAnchorSelector(Protocol):
    """Interface boundary for a causal anchor/excursion selection algorithm.

    **BLOCKER 1 — UNFROZEN. No concrete implementation is provided anywhere in
    this repository, by design.** The exact deterministic, causal
    extremum-identification algorithm (lookback ``k``, tie-breaking, minimum
    excursion size ``delta_min``, confirmation delay) is the primary hidden
    p-hacking pathway (Gemini dim 3; Attack Vectors 1 and 9) and must be frozen
    by a superseding ADR before any confirmatory feature is computed. This
    ``Protocol`` only declares the *shape* such an algorithm must satisfy so the
    boundary is explicit in code; it deliberately provides no behaviour.
    """

    def select(self, series: Sequence[float], *, decision_index: int) -> tuple[int, int] | None:
        """Return causal ``(a, e)`` anchor indices for ``decision_index``, or ``None``.

        Any conforming implementation MUST use only information available at or
        before the decision instant (``availability_time <= T and event_time <
        T``); an extremum may not be confirmed using future observations.
        """
        ...
