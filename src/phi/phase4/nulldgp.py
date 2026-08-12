"""Null data-generating processes and a φ-biased positive control (spec §XLIII, §XLV).

Every process here contains **no φ mechanism** (except the explicitly-labelled
positive control). They exist to make the methodology try to produce false
positives: if the pipeline reports φ superiority under these known-null processes
more often than ``alpha``, the methodology is invalid (spec §XLIV — a hard gate).

All generators are deterministic given a :class:`numpy.random.Generator` (PCG64
via :func:`numpy.random.default_rng`), so a registered seed reproduces every
series exactly (spec §XXXV). Parameters shown are defaults; the confirmatory suite
must register the exact parameterisation (Arbiter Blocker: DGP parameters).
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

Generator = np.random.Generator
DGP = Callable[[Generator, int], np.ndarray]


def iid_gaussian(rng: Generator, n: int) -> np.ndarray:
    """DGP 1: IID Gaussian white noise (spec §XLIII)."""
    return rng.standard_normal(n)


def iid_heavy_tailed(rng: Generator, n: int, *, df: float = 3.0) -> np.ndarray:
    """DGP 2: IID Student-t innovations — robustness to non-Gaussianity (spec §XLIII)."""
    return rng.standard_t(df, size=n)


def random_walk(rng: Generator, n: int) -> np.ndarray:
    """DGP 3: Gaussian random walk — natural non-uniform retracement geometry (spec §XLIII)."""
    return np.cumsum(rng.standard_normal(n))


def ar1(rng: Generator, n: int, *, rho: float = 0.5) -> np.ndarray:
    """DGP 4: AR(1) with coefficient ``rho`` (spec §XLIII)."""
    x = np.empty(n, dtype=np.float64)
    eps = rng.standard_normal(n)
    x[0] = eps[0]
    for t in range(1, n):
        x[t] = rho * x[t - 1] + eps[t]
    return x


def heteroskedastic(rng: Generator, n: int) -> np.ndarray:
    """DGP 5: deterministic time-varying variance (spec §XLIII)."""
    sigma = 1.0 + np.linspace(0.0, 3.0, n)
    return rng.standard_normal(n) * sigma


def garch11(
    rng: Generator, n: int, *, omega: float = 0.1, alpha: float = 0.1, beta: float = 0.85
) -> np.ndarray:
    """DGP 6: GARCH(1,1) volatility clustering (spec §XLIII)."""
    x = np.empty(n, dtype=np.float64)
    sigma2 = omega / max(1.0 - alpha - beta, 1e-6)
    z = rng.standard_normal(n)
    for t in range(n):
        x[t] = np.sqrt(sigma2) * z[t]
        sigma2 = omega + alpha * x[t] ** 2 + beta * sigma2
    return x


def regime_switching(
    rng: Generator, n: int, *, p_switch: float = 0.02, sigma_lo: float = 0.5, sigma_hi: float = 3.0
) -> np.ndarray:
    """DGP 7: two-state (low/high variance) Markov regime switching (spec §XLIII)."""
    x = np.empty(n, dtype=np.float64)
    z = rng.standard_normal(n)
    switch = rng.random(n) < p_switch
    high = False
    for t in range(n):
        if switch[t]:
            high = not high
        x[t] = z[t] * (sigma_hi if high else sigma_lo)
    return x


def trend_plus_noise(rng: Generator, n: int, *, slope: float = 5.0) -> np.ndarray:
    """DGP 8: deterministic linear trend plus IID noise (spec §XLIII)."""
    return np.linspace(0.0, slope, n) + rng.standard_normal(n)


def seasonality(rng: Generator, n: int, *, period: float = 20.0, amp: float = 3.0) -> np.ndarray:
    """DGP 9: sinusoidal seasonality plus IID noise (spec §XLIII)."""
    t = np.arange(n, dtype=np.float64)
    return amp * np.sin(2.0 * np.pi * t / period) + rng.standard_normal(n)


def market_like(rng: Generator, n: int, *, rho: float = 0.3) -> np.ndarray:
    """DGP 10: AR(1) mean with GARCH(1,1) heavy-tailed shocks (spec §XLIII)."""
    vol = garch11(rng, n)
    x = np.empty(n, dtype=np.float64)
    x[0] = vol[0]
    for t in range(1, n):
        x[t] = rho * x[t - 1] + vol[t]
    return x


def coarse_tick(rng: Generator, n: int, *, rho: float = 0.5, tick: float = 0.25) -> np.ndarray:
    """Red-team null: AR(1) discretised to a coarse tick grid (spec §XLIII additional null).

    Rounding to a coarse grid forces retracements into rational fractions such as
    ``5/8 = 0.625 ≈ q_φ`` — a microstructure artefact, not a φ mechanism (red-team
    Attack: Tick Size Artifacts). The pipeline must not mistake it for φ.
    """
    return np.round(ar1(rng, n, rho=rho) / tick) * tick


#: The registered null-DGP suite (spec §XLIII). Names are stable identifiers.
NULL_DGPS: dict[str, DGP] = {
    "iid_gaussian": iid_gaussian,
    "iid_heavy_tailed": iid_heavy_tailed,
    "random_walk": random_walk,
    "ar1": ar1,
    "heteroskedastic": heteroskedastic,
    "garch11": garch11,
    "regime_switching": regime_switching,
    "trend_plus_noise": trend_plus_noise,
    "seasonality": seasonality,
    "market_like": market_like,
    "coarse_tick": coarse_tick,
}


def phi_biased_positive_control(
    rng: Generator, n: int, *, bias: float = 0.9, noise: float = 0.05
) -> np.ndarray:
    """Positive control with an **injected** φ preference (spec §XLV).

    Builds an alternating zig-zag whose each successive swing is ``q_φ`` times the
    previous one (with ``bias`` toward q_φ and small ``noise``), so retracements
    concentrate near ``q_φ``. Used ONLY to confirm the pipeline can detect its own
    target (power > 0); it is never real-world evidence.
    """
    q_phi = 1.0 / ((1.0 + 5.0**0.5) / 2.0)
    x = np.empty(n, dtype=np.float64)
    x[0] = 0.0
    swing = 1.0
    direction = 1.0
    for t in range(1, n):
        x[t] = x[t - 1] + direction * swing
        ratio = bias * q_phi + (1.0 - bias) * rng.uniform(0.2, 0.9) + noise * rng.standard_normal()
        swing = abs(swing * ratio)
        direction = -direction
    return x
