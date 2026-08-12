"""Fail-closed confirmatory gate and discovery/confirmation/replication separation."""

from __future__ import annotations

import pytest

from phi.phase4.datasets import DataRole, DataSeparationError, RegisteredDataset
from phi.phase4.pipeline import (
    ConfirmatoryNotAuthorizedError,
    run_confirmatory,
    run_exploratory,
    run_replication,
)
from phi.phase4.registration import ComparisonSet, Phase4PreRegistration
from tests.phase4.conftest import authorized_registration, random_walk_series

_CONFIRM_DS = RegisteredDataset(
    dataset_id="DATASET_A", content_hash="a" * 64, role=DataRole.CONFIRMATION
)
_REPLICATE_DS = RegisteredDataset(
    dataset_id="DATASET_B", content_hash="b" * 64, role=DataRole.EXTERNAL
)


class TestFailClosed:
    def test_confirmatory_refused_when_unregistered(self) -> None:
        bare = Phase4PreRegistration(
            experiment_id="e", experiment_version="1", research_question="q", primary_hypothesis="h"
        )
        with pytest.raises(ConfirmatoryNotAuthorizedError):
            run_confirmatory(random_walk_series(), registration=bare, dataset=_CONFIRM_DS)

    def test_confirmatory_runs_when_fully_authorized(self) -> None:
        analysis = run_confirmatory(
            random_walk_series(), registration=authorized_registration(), dataset=_CONFIRM_DS
        )
        assert analysis.bootstrap is not None
        assert analysis.n_eligible >= 2


class TestDataSeparation:
    def test_discovery_dataset_cannot_be_confirmatory(self) -> None:
        discovery = RegisteredDataset(
            dataset_id="DATASET_A", content_hash="a" * 64, role=DataRole.DISCOVERY
        )
        with pytest.raises(DataSeparationError, match="role"):
            run_confirmatory(
                random_walk_series(), registration=authorized_registration(), dataset=discovery
            )

    def test_mismatched_hash_is_rejected(self) -> None:
        wrong = RegisteredDataset(
            dataset_id="DATASET_A", content_hash="deadbeef", role=DataRole.CONFIRMATION
        )
        with pytest.raises(DataSeparationError, match="does not match"):
            run_confirmatory(
                random_walk_series(), registration=authorized_registration(), dataset=wrong
            )

    def test_replication_requires_external_dataset_b(self) -> None:
        analysis = run_replication(
            random_walk_series(seed=2),
            registration=authorized_registration(),
            dataset=_REPLICATE_DS,
        )
        assert analysis.bootstrap is not None
        # Dataset A cannot stand in for the replication dataset.
        with pytest.raises(DataSeparationError):
            run_replication(
                random_walk_series(), registration=authorized_registration(), dataset=_CONFIRM_DS
            )


class TestExploratoryAndReproducibility:
    def test_exploratory_runs_without_authorization(self) -> None:
        c = ComparisonSet.build(delta=0.05, k_per_side=4).constants
        analysis = run_exploratory(random_walk_series(), c, replicates=200, seed=20260812)
        assert analysis.bootstrap is not None

    def test_confirmatory_result_is_reproducible(self) -> None:
        a = run_confirmatory(
            random_walk_series(), registration=authorized_registration(), dataset=_CONFIRM_DS
        )
        b = run_confirmatory(
            random_walk_series(), registration=authorized_registration(), dataset=_CONFIRM_DS
        )
        assert a.delta_hat == b.delta_hat
        assert a.bootstrap is not None and b.bootstrap is not None
        assert a.bootstrap.p_value == b.bootstrap.p_value
        assert a.bootstrap.ci_low == b.bootstrap.ci_low
