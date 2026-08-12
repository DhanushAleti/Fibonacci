"""Surrogate null ensemble (Repair Contract Part 4).

The repaired primary test standardizes the observed advantage against surrogates
of the **same series** that preserve its topology (geometry, local dependence,
granularity, volatility clustering) while destroying any phi-specific alignment.
Under a null process the observed series is exchangeable with its surrogates, so
the surrogate reference neutralizes the geometric/convexity bias that made the
original ``Delta_phi > 0`` test reject at FPR = 1.0.

Hierarchy (Part 4):
1. **Block-permutation** (PRIMARY) - preserves local non-linear dependence,
   tick-size granularity, and volatility clustering by keeping intact blocks and
   only reordering them.
2. **GARCH(1,1) parametric** (SECONDARY) - preserves volatility clustering and
   heavy tails; tests whether the effect is merely a variance artefact.
3. **IAAFT** (TERTIARY) - preserves the linear autocorrelation (power spectrum)
   and the marginal distribution only.

These are the *only* surrogate families; the primary confirmatory test uses
block-permutation, with GARCH and IAAFT as the mandated secondary/tertiary audit.
No surrogate may be chosen because it yields a better FPR (Repair Contract:
"do not select a surrogate because it gives better FPR").
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from phi.phase4.inference import politis_white_block_length

Generator = np.random.Generator
#: All surrogate generators share the signature ``(series, rng, *, block_length=None)``
#: so callers can invoke any family uniformly; families that do not use a block
#: length accept and ignore it.
Surrogate = Callable[..., np.ndarray]


def block_length_for(series: np.ndarray) -> float:
    """Automatic block length (Politis-White) from the increment dependence."""
    x = np.asarray(series, dtype=np.float64)
    if x.size < 3:
        return 1.0
    return politis_white_block_length(np.diff(x))


def block_permutation_surrogate(
    series: np.ndarray, rng: Generator, *, block_length: float | None = None
) -> np.ndarray:
    """PRIMARY surrogate: circular block permutation of the series values (Part 4).

    A random circular rotation varies the block phase; the series is then split
    into consecutive length-``L`` blocks whose order is permuted. The exact
    marginal distribution and all within-block local structure (granularity,
    volatility clusters) are preserved; global ordering is destroyed.
    """
    x = np.asarray(series, dtype=np.float64)
    n = x.size
    if n < 2:
        return x.copy()
    length = block_length_for(x) if block_length is None else block_length
    step = max(1, min(round(length), n))
    rotated = np.roll(x, int(rng.integers(n)))
    blocks = [rotated[s : s + step] for s in range(0, n, step)]
    order = rng.permutation(len(blocks))
    return np.concatenate([blocks[i] for i in order])


def garch_surrogate(
    series: np.ndarray,
    rng: Generator,
    *,
    alpha: float = 0.1,
    beta: float = 0.85,
    block_length: float | None = None,  # uniform signature; unused by this family
) -> np.ndarray:
    """SECONDARY surrogate: GARCH(1,1) increments matched to the series' variance.

    Preserves volatility clustering and heavy tails (approximately), on the
    increment scale, then reconstructs a level series from the original start.
    ``omega`` is set from the sample increment variance so the unconditional
    variance matches; ``alpha, beta`` are fixed clustering parameters.
    """
    x = np.asarray(series, dtype=np.float64)
    n = x.size
    if n < 3:
        return x.copy()
    incr = np.diff(x)
    target_var = float(np.var(incr)) or 1.0
    omega = target_var * max(1.0 - alpha - beta, 1e-3)
    sim = np.empty(n - 1, dtype=np.float64)
    sigma2 = target_var
    z = rng.standard_normal(n - 1)
    for t in range(n - 1):
        sim[t] = np.sqrt(sigma2) * z[t]
        sigma2 = omega + alpha * sim[t] ** 2 + beta * sigma2
    out = np.empty(n, dtype=np.float64)
    out[0] = x[0]
    out[1:] = x[0] + np.cumsum(sim)
    return out


def iaaft_surrogate(
    series: np.ndarray,
    rng: Generator,
    *,
    iterations: int = 100,
    block_length: float | None = None,  # uniform signature; unused by this family
) -> np.ndarray:
    """TERTIARY surrogate: iterative amplitude-adjusted Fourier transform (Part 4).

    Preserves the power spectrum (linear autocorrelation) and the exact marginal
    distribution, destroying non-linear structure. Standard IAAFT iteration.
    """
    x = np.asarray(series, dtype=np.float64)
    n = x.size
    if n < 4:
        return x.copy()
    sorted_values = np.sort(x)
    target_amplitude = np.abs(np.fft.rfft(x))
    surrogate = rng.permutation(x)
    for _ in range(iterations):
        spectrum = np.fft.rfft(surrogate)
        spectrum = target_amplitude * np.exp(1j * np.angle(spectrum))
        surrogate = np.fft.irfft(spectrum, n=n)
        ranks = np.argsort(np.argsort(surrogate))
        surrogate = sorted_values[ranks]
    return surrogate


#: The mandated surrogate hierarchy (Part 4). ``block_permutation`` is primary.
SURROGATES: dict[str, Surrogate] = {
    "block_permutation": block_permutation_surrogate,
    "garch": garch_surrogate,
    "iaaft": iaaft_surrogate,
}
PRIMARY_SURROGATE: str = "block_permutation"
