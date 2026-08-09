# Project PHI — File Inventory

Generated from a direct audit of repository contents, updated 2026-08-10 after identity resolution and AcademicOS isolation. Classifications: `FIBONACCI_CORE`, `FIBONACCI_SUPPORTING`, `ACADEMICOS`, `ARCHIVED`, `HISTORICAL`, `SHARED/UNCERTAIN`, `UNKNOWN — REQUIRES REVIEW`. Boilerplate `.gitkeep` placeholders and per-section index READMEs are grouped rather than listed individually.

## Root

| Path | Purpose | Classification | Notes |
|---|---|---|---|
| `README.md` | Project overview, structure, getting-started | FIBONACCI_SUPPORTING | Updated this session to explicitly state PHI's identity and disclaim AcademicOS |
| `CHANGELOG.md` | Version history (Keep a Changelog) | FIBONACCI_SUPPORTING | Generic scaffolding history, no domain-specific content |
| `TODO.md` | High-level task list | FIBONACCI_SUPPORTING | Generic stubs (Backend, Frontend, AI Engine, Database, Authentication, Deployment) — not academic-specific |
| `VERSION` | Version string | FIBONACCI_SUPPORTING | `0.1.0` |
| `.gitignore` | Python/Node/OS exclusions | FIBONACCI_SUPPORTING | Already excludes `.env`/`.venv` |

## FIBONACCI_CORE — the actual research definition

| Path | Purpose | Status |
|---|---|---|
| `docs/02-project/PHI_PRD.md` | Full PRD — research question, hypothesis, control framework, backtesting/validation requirements, phase plan | Draft, substantially complete (448 lines) |
| `docs/03-architecture/SYSTEM_ARCHITECTURE.md` | System architecture built to satisfy the PRD | Substantially drafted |
| `docs/04-research/RESEARCH_HYPOTHESES.md` | Formal H1/H0 hypothesis statements | Drafted |
| `docs/04-research/VALIDATION_CHECKLIST.md` | Validation methodology checklist | Drafted |

## FIBONACCI_SUPPORTING — generic infrastructure currently serving the Fibonacci project

| Path | Purpose | Status |
|---|---|---|
| `docs/03-architecture/{AI,API,BACKEND,DATABASE,DATA,FRONTEND}_ARCHITECTURE.md` | Per-layer architecture docs | Drafted; reviewed for academic content — clean |
| `docs/01-ai-playbooks/PHI_SYSTEM.md` | AIOS behavior contract for AI collaborators | Draft, domain-agnostic |
| `docs/01-ai-playbooks/{chatgpt_architect,claude_engineer,code_review,debugging,feature_planning,gemini_analyst,perplexity_research}.md` | Role-specific AI playbooks | Drafted, domain-agnostic |
| `docs/15-templates/*.md` (10 files) | Reusable templates | Active, domain-agnostic |
| `docs/16-workflows/*.md` (7 files) | Process workflows | Drafted, domain-agnostic |
| `docs/17-standards/*.md` (9 files) | Engineering standards | Drafted, domain-agnostic |
| `docs/21-releases/v0.1.0.md` | Release notes for v0.1.0 | Active |
| `docs/REFERENCE/MILESTONES.md`, `docs/REFERENCE/GITHUB_LABELS.md` | Reference material | Drafted |
| `docs/ROADMAP/NEXT_STEPS.md` | **Canonical** roadmap for Project PHI | Active — items are generic engineering milestones, not academic-specific |
| `docs/research/RESEARCH_LOG.md` | **Canonical** chronological research/development log | Active — see HISTORICAL note below re: its content |

## SHARED / UNCERTAIN

| Path | Purpose | Notes |
|---|---|---|
| `docs/DEVELOPMENT_PRINCIPLES.md` | 6 development principles | 5 of 6 principles are generic and reusable (source of truth, incremental implementation, explicit unknowns, test-before-expansion, traceability). Principle #3 ("Evidence First") contains one AcademicOS-flavored sentence: "Academic automation should rely on verified source data instead of assumptions." **Not archived** — moving the whole file would strip genuinely useful, actively-relevant content from the Fibonacci project. Left in place, flagged here. Content not rewritten (out of scope for an organization pass). |

## ARCHIVED — moved to `archive/academicos/` this session

| Path (new) | Path (original) | Why archived |
|---|---|---|
| `archive/academicos/ARCHITECTURE_NOTES.md` | `docs/ARCHITECTURE_NOTES.md` | 100% AcademicOS content — four-layer architecture for academic data/portals/planning, zero Fibonacci content |
| `archive/academicos/DATA_QUALITY_RULES.md` | `docs/DATA_QUALITY_RULES.md` | 100% AcademicOS content — rules framed around "academic data" and "semester information" |
| `archive/academicos/IMPLEMENTATION_CHECKLIST.md` | `docs/IMPLEMENTATION_CHECKLIST.md` | Substantively AcademicOS (Academic Data / Integrations / Intelligence sections); its one generic "Foundation" subsection is independently preserved in `README.md`/`CHANGELOG.md`, so nothing unique was lost |
| `archive/academicos/RELEASE_READINESS.md` | `docs/RELEASE_READINESS.md` | Its "Release Rule" defines production-readiness in terms of "academic data flows," a definition that does not apply to the Fibonacci platform's own acceptance criteria (PRD §34) |

See `archive/academicos/README.md` for full rationale, commit provenance, and content summaries. Files were moved via plain filesystem move (not `git mv` — see Organization Report for why) and are currently showing as deleted-from-`docs/`+untracked-in-`archive/` in `git status`; content and history remain fully recoverable via git regardless.

## HISTORICAL — chronological log entries, left untouched

| Path | Status | Notes |
|---|---|---|
| `docs/research/RESEARCH_LOG.md` | Canonical (see FIBONACCI_SUPPORTING above) | Contains a historical entry (2026-08-09) that mentions "the PHI AcademicOS architecture" as a factual record of what was being worked on that day. This is a log of history, not AcademicOS material itself — left untouched and not archived. |
| `docs/04-research/RESEARCH_LOG.md` | Deprecated stub | Points to canonical log; content already merged there |
| `docs/research/2026-08-09.md` | Deprecated stub | Points to canonical log; content already merged there |
| `docs/logs/2026-08-05.md` | Deprecated stub | Points to canonical log; content already merged there |

## Index-Only Sections (scaffolded, not yet populated)

`docs/NN-topic/README.md` files describing what should eventually go in that section — flagged `UNKNOWN — REQUIRES REVIEW` for whether/when populated: `05-mathematics`, `06-ai`, `07-backend`, `08-frontend`, `09-data`, `10-api`, `11-testing`, `12-security`, `13-devops`, `14-prompts`, `18-decisions`, `20-meeting-notes`, `00-ai-command-center`. `19-roadmap/README.md` is also index-only but was actively rewritten as a pointer to the canonical roadmap (FIBONACCI_SUPPORTING).

## Code Scaffolding (empty)

`backend/`, `frontend/`, `data/`, `models/`, `notebooks/`, `scripts/`, `tests/` — each contains only `.gitkeep`. SHARED/UNCERTAIN: not yet used by either vision, confirmed empty by direct listing.

## Meta / Audit Documentation

| Path | Purpose |
|---|---|
| `docs/PROJECT_MAP.md` | Repository map, updated this session |
| `docs/FILE_INVENTORY.md` | This file |
| `docs/ORGANIZATION_REPORT.md` | Full audit trail of the identity-resolution and isolation work |
| `archive/academicos/README.md` | Explains the archived material |

## Secrets / Sensitive Material

None found. No `.env`, `.pem`, `.key`, credential, or token files exist anywhere in the repository (including `archive/academicos/`). `.gitignore` already excludes `.env`, `.envrc`, and virtual environments. Text matches for "secret"/"token"/"API key" are policy language inside `PHI_PRD.md` (e.g. PRD-SEC-001), not actual leaked values.

## Git

- Remote: `https://github.com/DhanushAleti/project-phi`
- Branch: `main`
- HEAD before and after this session: `70598e3` (unchanged — no commit made)
- Working tree: carries this session's uncommitted moves/edits plus the prior session's uncommitted documentation-drift cleanup — see `docs/ORGANIZATION_REPORT.md` for the full list
- No commits, branches, or history were modified
