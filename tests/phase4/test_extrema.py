"""Three-point extrema: hand-verified turning points, plateau rule, leakage (spec §VI)."""

from __future__ import annotations

import pytest

from phi.phase4.extrema import (
    ExtremumKind,
    NonFiniteSeriesError,
    build_excursions,
    three_point_extrema,
)


class TestHandVerifiedExtrema:
    def test_simple_zigzag(self) -> None:
        ex = three_point_extrema([0, 2, 1, 3, 0])
        assert [(e.index, e.value, e.kind) for e in ex] == [
            (1, 2.0, ExtremumKind.MAX),
            (2, 1.0, ExtremumKind.MIN),
            (3, 3.0, ExtremumKind.MAX),
        ]

    def test_monotone_series_has_no_extrema(self) -> None:
        assert three_point_extrema([0, 1, 2, 3, 4]) == []

    def test_first_and_last_points_are_never_extrema(self) -> None:
        # A peak at the very end cannot be confirmed (needs a right neighbour).
        assert three_point_extrema([0, 5]) == []


class TestPlateauRule:
    def test_odd_length_plateau_collapses_to_midpoint(self) -> None:
        # [0,5,5,5,0]: the length-3 top run has a unique midpoint (index 2).
        ex = three_point_extrema([0, 5, 5, 5, 0])
        assert len(ex) == 1
        assert ex[0].index == 2
        assert ex[0].kind is ExtremumKind.MAX

    def test_even_length_plateau_is_not_an_extremum(self) -> None:
        # [0,5,5,0]: the length-2 top run has no unique midpoint -> dropped (spec §VI).
        assert three_point_extrema([0, 5, 5, 0]) == []


class TestNonFinite:
    @pytest.mark.parametrize("bad", [float("inf"), float("-inf"), float("nan")])
    def test_non_finite_raises(self, bad: float) -> None:
        with pytest.raises(NonFiniteSeriesError):
            three_point_extrema([0.0, 1.0, bad, 0.0])


class TestExcursions:
    def test_consecutive_opposite_extrema_pair(self) -> None:
        ex = three_point_extrema([0, 2, 1, 3, 0])
        exc = build_excursions(ex)
        assert len(exc) == 2
        assert exc[0].is_up is False and exc[0].magnitude == 1.0  # 2 -> 1
        assert exc[1].is_up is True and exc[1].magnitude == 2.0  # 1 -> 3


class TestLeakageInvariance:
    """Appending future data cannot change an already-confirmed earlier extremum."""

    def test_future_append_does_not_change_earlier_extrema(self) -> None:
        base = [0, 5, 2, 7, 1, 6, 3, 8, 0]
        ex_base = three_point_extrema(base)
        for injected in (1e10, -1e10, 0.5):
            ex_ext = three_point_extrema([*base, injected])
            # Every extremum confirmed strictly before the appended index is unchanged.
            safe = [e for e in ex_base if e.index <= len(base) - 3]
            assert safe == [e for e in ex_ext if e.index <= len(base) - 3]
