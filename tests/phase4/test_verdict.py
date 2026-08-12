"""The four permitted outcomes, decided by CI position vs delta_min (spec §LIV-§LVII)."""

from __future__ import annotations

import pytest

from phi.phase4.inference import BootstrapResult
from phi.phase4.verdict import Outcome, classify_outcome


def _result(ci_low: float, ci_high: float) -> BootstrapResult:
    return BootstrapResult(
        delta_hat=(ci_low + ci_high) / 2,
        ci_low=ci_low,
        ci_high=ci_high,
        p_value=0.01,
        p_value_mc_se=0.0,
        block_length=1.0,
        replicates=10,
        seed=1,
        n=10,
    )


class TestClassifyOutcome:
    def test_supporting_when_ci_above_delta_min(self) -> None:
        assert classify_outcome(_result(0.03, 0.06), delta_min=0.02) is Outcome.SUPPORTING

    def test_against_when_ci_below_negative_delta_min(self) -> None:
        assert classify_outcome(_result(-0.06, -0.03), delta_min=0.02) is Outcome.AGAINST

    def test_indistinguishable_when_ci_within_equivalence_band(self) -> None:
        assert classify_outcome(_result(-0.01, 0.01), delta_min=0.02) is Outcome.INDISTINGUISHABLE

    def test_inconclusive_when_ci_spans_both(self) -> None:
        assert classify_outcome(_result(-0.05, 0.05), delta_min=0.02) is Outcome.INCONCLUSIVE

    def test_positive_but_within_band_is_not_supporting(self) -> None:
        # A positive point estimate whose CI still touches the equivalence region
        # is NOT "supporting" — guards against Δ̂_φ > 0 being over-claimed.
        assert classify_outcome(_result(0.01, 0.03), delta_min=0.02) is Outcome.INCONCLUSIVE

    def test_delta_min_must_be_positive(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            classify_outcome(_result(0.03, 0.06), delta_min=0.0)
