# Archive — AcademicOS Material

**What this is:** four documentation files that were originally committed inside `docs/` under the "Project PHI" name, but describe a materially different, unrelated product vision — an "AcademicOS" combining academic data, schedules, assessments, grades, and academic planning automation. This has no meaningful overlap with PHI's Golden Ratio/Fibonacci quantitative market research vision (see `docs/02-project/PHI_PRD.md`).

**Why isolated:** the repository's git history shows these four files were added in a single batch (four commits, all timestamped `2026-08-09 23:15:17–18 +0530`), immediately after and separate from the earlier, more extensively developed Fibonacci research documentation (PRD, system architecture, research hypotheses — committed on 2026-08-07/08). The two visions do not reference each other and describe incompatible products. To avoid ambiguity about what PHI actually is, this material has been separated from the active documentation tree rather than left mixed in.

**What was NOT done:** nothing was deleted. No judgment was made about which vision is "correct" or whether AcademicOS should eventually become its own project, be merged, or be discarded — that decision belongs to the project owner, not to this reorganization. This is Option A (archive-in-place) rather than Option B (spin off as a separate project) because there isn't yet enough independent structure (no code, no separate scaffolding, no distinct history) to justify a second canonical project location.

## Original locations

| File | Original path | Commit that added it |
|---|---|---|
| `ARCHITECTURE_NOTES.md` | `docs/ARCHITECTURE_NOTES.md` | `e177e67` — "docs: document PHI architecture layers" |
| `DATA_QUALITY_RULES.md` | `docs/DATA_QUALITY_RULES.md` | `5cf41e1` — "docs: define academic data quality rules" |
| `IMPLEMENTATION_CHECKLIST.md` | `docs/IMPLEMENTATION_CHECKLIST.md` | `8af707b` — "docs: add PHI implementation checklist" |
| `RELEASE_READINESS.md` | `docs/RELEASE_READINESS.md` | `70598e3` — "docs: add PHI release readiness checklist" |

All four commits are still present, unaltered, in `main`'s history — moving these files did not remove or rewrite that history. Their content is unchanged from the original; only their location moved.

## Content summary (for orientation, not evaluation)

- **`ARCHITECTURE_NOTES.md`** — describes four layers (Data: student info/courses/assessments/marks/grades/academic goals; Integration: academic portals/email/calendar/LMS; Intelligence: planning/analysis/recommendations/academic performance projections; Interface: CLI + future UI).
- **`DATA_QUALITY_RULES.md`** — data-quality rules framed around "academic data" and "semester information."
- **`IMPLEMENTATION_CHECKLIST.md`** — an implementation checklist whose substantive sections (Academic Data, Integrations, Intelligence) are entirely AcademicOS-scoped; only its "Foundation" section (repo init, doc structure, AI playbook structure) was generic, and that information is independently preserved in `README.md` and `CHANGELOG.md`, so nothing unique was lost by archiving the whole file.
- **`RELEASE_READINESS.md`** — a release-readiness checklist whose "Release Rule" explicitly ties production-readiness to "academic data flows" being verified — a definition of done that does not apply to the Fibonacci research platform (which has its own, different acceptance criteria in `docs/02-project/PHI_PRD.md` §34).

## Note on a related file that was NOT archived

`docs/DEVELOPMENT_PRINCIPLES.md` was reviewed for the same reason but was **not** moved here. Five of its six principles are generic and apply equally to either vision (source of truth, incremental implementation, explicit unknowns, test-before-expansion, traceability); only principle #3 ("Evidence First") contains one AcademicOS-flavored sentence ("Academic automation should rely on verified source data instead of assumptions."). Moving the whole file would have removed genuinely reusable, actively-relevant principles from the Fibonacci project's documentation. It was left in place and flagged instead — see `docs/FILE_INVENTORY.md`.
