"""Phase 2 φ-feature package — one authoritative feature, one Phase-4 primitive.

The feature-authority question is **decided** (ADR 0003, 2026-08-12, Option B):

1. **Rolling-window position** (``candidate``/``controls``/``engine``/``pipeline``)
   — the **authoritative Phase-2 feature**, frozen and implemented under
   ``docs/05-mathematics/phi-retracement-feature-contract.md`` and ADR 0002.
   Entry point: :func:`compute_phi_retracement_features`.
2. **Excursion retracement** (``retracement``) — retained as **Phase-4 statistical
   guidance only**, *not* the authoritative Phase-2 feature and deliberately not
   wired into the compute path above. Only the *frozen math* of the external
   "Authoritative Scientific Contract" (``R_t = |X_t - X_e| / |X_e - X_a|``) is
   implemented; the causal anchor selection algorithm (Blocker 1) and threshold
   ``epsilon_phi`` (Blocker 2) are NOT implemented — see ADR 0003.

Per both contracts' scientific-claim boundary: this package establishes
deterministic construction, temporal validity, reproducibility, and matched
control generation only. It makes **no** claim that any φ feature is predictive.
"""

from __future__ import annotations

from phi.features.candidate import f_A
from phi.features.constants import DEFAULT_SEED, DEFAULT_WINDOW, G_HALF, G_PHI, G_SQRT2
from phi.features.controls import (
    InsufficientSupportForRotationError,
    f_C1,
    f_C2,
    f_D,
    f_E_series,
    f_F,
    rotate_series,
)
from phi.features.engine import FeatureRow, compute_phi_retracement_features
from phi.features.pipeline import (
    DuplicateEventTimeError,
    MixedSymbolError,
    NonMonotonicBarSequenceError,
    WindowResult,
    compute_window,
    compute_windows,
    validate_bar_sequence,
)
from phi.features.retracement import (
    Q_PHI,
    ExcursionAnchorSelector,
    NonFiniteRetracementError,
    is_phi_hit,
    phi_distance,
    retracement_ratio,
)

__all__ = [
    "DEFAULT_SEED",
    "DEFAULT_WINDOW",
    "G_HALF",
    "G_PHI",
    "G_SQRT2",
    "Q_PHI",
    "DuplicateEventTimeError",
    "ExcursionAnchorSelector",
    "FeatureRow",
    "InsufficientSupportForRotationError",
    "MixedSymbolError",
    "NonFiniteRetracementError",
    "NonMonotonicBarSequenceError",
    "WindowResult",
    "compute_phi_retracement_features",
    "compute_window",
    "compute_windows",
    "f_A",
    "f_C1",
    "f_C2",
    "f_D",
    "f_E_series",
    "f_F",
    "is_phi_hit",
    "phi_distance",
    "retracement_ratio",
    "rotate_series",
    "validate_bar_sequence",
]
