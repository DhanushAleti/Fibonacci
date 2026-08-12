# Project PHI — Organization Report

**Latest update:** 2026-08-10 — Identity resolution + AcademicOS isolation
**Prior sessions:** 2026-08-10 — Documentation-drift cleanup (roadmap/research logs); System-wide discovery audit

---

## Identity Resolution (this session)

The repository was found to contain two materially different, non-overlapping product visions under the single name "Project PHI":

1. **Golden Ratio / Fibonacci quantitative research platform** — defined in `docs/02-project/PHI_PRD.md`, `docs/03-architecture/SYSTEM_ARCHITECTURE.md`, `docs/04-research/RESEARCH_HYPOTHESES.md`, `docs/04-research/VALIDATION_CHECKLIST.md`. This is extensively developed (448-line PRD with named hypotheses, 10 φ-feature families — PRD-GRF-001…010; GRF-011/012 are process rules, not families, see [ADR 0002](18-decisions/0002-phase2-feature-and-control-design-lock.md) — a mandatory 6-category control/placebo framework, phase plan) and consistently cross-referenced across those four documents.
2. **"AcademicOS"** — defined in `docs/ARCHITECTURE_NOTES.md`, `docs/DATA_QUALITY_RULES.md`, `docs/IMPLEMENTATION_CHECKLIST.md`, `docs/RELEASE_READINESS.md`. Describes an academic data/scheduling/assessment/planning platform with zero Fibonacci or golden-ratio content.

Git history shows these are not incremental evolution of one idea: the four AcademicOS files were added in a tight batch of four commits, all timestamped within two seconds of each other (`2026-08-09 23:15:17`–`18 +0530`) — `e177e67`, `5cf41e1`, `8af707b`, `70598e3` — after and separate from the Fibonacci research foundation (`fa5f0cf`, `c6d8de2`, `13901d7`, etc., committed 2026-08-07/08). The two visions never reference each other.

## Canonical Identity

**Project PHI is now treated as the Golden Ratio / Fibonacci quantitative research platform**, per the instruction that established this as the working conclusion. This is not an arbitrary tie-break: the Fibonacci vision is the older, more extensively developed, more internally cross-referenced material, and it is the vision independently confirmed as "the Fibonacci project" in an earlier verification session. The AcademicOS material does not meet the same bar of development or internal consistency and does not share any content with the Fibonacci vision.

## AcademicOS Material — What Happened To It

**Isolated in place, not deleted, not judged.** The four AcademicOS-authored files were moved from `docs/` to a new `archive/academicos/` directory, accompanied by a README explaining what they are, why they were isolated, their original paths, and the exact commits that introduced them. See `archive/academicos/README.md`.

No decision was made about whether this material should eventually be deleted, merged, or spun into its own project — that is explicitly left open, per instruction.

One related file was reviewed but **not** archived: `docs/DEVELOPMENT_PRINCIPLES.md`. Five of its six principles are generic and equally applicable to the Fibonacci project (source of truth, incremental implementation, explicit unknowns, test-before-expansion, traceability); only principle #3 contains one AcademicOS-flavored sentence. Archiving the whole file would have removed genuinely reusable content from the active project, so it was left in place and flagged in `docs/FILE_INVENTORY.md` instead (`SHARED/UNCERTAIN`). Its content was not rewritten.

## Files Moved

| From | To |
|---|---|
| `docs/ARCHITECTURE_NOTES.md` | `archive/academicos/ARCHITECTURE_NOTES.md` |
| `docs/DATA_QUALITY_RULES.md` | `archive/academicos/DATA_QUALITY_RULES.md` |
| `docs/IMPLEMENTATION_CHECKLIST.md` | `archive/academicos/IMPLEMENTATION_CHECKLIST.md` |
| `docs/RELEASE_READINESS.md` | `archive/academicos/RELEASE_READINESS.md` |

**Move mechanism note:** these were moved via a plain filesystem move, not `git mv`. `git mv`/`git add` failed with `fatal: Unable to create '.git/index.lock': File exists` — a stale lock file left in the mounted repository from an earlier process. Attempts to remove the lock (`rm -f .git/index.lock`) also failed with `Operation not permitted`, which appears to be a filesystem-level restriction on this specific pre-existing file rather than a repository problem. Read-only git commands (`status`, `diff`, `log`) continue to work normally. The practical effect is identical to `git mv`: `git status --short` shows the files as `D` (deleted) from their old path and `??` (untracked) under `archive/`; when this is eventually staged and committed (not done in this session), git's standard rename detection will recognize them as renames given the identical content. File content itself is byte-for-byte unchanged by the move.

## Files Renamed

None — file contents and names are unchanged; only directory location moved (see above).

## Files Archived

Same four files listed under "Files Moved" — `archive/` is the archive destination, so "moved" and "archived" refer to the same action in this case.

## Files Modified

- `README.md` — added two short paragraphs stating PHI's actual identity (Fibonacci research) and disclaiming AcademicOS, with a pointer to `archive/academicos/`. Also added `archive/` to the structure tree. No other content changed; the PRD/architecture were not rewritten.
- `docs/PROJECT_MAP.md` — rewritten to reflect final structure, canonical identity, and AcademicOS isolation (per PHASE 9 required format).
- `docs/FILE_INVENTORY.md` — rewritten with `FIBONACCI_CORE` / `FIBONACCI_SUPPORTING` / `ACADEMICOS` / `ARCHIVED` / `HISTORICAL` / `SHARED-UNCERTAIN` classification scheme.
- `docs/ORGANIZATION_REPORT.md` — this file.

## Files Created

- `archive/academicos/README.md`

## Files Untouched (important areas)

- `docs/02-project/PHI_PRD.md`, `docs/03-architecture/SYSTEM_ARCHITECTURE.md`, `docs/04-research/RESEARCH_HYPOTHESES.md`, `docs/04-research/VALIDATION_CHECKLIST.md` — the Fibonacci core, content unchanged
- `docs/DEVELOPMENT_PRINCIPLES.md` — reviewed, flagged, not moved or edited
- `docs/research/RESEARCH_LOG.md` and its deprecated-stub predecessors — untouched (contains a historical, factual mention of AcademicOS work, which is a log entry, not AcademicOS material itself)
- All empty scaffolding (`backend/`, `frontend/`, `data/`, `models/`, `notebooks/`, `scripts/`, `tests/`)
- All generic `docs/` sections (`15-templates/`, `16-workflows/`, `17-standards/`, `01-ai-playbooks/`, etc.)
- `CHANGELOG.md`, `TODO.md`, `VERSION`, `.gitignore` — unchanged

## References Checked

Searched the full repository for references to the four moved files by name. Only references found were inside `docs/PROJECT_MAP.md` and `docs/FILE_INVENTORY.md` — both of which were being rewritten anyway as part of this task. No README links, script paths, or other cross-references pointed to the moved files, so no additional repair was needed.

## Secrets / Security

No `.env`, `.pem`, `.key`, credential, or token files found anywhere in the repository, including inside the newly created `archive/academicos/`. `.gitignore` already covers standard secret patterns. No secret contents were printed at any point.

## Git Safety

- **HEAD before:** `70598e3` (unchanged after)
- **HEAD after:** `70598e3`
- **Branch:** `main`, still tracking `origin/main`
- **History:** fully preserved — all 20 prior commits, including the four AcademicOS-introducing commits, remain intact and unaltered. Moving the files did not touch commit history; it only changed working-tree file locations.
- No `reset`, `clean`, `stash`, `revert`, `rebase`, branch deletion, or force-push was performed.
- No commit or push was made this session.

## Validation Performed

- Full-content grep across the repository for academic-domain terms (`academic`, `student`, `course`, `assessment`, `grade`, `semester`, `LMS`, `learning management`) to find every AcademicOS-tainted file, not just the two originally flagged — this is how `IMPLEMENTATION_CHECKLIST.md` and `RELEASE_READINESS.md` were additionally identified (they were not part of the earlier verification's file list)
- Manual read of every flagged file's full content to distinguish genuine AcademicOS material from incidental/false-positive matches (e.g. "research-grade," "production-grade" in `SYSTEM_ARCHITECTURE.md`/`PHI_PRD.md`/`README.md` were false positives, correctly excluded)
- Commit-level provenance check (`git show -s --format` on each relevant commit) to establish when and how the AcademicOS material entered the repo
- Reference search for the four moved files' old paths, to confirm nothing else linked to them
- `git status --short` captured before and after every phase of work to confirm the pre-existing uncommitted changes were never disturbed
- Secrets scan repeated including the new `archive/` directory

## Remaining Ambiguities

- **AcademicOS's long-term fate is undecided by design.** Archived, not deleted, not spun into a separate project. This requires your decision, not an inference.
- **`docs/DEVELOPMENT_PRINCIPLES.md` principle #3** still contains one AcademicOS-flavored sentence. Flagged, not corrected, since editing document content (versus organizing file location) was treated as out of scope for this pass.
- **The stale `.git/index.lock`** could not be removed by this session (`Operation not permitted`). This blocked `git mv`/`git add`/any git write operation. A plain filesystem move was used instead, which is functionally equivalent but means the move is not yet staged in git's index — `git status --short` shows it as delete+untracked rather than a tracked rename. This does not lose any information and git will still detect it as a rename once staged, but you (or whoever has permission on the host filesystem) may want to manually clear that lock file before your next commit.
- Carried over from prior sessions: several `docs/NN-topic/README.md` sections remain index-only placeholders (expected for this project phase, not blocking).

## Working Tree State (uncommitted, unchanged in intent from prior sessions plus this session's additions)

This session's changes are layered on top of the prior session's uncommitted documentation-drift cleanup. Nothing from that prior work was reset, discarded, or altered. Combined, the working tree now carries:

- Modified: `docs/04-research/RESEARCH_LOG.md`, `docs/19-roadmap/README.md`, `docs/ROADMAP/NEXT_STEPS.md`, `docs/logs/2026-08-05.md`, `docs/research/2026-08-09.md` (prior session), plus `README.md`, `docs/PROJECT_MAP.md`, `docs/FILE_INVENTORY.md`, `docs/ORGANIZATION_REPORT.md` (this session, some of these were previously untracked and are now content-updated)
- Deleted from `docs/` (moved, not lost): `docs/ARCHITECTURE_NOTES.md`, `docs/DATA_QUALITY_RULES.md`, `docs/IMPLEMENTATION_CHECKLIST.md`, `docs/RELEASE_READINESS.md`
- New/untracked: `archive/` (containing the 4 moved files + README), `docs/research/RESEARCH_LOG.md` (prior session)

No commit or push has been made at any point across any of these sessions.

---

## Appendix — Prior Session Findings (preserved for context)

### System-Wide Discovery (first session)

A system-wide search was performed across `~/Documents` (including `~/Documents/GitHub`), `~/Desktop`, `~/Downloads`, and `~/code` for filenames and content matching `fibonacci`, `fib`, `fibo`, `golden ratio`, `fib retracement`, `fib extension`, `fibonacci retracement/extension/trading/strategy/levels`, excluding `node_modules`/`.venv`/`.git`. `~/Projects`, `~/Developer`, `~/Development`, `~/dev`, `~/workspace`, `~/repos`, `~/github` do not exist on this machine.

**Result:** exactly one project matched — `~/Documents/project-phi`. One other git repo, `~/Documents/GitHub/tesla46`, was inspected and ruled unrelated (bare README, unrelated commit history, zero Fibonacci content on full-content search). All other "golden ratio"/"fib" matches system-wide were third-party library internals (`plotly`, `scipy`, `sympy`, `mpmath`, `reusify`, npm `effect` package, a font file) — dependency noise, not user content.

### Documentation-Drift Cleanup (second session)

Resolved pre-existing internal duplication:
- **Roadmap:** `docs/ROADMAP/NEXT_STEPS.md` established as canonical; `docs/19-roadmap/README.md` converted to a navigation index.
- **Research/development log:** `docs/research/RESEARCH_LOG.md` created as canonical, merging verbatim the three previously scattered dated entries (2026-08-05 dev log, 2026-08-08 research log, 2026-08-09 research log). The three original files were converted to deprecation stubs, not deleted.

No information was lost in either prior session; see git diffs from those sessions for exact before/after content.
