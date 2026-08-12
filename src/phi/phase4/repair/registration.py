"""Repaired fail-closed registration and confirmatory/secondary/exploratory paths.

Encodes the repaired confirmatory gate (Repair Contract Parts 8-9): a
:class:`RepairPreRegistration` is confirmatory-authorized only when every numerical
registration is present AND all five validation gates pass. The confirmatory entry
point uses the surrogate-standardized ``Z_phi`` test and the rational-fraction
specificity check; it **cannot** silently run the forbidden ``Delta_phi > 0`` test or
any exploratory method - those live behind distinct functions.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar

import numpy as np

from phi.phase4.constants import ALPHA
from phi.phase4.datasets import DataRole, DataSeparationError, RegisteredDataset
from phi.phase4.estimand import delta_phi, grid_landscape
from phi.phase4.multiplicity import holm_step_down
from phi.phase4.repair.rational import FIVE_EIGHTHS, Q_PHI, RATIONAL_CONSTANTS
from phi.phase4.repair.surrogates import PRIMARY_SURROGATE
from phi.phase4.repair.zscore import RepairScore, eligible_retracements, standardized_null_score

_RATIONALS = tuple(RATIONAL_CONSTANTS.values())
DEFAULT_SURROGATES: int = 999


class ConfirmatoryNotAuthorizedError(RuntimeError):
    """Confirmatory analysis requested before the repaired validation gates passed."""


# --------------------------------------------------------------------------- #
# CONFIRMATORY: surrogate-standardized Z_phi + rational-fraction specificity
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ConfirmatoryResult:
    """Per-dataset repaired confirmatory result (statistical, pre-replication)."""

    score: RepairScore
    per_rational_p: dict[str, float]
    per_rational_adjusted_p: dict[str, float]
    beats_all_rationals: bool
    beats_five_eighths: bool

    @property
    def z_phi(self) -> float:
        return self.score.z_phi

    @property
    def supports_phi(self) -> bool:
        """Statistical support on THIS dataset (full claim also needs authorization + replication).

        Requires: phi beats the rational set with surrogate ``p < alpha`` AND phi beats
        every individual rational fraction (Holm-adjusted), including 5/8.
        """
        return self.score.surrogate_p < ALPHA and self.beats_all_rationals


def confirmatory_phi_test(
    series: Sequence[float] | np.ndarray,
    *,
    n_surrogates: int = DEFAULT_SURROGATES,
    seed: int,
    alpha: float = ALPHA,
) -> ConfirmatoryResult | None:
    """The repaired primary confirmatory test (Parts 2-3): ``Z_phi`` + rational Holm.

    Returns ``None`` if the series yields too few eligible retracements/surrogates.
    Uses ONLY the surrogate-standardized advantage over rational constants - never the
    forbidden ``Delta_phi > 0`` statistic.
    """
    score = standardized_null_score(
        series, constants=_RATIONALS, focal=Q_PHI, n_surrogates=n_surrogates, seed=seed
    )
    if score is None:
        return None
    names = list(RATIONAL_CONSTANTS)
    per_p: dict[str, float] = {}
    for offset, name in enumerate(names, start=1):
        c = RATIONAL_CONSTANTS[name]
        s = standardized_null_score(
            series, constants=(c,), focal=Q_PHI, n_surrogates=n_surrogates, seed=seed + offset
        )
        per_p[name] = s.surrogate_p if s is not None else 1.0
    holm = holm_step_down([per_p[n] for n in names], alpha=alpha)
    adjusted = dict(zip(names, holm.adjusted_p_values, strict=True))
    rejected = dict(zip(names, holm.rejected, strict=True))
    return ConfirmatoryResult(
        score=score,
        per_rational_p=per_p,
        per_rational_adjusted_p=adjusted,
        beats_all_rationals=all(rejected.values()),
        beats_five_eighths=rejected["5/8"],
    )


# --------------------------------------------------------------------------- #
# SECONDARY / EXPLORATORY (descriptive only; never confirmatory)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class SecondaryProfile:
    """Descriptive constant profile - explicitly NON-confirmatory (Repair: Delta_phi demoted)."""

    landscape_argmin_q: float
    delta_phi_vs_symmetric_controls: float
    note: str = "SECONDARY/DESCRIPTIVE ONLY: Delta_phi>0 is forbidden as confirmatory evidence"


def run_secondary_profile(
    series: Sequence[float] | np.ndarray, *, symmetric_controls: Sequence[float]
) -> SecondaryProfile:
    """The old Delta_phi landscape as a SECONDARY descriptive statistic (never confirmatory)."""
    r = eligible_retracements(series)
    grid = np.linspace(0.05, 0.95, 181)
    land = grid_landscape(r, grid)
    return SecondaryProfile(
        landscape_argmin_q=float(grid[int(np.argmin(land))]),
        delta_phi_vs_symmetric_controls=float(delta_phi(r, symmetric_controls)),
    )


# --------------------------------------------------------------------------- #
# Fail-closed pre-registration
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class RepairPreRegistration:
    """Immutable repaired pre-registration with a fail-closed five-part gate."""

    experiment_id: str
    experiment_version: str
    research_question: str
    primary_hypothesis: str

    # Frozen method (defaults = repaired contract)
    focal_constant: float = Q_PHI
    rational_constants: tuple[float, ...] = _RATIONALS
    primary_surrogate: str = PRIMARY_SURROGATE
    primary_estimand: str = "standardized_null_score_Z_phi"
    alpha: float = ALPHA
    n_surrogates: int = DEFAULT_SURROGATES

    # Numerical registrations (None until frozen)
    dataset_a_id: str | None = None
    dataset_a_hash: str | None = None
    dataset_b_id: str | None = None
    dataset_b_hash: str | None = None
    sampling_frequency: str | None = None
    block_length_config: str | None = None
    random_seed: int | None = None
    code_version: str | None = None
    environment_lock_hash: str | None = None

    # Validation-gate evidence (Part 8) - fail-closed until demonstrated
    aggregate_fpr: float | None = None
    max_per_dgp_fpr: float | None = None
    positive_control_power_medium: float | None = None
    granularity_passes: bool = False
    constant_sweep_symmetric: bool = False

    REQUIRED_REGISTRATIONS: ClassVar[tuple[str, ...]] = (
        "dataset_a_id",
        "dataset_a_hash",
        "dataset_b_id",
        "dataset_b_hash",
        "sampling_frequency",
        "block_length_config",
        "random_seed",
        "code_version",
        "environment_lock_hash",
    )

    def missing_registrations(self) -> tuple[str, ...]:
        return tuple(n for n in self.REQUIRED_REGISTRATIONS if getattr(self, n) is None)

    def failed_gates(self) -> tuple[str, ...]:
        """The five-part acceptance gate (Part 8); empty when all pass."""
        failed: list[str] = []
        if self.aggregate_fpr is None or self.aggregate_fpr > self.alpha:
            failed.append("aggregate_fpr<=0.05")
        if self.max_per_dgp_fpr is None or self.max_per_dgp_fpr > 0.07:
            failed.append("per_dgp_fpr<=0.07")
        if self.positive_control_power_medium is None or self.positive_control_power_medium < 0.80:
            failed.append("power>=0.80")
        if not self.granularity_passes:
            failed.append("granularity_rejection")
        if not self.constant_sweep_symmetric:
            failed.append("constant_sweep_symmetry")
        return tuple(failed)

    def is_confirmatory_authorized(self) -> bool:
        """Fail-closed: True only if fully registered AND all five gates pass."""
        return not self.missing_registrations() and not self.failed_gates()

    def content_hash(self) -> str:
        payload = json.dumps(dataclasses.asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def run_confirmatory_repair(
    series: Sequence[float] | np.ndarray,
    *,
    registration: RepairPreRegistration,
    dataset: RegisteredDataset,
) -> ConfirmatoryResult:
    """Run the repaired confirmatory Z_phi test on Dataset A. Fails closed.

    Uses ONLY the surrogate-standardized confirmatory test - structurally unable to
    execute the forbidden Delta_phi>0 statistic or any exploratory method.
    """
    if not registration.is_confirmatory_authorized():
        raise ConfirmatoryNotAuthorizedError(
            "repaired confirmatory analysis refused (fail-closed): "
            f"missing={registration.missing_registrations()}; "
            f"failed gates={registration.failed_gates()}"
        )
    if dataset.role is not DataRole.CONFIRMATION:
        raise DataSeparationError(
            f"dataset role {dataset.role!r} may not be used for a confirmatory run"
        )
    if dataset.dataset_id != registration.dataset_a_id or (
        dataset.content_hash != registration.dataset_a_hash
    ):
        raise DataSeparationError("dataset does not match the registered confirmatory Dataset A")
    seed = registration.random_seed
    assert seed is not None  # guaranteed by is_confirmatory_authorized()
    result = confirmatory_phi_test(series, n_surrogates=registration.n_surrogates, seed=seed)
    if result is None:
        raise ValueError("confirmatory series yielded too few eligible retracements/surrogates")
    return result


#: 5/8 is exported for tests / callers that assert the specificity target.
FIVE_EIGHTHS_TARGET: float = FIVE_EIGHTHS
