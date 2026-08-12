# Changelog

All notable changes to Project PHI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Phase 0 — Engineering Foundation:** `pyproject.toml` (uv/hatchling build, pinned runtime deps: polars, numpy, pydantic; dev deps: pytest, pytest-cov, hypothesis, ruff, mypy); `src/phi/{__init__,config,logging,cli}.py` — deterministic settings, secret handling (never hardcoded, never logged), structured JSON logging, a minimal introspection CLI (`phi version`, `phi info`).
- **Phase 1 — Data Foundation** (`src/phi/data/`): the time-semantics backbone and T-1/information-barrier enforcement (`time.py`); domain schemas for `Instrument`, `PriceBar`, `DataProvenance`, `DataQualityFlag` (`schemas.py`); a minimal weekday-based trading calendar (`calendar.py`); Data Validation covering gap detection, duplicate/conflict handling, arrival-order monotonicity, and leave-one-out volume-plausibility checks (`validation.py`); a deterministic, clearly-labeled synthetic OHLCV provider for engineering validation only (`providers/synthetic.py`); a local, content-hashed, append-only Parquet-backed `PriceBarRepository` (`storage.py`); ingestion orchestration (`ingestion.py`); and a point-in-time query helper plus a worked example demonstrating availability-time-vs-decision-time correctness end to end, satisfying PRD-ACCEPT-002 (`pointintime.py`).
- **Phase 0.5 — Design Lock:** the canonical first φ feature and its six-category matched control set frozen to implementation-grade precision — [ADR 0002](docs/18-decisions/0002-phase2-feature-and-control-design-lock.md) and the [feature & control contract](docs/05-mathematics/phi-retracement-feature-contract.md).
- **Phase 2 — φ-feature construction** (`src/phi/features/`): the authoritative rolling-window candidate `f_A(t) = |p_t − 1/φ|` and its six-category matched control set (A/B/C1/C2/D/E/F) over one shared leakage-safe pipeline (`L = 20`), with an adversarial future-injection leakage test. The excursion-retracement **arithmetic** (`retracement.py`) is present as Phase-4 guidance only (anchor selector and `ε_φ` deliberately unimplemented).
- **Experiment infrastructure** (`src/phi/experiment/`, science-neutral): an immutable content-hashed pre-registration manifest whose `is_confirmatory_ready()` refuses confirmatory analysis while the scientific blockers are unfrozen; an exclusion-accounting ledger; and code/environment provenance capture (git SHA + lockfile hash).
- **Phase 4 — confirmatory methodology** (`src/phi/phase4/`): the now-frozen (GO-with-conditions) methodology implemented exactly to the Phase-4 Specification — deterministic three-point extrema anchor, per-excursion terminal retracements, continuous φ-distance, the `Δ_φ` vs matched-constants estimand, stationary-bootstrap dependence-aware inference (Politis–Romano + automatic Politis–White block length, `B=10,000`), Holm multiplicity, the null-DGP false-positive **calibration** and **power** harnesses, strict discovery/confirmation/replication separation, and a **fail-closed** confirmatory gate that refuses to run until the numerical pre-registration is complete and the validation gates pass. See the [Phase-4 contract](docs/05-mathematics/phi-phase4-scientific-contract.md) and [readiness report](docs/21-releases/PHI_PHASE4_READINESS.md). **No confirmatory experiment has been run.** A documented, locked finding: the primary estimand as specified is not null-calibrated (Jensen bias ⇒ FPR ≈ 1.0), so it fails the contract's own hard gate — resolving it is a methodologist decision, not a code change.
- **Phase 4 — synthetic false-positive torture test** (`scripts/phase4_synthetic_validation.py`, `results/phase4_validation/results.json`, [report](docs/21-releases/PHI_PHASE4_SYNTHETIC_VALIDATION.md)): the frozen pipeline run against 13 known-null processes plus positive/negative controls, a constant sweep, a leakage battery, and reproducibility checks. **Verdict: FAIL** — false-positive rate = 1.0 on every null; the constant sweep shows φ is *not* specifically preferred; construction/leakage/reproducibility are sound. PHI is **not cleared for real data** until the estimand is revised.
- **Phase 4 — arbitrated repair** (`src/phi/phase4/repair/`, [report](docs/21-releases/PHI_PHASE4_REPAIR_READINESS.md)): the surrogate-standardized `Z_φ` estimand (`Δ_φ > 0` permanently forbidden as confirmatory), rational-fraction controls `{1/2,3/5,5/8,2/3}` (φ must beat 5/8), a block-permutation/GARCH/IAAFT surrogate ensemble, a φ-attractor GARCH positive control, a granularity audit, a five-part acceptance gate, and a fail-closed confirmatory path with confirmatory/secondary/exploratory separation. **Status: IMPLEMENTATION COMPLETE / VALIDATION PENDING.** Small-scale validation: FPR 1.0 → **0.011**, power **0.82**, constant-sweep symmetric — but the **granularity gate fails** (φ FPR 0.22 at the coarsest tick grid), reported honestly and not tuned away. PHI stays fail-closed / not cleared for real data.
- [ADR 0002](docs/18-decisions/0002-phase2-feature-and-control-design-lock.md) and [ADR 0003](docs/18-decisions/0003-phase2-external-review-nogo-and-feature-authority.md) — the design lock and the external-review NO-GO / feature-authority decision (Option B: rolling-window authoritative; excursion = Phase-4 guidance).
- [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) and [`CONTRIBUTING.md`](CONTRIBUTING.md) — exact reproduction commands and the scientific-integrity contribution rules.
- [docs/18-decisions/0001-phase1-local-storage-implementation.md](docs/18-decisions/0001-phase1-local-storage-implementation.md) — first ADR, recording why Phase 1 storage is a local Parquet repository rather than the architecture's committed PostgreSQL/TimescaleDB (no database server available in this development environment).

### Fixed

- **Non-finite prices could silently pass validation** and produce a plausible-looking feature value (`+inf` high → range `inf` → `p = 0.0` → a fake φ-hit). `PriceBar` now rejects `±inf`/`NaN` at construction (`allow_inf_nan=False`), making the "non-finite impossible" premise the feature layer relies on actually true (audit I-1).
- **Confirmatory-readiness gate was too weak** — a manifest could be "ready" without a registered multiplicity correction, confidence level, or control set. `is_confirmatory_ready()` now requires all three, strictly stronger than the Blocker 1–4 check (audit I-2).
- **Determinism test overstated its coverage** — added a real cross-process determinism test (fresh interpreter, unpinned hash seed, SHA-256 of the output) (audit I-3).
- **Category F zero-denominator edge** made unrepresentable by guarding `window ≥ 2` at the pipeline boundary (audit I-11).

### Changed

- The experiment manifest now binds **code and environment provenance** (`code_version`, `environment_lock_hash`), so equal manifest hashes imply the same *executable* experiment, not just the same parameters (audit I-5; contract §26, §36).
- Test suite grew to the full Phase 0–2 + experiment set (property-based via Hypothesis, leakage, determinism, reproducibility); the suite passes at ~98% branch coverage, Ruff- and mypy-clean. Run `uv run pytest` for the live count.

## [0.1.0] - 2026-08-02 — AIOS Foundation

### Added

- Repository initialization for Project PHI
- AI Operating System (AIOS) documentation structure under `docs/`, spanning 22 numbered sections (`00-ai-command-center` through `21-releases`)
- `PHI_SYSTEM.md` — AIOS behavior contract playbook (draft)
- Foundational AIOS documentation structure (draft)
- `PHI_PRD.md` — Product Requirements Document skeleton (25 sections, all placeholders pending content)
- Architecture document skeletons: system, AI, API, backend, frontend, database, and data architecture (`docs/03-architecture/`)
- AI playbook skeletons for architect, engineer, research, and analyst roles (`docs/01-ai-playbooks/`)
- Document templates: ADR, API, bug, feature, meeting, model card, PRD, release, research, test plan (`docs/15-templates/`)
- Workflow skeletons: bug, code review, deployment, feature, model training, release, research (`docs/16-workflows/`)
- Standards skeletons: Docker, documentation, FastAPI, Git, Next.js, PostgreSQL, Python, testing, TypeScript (`docs/17-standards/`)
- Top-level project scaffolding: `backend/`, `frontend/`, `data/`, `models/`, `notebooks/`, `scripts/`, `tests/`, `.github/`
- `.gitignore` configured for Python and general project artifacts

### Changed

- Repository cleaned up: removed macOS filesystem artifacts (e.g. `.DS_Store`) and hardened `.gitignore`

[Unreleased]: https://github.com/DhanushAleti/project-phi/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/DhanushAleti/project-phi/releases/tag/v0.1.0
