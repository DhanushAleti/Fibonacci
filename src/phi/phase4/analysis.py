"""Core per-series analysis path: series -> extrema -> excursions -> R -> Z -> Δ̂_φ.

This is the **science-neutral compute core** shared by the confirmatory pipeline
(:mod:`phi.phase4.pipeline`, which gates it behind the fail-closed
pre-registration) and by the validation harnesses
(:mod:`phi.phase4.calibration`). It runs the frozen methodology on a single
ordered value series and returns the estimate, the bootstrap inference, and a
fully-reconciled exclusion ledger. It makes no confirmatory claim and does not
check authorization — callers do.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from phi.experiment.exclusions import ExclusionAccountant, ExclusionReason, ExclusionSummary
from phi.phase4.constants import Q_PHI
from phi.phase4.estimand import paired_z
from phi.phase4.extrema import build_excursions, three_point_extrema
from phi.phase4.inference import BootstrapResult, bootstrap_delta_phi
from phi.phase4.retracement import excursion_retracements

#: Minimum eligible retracements for the stationary bootstrap to run.
MIN_ELIGIBLE: int = 2


@dataclass(frozen=True)
class SeriesAnalysis:
    """Frozen result of running the Phase-4 methodology on one series."""

    n_excursions: int
    n_eligible: int
    n_overshoot: int
    exclusions: ExclusionSummary
    delta_hat: float | None
    bootstrap: BootstrapResult | None

    @property
    def rejected_h0(self) -> bool:
        """One-sided reject of ``H0: Δ_φ ≤ 0`` at the bootstrap p-value's face value.

        ``False`` when inference did not run (too few eligible retracements). This
        is the raw per-test decision the calibration harness counts; the
        confirmatory verdict additionally requires effect size, CI, multiplicity,
        and the validation gates (spec §LIV).
        """
        return self.bootstrap is not None and self.bootstrap.p_value < 0.05


def analyze_series(
    values: Sequence[float] | np.ndarray,
    comparison_set: Sequence[float],
    *,
    replicates: int,
    seed: int,
    confidence_level: float = 0.95,
    q_phi: float = Q_PHI,
) -> SeriesAnalysis:
    """Run the frozen Phase-4 pipeline on one ordered series.

    Excursions with no successor (incomplete), zero denominator, or ``R > 1``
    (overshoot / excursion invalidation, spec §XXII) are excluded from the primary
    ``R ∈ [0,1]`` sample and logged — never silently dropped. Returns
    ``bootstrap=None`` (and ``delta_hat=None``) when fewer than
    :data:`MIN_ELIGIBLE` eligible retracements remain.
    """
    series = np.asarray(values, dtype=np.float64).tolist()
    extrema = three_point_extrema(series)
    excursions = build_excursions(extrema)
    result = excursion_retracements(excursions)
    eligible = [o.r for o in result.eligible]
    overshoots = result.overshoots

    accountant = ExclusionAccountant(raw_count=result.n_excursions)
    accountant.record(ExclusionReason.INSUFFICIENT_HISTORY, result.n_incomplete)
    accountant.record(ExclusionReason.ZERO_EXCURSION, result.n_zero_denominator)
    accountant.record(ExclusionReason.DOMAIN_ERROR, len(overshoots))  # R>1 overshoot (§XXII)
    exclusions = accountant.summary()

    if len(eligible) < MIN_ELIGIBLE:
        return SeriesAnalysis(
            n_excursions=result.n_excursions,
            n_eligible=len(eligible),
            n_overshoot=len(overshoots),
            exclusions=exclusions,
            delta_hat=None,
            bootstrap=None,
        )
    z = paired_z(eligible, comparison_set, q_phi=q_phi)
    boot = bootstrap_delta_phi(
        z, replicates=replicates, seed=seed, confidence_level=confidence_level
    )
    return SeriesAnalysis(
        n_excursions=result.n_excursions,
        n_eligible=len(eligible),
        n_overshoot=len(overshoots),
        exclusions=exclusions,
        delta_hat=boot.delta_hat,
        bootstrap=boot,
    )
