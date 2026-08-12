"""Frozen constants for the Phase 2 φ retracement feature and its controls.

Values are pinned by *expression*, not decimal literal, per the frozen
contract (``docs/05-mathematics/phi-retracement-feature-contract.md`` §1) so
float64 results are bitwise-reproducible across implementations that reuse
this module rather than re-deriving the constants independently. None of
these may change without a superseding ADR (contract §9) — this module has
no "tunable" surface.
"""

from __future__ import annotations

from phi import PHI
from phi.config import Settings

#: Prior-window length in sequence bars (contract §1). Frozen; no window
#: grid, no result-driven tuning (contract §9).
DEFAULT_WINDOW: int = 20

#: Golden-ratio retracement level, in position-from-low coordinates (§1, §3).
G_PHI: float = 1.0 / PHI

#: Fixed round-number benchmark constant (Category C1, §7).
G_HALF: float = 0.5

#: Non-φ irrational benchmark constant (Category C2, §7).
G_SQRT2: float = 1.0 / (2.0**0.5)

#: Default seed for Category B's deterministic circular rotation (§7.1).
#: Matches ``phi.config.Settings.random_seed`` (the ecosystem-wide default),
#: not an independently chosen value.
DEFAULT_SEED: int = Settings().random_seed
