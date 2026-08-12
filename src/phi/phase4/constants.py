"""Frozen Phase-4 methodology constants (PHI — Phase 4 Scientific Specification).

These encode the parts of the Phase-4 contract that the Chief Scientific
Methodologist froze at the **method** level (status: GO-with-conditions). They
are pinned by expression and must not change without a superseding contract
version. The values that remain **unfrozen** (the exact comparison set ``C``,
``delta_min``, Dataset A/B identities, block-length configuration, and the RNG
seed) are NOT here — they are per-experiment registrations in
:mod:`phi.phase4.registration` and are what the fail-closed confirmatory gate
requires before any confirmatory analysis.

This module contains no data, computes no estimate, and asserts nothing about φ.
"""

from __future__ import annotations

from phi import PHI

#: q_φ = 1/φ, the Golden-Ratio retracement value under test (spec §II, §IV).
#: Reuses the single frozen source of truth in :mod:`phi`.
Q_PHI: float = 1.0 / PHI  # ≈ 0.6180339887498949

#: Significance level for the confirmatory family (spec §XXXVIII). Frozen.
ALPHA: float = 0.05

#: Two-sided confidence level for the primary effect (spec §XXXVI). Frozen.
CONFIDENCE_LEVEL: float = 0.95

#: Bootstrap replicate count (spec §XXXIV). A computational specification, not a
#: statistical knob; the Monte-Carlo error of the p-value is monitored separately.
BOOTSTRAP_REPLICATES: int = 10_000

#: Primary test direction (spec §XXXVII): one-sided ``H0: Δ_φ ≤ 0`` vs ``H1: Δ_φ > 0``.
PRIMARY_TEST_DIRECTION: str = "one-sided-greater"

#: Canonical anchor algorithm identifier (spec §V-§VI). Frozen.
ANCHOR_ALGORITHM: str = "deterministic-three-point-extrema"

#: Canonical primary estimand identifier (spec §XIX).
PRIMARY_ESTIMAND: str = "delta_phi_mean_paired_distance_advantage"

#: Canonical distance metric identifier (spec §IX): continuous absolute distance.
DISTANCE_METRIC: str = "absolute_R_minus_q"

#: Canonical dependence-aware inference identifier (spec §XXXII).
INFERENCE_METHOD: str = "stationary-block-bootstrap-politis-romano"

#: Canonical multiplicity procedure (spec §XXXIX).
MULTIPLICITY_METHOD: str = "holm-step-down"

#: Minimum simulation-based power at ``delta_min`` for a confirmatory claim (spec §XLII).
POWER_THRESHOLD: float = 0.80

#: Primary retracement domain (spec §XXII): ``R ∈ [0, 1]``; ``R > 1`` is a reported
#: overshoot / excursion invalidation, never silently deleted.
RETRACEMENT_MIN: float = 0.0
RETRACEMENT_MAX: float = 1.0
