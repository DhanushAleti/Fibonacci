# Project PHI — Project Map

**Status:** Current as of identity resolution + AcademicOS isolation (2026-08-10)

## Canonical Project

**PHI — Golden Ratio / Fibonacci Quantitative Research Platform**

## Primary Purpose

To answer one specific, falsifiable research question: do Golden Ratio (φ ≈ 1.6180339887) and Fibonacci-derived mathematical features carry statistically useful, out-of-sample predictive information about financial markets, once measured against realistic controls? PHI is not built to confirm that they do — it is built to find out, and to be equally credible whichever way the evidence points. (Source: `docs/02-project/PHI_PRD.md` §2.)

## Canonical Research Documents

- [`docs/02-project/PHI_PRD.md`](02-project/PHI_PRD.md) — Product Requirements Document: research question, hypotheses (H1/H0), 10 named φ-feature families (PRD-GRF-001…010; GRF-011/012 are process rules, not families — see [ADR 0002](18-decisions/0002-phase2-feature-and-control-design-lock.md)), mandatory 6-category control/placebo framework, backtesting/validation requirements, phase plan
- [`docs/03-architecture/SYSTEM_ARCHITECTURE.md`](03-architecture/SYSTEM_ARCHITECTURE.md) — system architecture built to satisfy the PRD (modular monolith, falsifiable research core, time-semantics, bias-prevention architecture)
- [`docs/04-research/RESEARCH_HYPOTHESES.md`](04-research/RESEARCH_HYPOTHESES.md) — formal hypothesis statements
- [`docs/04-research/VALIDATION_CHECKLIST.md`](04-research/VALIDATION_CHECKLIST.md) — validation methodology checklist

## Research Architecture (per PRD §14)

```text
Raw data → validation → point-in-time dataset
  → feature construction (Golden Ratio + baseline/placebo, in parallel)
  → control construction
  → train/validation/test separation
  → event-driven backtesting (realistic frictions)
  → walk-forward evaluation
  → statistical testing (multiple-testing aware)
  → robustness analysis
  → interpretation (support / inconclusive / falsified)
  → reproducible research record
```

No stage in this workflow has been implemented yet — see Current Phase below. This is the target architecture, not current status.

## Validation

Per PRD §20: out-of-sample testing, walk-forward testing, multi-regime evaluation, cross-asset validation, mandatory placebo comparison against 6 control categories, permutation testing, multiple-testing correction (Deflated Sharpe Ratio, Probability of Backtest Overfitting). None of this tooling exists yet — it is specified, not built.

## AcademicOS Material

**Isolated.** See [archive/academicos/README.md](../archive/academicos/README.md) for full detail. Summary: four documentation files (`ARCHITECTURE_NOTES.md`, `DATA_QUALITY_RULES.md`, `IMPLEMENTATION_CHECKLIST.md`, `RELEASE_READINESS.md`) describing an unrelated "AcademicOS" vision (academic data, courses, assessments, grades, scheduling) were committed under the same "Project PHI" name in a batch of four commits on 2026-08-09, separate from and inconsistent with the Fibonacci research vision. They have been moved, unmodified, to `archive/academicos/` with an explanatory README. No decision has been made about their long-term fate (delete, spin off, or otherwise) — that is intentionally left to you.

One related file, `docs/DEVELOPMENT_PRINCIPLES.md`, was reviewed and **kept in place** rather than archived: five of its six principles are generic and apply to the Fibonacci project as-is; only one sentence ("Academic automation should rely on verified source data instead of assumptions.") is AcademicOS-flavored. Flagged in `FILE_INVENTORY.md` rather than moved, to avoid stripping genuinely reusable content out of the active project.

## Current Phase

**Documentation-first (PRD Phase 0 — Research Specification).** No application code exists: `backend/`, `frontend/`, `data/`, `models/`, `notebooks/`, `scripts/`, `tests/` all contain only `.gitkeep` placeholders (confirmed by direct filesystem listing). `docs/02-project/PHI_PRD.md` and `docs/03-architecture/SYSTEM_ARCHITECTURE.md` are the most substantive, reviewed-level documents. Many `docs/` subsections (05 through 14, 18, 20) remain index-only READMEs describing what should eventually go there.

## Known Limitations / Unresolved Areas

- AcademicOS material's long-term disposition is undecided (archived, not deleted or resolved) — see above.
- `docs/DEVELOPMENT_PRINCIPLES.md` principle #3 contains one AcademicOS-flavored sentence not yet corrected — flagged, not edited, since content correction was out of scope for this organization pass.
- Several `docs/NN-topic/` sections remain unpopulated placeholders (expected for this phase).
- No code, data, or experiments exist yet to validate the research architecture against.

## Full Directory Structure

```text
project-phi/
├── README.md              → Project overview; now states PHI's identity explicitly and points to archive/academicos/
├── CHANGELOG.md           → Version history (Keep a Changelog format)
├── TODO.md                → High-level task list (generic stubs, not academic-specific)
├── VERSION                → Current version string (0.1.0)
├── .gitignore              → Python/Node/OS artifact exclusions; .env already ignored
│
├── archive/
│   └── academicos/          → Isolated AcademicOS material (4 files) + explanatory README
│
├── backend/ frontend/ data/ models/ notebooks/ scripts/ tests/   → SCAFFOLDED, EMPTY (.gitkeep only)
│
├── docs/
│   ├── PROJECT_MAP.md          → this file
│   ├── FILE_INVENTORY.md       → full artifact-by-artifact classification
│   ├── ORGANIZATION_REPORT.md  → full audit trail of all organization actions taken
│   │
│   ├── 00-ai-command-center/  → Docs entry point / master index
│   ├── 01-ai-playbooks/       → Role playbooks (generic — architect, engineer, researcher, analyst) + PHI_SYSTEM.md
│   ├── 02-project/            → PHI_PRD.md — FIBONACCI_CORE
│   ├── 03-architecture/       → SYSTEM_ARCHITECTURE.md — FIBONACCI_CORE; other *_ARCHITECTURE.md files generic/supporting
│   ├── 04-research/           → RESEARCH_HYPOTHESES.md, VALIDATION_CHECKLIST.md — FIBONACCI_CORE; RESEARCH_LOG.md here is a deprecated stub → docs/research/RESEARCH_LOG.md
│   ├── 05-mathematics/ … 14-prompts/  → index-only placeholders (generic)
│   ├── 15-templates/ 16-workflows/ 17-standards/  → generic, reusable, not domain-specific
│   ├── 18-decisions/ 20-meeting-notes/  → index-only placeholders
│   ├── 19-roadmap/             → navigation index → points to canonical roadmap
│   ├── 21-releases/            → release notes (v0.1.0.md)
│   ├── REFERENCE/              → GITHUB_LABELS.md, MILESTONES.md — generic
│   ├── ROADMAP/                → NEXT_STEPS.md — CANONICAL roadmap
│   ├── logs/                   → 2026-08-05.md — deprecated stub → docs/research/RESEARCH_LOG.md
│   ├── research/                → RESEARCH_LOG.md — CANONICAL chronological research/dev log; 2026-08-09.md — deprecated stub
│   └── DEVELOPMENT_PRINCIPLES.md  → SHARED/UNCERTAIN — see "Known Limitations" above
│
└── .github/                 → GitHub configuration (placeholder)
```
