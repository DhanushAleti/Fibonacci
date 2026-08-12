"""Standardized Null Score Z_phi - the repaired primary estimand (Repair Contract Part 2).

The original ``Delta_phi > 0`` test is **permanently forbidden** as confirmatory
evidence (it is mechanically positive under geometric bounds). The repaired
primary estimand standardizes the observed advantage against a surrogate ensemble
of the same series:

    Delta_obs = mean_c E|R - q_c| - E|R - q_phi|            (advantage over controls)
    Z_phi     = (Delta_obs - mu_null) / sigma_null          (mu, sigma from surrogates)

Under the null, ``E[Z_phi] = 0`` because the surrogates preserve the geometry that
drives ``Delta`` while destroying any phi structure. The confirmatory p-value is the
surrogate-rank p-value ``p = (1 + #{Delta^(s) >= Delta_obs}) / (S + 1)``.

This module computes the estimand and per-constant surrogate tests. It makes no
confirmatory claim on its own; the validation gate (:mod:`phi.phase4.repair.validation`)
and the fail-closed registration decide authorization.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from phi.phase4.extrema import build_excursions, three_point_extrema
from phi.phase4.repair.rational import Q_PHI
from phi.phase4.repair.surrogates import Surrogate, block_length_for, block_permutation_surrogate
from phi.phase4.retracement import excursion_retracements

MIN_ELIGIBLE: int = 2
MIN_SURROGATES: int = 10


def eligible_retracements(series: Sequence[float] | np.ndarray) -> np.ndarray:
    """Eligible (R in [0,1]) per-excursion retracements of a raw series."""
    values = np.asarray(series, dtype=np.float64).tolist()
    result = excursion_retracements(build_excursions(three_point_extrema(values)))
    return np.array([o.r for o in result.eligible], dtype=np.float64)


def phi_advantage(r: np.ndarray, *, focal: float = Q_PHI, constants: Sequence[float]) -> float:
    """``mean_c E|R - c| - E|R - focal|`` - focal's mean proximity advantage over ``constants``."""
    if r.size == 0:
        return float("nan")
    mean_control = float(np.mean([np.mean(np.abs(r - c)) for c in constants]))
    return mean_control - float(np.mean(np.abs(r - focal)))


@dataclass(frozen=True)
class RepairScore:
    """Standardized null score for one series (Part 2)."""

    delta_obs: float
    mu_null: float
    sigma_null: float
    z_phi: float
    surrogate_p: float
    n_surrogates: int
    n_eligible: int

    @property
    def is_valid(self) -> bool:
        return self.n_eligible >= MIN_ELIGIBLE and self.n_surrogates >= MIN_SURROGATES


def standardized_null_score(
    series: Sequence[float] | np.ndarray,
    *,
    constants: Sequence[float],
    focal: float = Q_PHI,
    n_surrogates: int,
    seed: int,
    surrogate_fn: Surrogate = block_permutation_surrogate,
) -> RepairScore | None:
    """Compute ``Z_phi`` and the surrogate-rank p-value for ``series`` (Part 2).

    Returns ``None`` when there are too few eligible retracements or usable
    surrogates to standardize against.
    """
    x = np.asarray(series, dtype=np.float64)
    r_obs = eligible_retracements(x)
    if r_obs.size < MIN_ELIGIBLE:
        return None
    delta_obs = phi_advantage(r_obs, focal=focal, constants=constants)
    length = block_length_for(x)
    rng = np.random.default_rng(seed)
    surrogate_deltas: list[float] = []
    for _ in range(n_surrogates):
        surrogate = surrogate_fn(x, rng, block_length=length)
        r_s = eligible_retracements(surrogate)
        if r_s.size >= MIN_ELIGIBLE:
            surrogate_deltas.append(phi_advantage(r_s, focal=focal, constants=constants))
    if len(surrogate_deltas) < MIN_SURROGATES:
        return None
    deltas = np.asarray(surrogate_deltas, dtype=np.float64)
    mu = float(deltas.mean())
    sigma = float(deltas.std(ddof=1))
    z_phi = (delta_obs - mu) / sigma if sigma > 0.0 else 0.0
    exceed = int(np.count_nonzero(deltas >= delta_obs))
    surrogate_p = (1.0 + exceed) / (len(deltas) + 1.0)
    return RepairScore(
        delta_obs=delta_obs,
        mu_null=mu,
        sigma_null=sigma,
        z_phi=z_phi,
        surrogate_p=surrogate_p,
        n_surrogates=len(deltas),
        n_eligible=int(r_obs.size),
    )
