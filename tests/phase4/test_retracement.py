"""Per-excursion retracement: hand-verified terminal R, overshoot, reconciliation (spec §XXII)."""

from __future__ import annotations

import pytest

from phi.phase4.extrema import build_excursions, three_point_extrema
from phi.phase4.retracement import (
    RetracementObservation,
    RetracementResult,
    excursion_retracements,
)


def _retracements(values: list[float]) -> RetracementResult:
    return excursion_retracements(build_excursions(three_point_extrema(values)))


class TestTerminalRetracement:
    def test_hand_computed_eligible_value(self) -> None:
        # Extrema MAX@1(10), MIN@2(4), MAX@3(6). Excursion0 = 10->4 (mag 6);
        # completed at the next extremum (6): R_0 = |6-4| / |4-10| = 2/6.
        result = _retracements([0, 10, 4, 6, 5])
        assert result.n_excursions == 2
        assert result.n_incomplete == 1  # last excursion has no successor
        assert len(result.eligible) == 1
        assert result.eligible[0].r == pytest.approx(2.0 / 6.0)

    def test_overshoot_is_flagged_not_deleted(self) -> None:
        # Excursion0 = 10->4 (mag 6); next extremum 20 -> R_0 = 16/6 = 2.667 > 1.
        result = _retracements([0, 10, 4, 20, 0])
        assert len(result.eligible) == 0
        assert len(result.overshoots) == 1
        assert result.overshoots[0].r == pytest.approx(16.0 / 6.0)
        assert result.overshoots[0].is_overshoot is True

    def test_boundary_values_zero_and_one_are_eligible(self) -> None:
        assert RetracementObservation(0, 0.0).is_eligible is True
        assert RetracementObservation(0, 1.0).is_eligible is True
        assert RetracementObservation(0, 1.0).is_overshoot is False


class TestReconciliation:
    def test_counts_reconcile(self) -> None:
        result = _retracements([0, 10, 4, 6, 5])
        accounted = len(result.observations) + result.n_zero_denominator + result.n_incomplete
        assert accounted == result.n_excursions
