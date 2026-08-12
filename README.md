# Project PHI

Project PHI is a research-grade quantitative platform built to answer one specific, falsifiable question: does a **pre-specified φ-retracement structure** (built from the Golden Ratio, φ ≈ 1.6180339887) occur in eligible market observations at a frequency or magnitude **distinguishable from appropriately matched non-φ controls**, under an information-safe, multiplicity-controlled procedure? See [docs/02-project/PHI_PRD.md](docs/02-project/PHI_PRD.md) for the full research question and hypotheses, [docs/03-architecture/SYSTEM_ARCHITECTURE.md](docs/03-architecture/SYSTEM_ARCHITECTURE.md) for the architecture, and the frozen [feature & control contract](docs/05-mathematics/phi-retracement-feature-contract.md) for the exact, implementation-grade specification.

> **Scientific-claim boundary (read first).** PHI has produced **no φ result, and makes no φ claim.** What is implemented is the *leakage-safe construction* of one candidate feature and six matched controls, plus science-neutral pre-registration/reproducibility infrastructure that is deliberately **prevented in code** from running a confirmatory analysis while the core scientific decisions are unfrozen. Passing tests and high coverage are **engineering facts, not scientific validation** (per the [authoritative contract](docs/05-mathematics/phi-retracement-feature-contract.md) §0A and PRD-GRF-012). The eventual verdict — *evidence for*, *no convincing evidence*, or *evidence against* — belongs to a properly registered experiment that has **not** been run.

**What PHI is not:** PHI is not a general-purpose academic/education platform. Earlier in this repository's history, a materially different "AcademicOS" documentation set (academic data, courses, assessments, grades, scheduling) was added alongside the Fibonacci research material under the same project name. That material has been separated out to [archive/academicos/](archive/academicos/README.md) so it isn't mistaken for this project's actual scope — see that folder's README for why, and [docs/ORGANIZATION_REPORT.md](docs/ORGANIZATION_REPORT.md) for the full identity-resolution audit. Nothing was deleted; no decision has been made about that material's future.

## Current Status

**Version:** 0.2.0 — Phases 0–2 (engineering, data, φ-feature construction) plus science-neutral experiment infrastructure are implemented and tested. The full suite passes at ~98% branch coverage, Ruff- and mypy-clean; run `uv sync --extra dev && uv run pytest` for the live count (see [REPRODUCIBILITY.md](REPRODUCIBILITY.md)).

- **Implemented and tested:**
  - **Phase 0 — engineering:** `src/phi/{config,logging,cli}.py` — deterministic settings, secret-safe structured logging, an introspection CLI.
  - **Phase 1 — data:** `src/phi/data/` — time semantics / the T-1 information barrier, domain schemas (non-finite prices rejected at construction), validation (gap/duplicate/monotonicity/volume), a clearly-labeled **synthetic** provider, a Parquet-backed repository, ingestion, and point-in-time queries.
  - **Phase 2 — φ-feature construction** (`src/phi/features/`): the **authoritative** rolling-window candidate `f_A(t) = |p_t − 1/φ|` and its **six-category matched control set** (A/B/C1/C2/D/E/F), all sharing one leakage-safe pipeline, `L = 20`, with an adversarial future-injection leakage test. Also present: the excursion-retracement **arithmetic** (`retracement.py`) as **Phase-4 guidance only**, per the feature-authority decision ([ADR 0003](docs/18-decisions/0003-phase2-external-review-nogo-and-feature-authority.md)).
  - **Experiment infrastructure** (`src/phi/experiment/`, science-neutral): an immutable, content-hashed pre-registration **manifest** whose `is_confirmatory_ready()` refuses to authorize confirmatory analysis while the scientific blockers are unfrozen; an **exclusion-accounting** ledger; and **provenance** capture (git SHA + lockfile hash).
  - **Phase 4 — confirmatory methodology** (`src/phi/phase4/`): the now-frozen (GO-with-conditions) methodology implemented exactly — deterministic three-point extrema anchor, per-excursion retracements, continuous φ-distance, the Δ_φ vs matched-constants estimand, stationary-bootstrap dependence-aware inference, Holm multiplicity, the null-DGP false-positive calibration + power harnesses, strict discovery/confirmation/replication separation, and a **fail-closed** confirmatory gate. See the [Phase-4 contract](docs/05-mathematics/phi-phase4-scientific-contract.md).
- **Confirmatory execution is NOT authorized (fail-closed).** The methodology is frozen, but *running* it is blocked in code until a human registers the numerical pre-registration (exact control set `C`, `δ_min`, Dataset A/B) and the validation gates pass. **Honest finding:** the primary estimand *as specified* is **not null-calibrated** — by Jensen's inequality a symmetric control set makes `Δ_φ ≥ 0` on pure noise (empirical false-positive rate ≈ 1.0), so it fails the contract's own hard gate (§XLIV). This correctly keeps confirmatory analysis blocked and is a **methodologist decision to resolve**, not a code fix. A full **synthetic false-positive torture test** ([report](docs/21-releases/PHI_PHASE4_SYNTHETIC_VALIDATION.md)) confirms it: FPR = 1.0 across all 13 null processes, and a constant sweep shows φ is *not* preferred over other constants. The arbitrated **repair** (`src/phi/phase4/repair/`, [report](docs/21-releases/PHI_PHASE4_REPAIR_READINESS.md)) replaces `Δ_φ` with a surrogate-standardized `Z_φ`, rational-fraction controls, and a five-part gate: small-scale validation cuts FPR from **1.0 → 0.011** with power 0.82, but the **granularity gate still fails** at the coarsest tick grid (φ FPR 0.22). So PHI remains **not cleared for real data** and the confirmatory path stays fail-closed. See also the [Phase-4 readiness report](docs/21-releases/PHI_PHASE4_READINESS.md).
- **No real market data** is connected — all validated data is clearly-labeled synthetic and never presented as market evidence (PRD-OPEN-001 open by design). `backend/`, `frontend/`, `models/`, `notebooks/` remain empty, deferred to later phases.

## Roadmap

See [docs/ROADMAP/NEXT_STEPS.md](docs/ROADMAP/NEXT_STEPS.md) for what is done versus deferred, and [docs/19-roadmap/README.md](docs/19-roadmap/README.md) / [docs/REFERENCE/MILESTONES.md](docs/REFERENCE/MILESTONES.md) for the milestone plan. The next milestone is **not** more feature code: it is the human freezing of the four scientific blockers (anchor algorithm, `ε_φ`, primary estimand, dependence-aware inference) that alone can authorize a confirmatory Phase-4 experiment.

## Repository Structure

```
project-phi/
├── src/phi/                   # Implementation: config/logging/cli, data/, features/, experiment/
├── tests/                     # Test suite (data/, features/, experiment/) — mirrors src/phi
├── backend/                   # Backend service code (not yet started)
├── frontend/                  # Frontend application code (not yet started)
├── data/                      # Data assets and pipelines (not yet started)
├── models/                    # ML/AI model artifacts (not yet started)
├── notebooks/                 # Research and analysis notebooks (not yet started)
├── scripts/                   # Utility and automation scripts (not yet started)
├── docs/                      # AI Operating System (AIOS) documentation
│   ├── 00-ai-command-center/  # Docs entry point / index
│   ├── 01-ai-playbooks/       # AI role playbooks (PHI_SYSTEM.md, etc.)
│   ├── 02-project/            # Project-level context and PRD
│   ├── 03-architecture/       # System/AI/API/backend/frontend/data/database architecture
│   ├── 04-research/           # Research notes
│   ├── 05-mathematics/        # Quantitative/mathematical foundations
│   ├── 06-ai/                 # AI/ML documentation
│   ├── 07-backend/            # Backend documentation
│   ├── 08-frontend/           # Frontend documentation
│   ├── 09-data/               # Data documentation
│   ├── 10-api/                # API documentation
│   ├── 11-testing/            # Testing documentation
│   ├── 12-security/           # Security documentation
│   ├── 13-devops/             # DevOps documentation
│   ├── 14-prompts/            # Prompt library
│   ├── 15-templates/          # Reusable document templates
│   ├── 16-workflows/          # Process workflows
│   ├── 17-standards/          # Engineering standards
│   ├── 18-decisions/          # Architecture Decision Records
│   ├── 19-roadmap/            # Roadmap
│   ├── 20-meeting-notes/      # Meeting notes
│   ├── 21-releases/           # Release notes
│   └── REFERENCE/             # GitHub labels, milestones, and other reference docs
├── archive/                    # Isolated, non-canonical material (e.g. archive/academicos/ — see its README)
├── .github/                   # GitHub configuration
├── CHANGELOG.md               # Version history (Keep a Changelog format)
├── VERSION                    # Current version string
└── README.md                  # This file
```

## Getting Started

1. Clone the repository.
2. `uv sync --extra dev` to install pinned dependencies into `.venv`.
3. `uv run pytest` to run the test suite (`ruff check .` and `uv run mypy` for lint/type-checking).
4. Start at [docs/00-ai-command-center/README.md](docs/00-ai-command-center/README.md) — the entry point and index for all documentation.
5. Read [docs/02-project/PHI_PRD.md](docs/02-project/PHI_PRD.md) for product context and [docs/03-architecture/README.md](docs/03-architecture/README.md) for the architecture overview.
6. Review [docs/17-standards/README.md](docs/17-standards/README.md) and [docs/16-workflows/README.md](docs/16-workflows/README.md) before contributing.

## Documentation

All project documentation lives under [`docs/`](docs/), organized into numbered sections by topic. Each section has its own `README.md` describing its purpose, scope, and conventions. See [docs/00-ai-command-center/README.md](docs/00-ai-command-center/README.md) as the starting point.

Reusable document templates (PRD, ADR, feature, bug, release, etc.) are available in [docs/15-templates/](docs/15-templates/).

## Development Workflow

Process workflows are documented in [docs/16-workflows/](docs/16-workflows/), covering feature development, bug fixes, code review, deployment, model training, release, and research. Engineering standards (Git, testing, Docker, and per-stack conventions) are documented in [docs/17-standards/](docs/17-standards/). Architecture Decision Records are tracked in [docs/18-decisions/](docs/18-decisions/).
