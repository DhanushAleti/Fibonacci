# Project PHI

Project PHI is a research-grade quantitative platform built to answer one specific, falsifiable question: do Golden Ratio (φ ≈ 1.6180339887) and Fibonacci-derived mathematical features carry statistically useful, out-of-sample predictive information about financial markets, once measured against realistic controls? See [docs/02-project/PHI_PRD.md](docs/02-project/PHI_PRD.md) for the full research question, hypotheses, and product requirements, and [docs/03-architecture/SYSTEM_ARCHITECTURE.md](docs/03-architecture/SYSTEM_ARCHITECTURE.md) for the architecture built to answer it. This repository currently contains the project's foundational documentation and repository scaffolding — application code has not yet been written.

**What PHI is not:** PHI is not a general-purpose academic/education platform. Earlier in this repository's history, a materially different "AcademicOS" documentation set (academic data, courses, assessments, grades, scheduling) was added alongside the Fibonacci research material under the same project name. That material has been separated out to [archive/academicos/](archive/academicos/README.md) so it isn't mistaken for this project's actual scope — see that folder's README for why, and [docs/ORGANIZATION_REPORT.md](docs/ORGANIZATION_REPORT.md) for the full identity-resolution audit. Nothing was deleted; no decision has been made about that material's future.

## Current Status

**Version:** 0.2.0 — Phase 0 (Engineering Foundation) and Phase 1 (Data Foundation) implemented and tested (see [CHANGELOG.md](CHANGELOG.md) and [docs/ROADMAP/NEXT_STEPS.md](docs/ROADMAP/NEXT_STEPS.md))

The PRD (`docs/02-project/PHI_PRD.md`) and architecture documents (`docs/03-architecture/`) are drafted with real content (not skeletons), and application code has now begun against them:

- **Implemented and tested:** `src/phi/{config,logging,cli}.py` (Phase 0), and `src/phi/data/` — time semantics / the T-1 information barrier, domain schemas, data validation (gap/duplicate/monotonicity/volume checks), a synthetic (test-only) data provider, a local Parquet-backed storage repository, and ingestion orchestration (Phase 1). 77 tests, 97% coverage, lint- and type-clean. Run `uv sync --extra dev && uv run pytest` to verify.
- **Not yet implemented:** feature engineering / the Golden Ratio feature laboratory (Phase 2), the event-driven backtester (Phase 3), statistical validation (Phase 4), and experiment tracking (Phase 5). No real market-data provider is connected — all validated data so far is clearly-labeled synthetic, never presented as market evidence. See [docs/ROADMAP/NEXT_STEPS.md](docs/ROADMAP/NEXT_STEPS.md) for what's done versus deferred, and [docs/18-decisions/](docs/18-decisions/) for implementation-environment decisions (e.g. why Phase 1 storage is Parquet rather than the architecture's committed PostgreSQL/TimescaleDB).
- `backend/`, `frontend/`, `models/`, `notebooks/` remain empty — correctly deferred to their respective phases.

## Roadmap

See [docs/19-roadmap/README.md](docs/19-roadmap/README.md) for the roadmap and [docs/REFERENCE/MILESTONES.md](docs/REFERENCE/MILESTONES.md) for the proposed phased milestone plan. At a high level, the next step after this foundation release is to move the PRD and architecture documents from skeletons to reviewed, real content ahead of any application code.

## Repository Structure

```
project-phi/
├── backend/                   # Backend service code (not yet started)
├── frontend/                  # Frontend application code (not yet started)
├── data/                      # Data assets and pipelines (not yet started)
├── models/                    # ML/AI model artifacts (not yet started)
├── notebooks/                 # Research and analysis notebooks (not yet started)
├── scripts/                   # Utility and automation scripts (not yet started)
├── tests/                     # Test suites (not yet started)
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
