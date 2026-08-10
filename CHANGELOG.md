# Changelog

All notable changes to Project PHI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Phase 0 — Engineering Foundation:** `pyproject.toml` (uv/hatchling build, pinned runtime deps: polars, numpy, pydantic; dev deps: pytest, pytest-cov, hypothesis, ruff, mypy); `src/phi/{__init__,config,logging,cli}.py` — deterministic settings, secret handling (never hardcoded, never logged), structured JSON logging, a minimal introspection CLI (`phi version`, `phi info`).
- **Phase 1 — Data Foundation** (`src/phi/data/`): the time-semantics backbone and T-1/information-barrier enforcement (`time.py`); domain schemas for `Instrument`, `PriceBar`, `DataProvenance`, `DataQualityFlag` (`schemas.py`); a minimal weekday-based trading calendar (`calendar.py`); Data Validation covering gap detection, duplicate/conflict handling, arrival-order monotonicity, and leave-one-out volume-plausibility checks (`validation.py`); a deterministic, clearly-labeled synthetic OHLCV provider for engineering validation only (`providers/synthetic.py`); a local, content-hashed, append-only Parquet-backed `PriceBarRepository` (`storage.py`); ingestion orchestration (`ingestion.py`); and a point-in-time query helper plus a worked example demonstrating availability-time-vs-decision-time correctness end to end, satisfying PRD-ACCEPT-002 (`pointintime.py`).
- [docs/18-decisions/0001-phase1-local-storage-implementation.md](docs/18-decisions/0001-phase1-local-storage-implementation.md) — first ADR, recording why Phase 1 storage is a local Parquet repository rather than the architecture's committed PostgreSQL/TimescaleDB (no database server available in this development environment).
- 77 tests (unit, leakage, property-based via Hypothesis), 97% coverage, ruff- and mypy-clean.

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
