# PHI — Phase 4 Repair Implementation Report

**Date:** 2026-08-12 · **Status: IMPLEMENTATION COMPLETE / VALIDATION PENDING**
**Data:** synthetic only. **REAL DATA HAS NOT BEEN RUN. No φ claim is made.**

> The original `Δ_φ > 0` test FAILED synthetic validation (FPR = 1.0 across 13 nulls). This report covers the implementation of the arbitrated **Repair Contract**. It does **not** claim scientific success: the small-scale validation shows the repair fixes the geometric bias and is powered, but **fails one of the five gates** (granularity) — reported honestly and **not tuned away** (Repair Contract absolute rule).

## 1. Exact scientific decisions implemented
- Primary estimand replaced by the **Standardized Null Score `Z_φ`** (`Δ_φ > 0` permanently forbidden as confirmatory evidence; demoted to a labelled SECONDARY descriptive statistic).
- **Rational-fraction controls** `{1/2, 3/5, 5/8, 2/3}`; φ must specifically beat **5/8**; the "top-1% of a dense grid" rule is **rejected/absent**.
- **Surrogate ensemble**: block-permutation (primary), GARCH(1,1) (secondary), IAAFT (tertiary).
- **Null hypothesis**: `Z_φ ≤ 0` — φ-proximity fully explained by the surrogate topology.
- **φ-attractor GARCH positive control** (clean zig-zag rejected); **granularity audit**; **five-part FPR gate**; **fail-closed** confirmatory gate; **confirmatory / secondary / exploratory** path separation.

## 2. Exact mathematical definitions
- `Δ_obs = mean_{c∈C} E|R − c| − E|R − q_φ|` with `C = {1/2, 3/5, 5/8, 2/3}`.
- `Z_φ = (Δ_obs − μ_null) / σ_null`, where `μ_null, σ_null` are the mean/SD of `Δ^(s)` over surrogates of the same series.
- Confirmatory p-value: `p = (1 + #{Δ^(s) ≥ Δ_obs}) / (S + 1)` (surrogate-rank); reject `H0: Z_φ ≤ 0` iff `p < α`.
- φ-specificity: per-rational surrogate p-values, **Holm** step-down; φ must beat every rational (incl. 5/8).

## 3. Files changed
**Created — `src/phi/phase4/repair/`:** `__init__, surrogates, rational, zscore, positive_control, granularity, validation, registration` (8 modules). **Tests — `tests/phase4/repair/`:** 6 files. **Scripts:** `scripts/phase4_repair_validation.py`. **Artefact:** `results/phase4_repair_validation/results.json`. **This report.** No pre-existing source module was modified (Phases 0–4 original preserved; the original Δ_φ pipeline remains as the secondary/descriptive layer).

## 4. Architecture changes
A `phi.phase4.repair` subpackage layered on the existing Phase-4 primitives (extrema, retracement, multiplicity, datasets). Confirmatory path (`run_confirmatory_repair` → `Z_φ` + rational Holm) is structurally separate from the secondary profile (`run_secondary_profile`, explicitly non-confirmatory) and cannot silently run the forbidden `Δ_φ` statistic.

## 5–8. Tests / passing / coverage / lint-type
- **Tests added:** 39 (6 files) — surrogate determinism + marginal preservation, `Z_φ` math/null/injection, fail-closed gate, data separation, the contract invariants (Δ_φ not confirmatory, rational controls, no top-1% rule, 13-DGP immutability, positive control exists), granularity + positive control, and the harness at tiny scale.
- **Full suite: 347 passed** · **coverage 98%** (repair modules 91–100%) · **Ruff (lint+format) clean** · **mypy clean (47 files)**.

## 9. Reproducibility
Deterministic: PCG64 seeded throughout (surrogates, DGPs, harness); frozen constants by expression; content-hashed registration. In-/cross-process determinism covered by the existing Phase-4 reproducibility tests; `standardized_null_score` determinism is asserted.

## 10. Validation commands
```bash
uv run pytest tests/phase4/repair -q                       # 39 tests
uv run python scripts/phase4_repair_validation.py          # small-scale 5-part gate (~90s)
uv run python scripts/phase4_repair_validation.py --full   # the fuller run (1000×999) — heavier
```
The FINAL 10,000/20,000-per-DGP validation is deliberately **not** run here (Repair Contract).

## 11. Remaining blockers

**Small-scale validation (n_series=100, S=99, seed 20260812) — 4/5 gates pass:**

| Gate | Result | Pass |
|---|---|---|
| 1 Aggregate FPR ≤ 0.05 | **0.011** (was **1.000** pre-repair) | ✅ |
| 2 Per-DGP FPR ≤ 0.07 | max 0.070 (trend+noise; rest ≤0.05) | ✅ |
| 3 Power ≥ 0.80 (medium α=0.15) | **0.82** | ✅ |
| 5 Constant-sweep symmetry | φ / 0.382 / 0.5 all 0.0 | ✅ |
| **4 Granularity (φ FPR ≤ 0.07 per tick)** | 1000:0.0 · 100:0.0 · 50:0.0 · **10:0.22** | ❌ |

1. **Granularity gate FAILS at the coarsest (10-tick) resolution** (φ FPR 0.22). This is the 5/8 ≈ φ discretization artefact the audit exists to catch — φ's false-positive rate scales inversely with resolution. **Not tuned away.** Consequence: the pipeline is **not cleared for coarsely-discretized data**; the fail-closed gate keeps confirmatory blocked. Candidate refinements (a methodologist decision, not a results-driven tweak): the exact Cholesky/Davies-Harte fBm and exact GARCH/IAAFT surrogates (this build uses documented approximations), and/or a minimum-tick-resolution eligibility rule registered in advance.
2. **Full-scale validation not run** (10k/20k per DGP) — required before any confirmatory step.
3. **Numerical pre-registration unfrozen** (Dataset A/B identities, block-length config, seed) — human decision.

## 12. REAL DATA
**No real-world data has been run. No confirmatory analysis has been executed.** The confirmatory path (`run_confirmatory_repair`) fails closed (`RepairPreRegistration.is_confirmatory_authorized()` is `False`), and — because the granularity gate does not pass — would remain refused even with all numerical registrations supplied.

## Bottom line
The repair is implemented exactly and neutralizes the catastrophic geometric bias (FPR 1.0 → 0.011) with adequate power (0.82) and confirmed constant-sweep symmetry. Its own mandated granularity audit then correctly flags a residual tick-discretization vulnerability at extreme coarseness, so **PHI is not cleared for real data**. This is the scientifically correct outcome: the machinery detects a real signal, refuses a false one, and refuses itself where an artefact remains.
