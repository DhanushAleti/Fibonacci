"""Primary estimand Δ_φ and secondary landscape statistics (spec §XV-§XIX, §XXVIII).

Primary (spec §XIX, §XXVIII), a **paired, excursion-level** comparison of the
continuous distance ``D(R, q) = |R - q|``:

    Z_i(q) = |R_i - q| - |R_i - q_φ|                       (per control q, per excursion)
    Z_i    = (1/K) Σ_{q∈C} Z_i(q)                          (mean over the control set)
    Δ̂_φ    = (1/N) Σ_i Z_i                                 (mean over excursions)

``Δ̂_φ > 0`` favours φ (φ is, on the same excursions, closer on average than the
matched controls). The pairing removes excursion-level variation, so the test
asks "on the same realisations, is φ closer?" not "does φ look good in isolation."

Secondary (spec §XXIII, §XXV): the global landscape ``M(q) = E|R - q|`` over a
dense grid (to see whether φ sits at an exceptional minimum or merely inside a
broad basin), the mean/median φ distance, and φ's rank among the controls. These
are descriptive/secondary and can never override the primary Δ_φ (spec §XXIII).

φ receives **no** special treatment here beyond being the registered focal
constant: the same ``|R - q|`` is applied to φ and to every control.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from phi.phase4.constants import Q_PHI


def _as_array(r_values: Sequence[float] | np.ndarray) -> np.ndarray:
    return np.asarray(r_values, dtype=np.float64)


def paired_z(
    r_values: Sequence[float] | np.ndarray,
    comparison_set: Sequence[float],
    *,
    q_phi: float = Q_PHI,
) -> np.ndarray:
    """Per-excursion paired advantage ``Z_i`` (spec §XXVIII). Shape ``(N,)``.

    ``Z_i > 0`` ⇔ φ is closer than the average control on excursion ``i``.
    """
    r = _as_array(r_values)
    c = np.asarray(list(comparison_set), dtype=np.float64)
    if r.size == 0:
        return np.empty(0, dtype=np.float64)
    if c.size == 0:
        raise ValueError("comparison_set is empty; Δ_φ requires matched controls (spec §XXIV)")
    d_phi = np.abs(r - q_phi)  # (N,)
    d_controls = np.abs(r[:, None] - c[None, :])  # (N, K)
    return d_controls.mean(axis=1) - d_phi  # (N,)


def delta_phi(
    r_values: Sequence[float] | np.ndarray,
    comparison_set: Sequence[float],
    *,
    q_phi: float = Q_PHI,
) -> float:
    """Primary estimand Δ̂_φ = mean of the per-excursion advantages (spec §XIX)."""
    z = paired_z(r_values, comparison_set, q_phi=q_phi)
    if z.size == 0:
        raise ValueError("no eligible retracements: Δ_φ is undefined for an empty sample")
    return float(z.mean())


def mean_phi_distance(r_values: Sequence[float] | np.ndarray, *, q_phi: float = Q_PHI) -> float:
    """Secondary 1 (spec §XXIII): E|R - q_φ|."""
    r = _as_array(r_values)
    return float(np.abs(r - q_phi).mean())


def median_phi_distance(r_values: Sequence[float] | np.ndarray, *, q_phi: float = Q_PHI) -> float:
    """Secondary 2 (spec §XXIII): median|R - q_φ|."""
    r = _as_array(r_values)
    return float(np.median(np.abs(r - q_phi)))


def phi_rank(
    r_values: Sequence[float] | np.ndarray,
    comparison_set: Sequence[float],
    *,
    q_phi: float = Q_PHI,
) -> float:
    """Secondary 3 (spec §XXIII): fraction of controls that φ beats on mean distance.

    ``1.0`` ⇒ φ has the lowest mean distance of all; ``0.0`` ⇒ the highest.
    """
    r = _as_array(r_values)
    c = np.asarray(list(comparison_set), dtype=np.float64)
    m_phi = float(np.abs(r - q_phi).mean())
    m_controls = np.abs(r[:, None] - c[None, :]).mean(axis=0)  # (K,)
    return float(np.mean(m_controls > m_phi))


def dense_grid(*, lo: float = 0.05, hi: float = 0.95, step: float = 0.001) -> np.ndarray:
    """The pre-registered secondary global grid over ``[lo, hi]`` (spec §XXV)."""
    n = round((hi - lo) / step) + 1
    return np.linspace(lo, hi, n, dtype=np.float64)


def grid_landscape(
    r_values: Sequence[float] | np.ndarray, grid: Sequence[float] | np.ndarray
) -> np.ndarray:
    """Secondary landscape ``M(q) = E|R - q|`` over ``grid`` (spec §XXV). Shape ``(len(grid),)``."""
    r = _as_array(r_values)
    q = np.asarray(grid, dtype=np.float64)
    return np.abs(r[:, None] - q[None, :]).mean(axis=0)
