"""Shared Phase-4 test fixtures: a fully-authorized pre-registration and a data series."""

from __future__ import annotations

import numpy as np

from phi.phase4.registration import ComparisonSet, Phase4PreRegistration


def authorized_registration(**overrides: object) -> Phase4PreRegistration:
    """A pre-registration that :meth:`is_confirmatory_authorized` accepts.

    ``bootstrap_replicates`` is lowered to keep confirmatory-path tests fast; the
    frozen default (10,000) is exercised by the constants test.
    """
    fields: dict[str, object] = dict(
        experiment_id="phase4-exp-0001",
        experiment_version="1",
        research_question="Is q_phi distinguished from matched non-phi constants?",
        primary_hypothesis="Delta_phi > 0 vs matched controls",
        comparison_set=ComparisonSet.build(delta=0.05, k_per_side=4).constants,
        bootstrap_replicates=200,
        delta_min=0.02,
        dataset_a_id="DATASET_A",
        dataset_a_hash="a" * 64,
        dataset_b_id="DATASET_B",
        dataset_b_hash="b" * 64,
        sampling_frequency="1d",
        block_length_config="politis-white;min=1;max=3sqrt(n);fallback=1",
        random_seed=20260812,
        code_version="0" * 40,
        environment_lock_hash="c" * 64,
        falsification_criteria="phi does not exceed matched controls by delta_min",
        bootstrap_coverage_validated=True,
        null_fpr_calibrated=True,
        power_at_delta_min=0.85,
    )
    fields.update(overrides)
    return Phase4PreRegistration(**fields)  # type: ignore[arg-type]


def random_walk_series(n: int = 600, seed: int = 1) -> np.ndarray:
    return np.cumsum(np.random.default_rng(seed).standard_normal(n))
