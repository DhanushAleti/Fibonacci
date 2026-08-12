"""Reproducibility infrastructure for PHI experiments (external contract §26-§38).

This package holds **science-neutral** experiment infrastructure that is
mandated by the external contract and is valid regardless of which Phase-2
feature is authoritative (ADR 0003):

* :mod:`phi.experiment.manifest` — the immutable, content-hashed experiment
  manifest (§29) that pins every experiment parameter and, critically, refuses
  to be marked *confirmatory-ready* while any unfrozen scientific decision
  (Blockers 1-4) is still absent.
* :mod:`phi.experiment.exclusions` — exclusion accounting (§7, §35): raw /
  excluded / valid counts with explicit reasons and a missingness rate.
* :mod:`phi.experiment.provenance` — reproducible capture of the code commit and
  dependency-lockfile hash (§26, §36) that a manifest must bind.

Nothing in this package computes a feature, chooses a threshold, designates an
estimand, or runs a statistical test. Those depend on frozen scientific
decisions that do not yet exist (see ADR 0003) and are intentionally absent.
"""

from __future__ import annotations

from phi.experiment.exclusions import (
    ExclusionAccountant,
    ExclusionReason,
    ExclusionSummary,
)
from phi.experiment.manifest import ExperimentManifest
from phi.experiment.provenance import capture, current_git_sha, hash_file

__all__ = [
    "ExclusionAccountant",
    "ExclusionReason",
    "ExclusionSummary",
    "ExperimentManifest",
    "capture",
    "current_git_sha",
    "hash_file",
]
