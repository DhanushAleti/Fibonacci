"""Whole-series computation: candidate + six controls, aligned by bar (contract §8.2).

The single public entry point (:func:`compute_phi_retracement_features`)
computes the candidate φ feature and all six matched controls together, so
callers cannot accidentally compute one without the others — Phase 2's
control framework is mandatory, not optional (PRD-CONTROL-008).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from phi.data.schemas import PriceBar
from phi.features.candidate import f_A
from phi.features.constants import DEFAULT_SEED, DEFAULT_WINDOW
from phi.features.controls import f_C1, f_C2, f_D, f_E_series, f_F, rotate_series
from phi.features.pipeline import compute_windows


@dataclass(frozen=True)
class FeatureRow:
    """One aligned row: candidate + six controls for a single decision index.

    Alignment key is ``(symbol, event_time, availability_time)``, per
    contract §8.2.
    """

    symbol: str
    event_time: datetime
    availability_time: datetime
    p: float | None
    f_a: float | None
    f_b: float | None
    f_c1: float | None
    f_c2: float | None
    f_d: float | None
    f_e: float | None
    f_f: float | None


def compute_phi_retracement_features(
    bars: Sequence[PriceBar],
    *,
    window: int = DEFAULT_WINDOW,
    seed: int = DEFAULT_SEED,
) -> list[FeatureRow]:
    """Compute the candidate φ feature and all six matched controls for ``bars``.

    ``bars`` must be one instrument's validated series, ordered by
    ``event_time`` ascending (contract §1) — validated once via
    :func:`phi.features.pipeline.compute_windows`.

    Returns one :class:`FeatureRow` per input bar. A, C1, C2, D, and F share
    an identical support and NULL mask by construction (all derive from the
    same :class:`~phi.features.pipeline.WindowResult`, contract §8.1-§8.2);
    B's support and NULL mask equal A's (§7.1); E's support is A's shifted
    by exactly one bar (§11 item 8).
    """
    windows = compute_windows(bars, window=window)

    f_a_values = [f_A(w) for w in windows]
    p_values = [w.p for w in windows]
    f_e_values = f_E_series(p_values)
    f_b_values = rotate_series(f_a_values, seed=seed, window=window)

    rows_zip = zip(bars, windows, f_a_values, f_b_values, f_e_values, strict=True)
    return [
        FeatureRow(
            symbol=bar.symbol,
            event_time=bar.event_time,
            availability_time=bar.availability_time,
            p=w.p,
            f_a=fa,
            f_b=fb,
            f_c1=f_C1(w),
            f_c2=f_C2(w),
            f_d=f_D(w),
            f_e=fe,
            f_f=f_F(w),
        )
        for bar, w, fa, fb, fe in rows_zip
    ]
