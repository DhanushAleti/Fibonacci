"""Holm step-down FWER control (spec §XXXIX)."""

from __future__ import annotations

import pytest

from phi.phase4.multiplicity import holm_step_down


class TestHolm:
    def test_known_example(self) -> None:
        # p = [0.01, 0.04, 0.03], m=3: adjusted = [0.03, 0.06, 0.06]; only the first rejects.
        result = holm_step_down([0.01, 0.04, 0.03], alpha=0.05)
        assert result.adjusted_p_values == pytest.approx((0.03, 0.06, 0.06))
        assert result.rejected == (True, False, False)

    def test_adjusted_p_values_are_monotone_in_original_p(self) -> None:
        result = holm_step_down([0.001, 0.2, 0.049, 0.5], alpha=0.05)
        # A smaller raw p never gets a larger adjusted p than a larger raw p.
        pairs = sorted(zip([0.001, 0.2, 0.049, 0.5], result.adjusted_p_values, strict=True))
        adj = [a for _, a in pairs]
        assert adj == sorted(adj)

    def test_empty_family(self) -> None:
        result = holm_step_down([], alpha=0.05)
        assert result.adjusted_p_values == () and result.rejected == ()

    @pytest.mark.parametrize("bad", [-0.1, 1.1])
    def test_rejects_out_of_range_p(self, bad: float) -> None:
        with pytest.raises(ValueError, match="outside"):
            holm_step_down([0.01, bad], alpha=0.05)
