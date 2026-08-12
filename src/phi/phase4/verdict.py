"""The four permitted confirmatory outcomes (spec §XXVII, §LIV-§LVII).

PHI may reach exactly four conclusions, decided by where the two-sided CI for
``Δ_φ`` sits relative to the equivalence region ``[-δ_min, +δ_min]``. This encodes
the frozen decision rule so a result cannot be narrated into a more favourable
outcome. It classifies a *single* result; a SUPPORTING **claim** additionally
requires the gate-level conditions (null calibration, power, robustness,
replication) enumerated in spec §LIV, which live on the pre-registration.
"""

from __future__ import annotations

from enum import StrEnum

from phi.phase4.inference import BootstrapResult


class Outcome(StrEnum):
    SUPPORTING = "evidence_supporting_phi"  # CI entirely above +δ_min (spec §LIV)
    AGAINST = "evidence_against_phi"  # CI entirely below -δ_min (spec §LV)
    INDISTINGUISHABLE = "practically_indistinguishable"  # CI within [-δ_min,+δ_min] (§LVI)
    INCONCLUSIVE = "inconclusive"  # CI spans meaningful +/- effects (spec §LVII)


def classify_outcome(result: BootstrapResult, *, delta_min: float) -> Outcome:
    """Classify a Δ_φ bootstrap result against the equivalence margin ``delta_min``.

    Uses the two-sided CI bounds only, per the frozen decision rule (spec §LIV-
    §LVII). ``delta_min`` must be a positive, pre-registered, domain-justified
    effect size (never derived from the data — spec §XL).
    """
    if delta_min <= 0.0:
        raise ValueError(f"delta_min must be positive and pre-registered; got {delta_min!r}")
    lo, hi = result.ci_low, result.ci_high
    if lo > delta_min:
        return Outcome.SUPPORTING
    if hi < -delta_min:
        return Outcome.AGAINST
    if -delta_min <= lo and hi <= delta_min:
        return Outcome.INDISTINGUISHABLE
    return Outcome.INCONCLUSIVE
