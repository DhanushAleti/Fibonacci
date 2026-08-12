"""Immutable, content-hashed experiment manifest (external contract §29, §36).

The manifest is the anti-p-hacking keystone: it freezes every experiment
parameter *before* analysis, and its SHA-256 content hash lets any later run
prove it used the identical registered plan (Gemini dim 2 / dim 14 / Attack
Vector 7: "cryptographic manifest parameter locking").

Machine-checkable enforcement of the NO-GO (ADR 0003): the five scientific
decisions that the external reviews left unfrozen (Blockers 1-4) are modelled
as fields that default to ``None``. :meth:`ExperimentManifest.is_confirmatory_ready`
returns ``False`` — and :meth:`unfrozen_blockers` names the offenders — until a
human freezes them. Confirmatory analysis code is expected to gate on this, so
an experiment literally cannot be run confirmatorily while the science is open.

This module stores and hashes the plan; it does not execute anything, does not
supply any scientific default (no anchor algorithm, no ``epsilon_phi``, no
estimand, no inference method), and makes no claim about results.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class ExperimentManifest:
    """A frozen, hashable registration of one experiment's exact parameters.

    Frozen fields with **no default** are the always-required registration
    facts (identity, dataset + code + environment provenance, the frozen feature
    formula, seed, falsification criteria). ``code_version`` and
    ``environment_lock_hash`` bind the exact commit and dependency environment so
    that an equal :meth:`content_hash` implies the same *executable* experiment,
    not merely the same parameters (external audit I-5; contract §26, §36); capture
    them reproducibly via :func:`phi.experiment.provenance.capture`. Fields
    defaulting to ``None`` / ``()`` are the scientifically **unfrozen** decisions
    (Blockers 1-4); a manifest is not confirmatory-ready until they are all set
    (see :meth:`is_confirmatory_ready`).
    """

    # --- Always-required registration facts -------------------------------
    experiment_id: str
    experiment_version: str
    research_question: str
    primary_hypothesis: str
    dataset: str
    dataset_version: str
    dataset_content_hash: str
    #: git commit SHA (external audit I-5; contract §36); capture via phi.experiment.provenance
    code_version: str
    #: dependency-lockfile SHA-256 (contract §26 item 4)
    environment_lock_hash: str
    time_range: str
    primary_feature: str
    feature_formula: str
    normalization: str
    missing_data_policy: str
    random_seed: int
    falsification_criteria: str

    # --- Unfrozen scientific decisions (Blockers 1-4): None until frozen ---
    anchor_algorithm: str | None = None  # Blocker 1 (causal extremum algorithm)
    window: int | None = None  # pre-registered evaluation window
    threshold: float | None = None  # Blocker 2 (epsilon_phi)
    target: str | None = None
    horizon: str | None = None
    controls: tuple[str, ...] = ()
    primary_statistic: str | None = None  # Blocker 3 (primary estimand)
    inference_method: str | None = None  # Blocker 4 (dependence-aware inference)
    confidence_level: float | None = None
    multiplicity_method: str | None = None

    #: Fields that must be non-``None`` for a confirmatory (not exploratory) run.
    #: These map one-to-one onto the external reviews' unfrozen Blockers 1-4.
    UNFROZEN_SCIENTIFIC_FIELDS: ClassVar[tuple[str, ...]] = (
        "anchor_algorithm",
        "window",
        "threshold",
        "primary_statistic",
        "inference_method",
    )

    #: Registrations that must ALSO be set for a confirmatory run, beyond the
    #: Blocker 1-4 fields above. These are not the external reviews' named
    #: "Blockers", but a confirmatory analysis is unsound without them under this
    #: project's own multiple-testing discipline: the comparison space is logged
    #: for multiplicity accounting (contract §9) and the design is control-based,
    #: so a confirmatory run may not proceed without a registered multiple-testing
    #: correction, a registered confidence level, and a non-empty registered
    #: control set. Requiring them here forces a human to *register* each decision
    #: — it chooses no method, level, or control (the same discipline as
    #: ``threshold`` carrying no default). ``controls`` is checked for
    #: non-emptiness separately because its unset sentinel is ``()``, not ``None``.
    REQUIRED_CONFIRMATORY_REGISTRATIONS: ClassVar[tuple[str, ...]] = (
        "multiplicity_method",
        "confidence_level",
    )

    def canonical_json(self) -> str:
        """Deterministic JSON serialization (sorted keys, no insignificant space).

        This is the exact byte sequence that :meth:`content_hash` digests, so
        two manifests with equal field values always produce the same hash,
        independent of field declaration order or process.
        """
        payload = dataclasses.asdict(self)
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))

    def content_hash(self) -> str:
        """SHA-256 hex digest of :meth:`canonical_json`.

        This is an honest, demonstrable byte-identity property of the *manifest*
        only. It is deliberately **not** a claim of byte-identical reproducibility
        of a whole experiment pipeline, which the external contract §33 forbids
        asserting unless separately demonstrated.
        """
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()

    def unfrozen_blockers(self) -> tuple[str, ...]:
        """Names of unfrozen Blocker 1-4 fields still ``None`` (empty when all frozen).

        This reports *only* the external reviews' named Blockers, preserving the
        one-to-one mapping documented on :attr:`UNFROZEN_SCIENTIFIC_FIELDS`. The
        confirmatory gate additionally requires the fields in
        :attr:`REQUIRED_CONFIRMATORY_REGISTRATIONS` — see
        :meth:`missing_confirmatory_registrations`.
        """
        return tuple(
            name for name in self.UNFROZEN_SCIENTIFIC_FIELDS if getattr(self, name) is None
        )

    def missing_confirmatory_registrations(self) -> tuple[str, ...]:
        """Every registration still missing for a confirmatory run (empty when ready).

        The Blocker 1-4 fields (:meth:`unfrozen_blockers`) **plus** the mandatory
        confirmatory registrations (a multiple-testing correction, a confidence
        level, and a non-empty control set). Empty exactly when
        :meth:`is_confirmatory_ready` is ``True``.
        """
        missing = list(self.unfrozen_blockers())
        missing.extend(
            name for name in self.REQUIRED_CONFIRMATORY_REGISTRATIONS if getattr(self, name) is None
        )
        if not self.controls:
            missing.append("controls")
        return tuple(missing)

    def is_confirmatory_ready(self) -> bool:
        """Whether the manifest is fully registered for a confirmatory run.

        Requires every unfrozen scientific decision (Blockers 1-4) to be frozen
        **and** every mandatory confirmatory registration
        (:attr:`REQUIRED_CONFIRMATORY_REGISTRATIONS` plus a non-empty
        ``controls``) to be set. ``False`` means the manifest may back only
        *exploratory* work and a confirmatory run must refuse to proceed — the
        code-level expression of ADR 0003's NO-GO. This is strictly stronger
        than "Blockers 1-4 frozen": it still returns ``False`` while any Blocker
        is unset, and additionally while a multiple-testing correction,
        confidence level, or control set is unregistered.
        """
        return len(self.missing_confirmatory_registrations()) == 0
