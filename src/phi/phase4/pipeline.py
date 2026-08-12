"""Fail-closed confirmatory orchestration (spec §XLVII-§XLVIII; Arbiter NO-GO).

The confirmatory and replication entry points **refuse to run** unless the
pre-registration is complete, structurally valid, and validated
(:meth:`Phase4PreRegistration.is_confirmatory_authorized`) *and* the supplied
dataset matches the registered role and hash. An incomplete pre-registration
therefore makes confirmatory analysis literally unrunnable — the code-level
expression of the Final Arbiter's NO-GO. Exploratory/discovery runs are always
permitted (on synthetic/discovery data) but can never yield a confirmatory claim.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from phi.phase4.analysis import SeriesAnalysis, analyze_series
from phi.phase4.datasets import DataRole, DataSeparationError, RegisteredDataset
from phi.phase4.registration import Phase4PreRegistration


class ConfirmatoryNotAuthorizedError(RuntimeError):
    """Confirmatory analysis was requested before the pre-registration was complete.

    Carries the exact missing registrations and unpassed validation gates so the
    refusal is actionable, never silent.
    """


def run_exploratory(
    values: Sequence[float] | np.ndarray,
    comparison_set: Sequence[float],
    *,
    replicates: int,
    seed: int,
    confidence_level: float = 0.95,
) -> SeriesAnalysis:
    """Exploratory/discovery run — permitted on synthetic/discovery data only.

    Produces NO confirmatory claim (spec §XLVII: discovery data may not support
    confirmatory conclusions). Use for pipeline development and validation.
    """
    return analyze_series(
        values,
        comparison_set,
        replicates=replicates,
        seed=seed,
        confidence_level=confidence_level,
    )


def _require_authorized(registration: Phase4PreRegistration) -> None:
    if not registration.is_confirmatory_authorized():
        raise ConfirmatoryNotAuthorizedError(
            "confirmatory analysis refused (fail-closed): "
            f"missing registrations={registration.missing_registrations()}; "
            f"comparison_set_valid={registration.comparison_set_is_valid()}; "
            f"failed validation gates={registration.failed_validation_gates()}"
        )


def _run_registered(
    values: Sequence[float] | np.ndarray,
    registration: Phase4PreRegistration,
    dataset: RegisteredDataset,
    *,
    expected_role: DataRole,
    expected_id: str | None,
    expected_hash: str | None,
) -> SeriesAnalysis:
    _require_authorized(registration)
    if dataset.role is not expected_role:
        raise DataSeparationError(
            f"dataset role {dataset.role!r} may not be used for a {expected_role!r} run "
            "(spec §XLVII replication separation)"
        )
    if dataset.dataset_id != expected_id or dataset.content_hash != expected_hash:
        raise DataSeparationError(
            f"dataset {dataset.dataset_id!r}/{dataset.content_hash!r} does not match the "
            f"registered {expected_role.value} dataset {expected_id!r}/{expected_hash!r}"
        )
    seed = registration.random_seed
    assert seed is not None  # guaranteed non-None once is_confirmatory_authorized() is True
    return analyze_series(
        values,
        registration.comparison_set,
        replicates=registration.bootstrap_replicates,
        seed=seed,
        confidence_level=registration.confidence_level,
        q_phi=registration.q_phi,
    )


def run_confirmatory(
    values: Sequence[float] | np.ndarray,
    *,
    registration: Phase4PreRegistration,
    dataset: RegisteredDataset,
) -> SeriesAnalysis:
    """Run the primary confirmatory analysis on the registered Dataset A. Fails closed."""
    return _run_registered(
        values,
        registration,
        dataset,
        expected_role=DataRole.CONFIRMATION,
        expected_id=registration.dataset_a_id,
        expected_hash=registration.dataset_a_hash,
    )


def run_replication(
    values: Sequence[float] | np.ndarray,
    *,
    registration: Phase4PreRegistration,
    dataset: RegisteredDataset,
) -> SeriesAnalysis:
    """Run the independent replication on the registered Dataset B. Fails closed."""
    return _run_registered(
        values,
        registration,
        dataset,
        expected_role=DataRole.EXTERNAL,
        expected_id=registration.dataset_b_id,
        expected_hash=registration.dataset_b_hash,
    )
