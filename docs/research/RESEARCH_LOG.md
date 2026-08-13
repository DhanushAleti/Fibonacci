# PHI Research & Development Log

Canonical, chronological research and development log for Project PHI. This consolidates entries that were previously split across three locations — `docs/logs/`, `docs/research/`, and `docs/04-research/RESEARCH_LOG.md` — into one running log. All content below is preserved verbatim from those sources; each entry notes its original location for traceability. New entries should be appended below in chronological order.

## 2026-08-05 — Development Log

*(originally `docs/logs/2026-08-05.md`)*

### Work Completed

- Continued PHI system planning.
- Improved documentation structure.
- Reviewed architecture and roadmap.

### Tomorrow

- Continue system architecture.
- Begin backend implementation.
- Define database schema.
- Added GitHub contribution workflow.

## 2026-08-08 — Research Log

*(originally `docs/04-research/RESEARCH_LOG.md`)*

### Repository State

- Product requirements are defined.
- System architecture is substantially drafted.
- Research protocol is established.
- Current research direction is focused on falsifiable evaluation of
  Golden Ratio/Fibonacci-derived market features.

### Next Research Priorities

1. Define the canonical dataset contract.
2. Define feature-generation rules without look-ahead bias.
3. Establish baseline and placebo implementations.
4. Define the minimum backtesting and statistical evaluation protocol.
5. Build reproducible experiments only after these contracts are fixed.

## 2026-08-09 — Research Log

*(originally `docs/research/2026-08-09.md`)*

### Focus

Continued documenting the PHI AcademicOS architecture and implementation direction.

### Progress

- Reviewed the current documentation structure.
- Continued separating product requirements from implementation details.
- Maintained the repository as the source of truth for PHI development decisions.

### Next

- Continue backend integration work.
- Expand academic data ingestion documentation.
- Keep implementation decisions traceable through version-controlled documentation.

## 2026-08-11 — Development Log

### Focus

Implemented Phase 2 (`src/phi/features/`) to the frozen [feature & control contract](../05-mathematics/phi-retracement-feature-contract.md) — the canonical φ retracement feature and its full six-category matched control set — following the design lock recorded in [ADR 0002](../18-decisions/0002-phase2-feature-and-control-design-lock.md).

### Progress

- `phi.features.pipeline`: the shared §2 computation (eligibility filter, prior window, prior range, position-in-range) used identically by the candidate and every control, plus input-sequence validation (duplicate/non-monotonic/mixed-symbol rejection per §6 case 5 and the §1 ordering precondition).
- `phi.features.candidate`: Category A, `f_A(t) = |p_t - g_phi|`.
- `phi.features.controls`: C1, C2 (constant-swap benchmarks), D (position baseline), E (naive persistence), F (range-normalized OLS slope, §7.2), and B (seeded circular rotation placebo, §7.1).
- `phi.features.engine`: whole-series computation producing one aligned row per bar, keyed by `(symbol, event_time, availability_time)`.
- Full §11 test contract: mathematical worked examples, single-implementation determinism, temporal-leakage invariants, window-boundary exactness, insufficient-history and late-availability NULL handling, invalid-input rejection, a real (non-mocked) non-finite-output guard for `p_t`, Tier-1/Tier-2 matching parity, parameter parity, and metamorphic invariants (non-negativity, scale-invariance, translation-invariance, swap-constant identities) — 150 tests passing project-wide (73 new), 98% coverage, ruff/mypy clean.

### Scope boundary held

No real-market data, no labels, no backtest, no statistical/predictive claim — per the contract's §0A scientific claim boundary, this establishes deterministic construction, temporal validity, reproducibility, and matched-control generation only. See the acceptance-gate status note in the [feature & control contract](../05-mathematics/phi-retracement-feature-contract.md#12-phase-2-acceptance-gate) for the two honest caveats (cross-implementation reproducibility not yet applicable with a single implementation; Category F's non-finite-output guard is unexercised, believed but not proven unreachable).

### Next

- Phase 3 — Event-Driven Backtester (PRD §19). Entry condition (Phase 2 complete) is now satisfied; Phase 3 itself has not been started.
- Real market-data provider selection remains open (PRD-OPEN-001).

## 2026-08-12 — Development Log (external-review remediation + ship)

### Focus

Turned the three external reviews (Authoritative Contract, Perplexity, Gemini), the independent repository audit, and the hostile final peer review into a concrete, scientifically-bounded ship — fixing flagged defects and recording decisions **without** inventing any of the blocked science.

### Progress

- Recorded the **feature-authority decision** ([ADR 0003](../18-decisions/0003-phase2-external-review-nogo-and-feature-authority.md) → Accepted, Option B): rolling-window `p_t` authoritative; excursion arithmetic retained as Phase-4 guidance. Updated `features/__init__.py` and `retracement.py` from "open decision" to "decided."
- Verified the prior session's three HIGH code fixes are present and green: non-finite price rejection at construction (`allow_inf_nan=False`), a strengthened confirmatory-readiness gate (multiplicity / confidence level / controls now required), and a real cross-process determinism test.
- Added **code + environment provenance** to the manifest (`code_version`, `environment_lock_hash`) plus a reproducible `phi.experiment.provenance` capture helper (audit I-5; contract §26, §36).
- Enforced **window ≥ 2** at the pipeline boundary, making Category F's zero-denominator edge unrepresentable (audit I-11).
- Corrected stale/contradictory documentation (README no longer claims "no application code"; test counts de-brittled), added `REPRODUCIBILITY.md` and `CONTRIBUTING.md`, and committed the previously-uncommitted Phase-2 implementation to a branch (audit I-4).

### Scope boundary held

No anchor algorithm, no `ε_φ`, no primary estimand, no inference layer, no φ claim. The reviews' NO-GO on confirmatory analysis stands and is enforced in code by `ExperimentManifest.is_confirmatory_ready()`. What shipped is construction + reproducibility + honest documentation — **not** scientific validation.

### Next

- Blockers 1–4 (causal anchor algorithm, `ε_φ`, primary estimand, dependence-aware inference) remain the gate to any Phase-4 confirmatory experiment — a human decision, not a coding task.

## 2026-08-12 — Development Log (Phase 4 confirmatory methodology)

### Focus

Implemented the now-frozen Phase-4 confirmatory methodology (Chief Scientific Methodologist: GO-with-conditions; Final Arbiter: NO-GO to *run* until gates pass) exactly, without reinterpreting or optimizing for φ. New package `src/phi/phase4/`.

### Progress

- Anchor (`extrema.py`): deterministic three-point extrema with the plateau-midpoint parity rule; excursion pairing. Retracement (`retracement.py`): per-excursion terminal `R`, `R∈[0,1]` primary, `R>1` overshoot reported. Estimand (`estimand.py`): paired `Z_i`, `Δ̂_φ`, secondary landscape/rank. Inference (`inference.py`): Politis–White automatic block length + Politis–Romano stationary bootstrap, percentile CI, one-sided p-value with MC error. Multiplicity (`multiplicity.py`): Holm. Null-DGP suite + calibration + power (`nulldgp.py`, `calibration.py`). Replication separation (`datasets.py`), four-outcome verdict (`verdict.py`), and a fail-closed confirmatory gate (`registration.py`, `pipeline.py`). 83 methodology tests; project-wide gates green.

### Honest finding (locked as a regression)

The primary estimand *as specified* is **not null-calibrated**: by Jensen's inequality, symmetric controls make `Δ_φ ≥ 0` on pure noise, so the empirical false-positive rate is ≈ 1.0 under IID/random-walk/AR nulls. It fails the contract's own hard gate (§XLIV), which correctly keeps confirmatory analysis blocked. This is surfaced, not hidden or "fixed"; resolving it (e.g., testing `Δ̂_φ` against its null/surrogate distribution, or a convexity-corrected estimand) is a methodologist decision.

### Scope boundary held

No real data, no confirmatory run, no φ claim. Numerical pre-registration (`C`, `δ_min`, Dataset A/B, block-length config, seed) remains for a human to freeze; the code fails closed until then.

### Next

- Methodologist: resolve the estimand null-calibration finding; then freeze the numerical pre-registration and pass the validation gates.

## 2026-08-12 — Research Log (synthetic validation / false-positive torture test)

### Focus

Determine whether PHI can fool itself. Ran the frozen Phase-4 pipeline against synthetic processes with known generating mechanisms (`scripts/phase4_synthetic_validation.py`; machine-readable `results/phase4_validation/results.json`; [report](../21-releases/PHI_PHASE4_SYNTHETIC_VALIDATION.md)).

### Result — FAIL (do not proceed to real data)

- **13 null processes, FPR = 1.000 each** (Wilson CI [0.975, 1.0]); pooled 1,950 null simulations → 1,950 rejections. Nominal α = 0.05.
- **Constant sweep (decisive):** under IID-Gaussian nulls every focal constant gets `Δ_c > 0` and φ ranks 4th of 5 — φ is **not** specifically preferred. The landscape `M(q)` minimises at ≈ 0.396, not φ.
- **Controls:** the secondary landscape correctly localises injected structure (φ → 0.626, 0.5 → 0.506, 0.3 → 0.304); but the primary `Δ_φ`-vs-0 test falsely fires even for a 0.5-clustered process.
- **Leakage battery clean** (look-ahead diff 0; scale/shift invariant). **Reproducibility pass.**
- Root cause = Jensen bias of a symmetric-grid + convex-distance estimand tested against 0 (a geometric artefact, not φ). Fix is a methodologist decision, not a code change.

### Boundary held

Synthetic data only; no φ claim; confirmatory path remains fail-closed / NO-GO.

## 2026-08-12 — Development Log (Phase 4 post-failure repair)

### Focus

Implemented the arbitrated post-failure Repair Contract (`src/phi/phase4/repair/`) exactly, without tuning to pass: surrogate-standardized `Z_φ` estimand (`Δ_φ>0` permanently forbidden as confirmatory), rational-fraction controls `{1/2,3/5,5/8,2/3}`, block-permutation/GARCH/IAAFT surrogate ensemble, φ-attractor GARCH positive control, granularity audit, five-part gate, and a fail-closed confirmatory path with confirmatory/secondary/exploratory separation.

### Discovery (small-scale validation; honest, not tuned)

Surrogate-standardization neutralizes the geometric bias: aggregate null FPR **1.0 → 0.011**, per-DGP max 0.070, positive-control power (medium α=0.15) **0.82**, constant-sweep symmetric (φ/0.382/0.5 all 0.0). **But the granularity gate FAILS**: φ's FPR is 0.0 at 1000/100/50 tick levels and **0.22 at 10 levels** — the 5/8≈φ discretization artefact the audit exists to catch. Overall gate: does not pass. See `docs/21-releases/PHI_PHASE4_REPAIR_READINESS.md` and `results/phase4_repair_validation/results.json`.

### Status held

IMPLEMENTATION COMPLETE / VALIDATION PENDING. No real data run; confirmatory path fails closed (and would stay refused while the granularity gate fails). Full 10k/20k-per-DGP validation and the numerical pre-registration remain for a human/methodologist.

### Next

- Methodologist: resolve the granularity failure (exact fBm/GARCH/IAAFT surrogates and/or a registered minimum-tick-resolution rule) before the full validation and any confirmatory step.

## 2026-08-13 — Research Log (final scientific finalization)

### Focus

Final work session: reconcile all Phase-4 evidence, independently re-verify the one gate value sitting
exactly on its own threshold, and produce the authoritative scientific record —
[docs/PHI_FINAL_SCIENTIFIC_STATUS.md](../PHI_FINAL_SCIENTIFIC_STATUS.md),
[docs/PHI_FINAL_RESEARCH_REPORT.md](../PHI_FINAL_RESEARCH_REPORT.md),
[docs/RELEASE_STATUS.md](../RELEASE_STATUS.md). No methodology, threshold, DGP, or surrogate was
changed; no repair work was attempted.

### New finding — per-DGP FPR gate does not survive replication

The existing small-scale repair-validation artifact reported `trend_plus_noise` FPR = 0.07 — exactly
the Repair Contract's threshold — from a single seed at `n_series=100`. A targeted, moderate,
reproducible multi-seed re-check (`scripts/phase4_trend_plus_noise_reverification.py`, existing
harness, no changes) exactly reproduced the original value at its actual seed (20260819), then ran 6
further independent seeds (5 at `n=100`, 2 at `n=300`). Grand-pooled across all 8 runs (1,200 series):
**FPR ≈ 0.108, 95% CI [0.091, 0.126]** — decisively above 0.07. The originally reported value was the
low tail of sampling variability, not representative. **Gate 2 does not robustly pass**, alongside the
already-known Gate 4 (granularity) failure.

### Also documented (code review, not new code)

- The mandated secondary/tertiary surrogate families (GARCH, IAAFT) are implemented but exercised only
  in unit tests — every validation-gate calculation to date uses the primary block-permutation
  surrogate only.
- The φ-vs-5/8 rational-specificity test (`confirmatory_phi_test`, Holm-adjusted) is implemented but
  exercised only once, in a single unit test on one synthetic series — never against the 13-DGP null
  suite.

### Engineering re-verification

347 tests passed, 98% branch coverage, Ruff and mypy clean — run directly in this session, not assumed.

### Verdict

**B — NOT CLEARED — REPAIR REQUIRED.** Confirmatory path remains fail-closed. No real data analyzed.
Further repair is documented as future work, not attempted here (per this session's operating brief:
diagnose and record, do not repair).

---

*New entries: append a `## YYYY-MM-DD — <Research Log | Development Log>` section below, following the format above.*
