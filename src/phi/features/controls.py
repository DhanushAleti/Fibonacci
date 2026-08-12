"""The six-category matched control set (contract §7).

Tier 1 — strict constant-swap controls (C1, C2) share ``f(t) = |p_t - g|``
with the candidate (``candidate.f_A``) and differ only in the frozen
reference constant (contract §8.1).

Tier 2 — pipeline-matched alternative baselines (B, D, E, F) share the §2
pipeline but use genuinely different transforms (contract §8.2). D and F are
per-window like the candidate; E and B are inherently whole-series
constructions ("shifted by one bar" / "rotation of the realized series"), so
they are exposed as series-level functions rather than per-window ones —
this mirrors the contract's own framing, not an arbitrary API choice.
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence

from phi.features.constants import G_HALF, G_SQRT2
from phi.features.pipeline import WindowResult


class InsufficientSupportForRotationError(ValueError):
    """Too few non-NULL candidate values to draw a Category B rotation offset.

    Contract §7.1 requires ``|S| >= 2*window`` to draw ``offset`` from
    ``[window, |S|-window+1)``. A fixture below this size is a sizing error
    that must be surfaced, not silently returned as an all-NULL control
    column that looks like a normal (if uninformative) result.
    """


def f_C1(window: WindowResult) -> float | None:
    """Category C1: fixed round-number benchmark, ``|p_t - 0.5|``."""
    if window.p is None:
        return None
    return abs(window.p - G_HALF)


def f_C2(window: WindowResult) -> float | None:
    """Category C2: non-φ irrational benchmark, ``|p_t - 1/sqrt(2)|``."""
    if window.p is None:
        return None
    return abs(window.p - G_SQRT2)


def f_D(window: WindowResult) -> float | None:
    """Category D: the shared position primitive itself, ``p_t``."""
    return window.p


def f_E_series(p_values: Sequence[float | None]) -> list[float | None]:
    """Category E for a whole series: naive persistence, ``f_E(t) = p_{t-1}``.

    Index 0 has no ``t-1`` and is therefore ``None`` regardless of ``p_0``.
    """
    if not p_values:
        return []
    return [None, *p_values[:-1]]


def _ols_slope(closes: Sequence[float]) -> float:
    """OLS slope of ``closes`` against within-window ordinal position (§7.2).

    Closed-form: ``beta_hat = sum((x_k - x_mean)(y_k - y_mean)) / sum((x_k - x_mean)^2)``
    with ``x_k = k``, ``x_mean = (n-1)/2``, and the constant denominator
    ``sum((x_k - x_mean)^2) = n(n^2-1)/12`` (equals 665 for the frozen ``n = 20``).
    """
    n = len(closes)
    x_mean = (n - 1) / 2.0
    y_mean = sum(closes) / n
    numerator = sum((k - x_mean) * (y - y_mean) for k, y in enumerate(closes))
    denominator = n * (n**2 - 1) / 12.0
    return numerator / denominator


def f_F(window: WindowResult) -> float | None:
    """Category F: range-normalized OLS slope of the prior window's closes.

    ``f_F(t) = β̂_t / R_t`` (signed; never ``|·|``). ``None`` under the same
    NULL conditions as every other control (insufficient history or a
    degenerate flat window) — F shares ``WindowResult.is_null`` rather than
    deriving its own NULL rule, so its NULL mask cannot drift from the
    candidate's (contract §8.2).
    """
    if window.is_null:
        return None
    assert window.range_ is not None and window.range_ > 0  # implied by not is_null
    closes = [bar.close for bar in window.prior_window]
    slope = _ols_slope(closes)
    value = slope / window.range_
    if not math.isfinite(value):
        # Contract §6 case 8 applies identically to F's output.
        raise AssertionError(
            f"non-finite f_F={value!r} at t={window.t} despite range_="
            f"{window.range_!r} > 0; this indicates an implementation bug "
            "(contract §6 case 8)"
        )
    return value


def rotate_series(
    candidate_values: Sequence[float | None], *, seed: int, window: int
) -> list[float | None]:
    """Category B: seeded circular rotation of the realized candidate series (§7.1).

    Let ``S`` be the ascending indices where ``candidate_values`` is
    non-``None`` and ``n = |S|``. Draws one offset
    ``s = Random(seed).randrange(window, n - window + 1)`` and sets, for the
    ``k``-th support position, ``f_B(t_k) = candidate_values[t_{(k+s) mod n}]``.
    NULL positions of ``candidate_values`` remain ``NULL``.

    This is a **deterministic temporal-alignment placebo**, not a
    statistical null distribution — see contract §7.1's scope note. Raises
    :class:`InsufficientSupportForRotationError` if ``n < 2*window``, per the
    contract's explicit "surfaced, not silently tolerated" requirement for
    an undersized fixture.
    """
    support_positions = [i for i, v in enumerate(candidate_values) if v is not None]
    support_values = [candidate_values[i] for i in support_positions]
    n = len(support_values)

    if n < 2 * window:
        raise InsufficientSupportForRotationError(
            f"Category B requires at least 2*window={2 * window} non-NULL candidate "
            f"values to draw a rotation offset in [window, n-window+1); got n={n} "
            "(contract §7.1)."
        )

    rng = random.Random(seed)
    offset = rng.randrange(window, n - window + 1)
    rotated_support = [support_values[(k + offset) % n] for k in range(n)]

    result: list[float | None] = [None] * len(candidate_values)
    for position, value in zip(support_positions, rotated_support, strict=True):
        result[position] = value
    return result
