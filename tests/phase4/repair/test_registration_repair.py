"""Repaired fail-closed gate + confirmatory/secondary separation (Repair Parts 8-9)."""

from __future__ import annotations

import numpy as np
import pytest

from phi.phase4.datasets import DataRole, DataSeparationError, RegisteredDataset
from phi.phase4.repair.registration import (
    ConfirmatoryNotAuthorizedError,
    RepairPreRegistration,
    run_confirmatory_repair,
    run_secondary_profile,
)


def authorized(**overrides: object) -> RepairPreRegistration:
    fields: dict[str, object] = dict(
        experiment_id="repair-0001",
        experiment_version="1",
        research_question="Is Z_phi > 0 vs surrogate topology?",
        primary_hypothesis="Z_phi > 0",
        dataset_a_id="DATASET_A",
        dataset_a_hash="a" * 64,
        dataset_b_id="DATASET_B",
        dataset_b_hash="b" * 64,
        sampling_frequency="1d",
        block_length_config="politis-white/increments",
        random_seed=20260812,
        code_version="0" * 40,
        environment_lock_hash="c" * 64,
        aggregate_fpr=0.011,
        max_per_dgp_fpr=0.05,
        positive_control_power_medium=0.82,
        granularity_passes=True,
        constant_sweep_symmetric=True,
    )
    fields.update(overrides)
    return RepairPreRegistration(**fields)  # type: ignore[arg-type]


def _series() -> np.ndarray:
    return np.cumsum(np.random.default_rng(0).standard_normal(600))


class TestFailClosedGate:
    def test_bare_registration_not_authorized(self) -> None:
        reg = RepairPreRegistration(
            experiment_id="e", experiment_version="1", research_question="q", primary_hypothesis="h"
        )
        assert reg.is_confirmatory_authorized() is False
        assert "aggregate_fpr<=0.05" in reg.failed_gates()
        assert "dataset_a_id" in reg.missing_registrations()

    def test_fully_validated_is_authorized(self) -> None:
        assert authorized().is_confirmatory_authorized() is True

    def test_failing_granularity_blocks(self) -> None:
        # Mirrors the actual small-scale finding: granularity gate fails -> not authorized.
        reg = authorized(granularity_passes=False)
        assert reg.is_confirmatory_authorized() is False
        assert "granularity_rejection" in reg.failed_gates()

    def test_underpowered_blocks(self) -> None:
        assert authorized(positive_control_power_medium=0.5).is_confirmatory_authorized() is False

    def test_high_per_dgp_fpr_blocks(self) -> None:
        assert authorized(max_per_dgp_fpr=0.09).is_confirmatory_authorized() is False

    def test_content_hash_deterministic(self) -> None:
        assert authorized().content_hash() == authorized().content_hash()
        assert authorized().content_hash() != authorized(random_seed=1).content_hash()


class TestConfirmatoryPath:
    def test_refused_when_unauthorized(self) -> None:
        bare = RepairPreRegistration(
            experiment_id="e", experiment_version="1", research_question="q", primary_hypothesis="h"
        )
        ds = RegisteredDataset(
            dataset_id="DATASET_A", content_hash="a" * 64, role=DataRole.CONFIRMATION
        )
        with pytest.raises(ConfirmatoryNotAuthorizedError):
            run_confirmatory_repair(_series(), registration=bare, dataset=ds)

    def test_runs_when_authorized_and_uses_z_phi(self) -> None:
        ds = RegisteredDataset(
            dataset_id="DATASET_A", content_hash="a" * 64, role=DataRole.CONFIRMATION
        )
        result = run_confirmatory_repair(_series(), registration=authorized(), dataset=ds)
        assert hasattr(result, "z_phi") and hasattr(result, "score")

    def test_wrong_role_rejected(self) -> None:
        ds = RegisteredDataset(
            dataset_id="DATASET_A", content_hash="a" * 64, role=DataRole.DISCOVERY
        )
        with pytest.raises(DataSeparationError):
            run_confirmatory_repair(_series(), registration=authorized(), dataset=ds)

    def test_mismatched_hash_rejected(self) -> None:
        ds = RegisteredDataset(
            dataset_id="DATASET_A", content_hash="deadbeef", role=DataRole.CONFIRMATION
        )
        with pytest.raises(DataSeparationError):
            run_confirmatory_repair(_series(), registration=authorized(), dataset=ds)


class TestSecondaryIsNonConfirmatory:
    def test_secondary_profile_is_labelled_descriptive(self) -> None:
        profile = run_secondary_profile(_series(), symmetric_controls=(0.5, 0.55, 0.68, 0.73))
        assert "SECONDARY" in profile.note and "forbidden" in profile.note
