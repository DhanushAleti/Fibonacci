"""Experiment manifest: hashing determinism, immutability, confirmatory gate (§29)."""

from __future__ import annotations

import dataclasses
import json

import pytest

from phi.experiment.manifest import ExperimentManifest


def _base_manifest(**overrides: object) -> ExperimentManifest:
    fields: dict[str, object] = dict(
        experiment_id="exp-0001",
        experiment_version="1",
        research_question="Does phi retracement structure exceed matched controls?",
        primary_hypothesis="Delta_p > Delta_min against Family A controls",
        dataset="synthetic:phi-engineering-fixture",
        dataset_version="v0",
        dataset_content_hash="deadbeef",
        code_version="0" * 40,
        environment_lock_hash="cafebabe",
        time_range="2020-01-01/2020-08-01",
        primary_feature="excursion_retracement",
        feature_formula="R_t = |X_t - X_e| / |X_e - X_a|",
        normalization="none (intrinsic ratio)",
        missing_data_policy="explicit invalidation, zero imputation",
        random_seed=1618,
        falsification_criteria="phi does not exceed max Family A control by Delta_min",
    )
    fields.update(overrides)
    return ExperimentManifest(**fields)  # type: ignore[arg-type]


#: Every registration a confirmatory run requires: the Blocker 1-4 fields plus
#: the mandatory confirmatory registrations (multiplicity correction, confidence
#: level, non-empty control set). Used to build a fully-ready manifest.
_FULL_CONFIRMATORY: dict[str, object] = dict(
    anchor_algorithm="causal-k20-confirm",
    window=20,
    threshold=0.01,
    primary_statistic="delta_p_vs_family_a_supremum",
    inference_method="stationary-block-bootstrap-B10000",
    multiplicity_method="holm-bonferroni",
    confidence_level=0.95,
    controls=("A", "B", "C1", "C2", "D", "E", "F"),
)


class TestHashDeterminism:
    def test_equal_manifests_hash_identically(self) -> None:
        assert _base_manifest().content_hash() == _base_manifest().content_hash()

    def test_hash_is_stable_across_field_declaration_paths(self) -> None:
        # Building via replace must not change the hash if values are equal.
        a = _base_manifest()
        b = dataclasses.replace(a)
        assert a.content_hash() == b.content_hash()

    def test_changing_any_field_changes_hash(self) -> None:
        base_hash = _base_manifest().content_hash()
        assert _base_manifest(random_seed=1619).content_hash() != base_hash
        assert _base_manifest(dataset_content_hash="feedface").content_hash() != base_hash

    def test_code_and_environment_provenance_bind_the_hash(self) -> None:
        # I-5: code_version + environment_lock_hash are part of the registered
        # identity, so two runs pinning different code/environments hash differently
        # ("same manifest hash" => same executable experiment, not just same params).
        base_hash = _base_manifest().content_hash()
        assert _base_manifest(code_version="1" * 40).content_hash() != base_hash
        assert _base_manifest(environment_lock_hash="deadbeef").content_hash() != base_hash

    def test_hash_is_sha256_hex(self) -> None:
        digest = _base_manifest().content_hash()
        assert len(digest) == 64
        assert all(c in "0123456789abcdef" for c in digest)

    def test_canonical_json_is_sorted_and_compact(self) -> None:
        payload = _base_manifest().canonical_json()
        parsed = json.loads(payload)
        # sort_keys=True -> top-level keys are in sorted order.
        assert list(parsed.keys()) == sorted(parsed.keys())
        # separators=(",", ":") -> no space after the key/value colon.
        assert '"random_seed":1618' in payload


class TestImmutability:
    def test_manifest_is_frozen(self) -> None:
        manifest = _base_manifest()
        with pytest.raises(dataclasses.FrozenInstanceError):
            manifest.random_seed = 42  # type: ignore[misc]


class TestConfirmatoryReadinessGate:
    """Machine-checkable NO-GO: unfrozen Blockers 1-4 keep a manifest exploratory."""

    def test_base_manifest_is_not_confirmatory_ready(self) -> None:
        manifest = _base_manifest()
        assert manifest.is_confirmatory_ready() is False

    def test_unfrozen_blockers_names_all_missing_fields(self) -> None:
        manifest = _base_manifest()
        assert set(manifest.unfrozen_blockers()) == {
            "anchor_algorithm",
            "window",
            "threshold",
            "primary_statistic",
            "inference_method",
        }

    def test_partial_freeze_still_not_ready(self) -> None:
        manifest = _base_manifest(anchor_algorithm="causal-k20-confirm", window=20)
        assert manifest.is_confirmatory_ready() is False
        assert set(manifest.unfrozen_blockers()) == {
            "threshold",
            "primary_statistic",
            "inference_method",
        }

    def test_blockers_frozen_but_registrations_missing_is_not_ready(self) -> None:
        # All five Blockers frozen, but no multiplicity correction, confidence
        # level, or control set registered -> still NOT confirmatory-ready. This
        # is the hole the strengthened gate closes: a control-based, multiplicity-
        # counted design cannot be "ready" without those registrations.
        manifest = _base_manifest(
            anchor_algorithm="causal-k20-confirm",
            window=20,
            threshold=0.01,
            primary_statistic="delta_p_vs_family_a_supremum",
            inference_method="stationary-block-bootstrap-B10000",
        )
        assert manifest.unfrozen_blockers() == ()  # Blockers 1-4 are all frozen
        assert manifest.is_confirmatory_ready() is False  # but registrations missing
        assert set(manifest.missing_confirmatory_registrations()) == {
            "multiplicity_method",
            "confidence_level",
            "controls",
        }

    def test_partial_registration_still_not_ready(self) -> None:
        manifest = _base_manifest(
            anchor_algorithm="causal-k20-confirm",
            window=20,
            threshold=0.01,
            primary_statistic="delta_p_vs_family_a_supremum",
            inference_method="stationary-block-bootstrap-B10000",
            multiplicity_method="holm-bonferroni",
        )
        assert manifest.is_confirmatory_ready() is False
        assert set(manifest.missing_confirmatory_registrations()) == {
            "confidence_level",
            "controls",
        }

    def test_empty_controls_tuple_blocks_readiness(self) -> None:
        # controls defaults to () — its "unset" sentinel is empty, not None, so
        # it must be checked for non-emptiness explicitly.
        manifest = _base_manifest(
            **{**_FULL_CONFIRMATORY, "controls": ()}  # everything else registered
        )
        assert manifest.is_confirmatory_ready() is False
        assert manifest.missing_confirmatory_registrations() == ("controls",)

    def test_fully_registered_manifest_is_ready(self) -> None:
        manifest = _base_manifest(**_FULL_CONFIRMATORY)
        assert manifest.is_confirmatory_ready() is True
        assert manifest.unfrozen_blockers() == ()
        assert manifest.missing_confirmatory_registrations() == ()

    def test_freezing_blockers_changes_hash(self) -> None:
        # A confirmatory manifest is a different registered plan than the
        # exploratory skeleton, so its hash must differ.
        exploratory = _base_manifest().content_hash()
        confirmatory = _base_manifest(**_FULL_CONFIRMATORY).content_hash()
        assert exploratory != confirmatory
