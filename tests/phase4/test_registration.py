"""Pre-registration + fail-closed gate + comparison-set structural rules (spec §XXIV)."""

from __future__ import annotations

import pytest

from phi.phase4.constants import Q_PHI
from phi.phase4.registration import (
    ComparisonSet,
    ComparisonSetError,
    Phase4PreRegistration,
    validate_comparison_set,
)
from tests.phase4.conftest import authorized_registration


class TestFailClosedGate:
    def test_bare_registration_is_not_authorized(self) -> None:
        reg = Phase4PreRegistration(
            experiment_id="e", experiment_version="1", research_question="q", primary_hypothesis="h"
        )
        assert reg.is_confirmatory_authorized() is False
        assert "comparison_set" in reg.missing_registrations()
        assert "delta_min" in reg.missing_registrations()

    def test_fully_registered_and_validated_is_authorized(self) -> None:
        assert authorized_registration().is_confirmatory_authorized() is True

    def test_underpowered_is_not_authorized(self) -> None:
        reg = authorized_registration(power_at_delta_min=0.5)  # below 0.80 threshold
        assert reg.is_confirmatory_authorized() is False
        assert "power_at_delta_min" in reg.failed_validation_gates()

    def test_uncalibrated_null_fpr_is_not_authorized(self) -> None:
        reg = authorized_registration(null_fpr_calibrated=False)
        assert reg.is_confirmatory_authorized() is False
        assert "null_fpr_calibrated" in reg.failed_validation_gates()

    def test_missing_dataset_b_is_not_authorized(self) -> None:
        reg = authorized_registration(dataset_b_id=None)
        assert reg.is_confirmatory_authorized() is False
        assert "dataset_b_id" in reg.missing_registrations()


class TestComparisonSetRules:
    def test_valid_symmetric_set_passes(self) -> None:
        c = ComparisonSet.build(delta=0.05, k_per_side=3).constants
        validate_comparison_set(c)  # does not raise
        assert len(c) == 6

    def test_set_containing_phi_is_rejected(self) -> None:
        with pytest.raises(ComparisonSetError, match="exclude q_phi"):
            validate_comparison_set((Q_PHI - 0.05, Q_PHI, Q_PHI + 0.05))

    def test_asymmetric_set_is_rejected(self) -> None:
        with pytest.raises(ComparisonSetError):
            validate_comparison_set((Q_PHI - 0.05, Q_PHI + 0.10))

    def test_odd_count_is_rejected(self) -> None:
        with pytest.raises(ComparisonSetError, match="even count"):
            validate_comparison_set((Q_PHI - 0.05, Q_PHI + 0.05, Q_PHI + 0.10))

    def test_out_of_unit_interval_is_rejected(self) -> None:
        with pytest.raises(ComparisonSetError, match="strictly inside"):
            validate_comparison_set((0.0, 1.0))


class TestHash:
    def test_hash_is_deterministic_and_field_sensitive(self) -> None:
        a = authorized_registration()
        assert a.content_hash() == authorized_registration().content_hash()
        assert a.content_hash() != authorized_registration(random_seed=1).content_hash()
        assert len(a.content_hash()) == 64
