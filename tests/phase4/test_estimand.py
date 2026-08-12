"""Δ_φ estimand: hand value, the Jensen geometric-bias invariant, secondaries (spec §XIX)."""

from __future__ import annotations

import numpy as np
import pytest

from phi.phase4.constants import Q_PHI
from phi.phase4.estimand import delta_phi, grid_landscape, paired_z, phi_rank
from phi.phase4.registration import ComparisonSet


class TestDeltaPhiHandValue:
    def test_single_observation_on_phi(self) -> None:
        # At R = q_φ: Z = mean_q |q_φ - q| - 0. With C = {q_φ ± 0.05}: Z = 0.05.
        c = ComparisonSet.build(delta=0.05, k_per_side=1).constants
        assert delta_phi([Q_PHI], c) == pytest.approx(0.05)


class TestJensenGeometricBias:
    """The specified estimand + symmetric controls make Δ_φ >= 0 for ANY sample.

    By convexity of ``|R - q|``, the mean control distance is >= the φ distance for
    controls symmetric about q_φ (Jensen). So ``paired_z >= 0`` elementwise for
    every retracement, meaning a positive Δ̂_φ is a geometric artefact, NOT
    evidence of φ specialness. This test LOCKS that finding (red-team Attack Vector
    1 / spec §XVII); it is a documented blocker, not a target. See the Phase-4
    readiness report.
    """

    def test_paired_z_is_nonnegative_for_symmetric_controls(self) -> None:
        c = ComparisonSet.build(delta=0.05, k_per_side=4).constants
        rng = np.random.default_rng(0)
        for _ in range(20):
            r = rng.uniform(0.0, 1.0, size=200)
            z = paired_z(r, c)
            assert float(z.min()) >= -1e-12  # nonnegative up to float noise

    def test_delta_phi_positive_on_pure_uniform_noise(self) -> None:
        c = ComparisonSet.build(delta=0.05, k_per_side=4).constants
        r = np.random.default_rng(1).uniform(0.0, 1.0, size=5000)
        assert delta_phi(r, c) > 0.0  # geometry alone, no φ mechanism


class TestSecondaries:
    def test_grid_landscape_minimises_near_median(self) -> None:
        # M(q) = E|R - q| is minimised at the median; for U(0,1) that is ~0.5.
        r = np.random.default_rng(2).uniform(0.0, 1.0, size=20000)
        grid = np.linspace(0.05, 0.95, 91)
        m = grid_landscape(r, grid)
        assert abs(float(grid[int(np.argmin(m))]) - 0.5) < 0.05

    def test_phi_rank_in_unit_interval(self) -> None:
        c = ComparisonSet.build(delta=0.05, k_per_side=4).constants
        r = np.random.default_rng(3).uniform(0.0, 1.0, size=500)
        assert 0.0 <= phi_rank(r, c) <= 1.0
