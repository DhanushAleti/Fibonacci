"""The candidate φ feature — Category A (contract §3).

``f_A(t) = |p_t - g_phi|``: the distance between the current close's
position-in-range and the golden-ratio retracement level, in
position-from-low coordinates. This module contains no scientific claim of
predictive value — see the contract's §0A scientific claim boundary.
"""

from __future__ import annotations

from phi.features.constants import G_PHI
from phi.features.pipeline import WindowResult


def f_A(window: WindowResult) -> float | None:
    """Category A: ``|p_t - g_phi|``, or ``None`` if ``window`` is NULL."""
    if window.p is None:
        return None
    return abs(window.p - G_PHI)
