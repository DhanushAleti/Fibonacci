# PHI — Phase 4 Implementation Readiness Report

**Date:** 2026-08-12 · **Prepared by:** Principal research software engineer
**Status of methodology:** frozen (GO-with-conditions). **Status of execution:** **NOT authorized** (fail-closed).

> This attests to the readiness of the *implementation* of the frozen Phase-4 methodology. It does **not** report a φ result — no confirmatory experiment has been run, and one is not authorized. PHI is not "validated" and is not "perfect." Language here is deliberately falsificationist.

## Frozen decisions implemented (exactly as specified)

| Decision | Value | Where |
|---|---|---|
| Research question / hypotheses | φ specialness vs matched constants; `H0: Δ_φ ≤ 0`, one-sided, α=0.05 | `phase4/constants.py`, `registration.py` |
| Anchor | Deterministic three-point extrema, plateau-midpoint parity, opposite-extrema pairing | `phase4/extrema.py` |
| φ-distance / εφ | Continuous `|R − q|`; **no εφ** in primary inference | `phase4/estimand.py` |
| Primary estimand | `Δ_φ = (1/K)Σ_{q∈C} E[|R−q| − |R−q_φ|]`, paired at excursion level | `phase4/estimand.py` |
| Inference | Stationary bootstrap + automatic Politis–White block length, `B=10,000`, 95% CI, one-sided p (+ MC SE) | `phase4/inference.py` |
| φ vs alternatives | Symmetric equally-spaced matched controls (primary) + dense global grid (secondary) | `phase4/registration.py`, `estimand.py` |
| Multiplicity | Holm step-down FWER | `phase4/multiplicity.py` |
| Power | Monte-Carlo simulation harness, threshold ≥ 0.80 | `phase4/calibration.py` |
| Null-DGP suite | 10 DGPs + coarse-tick microstructure + φ-biased positive control | `phase4/nulldgp.py` |
| Replication | discovery / confirmation (A) / external (B) separation, enforced | `phase4/datasets.py`, `pipeline.py` |
| Confirmatory gate | fail-closed `is_confirmatory_authorized()` | `phase4/registration.py`, `pipeline.py` |
| Interpretation | four outcomes by CI vs `[−δ_min,+δ_min]` | `phase4/verdict.py` |

## Files changed

**Created — `src/phi/phase4/`:** `__init__.py`, `constants.py`, `registration.py`, `extrema.py`, `retracement.py`, `estimand.py`, `inference.py`, `multiplicity.py`, `nulldgp.py`, `calibration.py`, `analysis.py`, `datasets.py`, `verdict.py`, `pipeline.py` (14 modules). **Tests — `tests/phase4/`:** 11 files (`test_extrema/retracement/estimand/inference/multiplicity/registration/nulldgp/pipeline/verdict/calibration/reproducibility/edges`, + `conftest.py`). **Docs:** `docs/05-mathematics/phi-phase4-scientific-contract.md` (new), this report; updated README, CHANGELOG, NEXT_STEPS, RESEARCH_LOG, REPRODUCIBILITY. No existing source module was modified (Phase 0–2 reproducibility preserved).

## Tests / coverage / gates

- **pytest:** 308 passed (83 new Phase-4). **Coverage:** 98% branch. **Ruff** (lint+format) and **mypy** clean (39 source files).
- Tests verify *behavior*, not just coverage: hand-computed extrema/retracement/Δ_φ, the Jensen non-negativity invariant, block-length monotonicity with dependence, dependence-robust CI widening, Holm correctness, fail-closed gate, data-role separation, four-outcome classification, DGP determinism, and in-/cross-process determinism.

## Statistical validations (Arbiter Gates 3–8)

| Gate | Implemented | Result |
|---|---|---|
| 3 Bootstrap coverage | harness present | not yet demonstrated at scale (registration flag defaults False) |
| 4 Power ≥ 0.80 | `estimate_power` | not yet demonstrated at registered δ_min |
| 5/8 Null-FPR ≈ α (hard gate) | `null_calibration` | **FAILS as specified — FPR ≈ 1.0** (see below) |
| 6 Dataset A/B freeze | registration fields | open (human decision) |

## Null-DGP status (the headline finding)

The null-calibration harness, run on the primary estimand **as specified**, rejects `H0: Δ_φ ≤ 0` under pure-null DGPs (IID Gaussian, random walk, AR) at an empirical **false-positive rate ≈ 1.0**, with mean `Δ̂_φ ≈ +0.02`. This is **not** a bug: by Jensen's inequality, symmetric controls about `q_φ` with the convex `M(q)=E|R−q|` force `Δ_φ ≥ 0` for any distribution. So a positive `Δ̂_φ` tested against 0 is a **geometric artefact**, not φ evidence. The methodology therefore **fails its own hard gate (spec §XLIV)**, which correctly forbids a confirmatory claim. This is locked as a regression test and must be resolved by the **methodologist** (e.g., compare `Δ̂_φ` to its null/surrogate distribution, or a convexity-corrected estimand) — it must not be silently changed in code.

## Reproducibility

Deterministic: PCG64 (`numpy.default_rng`) seeded throughout; frozen constants by expression; the manifest binds code+environment provenance. In-process **and cross-process** determinism are asserted (`tests/phase4/test_reproducibility.py`). Null-DGP series and calibration are reproducible from a registered base seed.

## Remaining blockers (confirmatory analysis stays NO-GO)

1. **Estimand null-calibration failure** (above) — methodologist decision. *Hard gate.*
2. **Numerical pre-registration unfrozen:** exact `C` (δ, K), `δ_min` (domain-justified), Dataset A/B identities+hashes, block-length estimator config, DGP parameterisation, RNG seed.
3. **Validation not demonstrated at scale:** bootstrap coverage, power ≥ 0.80.

All are enforced in code: `is_confirmatory_authorized()` returns `False` and `run_confirmatory` raises until they are resolved.

## Exact commands

**Synthetic validation** (reduced scale; the finding above):
```bash
uv run pytest tests/phase4 -q
uv run python -c "
from phi.phase4.calibration import null_calibration, all_nulls_calibrated
from phi.phase4.registration import ComparisonSet
C = ComparisonSet.build(delta=0.05, k_per_side=4).constants   # ILLUSTRATIVE, not a registered value
r = null_calibration(C, n_series=200, series_length=500, replicates=999, base_seed=20260812)
print({k: round(v.rejection_rate,3) for k,v in r.items()}); print('all calibrated:', all_nulls_calibrated(r))"
```

**Confirmatory analysis:** *none is available.* It is gated NO-GO; there is no registered dataset and the null-calibration gate does not pass. Once a methodologist resolves the estimand and a human completes a `Phase4PreRegistration` whose `is_confirmatory_authorized()` is `True`, the entry point is `phi.phase4.run_confirmatory(values, registration=…, dataset=…)` — and only then.

## Bottom line

The frozen Phase-4 methodology is implemented exactly, tested for behavior, deterministic, and fail-closed. Its own honest validation shows the specified estimand is not null-calibrated, so PHI **cannot and does not** make a φ claim — the machinery correctly refuses. Whether φ is special remains undetermined and, under this contract, deliberately so.
