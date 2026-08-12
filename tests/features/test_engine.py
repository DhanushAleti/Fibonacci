"""Whole-series engine: alignment keys, integration, parameter parity (contract §8.2-§8.3)."""

from __future__ import annotations

import inspect

from phi.features.constants import DEFAULT_SEED, DEFAULT_WINDOW
from phi.features.engine import compute_phi_retracement_features
from tests.features.conftest import make_synthetic_bars


class TestAlignmentKeys:
    def test_one_row_per_input_bar_in_order(self) -> None:
        bars = make_synthetic_bars()
        rows = compute_phi_retracement_features(bars)
        assert len(rows) == len(bars)
        for bar, row in zip(bars, rows, strict=True):
            assert row.symbol == bar.symbol
            assert row.event_time == bar.event_time
            assert row.availability_time == bar.availability_time

    def test_some_rows_are_non_null_given_a_realistic_fixture(self) -> None:
        # Sanity check that the fixture actually exercises the non-warmup
        # path; a fixture that is all-NULL would make every parity test
        # below vacuously true and hide bugs.
        bars = make_synthetic_bars()
        rows = compute_phi_retracement_features(bars)
        assert any(row.f_a is not None for row in rows)
        assert any(row.f_a is None for row in rows)  # warmup period exists


class TestParameterParity:
    """Contract §8.3: no control introduces a tunable hyperparameter A lacks."""

    def test_engine_entry_point_has_no_extra_tunable_parameters(self) -> None:
        signature = inspect.signature(compute_phi_retracement_features)
        assert set(signature.parameters) == {"bars", "window", "seed"}
        assert signature.parameters["window"].default == DEFAULT_WINDOW
        assert signature.parameters["seed"].default == DEFAULT_SEED

    def test_defaults_match_frozen_contract_constants(self) -> None:
        assert DEFAULT_WINDOW == 20
        assert DEFAULT_SEED == 1618


class TestIntegrationSmoke:
    def test_runs_end_to_end_without_raising(self) -> None:
        bars = make_synthetic_bars()
        rows = compute_phi_retracement_features(bars)
        assert len(rows) > 0

    def test_different_symbols_are_independent(self) -> None:
        bars_a = make_synthetic_bars(symbol="AAA", seed=1)
        bars_b = make_synthetic_bars(symbol="BBB", seed=2)
        rows_a = compute_phi_retracement_features(bars_a)
        rows_b = compute_phi_retracement_features(bars_b)
        assert all(row.symbol == "AAA" for row in rows_a)
        assert all(row.symbol == "BBB" for row in rows_b)
