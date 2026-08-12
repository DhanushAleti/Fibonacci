"""Per-excursion retracement observations (spec §XXI-§XXII, §L).

The scientific unit is the **completed excursion** (spec §XXI), so each excursion
contributes exactly one retracement value. Between two consecutive three-point
extrema the series is monotonic (any intermediate reversal would itself be an
extremum), so the *completed* retracement of excursion ``i`` is its terminal
value, reached at the next extremum ``E_{i+1}``:

    R_i = |X_{E_{i+1}} - X_{E_i}| / |X_{E_i} - X_{A_i}|            (spec §XXII)

i.e. the next swing measured as a fraction of the current excursion. This reuses
the frozen arithmetic in :func:`phi.features.retracement.retracement_ratio`
(``x_a = X_{A_i}``, ``x_e = X_{E_i}``, ``x_t = X_{E_{i+1}}``).

Interpretation note (flagged for methodologist confirmation before the confirmatory
freeze): the spec defines ``R_it`` "for t > t_e" per observation but computes the
estimand with a single ``R_i`` per excursion (§XXVIII), and names the completed
excursion the unit (§XXI). This module takes the single per-excursion value to be
the **terminal** retracement at the next extremum, which is well-defined given
inter-extremum monotonicity. If the methodologist intends a different per-excursion
reduction, only this module changes.

Domain rules: zero excursion magnitude ⇒ ``R = NA`` (spec §L, no epsilon
denominator); ``R ∈ [0, 1]`` is eligible for primary inference; ``R > 1`` is a
reported **overshoot / excursion invalidation** (spec §XXII) — never silently
deleted, always counted and available to sensitivity analysis.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from phi.features.retracement import retracement_ratio
from phi.phase4.constants import RETRACEMENT_MAX, RETRACEMENT_MIN
from phi.phase4.extrema import Excursion


@dataclass(frozen=True)
class RetracementObservation:
    """One completed excursion's terminal retracement ``R`` (finite; overshoot kept)."""

    excursion_index: int
    r: float

    @property
    def is_overshoot(self) -> bool:
        """``R > 1``: the pullback exceeded the excursion (spec §XXII overshoot)."""
        return self.r > RETRACEMENT_MAX

    @property
    def is_eligible(self) -> bool:
        """``R ∈ [0, 1]``: eligible for primary inference (spec §XXII)."""
        return RETRACEMENT_MIN <= self.r <= RETRACEMENT_MAX


@dataclass(frozen=True)
class RetracementResult:
    """Retracements plus a full reconciliation of every excursion (spec §XLIX logging)."""

    observations: tuple[RetracementObservation, ...]
    n_excursions: int
    n_zero_denominator: int  # excluded: |X_e - X_a| == 0 (spec §L)
    n_incomplete: int  # excluded: no next extremum to complete the retracement

    @property
    def eligible(self) -> tuple[RetracementObservation, ...]:
        """Only ``R ∈ [0, 1]`` observations — the primary-inference sample."""
        return tuple(o for o in self.observations if o.is_eligible)

    @property
    def overshoots(self) -> tuple[RetracementObservation, ...]:
        return tuple(o for o in self.observations if o.is_overshoot)


def excursion_retracements(excursions: Sequence[Excursion]) -> RetracementResult:
    """Compute the terminal retracement of every completed excursion.

    Excursion ``i`` is completed by the end of excursion ``i+1`` (the next
    extremum). The final excursion has no successor and is counted as incomplete
    (excluded, logged). Zero-magnitude excursions yield ``NA`` and are excluded
    (logged), never epsilon-substituted (spec §L).
    """
    observations: list[RetracementObservation] = []
    n_zero = 0
    n_incomplete = 0
    for i, exc in enumerate(excursions):
        if i + 1 >= len(excursions):
            n_incomplete += 1
            continue
        next_extremum_value = excursions[i + 1].end.value
        r = retracement_ratio(exc.anchor.value, exc.end.value, next_extremum_value)
        if r is None:  # zero excursion magnitude → NA (spec §L)
            n_zero += 1
            continue
        observations.append(RetracementObservation(excursion_index=i, r=r))
    return RetracementResult(
        observations=tuple(observations),
        n_excursions=len(excursions),
        n_zero_denominator=n_zero,
        n_incomplete=n_incomplete,
    )
