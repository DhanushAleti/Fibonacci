"""Granularity / tick-discretization artefact audit (Repair Contract Part 6).

Coarse tick grids combined with three-point extrema force retracements into
rational fractions such as ``5/8 = 0.625 ~ 0.618``. This audit proves the pipeline
does not conflate that microstructure artefact with phi: a continuous fBm path is
discretized to progressively coarser grids and, at each resolution, the surrogate
test's phi false-positive rate is measured. If phi's FPR grows as the grid coarsens,
the effect is an artefact (fails). The surrogate reference preserves the tick
granularity, so a well-behaved test keeps phi's FPR <= alpha at every resolution.

**Flagged approximation.** ``fbm`` uses spectral synthesis (random-phase fGn with
spectral density ``|f|^(1-2H)``, cumulated) - an approximate fractional Brownian
motion adequate for generating tunable-``H`` continuous paths to discretize; it is
not an exact Cholesky/Davies-Harte fBm. Flagged for methodologist confirmation.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from phi.phase4.constants import ALPHA
from phi.phase4.repair.rational import FIVE_EIGHTHS, Q_PHI, RATIONAL_CONSTANTS
from phi.phase4.repair.zscore import standardized_null_score

Generator = np.random.Generator


def fbm(rng: Generator, n: int, *, hurst: float = 0.5) -> np.ndarray:
    """Approximate fractional Brownian motion (spectral synthesis), length ``n``."""
    freqs = np.fft.rfftfreq(n)[1:]
    amplitude = np.sqrt(freqs ** (1.0 - 2.0 * hurst))
    phases = rng.uniform(0.0, 2.0 * np.pi, size=amplitude.size)
    spectrum = np.concatenate([[0.0 + 0.0j], amplitude * np.exp(1j * phases)])
    fgn = np.fft.irfft(spectrum, n=n)
    std = float(fgn.std()) or 1.0
    return np.cumsum((fgn - fgn.mean()) / std)


def discretize(series: np.ndarray, *, n_levels: int) -> np.ndarray:
    """Round ``series`` onto a grid of ``n_levels`` equal ticks spanning its range."""
    x = np.asarray(series, dtype=np.float64)
    lo, hi = float(x.min()), float(x.max())
    if hi == lo:
        return x.copy()
    step = (hi - lo) / n_levels
    return lo + np.round((x - lo) / step) * step


def coarse_tick_fbm_null(
    rng: Generator, n: int, *, hurst: float = 0.5, n_levels: int = 50
) -> np.ndarray:
    """A tick-discretized fBm null DGP (no phi mechanism) at ``n_levels`` resolution."""
    return discretize(fbm(rng, n, hurst=hurst), n_levels=n_levels)


@dataclass(frozen=True)
class GranularityAudit:
    """Per-resolution phi false-positive rate under discretized-fBm nulls."""

    tick_levels: tuple[int, ...]
    phi_fpr_by_level: dict[int, float]
    max_phi_fpr: float
    passes: bool  # every resolution keeps phi FPR <= threshold


def granularity_audit(
    *,
    tick_levels: tuple[int, ...] = (1000, 100, 50, 10),
    hurst: float = 0.5,
    n: int = 400,
    n_series: int = 60,
    n_surrogates: int = 99,
    base_seed: int = 20260812,
    threshold: float = 0.07,
) -> GranularityAudit:
    """Estimate phi's surrogate-test FPR at each tick resolution (Part 6, Part 8 gate 4)."""
    constants = tuple(RATIONAL_CONSTANTS.values())
    fpr_by_level: dict[int, float] = {}
    for level in tick_levels:
        seeds = np.random.SeedSequence(base_seed + level).spawn(n_series)
        rejected = valid = 0
        for cs in seeds:
            gen = np.random.default_rng(cs)
            series = coarse_tick_fbm_null(gen, n, hurst=hurst, n_levels=level)
            boot_seed = int(cs.generate_state(1, dtype=np.uint32)[0])
            score = standardized_null_score(
                series, constants=constants, focal=Q_PHI, n_surrogates=n_surrogates, seed=boot_seed
            )
            if score is None:
                continue
            valid += 1
            if score.surrogate_p < ALPHA:
                rejected += 1
        fpr_by_level[level] = rejected / valid if valid else 0.0
    max_fpr = max(fpr_by_level.values()) if fpr_by_level else 0.0
    return GranularityAudit(
        tick_levels=tick_levels,
        phi_fpr_by_level=fpr_by_level,
        max_phi_fpr=max_fpr,
        passes=max_fpr <= threshold,
    )


def phi_vs_five_eighths_distance(r: np.ndarray) -> tuple[float, float]:
    """Mean ``|R - phi|`` and mean ``|R - 5/8|`` - are the two distributions distinguishable?"""
    r = np.asarray(r, dtype=np.float64)
    return float(np.mean(np.abs(r - Q_PHI))), float(np.mean(np.abs(r - FIVE_EIGHTHS)))
