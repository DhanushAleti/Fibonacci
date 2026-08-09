# Project PHI

Project PHI is a research-grade quantitative platform built to answer one specific, falsifiable question: do Golden Ratio (φ ≈ 1.6180339887) and Fibonacci-derived mathematical features carry statistically useful, out-of-sample predictive information about financial markets, once measured against realistic controls? See [docs/02-project/PHI_PRD.md](docs/02-project/PHI_PRD.md) for the full research question, hypotheses, and product requirements, and [docs/03-architecture/SYSTEM_ARCHITECTURE.md](docs/03-architecture/SYSTEM_ARCHITECTURE.md) for the architecture built to answer it. This repository currently contains the project's foundational documentation and repository scaffolding — application code has not yet been written.

**What PHI is not:** PHI is not a general-purpose academic/education platform. Earlier in this repository's history, a materially different "AcademicOS" documentation set (academic data, courses, assessments, grades, scheduling) was added alongside the Fibonacci research material under the same project name. That material has been separated out to [archive/academicos/](archive/academicos/README.md) so it isn't mistaken for this project's actual scope — see that folder's README for why, and [docs/ORGANIZATION_REPORT.md](docs/ORGANIZATION_REPORT.md) for the full identity-resolution audit. Nothing was deleted; no decision has been made about that material's future.

## Current Status

**Version:** 0.1.0 — AIOS Foundation (see [CHANGELOG.md](CHANGELOG.md) and [docs/21-releases/v0.1.0.md](docs/21-releases/v0.1.0.md))

The repository is in a documentation-first phase:

- The AI Operating System (AIOS) documentation structure is in place under `docs/`
- The Product Requirements Document (`docs/02-project/PHI_PRD.md`) and architecture documents (`docs/03-architecture/`) exist as reviewed skeletons — every section is explicitly marked `Status: Draft` with open TODOs
- `backend/`, `frontend/`, `data/`, `models/`, `notebooks/`, `scripts/`, and `tests/` are scaffolded but currently empty

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

This project does not yet have runnable application code, so there is no build or run step at this stage. To get oriented:

1. Clone the repository.
2. Start at [docs/00-ai-command-center/README.md](docs/00-ai-command-center/README.md) — the entry point and index for all documentation.
3. Read [docs/02-project/PHI_PRD.md](docs/02-project/PHI_PRD.md) for product context and [docs/03-architecture/README.md](docs/03-architecture/README.md) for the architecture overview.
4. Review [docs/17-standards/README.md](docs/17-standards/README.md) and [docs/16-workflows/README.md](docs/16-workflows/README.md) before contributing.

## Documentation

All project documentation lives under [`docs/`](docs/), organized into numbered sections by topic. Each section has its own `README.md` describing its purpose, scope, and conventions. See [docs/00-ai-command-center/README.md](docs/00-ai-command-center/README.md) as the starting point.

Reusable document templates (PRD, ADR, feature, bug, release, etc.) are available in [docs/15-templates/](docs/15-templates/).

## Development Workflow

Process workflows are documented in [docs/16-workflows/](docs/16-workflows/), covering feature development, bug fixes, code review, deployment, model training, release, and research. Engineering standards (Git, testing, Docker, and per-stack conventions) are documented in [docs/17-standards/](docs/17-standards/). Architecture Decision Records are tracked in [docs/18-decisions/](docs/18-decisions/).
