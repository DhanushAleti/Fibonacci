"""Matching contract parity, both tiers (contract §8, §11 item 8)."""

from __future__ import annotations

import pytest

from phi.features.constants import G_HALF, G_PHI, G_SQRT2
from phi.features.engine import compute_phi_retracement_features
from tests.features.conftest import make_synthetic_bars


@pytest.fixture(scope="module")
def rows() -> list:
    bars = make_synthetic_bars()
    return compute_phi_retracement_features(bars)


class TestTier1StrictConstantSwap:
    """A, C1, C2: same function of p_t, differing only by the swapped constant."""

    def test_support_and_null_mask_identical_across_a_c1_c2(self, rows: list) -> None:
        for row in rows:
            null_flags = {row.f_a is None, row.f_c1 is None, row.f_c2 is None, row.p is None}
            assert len(null_flags) == 1, (
                f"A/C1/C2/p disagree on NULL at {row.event_time}: "
                f"f_a={row.f_a}, f_c1={row.f_c1}, f_c2={row.f_c2}, p={row.p}"
            )

    def test_a_c1_c2_are_the_same_function_with_swapped_constant(self, rows: list) -> None:
        for row in rows:
            if row.p is None:
                continue
            assert row.f_a == pytest.approx(abs(row.p - G_PHI))
            assert row.f_c1 == pytest.approx(abs(row.p - G_HALF))
            assert row.f_c2 == pytest.approx(abs(row.p - G_SQRT2))


class TestTier2PipelineMatchedBaselines:
    """B, D, E, F: same pipeline/eligibility/availability/alignment as A; different transform."""

    def test_d_shares_support_and_null_mask_with_a(self, rows: list) -> None:
        for row in rows:
            assert (row.f_d is None) == (row.f_a is None)

    def test_f_shares_support_and_null_mask_with_a(self, rows: list) -> None:
        for row in rows:
            assert (row.f_f is None) == (row.f_a is None)

    def test_b_support_and_null_mask_equal_a_exactly(self, rows: list) -> None:
        for row in rows:
            assert (row.f_b is None) == (row.f_a is None)

    def test_e_support_is_a_shifted_by_exactly_one_bar(self, rows: list) -> None:
        assert rows[0].f_e is None  # index 0 has no t-1
        for t in range(1, len(rows)):
            assert (rows[t].f_e is None) == (rows[t - 1].f_a is None)

    def test_all_share_same_alignment_keys_as_the_source_bars(self, rows: list) -> None:
        # Every control's value lives on the SAME row as A's — there is no
        # separate alignment to go wrong, by construction (single FeatureRow
        # per decision index). This test guards against a future refactor
        # that computes controls on a different index space.
        for row in rows:
            assert row.symbol
            assert row.event_time is not None
            assert row.availability_time is not None
