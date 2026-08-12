"""Null-DGP false-positive calibration and simulation-based power (spec §XLI-§XLV).

Two mandatory pre-confirmatory validation harnesses:

* :func:`null_calibration` runs the full pipeline over the null-DGP suite and
  estimates the empirical rejection rate (false-positive rate). Under known-null
  processes it must be ``≈ alpha``; systematic over-rejection means the
  methodology is invalid (spec §XLIV — a **hard gate**). This is the honest
  "make it try to produce false positives" harness.
* :func:`estimate_power` runs the pipeline over the φ-biased positive control to
  confirm the method can detect its own target (spec §XLV, §XLII).

Both use independent PCG64 streams spawned from a registered base seed, so every
Monte-Carlo iteration is reproducible.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from phi.phase4.analysis import analyze_series
from phi.phase4.constants import ALPHA
from phi.phase4.nulldgp import DGP, NULL_DGPS, phi_biased_positive_control


@dataclass(frozen=True)
class CalibrationResult:
    """Empirical rejection rate of the pipeline under one DGP."""

    dgp_name: str
    n_series: int
    n_valid: int
    n_rejected: int
    rejection_rate: float
    rejection_se: float
    mean_delta_hat: float
    alpha: float

    def is_calibrated(self, *, tolerance_ses: float = 3.0) -> bool:
        """Whether the rejection rate is within ``tolerance_ses`` SEs above ``alpha``.

        A null DGP is calibrated when it does **not** reject materially more often
        than ``alpha`` (one-sided: over-rejection is the failure of interest).
        """
        return self.rejection_rate <= self.alpha + tolerance_ses * self.rejection_se


def estimate_rejection_rate(
    dgp: DGP,
    comparison_set: tuple[float, ...],
    *,
    n_series: int,
    series_length: int,
    replicates: int,
    base_seed: int,
    dgp_name: str = "dgp",
    alpha: float = ALPHA,
) -> CalibrationResult:
    """Fraction of ``n_series`` DGP realisations for which the pipeline rejects ``H0``.

    Each realisation uses an independent PCG64 stream for data generation and a
    separate integer stream for the bootstrap seed, both spawned from
    ``base_seed``. Series that yield too few eligible retracements to run inference
    are excluded from the denominator (counted as not-valid).
    """
    child_seeds = np.random.SeedSequence(base_seed).spawn(n_series)
    rejected = 0
    valid = 0
    delta_sum = 0.0
    for cs in child_seeds:
        gen_rng = np.random.default_rng(cs)
        series = dgp(gen_rng, series_length)
        boot_seed = int(cs.generate_state(1, dtype=np.uint32)[0])
        analysis = analyze_series(series, comparison_set, replicates=replicates, seed=boot_seed)
        if analysis.bootstrap is None or analysis.delta_hat is None:
            continue
        valid += 1
        delta_sum += analysis.delta_hat
        if analysis.bootstrap.p_value < alpha:
            rejected += 1
    rate = rejected / valid if valid else 0.0
    se = math.sqrt(rate * (1.0 - rate) / valid) if valid else 0.0
    return CalibrationResult(
        dgp_name=dgp_name,
        n_series=n_series,
        n_valid=valid,
        n_rejected=rejected,
        rejection_rate=rate,
        rejection_se=se,
        mean_delta_hat=(delta_sum / valid if valid else 0.0),
        alpha=alpha,
    )


def null_calibration(
    comparison_set: tuple[float, ...],
    *,
    n_series: int,
    series_length: int,
    replicates: int,
    base_seed: int,
    alpha: float = ALPHA,
) -> dict[str, CalibrationResult]:
    """Estimate the false-positive rate for every null DGP (spec §XLIV hard gate)."""
    results: dict[str, CalibrationResult] = {}
    for i, (name, dgp) in enumerate(NULL_DGPS.items()):
        results[name] = estimate_rejection_rate(
            dgp,
            comparison_set,
            n_series=n_series,
            series_length=series_length,
            replicates=replicates,
            base_seed=base_seed + i,
            dgp_name=name,
            alpha=alpha,
        )
    return results


def all_nulls_calibrated(
    results: dict[str, CalibrationResult], *, tolerance_ses: float = 3.0
) -> bool:
    """Whether every null DGP is calibrated — the ``null_fpr_calibrated`` gate value."""
    return all(r.is_calibrated(tolerance_ses=tolerance_ses) for r in results.values())


def estimate_power(
    comparison_set: tuple[float, ...],
    *,
    n_series: int,
    series_length: int,
    replicates: int,
    base_seed: int,
    alpha: float = ALPHA,
) -> CalibrationResult:
    """Rejection rate under the φ-biased positive control = empirical power (spec §XLV).

    The mapping from injection strength to the effect size ``δ_min`` is itself a
    pre-registration/calibration decision; this reports power at the control's
    default injection and must be re-run at the registered ``δ_min`` before a
    confirmatory power claim.
    """
    return estimate_rejection_rate(
        phi_biased_positive_control,
        comparison_set,
        n_series=n_series,
        series_length=series_length,
        replicates=replicates,
        base_seed=base_seed,
        dgp_name="phi_biased_positive_control",
        alpha=alpha,
    )
