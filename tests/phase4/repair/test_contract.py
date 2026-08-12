"""Scientific-contract invariants of the repair (Repair Contract testing section)."""

from __future__ import annotations

import numpy as np

from phi.phase4 import repair
from phi.phase4.estimand import delta_phi
from phi.phase4.registration import ComparisonSet
from phi.phase4.repair.rational import FIVE_EIGHTHS, RATIONAL_CONSTANTS
from phi.phase4.repair.registration import confirmatory_phi_test
from phi.phase4.repair.validation import REPAIR_NULL_SUITE
from phi.phase4.repair.zscore import eligible_retracements


class TestOriginalDeltaPhiNotConfirmatory:
    def test_forbidden_delta_phi_fires_but_repair_does_not(self) -> None:
        # The old symmetric-control Delta_phi is positive on a null series (Jensen);
        # the repaired confirmatory test standardizes against surrogates and does NOT
        # support phi. This is the core repair invariant: Delta_phi>0 is not evidence.
        series = np.cumsum(np.random.default_rng(0).standard_normal(600))
        r = eligible_retracements(series)
        symmetric = ComparisonSet.build(delta=0.05, k_per_side=4).constants
        old_delta = delta_phi(r, symmetric)  # the forbidden statistic
        result = confirmatory_phi_test(series, n_surrogates=99, seed=20260812)
        assert result is not None
        assert old_delta > 0.0  # forbidden statistic fires (geometric artefact)
        assert result.supports_phi is False  # repaired test confirms nothing


class TestRationalControls:
    def test_are_the_four_microstructure_fractions(self) -> None:
        assert set(RATIONAL_CONSTANTS) == {"1/2", "3/5", "5/8", "2/3"}
        assert FIVE_EIGHTHS == 0.625

    def test_no_dense_grid_top_percentile_rule_exists(self) -> None:
        names = " ".join(dir(repair)).lower()
        assert "top_1" not in names and "percentile_rank" not in names and "dense_grid" not in names


class TestDgpSuiteImmutable:
    def test_thirteen_named_null_dgps(self) -> None:
        assert len(REPAIR_NULL_SUITE) == 13
        assert "ar_p" in REPAIR_NULL_SUITE and "autocorr_heavy" in REPAIR_NULL_SUITE


class TestPositiveControlExists:
    def test_phi_attractor_is_importable(self) -> None:
        assert callable(repair.phi_attractor_garch)
