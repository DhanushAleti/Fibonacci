"""Dependence-aware inference: stationary bootstrap over excursion blocks (spec §XXX-§XXXVII).

Primary inference is the **stationary bootstrap** (Politis & Romano, 1994) applied
to the per-excursion advantage series ``Z_i`` (:mod:`phi.phase4.estimand`), with an
**automatic** block length (Politis & White, 2004) selected purely from the
series' dependence structure — never tuned toward significance (spec §XXXIII). IID
inference is prohibited (spec §XXX).

Outputs: the point estimate ``Δ̂_φ``, a two-sided 95% percentile confidence
interval, and a one-sided bootstrap p-value for ``H0: Δ_φ ≤ 0`` vs ``H1: Δ_φ > 0``
(spec §XXXVII), computed from the null-recentred bootstrap distribution. The
Monte-Carlo standard error of the p-value is reported so a near-boundary result
with material simulation error is classed *inconclusive*, not rounded into
significance (spec §XXXIV).

The CI/test method itself must be validated for coverage/type-I error on synthetic
DGPs before any confirmatory claim (spec §XXXVI; :mod:`phi.phase4.calibration`);
this module provides the estimator, calibration judges it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


def _autocovariance(x: np.ndarray, max_lag: int) -> np.ndarray:
    """Biased sample autocovariances ``R(0..max_lag)`` (divisor ``n``)."""
    n = x.size
    xc = x - x.mean()
    acov = np.empty(max_lag + 1, dtype=np.float64)
    for k in range(max_lag + 1):
        acov[k] = float(np.dot(xc[: n - k], xc[k:]) / n)
    return acov


def _flat_top_lambda(t: np.ndarray) -> np.ndarray:
    """Politis-White flat-top lag window: 1 for |t|≤1/2, taper to 0 by |t|=1."""
    a = np.abs(t)
    out = np.zeros_like(a)
    out[a <= 0.5] = 1.0
    mid = (a > 0.5) & (a <= 1.0)
    out[mid] = 2.0 * (1.0 - a[mid])
    return out


def politis_white_block_length(x: np.ndarray) -> float:
    """Automatic optimal stationary-bootstrap block length (Politis & White, 2004).

    Selected solely from the series' autocorrelation structure: stronger positive
    dependence ⇒ a longer block. Returns a value clamped to ``[1, b_max]`` with
    ``b_max = min(3√n, n/3)``. For (near-)independent series the estimate collapses
    to ``1``. Never a function of the test outcome (spec §XXXIII).
    """
    x = np.asarray(x, dtype=np.float64)
    n = x.size
    if n < 4:
        return 1.0
    kn = max(5, math.ceil(math.sqrt(math.log10(n))))
    m_max = math.ceil(math.sqrt(n)) + kn
    m_max = min(m_max, n - 1)
    acov = _autocovariance(x, m_max)
    if acov[0] <= 0.0:
        return 1.0
    rho = acov / acov[0]
    crit = 2.0 * math.sqrt(math.log10(n) / n)
    # m_hat: smallest lag after which |rho| stays below the significance band for kn lags.
    m_hat = m_max
    for m in range(1, m_max - kn + 1):
        if np.all(np.abs(rho[m + 1 : m + 1 + kn]) < crit):
            m_hat = m
            break
    big_m = min(2 * m_hat, m_max)
    lags = np.arange(-big_m, big_m + 1)
    lam = _flat_top_lambda(lags / big_m)
    r_full = acov[np.abs(lags)]  # R(-k) = R(k)
    g_hat = float(np.sum(lam * np.abs(lags) * r_full))
    d_hat = float(np.sum(lam * r_full))  # ≈ spectral density at 0 (unnormalised)
    if d_hat == 0.0:
        return 1.0
    b_opt = (2.0 * g_hat**2 / (2.0 * d_hat**2)) ** (1.0 / 3.0) * n ** (1.0 / 3.0)
    b_max = min(3.0 * math.sqrt(n), n / 3.0)
    if not math.isfinite(b_opt) or b_opt < 1.0:
        return 1.0
    return float(min(b_opt, b_max))


def stationary_bootstrap_indices(
    n: int, *, expected_block_length: float, rng: np.random.Generator
) -> np.ndarray:
    """Politis-Romano stationary-bootstrap resample indices of length ``n``.

    Geometric block lengths (mean ``expected_block_length``) with wrap-around, so
    the resample preserves short-range dependence and is itself stationary.
    """
    if n <= 0:
        return np.empty(0, dtype=np.int64)
    p = 1.0 / max(expected_block_length, 1.0)
    idx = np.empty(n, dtype=np.int64)
    idx[0] = int(rng.integers(n))
    restarts = rng.random(n) < p
    for t in range(1, n):
        idx[t] = int(rng.integers(n)) if restarts[t] else (idx[t - 1] + 1) % n
    return idx


@dataclass(frozen=True)
class BootstrapResult:
    """Primary inference output for Δ̂_φ (spec §XXXVI-§XXXVII)."""

    delta_hat: float
    ci_low: float
    ci_high: float
    p_value: float
    p_value_mc_se: float
    block_length: float
    replicates: int
    seed: int
    n: int

    @property
    def ci_excludes_zero(self) -> bool:
        return self.ci_low > 0.0 or self.ci_high < 0.0


def bootstrap_delta_phi(
    z_values: np.ndarray,
    *,
    replicates: int,
    seed: int,
    block_length: float | None = None,
    confidence_level: float = 0.95,
) -> BootstrapResult:
    """Stationary-bootstrap inference on the per-excursion advantage series ``Z``.

    ``Δ̂_φ = mean(Z)``. The block length defaults to
    :func:`politis_white_block_length` when not supplied. The p-value tests
    ``H0: Δ_φ ≤ 0`` from the null-recentred bootstrap distribution
    (``p = (1 + #{Δ̂*_b - Δ̂ ≥ Δ̂}) / (B+1)``) and carries its Monte-Carlo SE.
    """
    z = np.asarray(z_values, dtype=np.float64)
    n = z.size
    if n < 2:
        raise ValueError(f"stationary bootstrap needs >= 2 observations; got {n}")
    if block_length is None:
        block_length = politis_white_block_length(z)
    rng = np.random.default_rng(seed)
    delta_hat = float(z.mean())
    boot = np.empty(replicates, dtype=np.float64)
    for b in range(replicates):
        idx = stationary_bootstrap_indices(n, expected_block_length=block_length, rng=rng)
        boot[b] = float(z[idx].mean())
    tail = (1.0 - confidence_level) / 2.0
    ci_low = float(np.quantile(boot, tail))
    ci_high = float(np.quantile(boot, 1.0 - tail))
    # One-sided null-recentred p-value for H1: Δ_φ > 0 (spec §XXXVII).
    exceed = int(np.count_nonzero((boot - delta_hat) >= delta_hat))
    p_value = (1.0 + exceed) / (replicates + 1.0)
    p_value_mc_se = math.sqrt(p_value * (1.0 - p_value) / replicates)
    return BootstrapResult(
        delta_hat=delta_hat,
        ci_low=ci_low,
        ci_high=ci_high,
        p_value=p_value,
        p_value_mc_se=p_value_mc_se,
        block_length=float(block_length),
        replicates=replicates,
        seed=seed,
        n=n,
    )
