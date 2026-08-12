"""Repair validation harness and the five-part acceptance gate (Repair Contract Part 8).

Estimates, on synthetic data only, whether the repaired surrogate-standardized test
is null-calibrated and powered. The full acceptance gate is:

1. Aggregate FPR <= 0.05 across the whole null suite.
2. Per-DGP FPR <= 0.07 (a single failing DGP blocks the study).
3. Positive-control power >= 0.80 on the Medium (inject_prob = 0.15) control.
4. Granularity rejection: phi FPR <= 0.07 at every tick resolution.
5. Constant-sweep symmetry: FPR targeting q = 0.382 and 0.500 is indistinguishable
   from q = 0.618 (proves the Z-standardization neutralizes geometric bias).

**Absolute rule (Repair Contract):** these harnesses report whether PHI passes; they
are never tuned to make it pass. The 13 null DGPs are immutable.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from phi.phase4.constants import ALPHA
from phi.phase4.nulldgp import NULL_DGPS, iid_gaussian
from phi.phase4.repair.granularity import GranularityAudit, granularity_audit
from phi.phase4.repair.positive_control import phi_attractor_garch
from phi.phase4.repair.rational import Q_PHI, RATIONAL_CONSTANTS
from phi.phase4.repair.zscore import standardized_null_score

Generator = np.random.Generator
DGP = Callable[[Generator, int], np.ndarray]

_RATIONALS = tuple(RATIONAL_CONSTANTS.values())


def _ar_p(rng: Generator, n: int, *, coeffs: tuple[float, ...] = (0.5, 0.3)) -> np.ndarray:
    x = np.zeros(n, dtype=np.float64)
    eps = rng.standard_normal(n)
    for t in range(n):
        val = eps[t]
        for j, a in enumerate(coeffs, start=1):
            if t - j >= 0:
                val += a * x[t - j]
        x[t] = val
    return x


def _autocorr_heavy(rng: Generator, n: int, *, rho: float = 0.6, df: float = 4.0) -> np.ndarray:
    x = np.empty(n, dtype=np.float64)
    eps = rng.standard_t(df, size=n)
    x[0] = eps[0]
    for t in range(1, n):
        x[t] = rho * x[t - 1] + eps[t]
    return x


#: The immutable 13-DGP repair null suite (original 11 + AR(p) + autocorr heavy-tailed).
REPAIR_NULL_SUITE: dict[str, DGP] = {**NULL_DGPS, "ar_p": _ar_p, "autocorr_heavy": _autocorr_heavy}


def surrogate_fpr(
    dgp: DGP,
    *,
    focal: float = Q_PHI,
    constants: tuple[float, ...] = _RATIONALS,
    n_series: int,
    series_length: int,
    n_surrogates: int,
    base_seed: int,
    alpha: float = ALPHA,
) -> tuple[float, int]:
    """Surrogate-test rejection rate (FPR) of ``dgp`` and the valid-series count."""
    seeds = np.random.SeedSequence(base_seed).spawn(n_series)
    rejected = valid = 0
    for cs in seeds:
        gen = np.random.default_rng(cs)
        series = dgp(gen, series_length)
        boot_seed = int(cs.generate_state(1, dtype=np.uint32)[0])
        score = standardized_null_score(
            series, constants=constants, focal=focal, n_surrogates=n_surrogates, seed=boot_seed
        )
        if score is None:
            continue
        valid += 1
        if score.surrogate_p < alpha:
            rejected += 1
    return (rejected / valid if valid else 0.0, valid)


def null_suite_fpr(
    *, n_series: int, series_length: int, n_surrogates: int, base_seed: int
) -> dict[str, float]:
    """Per-DGP surrogate FPR across the immutable 13-DGP null suite."""
    out: dict[str, float] = {}
    for i, (name, dgp) in enumerate(REPAIR_NULL_SUITE.items()):
        rate, _ = surrogate_fpr(
            dgp,
            n_series=n_series,
            series_length=series_length,
            n_surrogates=n_surrogates,
            base_seed=base_seed + i,
        )
        out[name] = rate
    return out


def positive_control_power(
    *,
    inject_prob: float,
    n_series: int,
    series_length: int,
    n_surrogates: int,
    base_seed: int,
    alpha: float = ALPHA,
) -> float:
    """Rejection rate under the phi-attractor GARCH control = empirical power (Part 8 gate 3)."""

    def dgp(rng: Generator, n: int) -> np.ndarray:
        return phi_attractor_garch(rng, n, inject_prob=inject_prob)

    rate, _ = surrogate_fpr(
        dgp,
        n_series=n_series,
        series_length=series_length,
        n_surrogates=n_surrogates,
        base_seed=base_seed,
    )
    return rate


def constant_sweep_symmetry(
    *,
    n_series: int,
    series_length: int,
    n_surrogates: int,
    base_seed: int,
    focals: tuple[float, ...] = (0.382, 0.5, Q_PHI),
    tolerance: float = 0.05,
) -> tuple[dict[float, float], bool]:
    """FPR targeting several focal constants on an IID-Gaussian null (Part 8 gate 5).

    Symmetric if every focal's FPR is within ``tolerance`` of phi's - proving the
    Z-standardization neutralizes geometric baseline bias (no focal is preferred).
    """

    fpr_by_focal: dict[float, float] = {}
    for i, focal in enumerate(focals):
        # Controls symmetric about each focal (delta 0.02), keeping the comparison fair.
        controls = tuple(focal + s * 0.02 for s in (-2, -1, 1, 2))
        rate, _ = surrogate_fpr(
            iid_gaussian,
            focal=focal,
            constants=controls,
            n_series=n_series,
            series_length=series_length,
            n_surrogates=n_surrogates,
            base_seed=base_seed + i,
        )
        fpr_by_focal[focal] = rate
    phi_fpr = fpr_by_focal[Q_PHI]
    symmetric = all(abs(v - phi_fpr) <= tolerance for v in fpr_by_focal.values())
    return fpr_by_focal, symmetric


@dataclass(frozen=True)
class RepairValidation:
    """Result of the five-part repair acceptance gate."""

    per_dgp_fpr: dict[str, float]
    aggregate_fpr: float
    max_per_dgp_fpr: float
    positive_control_power_medium: float
    granularity: GranularityAudit
    constant_sweep_fpr: dict[float, float]
    constant_sweep_symmetric: bool
    aggregate_fpr_gate: bool
    per_dgp_gate: bool
    power_gate: bool
    granularity_gate: bool
    symmetry_gate: bool

    @property
    def passes(self) -> bool:
        return (
            self.aggregate_fpr_gate
            and self.per_dgp_gate
            and self.power_gate
            and self.granularity_gate
            and self.symmetry_gate
        )


def run_repair_validation(
    *,
    n_series: int = 120,
    series_length: int = 400,
    n_surrogates: int = 99,
    base_seed: int = 20260812,
    alpha: float = ALPHA,
) -> RepairValidation:
    """Run the full five-part gate at the given (reduced-by-default) scale."""
    per_dgp = null_suite_fpr(
        n_series=n_series,
        series_length=series_length,
        n_surrogates=n_surrogates,
        base_seed=base_seed,
    )
    aggregate = float(np.mean(list(per_dgp.values()))) if per_dgp else 0.0
    max_dgp = max(per_dgp.values()) if per_dgp else 0.0
    power = positive_control_power(
        inject_prob=0.15,
        n_series=n_series,
        series_length=series_length,
        n_surrogates=n_surrogates,
        base_seed=base_seed + 100,
    )
    gran = granularity_audit(
        n=series_length,
        n_series=max(40, n_series // 2),
        n_surrogates=n_surrogates,
        base_seed=base_seed + 200,
    )
    sweep, symmetric = constant_sweep_symmetry(
        n_series=n_series,
        series_length=series_length,
        n_surrogates=n_surrogates,
        base_seed=base_seed + 300,
    )
    return RepairValidation(
        per_dgp_fpr=per_dgp,
        aggregate_fpr=aggregate,
        max_per_dgp_fpr=max_dgp,
        positive_control_power_medium=power,
        granularity=gran,
        constant_sweep_fpr=sweep,
        constant_sweep_symmetric=symmetric,
        aggregate_fpr_gate=aggregate <= alpha,
        per_dgp_gate=max_dgp <= 0.07,
        power_gate=power >= 0.80,
        granularity_gate=gran.passes,
        symmetry_gate=symmetric,
    )
