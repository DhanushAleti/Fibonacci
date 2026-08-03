# Changelog

All notable changes to Project PHI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-08-02 — AIOS Foundation

### Added

- Repository initialization for Project PHI
- AI Operating System (AIOS) documentation structure under `docs/`, spanning 22 numbered sections (`00-ai-command-center` through `21-releases`)
- `PHI_SYSTEM.md` — AIOS behavior contract playbook (draft)
- Master blueprint and foundational AIOS documentation (draft)
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
