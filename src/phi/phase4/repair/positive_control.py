"""phi-Attractor GARCH positive control (Repair Contract Part 7).

The clean zig-zag positive control is REJECTED (topologically alien to the null
suite). This control instead builds a GARCH(1,1)-textured swing skeleton (so swing
magnitudes exhibit realistic volatility clustering and heavy tails) and, at a
randomly selected fraction ``inject_prob`` of excursions, forces the next swing
ratio to ``q_phi`` - i.e. injects a golden-ratio retracement into that excursion.
Per-bar noise keeps the extrema non-degenerate.

Signal strength (Part 7): ``inject_prob`` = probability an excursion receives the
phi-drift. Small = 0.05, Medium = 0.15, Large = 0.30.

**Flagged approximation.** The contract specifies an Ornstein-Uhlenbeck drift with
target ``X_e - phi*|X_e - X_a|`` superimposed on an AR(1)-GARCH(1,1) base. This
module injects the same phi retracement directly into the swing-ratio sequence of a
GARCH-magnitude skeleton, which realizes the same *effect* (phi-clustered
retracements at rate ``inject_prob`` over a heavy-tailed, vol-clustered base) with a
simpler, deterministic construction. The exact OU-on-GARCH realization is a
refinement for the methodologist to confirm before the confirmatory freeze. It is
used ONLY to verify pipeline power (Part 8 gate), never as real-world evidence.
"""

from __future__ import annotations

import numpy as np

from phi.phase4.repair.rational import Q_PHI

Generator = np.random.Generator


def _garch_magnitudes(
    rng: Generator, n: int, *, omega: float = 0.1, alpha: float = 0.1, beta: float = 0.85
) -> np.ndarray:
    """Absolute GARCH(1,1) innovations - swing magnitudes with volatility clustering."""
    mags = np.empty(n, dtype=np.float64)
    sigma2 = omega / max(1.0 - alpha - beta, 1e-6)
    z = rng.standard_normal(n)
    for t in range(n):
        val = np.sqrt(sigma2) * z[t]
        mags[t] = abs(val) + 1e-3
        sigma2 = omega + alpha * val**2 + beta * sigma2
    return mags


def phi_attractor_garch(
    rng: Generator, n: int, *, inject_prob: float = 0.15, seg_bars: int = 6, noise: float = 0.02
) -> np.ndarray:
    """GARCH-textured series with phi retracements injected into a fraction of excursions.

    Builds alternating swings whose magnitudes cluster (GARCH); for a fraction
    ``inject_prob`` of swings the magnitude is set to ``q_phi`` times the previous
    swing (a golden-ratio retracement), otherwise it follows the GARCH magnitude.
    Each swing is rendered as ``seg_bars`` points with additive noise.
    """
    n_swings = max(2, n // seg_bars)
    base_mags = _garch_magnitudes(rng, n_swings)
    inject = rng.random(n_swings) < inject_prob
    mags = base_mags.copy()
    for i in range(1, n_swings):
        if inject[i]:
            mags[i] = Q_PHI * mags[i - 1]
    values: list[float] = [0.0]
    direction = 1.0
    for i in range(n_swings):
        start = values[-1]
        for k in range(1, seg_bars + 1):
            frac = k / seg_bars
            point = start + direction * mags[i] * frac + noise * rng.standard_normal()
            values.append(point)
        direction = -direction
    return np.asarray(values[:n] if len(values) >= n else values, dtype=np.float64)
