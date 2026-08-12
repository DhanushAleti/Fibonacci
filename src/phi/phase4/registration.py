"""Immutable Phase-4 pre-registration and the fail-closed confirmatory gate.

The Phase-4 *methodology* is frozen (:mod:`phi.phase4.constants`), but the Final
Scientific Arbiter's NO-GO stands for **running** the confirmatory experiment
until the remaining numerical decisions are registered and the validation gates
pass. This module encodes exactly that:

* :class:`Phase4PreRegistration` holds the frozen-method identifiers **plus** the
  still-unfrozen numerical registrations (comparison set ``C``, ``delta_min``,
  Dataset A/B identities, block-length configuration, RNG seed, provenance) and
  the validation-gate evidence (bootstrap coverage, null-DGP FPR calibration,
  achieved power).
* :meth:`Phase4PreRegistration.is_confirmatory_authorized` returns ``True`` only
  when **every** registration is present, the comparison set is structurally
  valid, and **every** validation gate has passed. It **fails closed**: any
  missing item or unpassed gate ⇒ not authorized.

The confirmatory pipeline (:mod:`phi.phase4.pipeline`) refuses to run unless this
returns ``True``, so an incomplete pre-registration makes confirmatory analysis
literally unrunnable — the code-level expression of the Arbiter's NO-GO.

This module chooses no scientific value. It stores what a human registers and
checks completeness/validity; it never fills in ``C``, ``delta_min``, datasets,
the seed, or a gate result on the researcher's behalf.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import ClassVar

from phi.phase4.constants import (
    ALPHA,
    ANCHOR_ALGORITHM,
    BOOTSTRAP_REPLICATES,
    CONFIDENCE_LEVEL,
    DISTANCE_METRIC,
    INFERENCE_METHOD,
    MULTIPLICITY_METHOD,
    POWER_THRESHOLD,
    PRIMARY_ESTIMAND,
    Q_PHI,
)

#: Absolute tolerance for validating that the comparison set is symmetric and
#: equally spaced around ``q_φ`` (float-rounding only, not a scientific knob).
_SPACING_ATOL: float = 1e-9


class ComparisonSetError(ValueError):
    """The registered comparison set ``C`` violates the frozen structural rules.

    Spec §XXIV / red-team Attack Vector 1 (Grid Asymmetry): ``C`` must be
    non-empty, exclude ``q_φ``, and be symmetric and equally spaced about ``q_φ``,
    so the ``[0,1]`` geometry cannot be rigged to favour φ. A malformed ``C`` is
    surfaced here rather than silently accepted.
    """


def validate_comparison_set(comparison_set: tuple[float, ...], *, q_phi: float = Q_PHI) -> None:
    """Raise :class:`ComparisonSetError` unless ``comparison_set`` is well-formed.

    Rules (all frozen, spec §XXIV): non-empty; every constant strictly inside
    ``(0, 1)``; ``q_φ`` excluded; even count; and symmetric + equally spaced about
    ``q_φ`` (the sorted offsets from ``q_φ`` are ``±δ, ±2δ, …, ±(K/2)δ``).
    """
    if not comparison_set:
        raise ComparisonSetError("comparison set C is empty (spec §XXIV requires matched controls)")
    for q in comparison_set:
        if not (0.0 < q < 1.0):
            raise ComparisonSetError(f"comparison constant {q!r} is not strictly inside (0, 1)")
        if math.isclose(q, q_phi, abs_tol=_SPACING_ATOL):
            raise ComparisonSetError(f"comparison set must exclude q_phi; found {q!r}")
    if len(comparison_set) % 2 != 0:
        raise ComparisonSetError(
            f"comparison set must be symmetric about q_phi (even count); got {len(comparison_set)}"
        )
    offsets = sorted(q - q_phi for q in comparison_set)
    half = len(offsets) // 2
    below = offsets[:half]  # negative offsets, ascending
    above = offsets[half:]  # positive offsets, ascending
    # Symmetry: the k-th smallest below must mirror the k-th largest above.
    for lo, hi in zip(below, reversed(above), strict=True):
        if not math.isclose(-lo, hi, abs_tol=_SPACING_ATOL):
            raise ComparisonSetError(
                f"comparison set is not symmetric about q_phi: offset {lo!r} has no mirror {hi!r}"
            )
    # Equal spacing: consecutive positive offsets differ by a constant δ.
    delta = above[0]
    for k, off in enumerate(above, start=1):
        if not math.isclose(off, k * delta, abs_tol=_SPACING_ATOL):
            raise ComparisonSetError(
                f"comparison set is not equally spaced: offset {off!r} != {k}·δ ({k * delta!r})"
            )


@dataclass(frozen=True)
class Phase4PreRegistration:
    """A frozen, hashable Phase-4 pre-registration with a fail-closed gate.

    Frozen-method fields carry the contract's already-decided identifiers and
    default to the :mod:`phi.phase4.constants` values. Fields defaulting to
    ``None`` / ``()`` are the **unfrozen** numerical registrations and the
    validation-gate evidence; the manifest is not confirmatory-authorized until
    all are set/passed (see :meth:`is_confirmatory_authorized`).
    """

    # --- Identity (always required) --------------------------------------
    experiment_id: str
    experiment_version: str
    research_question: str
    primary_hypothesis: str

    # --- Frozen method (defaulted to the contract; part of the hashed plan) --
    q_phi: float = Q_PHI
    anchor_algorithm: str = ANCHOR_ALGORITHM
    distance_metric: str = DISTANCE_METRIC
    primary_estimand: str = PRIMARY_ESTIMAND
    inference_method: str = INFERENCE_METHOD
    multiplicity_method: str = MULTIPLICITY_METHOD
    bootstrap_replicates: int = BOOTSTRAP_REPLICATES
    alpha: float = ALPHA
    confidence_level: float = CONFIDENCE_LEVEL

    # --- Unfrozen numerical registrations (None/() until a human freezes) ----
    comparison_set: tuple[float, ...] = ()  # Arbiter Blocker 1 (exact C)
    delta_min: float | None = None  # Arbiter Blocker 2 (min meaningful effect)
    dataset_a_id: str | None = None  # Arbiter Blocker 3 (confirmatory dataset)
    dataset_a_hash: str | None = None
    dataset_b_id: str | None = None  # Arbiter Blocker 4 (replication dataset)
    dataset_b_hash: str | None = None
    sampling_frequency: str | None = None
    block_length_config: str | None = None  # Arbiter Blocker 5 (estimator/min/max/fallback)
    random_seed: int | None = None
    code_version: str | None = None
    environment_lock_hash: str | None = None
    falsification_criteria: str | None = None

    # --- Validation-gate evidence (fail-closed until demonstrated) -----------
    bootstrap_coverage_validated: bool = False  # Arbiter Blocker 6
    null_fpr_calibrated: bool = False  # Arbiter Blocker 8 (hard gate)
    power_at_delta_min: float | None = None  # Arbiter Blocker 7 (must be ≥ POWER_THRESHOLD)

    #: Numerical registrations that must be present for a confirmatory run.
    REQUIRED_REGISTRATIONS: ClassVar[tuple[str, ...]] = (
        "delta_min",
        "dataset_a_id",
        "dataset_a_hash",
        "dataset_b_id",
        "dataset_b_hash",
        "sampling_frequency",
        "block_length_config",
        "random_seed",
        "code_version",
        "environment_lock_hash",
        "falsification_criteria",
    )

    #: Validation gates that must pass (booleans True) for a confirmatory run.
    REQUIRED_VALIDATION_FLAGS: ClassVar[tuple[str, ...]] = (
        "bootstrap_coverage_validated",
        "null_fpr_calibrated",
    )

    def missing_registrations(self) -> tuple[str, ...]:
        """Names of unfrozen numerical registrations still absent (``()`` when complete)."""
        missing = [name for name in self.REQUIRED_REGISTRATIONS if getattr(self, name) is None]
        if not self.comparison_set:
            missing.append("comparison_set")
        return tuple(missing)

    def failed_validation_gates(self) -> tuple[str, ...]:
        """Names of validation gates not yet passed (``()`` when all pass)."""
        failed = [name for name in self.REQUIRED_VALIDATION_FLAGS if not getattr(self, name)]
        if self.power_at_delta_min is None or self.power_at_delta_min < POWER_THRESHOLD:
            failed.append("power_at_delta_min")
        return tuple(failed)

    def comparison_set_is_valid(self) -> bool:
        """Whether the registered ``comparison_set`` satisfies the structural rules."""
        if not self.comparison_set:
            return False
        try:
            validate_comparison_set(self.comparison_set, q_phi=self.q_phi)
        except ComparisonSetError:
            return False
        return True

    def is_confirmatory_authorized(self) -> bool:
        """Fail-closed gate: ``True`` only if fully registered, valid, and validated.

        Requires: every numerical registration present, the comparison set
        structurally valid, and every validation gate passed (including
        ``power_at_delta_min ≥`` :data:`~phi.phase4.constants.POWER_THRESHOLD`).
        Any single omission or unpassed gate ⇒ ``False``. Confirmatory code MUST
        gate on this; it is the machine-checkable expression of the Arbiter's
        NO-GO.
        """
        return (
            not self.missing_registrations()
            and self.comparison_set_is_valid()
            and not self.failed_validation_gates()
        )

    def canonical_json(self) -> str:
        """Deterministic JSON (sorted keys, compact) — the bytes :meth:`content_hash` digests."""
        return json.dumps(dataclasses.asdict(self), sort_keys=True, separators=(",", ":"))

    def content_hash(self) -> str:
        """SHA-256 of :meth:`canonical_json` — an honest byte-identity of the *plan* only."""
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ComparisonSet:
    """A symmetric, equally-spaced comparison set built from a registered ``(δ, K)``.

    ``K`` is the number of controls **per side**; the resulting set is
    ``{q_φ ± δ, q_φ ± 2δ, …, q_φ ± Kδ}`` (``2K`` constants, q_φ excluded). This
    only constructs the array from registered inputs; it does not choose ``δ`` or
    ``K`` — those are pre-registration decisions.
    """

    delta: float
    k_per_side: int
    q_phi: float = Q_PHI
    constants: tuple[float, ...] = field(default_factory=tuple)

    @classmethod
    def build(cls, *, delta: float, k_per_side: int, q_phi: float = Q_PHI) -> ComparisonSet:
        if delta <= 0.0:
            raise ComparisonSetError(f"delta must be positive; got {delta!r}")
        if k_per_side < 1:
            raise ComparisonSetError(f"k_per_side must be >= 1; got {k_per_side!r}")
        below = tuple(q_phi - j * delta for j in range(k_per_side, 0, -1))
        above = tuple(q_phi + j * delta for j in range(1, k_per_side + 1))
        constants = below + above
        validate_comparison_set(constants, q_phi=q_phi)
        return cls(delta=delta, k_per_side=k_per_side, q_phi=q_phi, constants=constants)
