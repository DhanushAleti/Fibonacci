"""PHI Phase 4 — the frozen confirmatory methodology (GO-with-conditions).

This package implements the Chief Scientific Methodologist's Phase-4
Specification exactly: the deterministic three-point extrema anchor, per-excursion
retracements, the continuous φ-distance, the Δ_φ vs matched-constants estimand,
stationary-bootstrap dependence-aware inference, Holm multiplicity, the null-DGP
false-positive calibration and power harnesses, strict discovery/confirmation/
replication separation, and a **fail-closed** confirmatory gate.

Scientific-claim boundary. The methodology is frozen; **running** the confirmatory
experiment is NOT authorized (Final Arbiter NO-GO) until the numerical
pre-registration is complete and the validation gates pass. No φ claim is made or
implied here. See ``docs/05-mathematics/phi-phase4-scientific-contract.md``.
"""

from __future__ import annotations

from phi.phase4.analysis import SeriesAnalysis, analyze_series
from phi.phase4.calibration import (
    CalibrationResult,
    all_nulls_calibrated,
    estimate_power,
    null_calibration,
)
from phi.phase4.constants import (
    ALPHA,
    BOOTSTRAP_REPLICATES,
    CONFIDENCE_LEVEL,
    POWER_THRESHOLD,
    Q_PHI,
)
from phi.phase4.datasets import DataRole, DataSeparationError, RegisteredDataset
from phi.phase4.estimand import delta_phi, grid_landscape, paired_z, phi_rank
from phi.phase4.extrema import (
    Excursion,
    Extremum,
    ExtremumKind,
    build_excursions,
    three_point_extrema,
)
from phi.phase4.inference import BootstrapResult, bootstrap_delta_phi, politis_white_block_length
from phi.phase4.multiplicity import HolmResult, holm_step_down
from phi.phase4.pipeline import (
    ConfirmatoryNotAuthorizedError,
    run_confirmatory,
    run_exploratory,
    run_replication,
)
from phi.phase4.registration import (
    ComparisonSet,
    ComparisonSetError,
    Phase4PreRegistration,
    validate_comparison_set,
)
from phi.phase4.retracement import RetracementObservation, RetracementResult, excursion_retracements
from phi.phase4.verdict import Outcome, classify_outcome

__all__ = [
    "ALPHA",
    "BOOTSTRAP_REPLICATES",
    "CONFIDENCE_LEVEL",
    "POWER_THRESHOLD",
    "Q_PHI",
    "BootstrapResult",
    "CalibrationResult",
    "ComparisonSet",
    "ComparisonSetError",
    "ConfirmatoryNotAuthorizedError",
    "DataRole",
    "DataSeparationError",
    "Excursion",
    "Extremum",
    "ExtremumKind",
    "HolmResult",
    "Outcome",
    "Phase4PreRegistration",
    "RegisteredDataset",
    "RetracementObservation",
    "RetracementResult",
    "SeriesAnalysis",
    "all_nulls_calibrated",
    "analyze_series",
    "bootstrap_delta_phi",
    "build_excursions",
    "classify_outcome",
    "delta_phi",
    "estimate_power",
    "excursion_retracements",
    "grid_landscape",
    "holm_step_down",
    "null_calibration",
    "paired_z",
    "phi_rank",
    "politis_white_block_length",
    "run_confirmatory",
    "run_exploratory",
    "run_replication",
    "three_point_extrema",
    "validate_comparison_set",
]
