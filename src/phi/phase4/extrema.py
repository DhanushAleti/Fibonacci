"""Deterministic three-point extrema anchor and excursion construction (spec §V-§VII).

The canonical anchor is *deterministic consecutive three-point local extrema with
consecutive opposite-extrema pairing, no smoothing, no amplitude threshold, no
fitted parameter* (spec §V). This module is the single, parameter-free
implementation of that rule. It has **no tuning surface**: the only input is the
ordered value sequence.

Plateau handling (spec §VI). Equal-valued runs are compressed; a run is a local
extremum iff its value is strictly greater (max) or strictly less (min) than
*both* neighbouring runs. Its location is the run's **midpoint index**, which
exists uniquely iff the run has odd length; an even-length run has no unique
midpoint and is therefore **not** treated as a distinct extremum (spec §VI:
"collapsed to its midpoint only if the plateau has a unique midpoint; otherwise
the entire plateau is not treated as a distinct extremum"). This is a faithful
implementation of the frozen rule, not a reinterpretation; its one consequence —
that an exactly-even-length reversal plateau yields no extremum — is documented
so it is auditable.

The rule is retrospective (an extremum at ``t`` needs ``t+1`` to confirm), which
is valid for PHI's retrospective/inferential primary analysis and MUST NOT be
reused as if it were real-time information in any predictive secondary analysis
(spec §IV, §LI).
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from itertools import pairwise


class NonFiniteSeriesError(ValueError):
    """The input series contains a non-finite value (``NaN``/``±inf``).

    Extrema identification requires a totally-ordered finite series; a non-finite
    value is a domain/ingestion error surfaced here, never silently skipped.
    """


class ExtremumKind(StrEnum):
    MAX = "max"
    MIN = "min"


@dataclass(frozen=True)
class Extremum:
    """A confirmed local extremum located at the midpoint of its (odd-length) run."""

    index: int
    value: float
    kind: ExtremumKind


@dataclass(frozen=True)
class Excursion:
    """A directional move between two consecutive opposite-type extrema (spec §VI).

    ``anchor`` → ``end``; ``magnitude = |X_e - X_a|`` is the excursion size used as
    the retracement denominator (spec §XXII).
    """

    anchor: Extremum
    end: Extremum

    @property
    def magnitude(self) -> float:
        return abs(self.end.value - self.anchor.value)

    @property
    def is_up(self) -> bool:
        return self.end.value > self.anchor.value


@dataclass(frozen=True)
class _Run:
    start: int
    end: int  # inclusive
    value: float

    @property
    def has_unique_midpoint(self) -> bool:
        # Unique integer midpoint iff the run length (end-start+1) is odd,
        # i.e. iff (start+end) is even.
        return (self.start + self.end) % 2 == 0

    @property
    def midpoint(self) -> int:
        return (self.start + self.end) // 2


def _compress_runs(values: Sequence[float]) -> list[_Run]:
    runs: list[_Run] = []
    start = 0
    for i in range(1, len(values)):
        if values[i] != values[start]:
            runs.append(_Run(start=start, end=i - 1, value=values[start]))
            start = i
    runs.append(_Run(start=start, end=len(values) - 1, value=values[start]))
    return runs


def three_point_extrema(values: Sequence[float]) -> list[Extremum]:
    """Return the deterministic three-point local extrema of ``values`` (spec §VI).

    A run strictly higher than both neighbours is a ``MAX``; strictly lower is a
    ``MIN``. Only interior runs (with a neighbour on each side) can be extrema, so
    the first and last runs are never extrema (retrospective confirmation, spec
    §IV). Even-length runs are dropped (no unique midpoint). Raises
    :class:`NonFiniteSeriesError` on any non-finite input.
    """
    for v in values:
        if not math.isfinite(v):
            raise NonFiniteSeriesError(f"series contains a non-finite value {v!r}")
    runs = _compress_runs(values)
    extrema: list[Extremum] = []
    for i in range(1, len(runs) - 1):
        run, prev_run, next_run = runs[i], runs[i - 1], runs[i + 1]
        if run.value > prev_run.value and run.value > next_run.value:
            kind = ExtremumKind.MAX
        elif run.value < prev_run.value and run.value < next_run.value:
            kind = ExtremumKind.MIN
        else:
            continue  # a shoulder / monotone step, not a turning point
        if not run.has_unique_midpoint:
            continue  # even-length plateau: no unique midpoint (spec §VI)
        extrema.append(Extremum(index=run.midpoint, value=run.value, kind=kind))
    return extrema


def build_excursions(extrema: Sequence[Extremum]) -> list[Excursion]:
    """Pair consecutive **opposite-type** extrema into excursions (spec §VI).

    Three-point extrema on compressed runs alternate MAX/MIN by construction; a
    dropped even-length plateau can leave two same-type extrema adjacent, in which
    case no excursion spans that gap (no nested/skipped/manual pairing is ever
    invented — spec §VI). Excursions preserve chronological order.
    """
    excursions: list[Excursion] = []
    for anchor, end in pairwise(extrema):
        if anchor.kind != end.kind:
            excursions.append(Excursion(anchor=anchor, end=end))
    return excursions
