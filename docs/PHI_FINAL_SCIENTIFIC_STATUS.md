# PHI Final Scientific Status

**Date:** 2026-08-13 · **Prepared as:** final scientific arbitration and release record
**Scope:** this document is the single authoritative statement of PHI's scientific status. Where it
conflicts with anything in `docs/21-releases/`, `docs/RESEARCH_LOG.md`, `docs/research/RESEARCH_LOG.md`,
or prose in the README, **this document governs** — those are retained as historical process record.

---

## 1. Research Question

Does a pre-specified φ-retracement structure (built from the Golden Ratio, `q_φ = 1/φ ≈ 0.618`) occur
in eligible time-series excursions at a frequency or magnitude distinguishable from appropriately
matched **non-φ** controls, after accounting for temporal dependence and multiplicity? The question
targets φ *specialness* — whether φ outperforms scientifically matched alternative constants — not
merely whether retracements cluster somewhere.

## 2. Scientific Contract

Frozen in `docs/05-mathematics/phi-phase4-scientific-contract.md` (methodology) and the Repair Contract
implemented in `src/phi/phase4/repair/` (post-failure repair). Key frozen elements: `H0: Δ_φ ≤ 0` /
`Z_φ ≤ 0` one-sided at `α = 0.05`; deterministic three-point extrema anchor; terminal per-excursion
retracement `R`; a fail-closed confirmatory gate (`is_confirmatory_authorized()`); discovery /
confirmation (Dataset A) / external replication (Dataset B) separation. None of these were altered
during this finalization pass.

## 3. Original Method

**Primary estimand:** `Δ_φ = mean_{q∈C} E|R−q| − E|R−q_φ|` for a symmetric, equally-spaced control set
`C`, tested against `0`. Implemented exactly in `src/phi/phase4/` (14 modules, `docs/21-releases/PHI_PHASE4_READINESS.md`).

## 4. Original Synthetic Validation

`scripts/phase4_synthetic_validation.py` → `results/phase4_validation/results.json` (git SHA
`f1467c1`). Config: 13 null DGPs × 150 series × length 400 × 199 bootstrap replicates (~2,100 total
runs including controls). **Verified directly from the artifact in this pass.**

## 5. Original Failure

**Pooled aggregate FPR = 1.000** (1,950/1,950 null simulations rejected `H0`), nominal `α = 0.05`. Every
one of the 13 null DGPs individually shows FPR = 1.000, Wilson 95% CI `[0.975, 1.0]`. This is a **hard
gate failure** against the contract's own §XLIV null-calibration requirement.

## 6. Mathematical Root Cause

By **Jensen's inequality**: for a convex functional `M(q) = E|R−q|` and a control set `C` symmetric
about `q_φ`, `Δ_φ = mean_{q∈C} M(q) − M(q_φ) ≥ 0` for **any** retracement distribution, null or not. A
positive `Δ̂_φ` tested against `0` is therefore a **geometric identity of the estimand**, not evidence
about φ. This is a mathematical proof, not an empirical pattern, and is locked as a regression test
(`tests/phase4/test_estimand.py::TestJensenGeometricBias`, confirmed present in this pass).

## 7. Constant-Sweep / Specificity Analysis

From the original torture test (pooled N = 14,753 retracements from IID-Gaussian nulls): **every**
tested focal constant (0.25, 0.40, 0.50, φ≈0.618, 0.75) gets `Δ_c > 0`; φ ranks **4th of 5**, and the
global landscape `M(q)` minimizes at `q ≈ 0.396` — nowhere near φ. `phi_is_specifically_preferred =
False`. This is the decisive evidence that the original failure is generic geometry, not a φ-specific
artifact of the data.

## 8. Repair Contract

Arbitrated, pre-registered repair (not invented during this session — implemented in an earlier
session and present at `src/phi/phase4/repair/`, 8 modules, 39 dedicated tests). Absolute rule stated
in the code and docstrings throughout: harnesses report whether PHI passes; **they are never tuned to
make it pass.** This finalization pass did not modify any repair module, threshold, DGP, or surrogate.

## 9. Implemented Repair

- **Estimand:** surrogate-standardized `Z_φ = (Δ_obs − μ_null)/σ_null`; `Δ_φ > 0` vs `0` is **permanently
  forbidden** as confirmatory evidence and demoted to a labeled secondary/descriptive statistic
  (`src/phi/phase4/repair/zscore.py`, `registration.py`).
- **Rational controls:** `{1/2, 3/5, 5/8, 2/3}` — pre-specified market-microstructure fractions, not a
  dense grid (`rational.py`). φ must specifically beat `5/8` in the (not-yet-run) confirmatory path.
- **Surrogate hierarchy:** block-permutation (primary), GARCH(1,1) (secondary), IAAFT (tertiary)
  (`surrogates.py`), justified as preserving different aspects of series topology while destroying
  φ-specific alignment.
- **Positive control:** φ-attractor GARCH-textured series with `q_φ`-ratio injections at a controlled
  rate (`positive_control.py`), replacing a rejected "clean zig-zag" control.
- **Granularity audit:** discretized-fBm nulls at multiple tick resolutions, checking whether φ's
  false-positive rate grows as the grid coarsens — the `5/8 ≈ φ` discretization artefact detector
  (`granularity.py`).
- **Five-part acceptance gate** and a fail-closed `RepairPreRegistration` (`registration.py`,
  `validation.py`) that requires all numerical pre-registration fields **and** all five gates before
  `run_confirmatory_repair` will execute.

## 10. Validation Evidence

**Existing small-scale artifact** (`results/phase4_repair_validation/results.json`, git SHA
`3412a67` — see §19 provenance note): `n_series=100, series_length=400, n_surrogates=99`, base seed
`20260812`.

**New evidence produced in this pass** (targeted, moderate, reproducible multi-seed re-check of the
one gate value sitting exactly on its threshold — no methodology, DGP, or threshold changed): see §11
and §12.

## 11. Gate-by-Gate Results

| Gate | Threshold | Small-scale artifact (single seed) | This pass's re-verification | Status |
|---|---|---|---|---|
| 1. Aggregate FPR | ≤ 0.05 | 0.0108 | not re-run (not borderline) | **PASS** (single-run evidence only) |
| 2. Per-DGP FPR (max) | ≤ 0.07 | 0.07 (trend_plus_noise, **exactly at threshold**) | **pooled ≈0.108–0.117 across 8 independent seeds/scales, 95% CI excludes 0.07** | **DOES NOT ROBUSTLY PASS** — see §12 |
| 3. Positive-control power (medium) | ≥ 0.80 | 0.82 | not re-run | **PASS** (single-run evidence only; see §14 caveat) |
| 4. Granularity (φ FPR by tick) | ≤ 0.07 at every resolution | 1000:0.0 · 100:0.0 · 50:0.0 · **10:0.22** | not re-run (already decisive) | **FAIL** |
| 5. Constant-sweep symmetry | φ/0.382/0.5 within tolerance | all 0.0 | not re-run | **PASS** (single-run evidence only) |

**Overall gate: FAILS.** (Confirmed both by the existing artifact's own `overall_pass: false` and
independently by the new per-DGP finding in §12, which shows the artifact's reported Gate 2 "pass" was
not robust.)

## 12. Per-DGP Results — New Finding (trend_plus_noise)

The existing artifact reports `trend_plus_noise` FPR = 0.07 at `n_series=100` — **exactly equal to** the
0.07 threshold, from a single seed. Per this session's brief (treat near-threshold results with
appropriate statistical uncertainty), a targeted, moderate, reproducible multi-seed verification was
run using the existing, unmodified `surrogate_fpr()` harness (`src/phi/phase4/repair/validation.py`),
never altering the DGP, estimand, or threshold:

- **Exact reproduction check:** `base_seed=20260819` (the seed `null_suite_fpr` actually assigns to
  `trend_plus_noise`, index 7 of 13 in `REPAIR_NULL_SUITE`, at harness `base_seed=20260812`),
  `n_series=100, series_length=400, n_surrogates=99` → **FPR = 0.07 (7/100)**, exactly reproducing the
  artifact. This confirms determinism and that the artifact's number is not a transcription error.
- **6 additional independent seeds at the same n=100 scale** (1007, 2007, 3007, 4007, 5007, plus the
  reproduction run): FPRs of 0.07, 0.11, 0.13, 0.16, 0.12, 0.11 → **pooled 70/600 = 0.1167**, SE ≈
  0.0131, approx. 95% CI **[0.091, 0.142]**.
- **2 independent seeds at a larger n=300 scale** (1007, 2007): FPRs of 0.1067, 0.0933 → **pooled
  60/600 = 0.1000**, SE ≈ 0.0122, approx. 95% CI **[0.076, 0.124]**.
- **Grand pooled across all 8 runs** (1,200 total valid series): **FPR ≈ 0.108**, approx. 95% CI
  **[0.091, 0.126]** — entirely above the frozen 0.07 threshold.

**Interpretation.** The single-seed value of 0.07 reported in the existing artifact was the low tail of
sampling variability at `n=100` (binomial SE at p≈0.11 is ≈0.03, so 0.07 is within ~1.4 SE of the
replicated estimate — plausible, not anomalous, but not representative). With replication, the
`trend_plus_noise` per-DGP FPR is reliably **above** the 0.07 threshold. **Gate 2 does not robustly
pass.** This is a second, independent reason (beyond granularity) that the repair does not clear its
own acceptance gate. Reproduction script and full seed-by-seed output are recorded in
`docs/REPRODUCIBILITY.md`.

No other per-DGP values were re-verified — the rest are either exactly 0.0 (13/13 zero rejections
leaves no plausible boundary ambiguity at this scale) or clearly under threshold with margin, so a
re-check would not be decisive and was not run, per the instruction to avoid an enormous full-suite
validation.

## 13. Granularity

**Confirmed real and reproducible from the existing artifact and source code** (`granularity.py`).
`φ`'s surrogate-test FPR is 0.0 at tick resolutions 1000/100/50 and **0.22 at resolution 10** — the
`5/8 = 0.625 ≈ q_φ = 0.618` discretization artefact the audit is explicitly designed to catch (see the
module docstring: "If phi's FPR grows as the grid coarsens, the effect is an artefact"). **No registered
minimum-tick-resolution eligibility rule exists anywhere in the contract or repair registration** — the
`RepairPreRegistration` schema has no such field, and the readiness report itself lists "a minimum-tick-
resolution eligibility rule registered in advance" as an unimplemented *candidate future refinement*,
not a decided exclusion. There is therefore no basis to treat 10-tick resolution as outside the
registered scientific domain — the failure is a real, undocumented-away vulnerability, not an
out-of-domain edge case.

## 14. Positive Control

**What it demonstrates:** the repaired pipeline can detect an injected `q_φ`-clustering signal (rate
`inject_prob=0.15`, "Medium") on a GARCH-volatility-clustered swing skeleton, at empirical power 0.82
(single small-scale run, `n_series=100`, not independently re-verified in this pass — not selected for
re-check because it is not near its threshold).

**What it does not demonstrate:** the injection mechanism is an explicitly flagged approximation
(`positive_control.py` docstring: the contract specifies an OU-drift-on-GARCH construction; the
implementation instead directly injects the φ ratio into a fraction of swing magnitudes — "a simpler,
deterministic construction," "a refinement for the methodologist to confirm"). Power was characterized
at exactly one signal-strength level in the available artifact (Medium); Small (0.05) and Large (0.30)
are defined in the docstring but no power result for them was found in any artifact. This power figure
characterizes sensitivity to a **stylized synthetic effect**, not to any known or hypothesized
real-market retracement effect size — no such effect size is registered (`δ_min` remains unfrozen, §9
of the original contract report).

## 15. Rational Controls

The four rational fractions (`1/2, 3/5, 5/8, 2/3`) are present in the estimand's control set `C`, and
the **aggregate** advantage over all four was exercised at the validated scale (all five gates use
`constants=RATIONAL_CONSTANTS.values()` as a group). However, the **specific pairwise φ-vs-5/8
Holm-adjusted specificity test** (`confirmatory_phi_test`, `ConfirmatoryResult.beats_five_eighths`,
`registration.py`) — the mechanism that would actually establish φ is preferred over its single closest
rational competitor, not just over the group average — is **implemented but exercised only once**, in a
single unit test on a single synthetic random-walk series with one seed
(`tests/phase4/repair/test_contract.py::TestOriginalDeltaPhiNotConfirmatory`). It has never been run
against the 13-DGP null suite or characterized for its own false-positive rate. **Conclusion: φ was
tested against a rational-fraction set that includes 5/8, and the aggregate test's calibration was
validated; but genuine φ-vs-5/8 specificity, at the level of rigor applied to the other gates, has not
been established.** This is a real, previously undocumented gap, not merely a restatement of the
existing granularity concern.

Separately: the mandated **secondary (GARCH) and tertiary (IAAFT) surrogate audits** (`surrogates.py`,
described in the module docstring as "the mandated secondary/tertiary audit") were verified in this
pass to be used **only in unit tests** (`tests/phase4/repair/test_surrogates.py`) — every validation-
battery function (`null_suite_fpr`, `granularity_audit`, `positive_control_power`,
`constant_sweep_symmetry`) uses the default `block_permutation_surrogate` (primary) exclusively. The
repair's calibration is therefore validated against one surrogate family, not the full mandated
hierarchy.

## 16. Statistical Uncertainty

All validation-battery numbers to date come from **one seed at small scale** (`n_series≈100`,
`n_surrogates=99`), except `trend_plus_noise` (§12, now multi-seed) and granularity (already decisive
at 0/0/0/0.22 — a 5.5σ-scale gap that does not need replication to trust its direction). Binomial
standard error at `n=100, p≈0.05–0.11` is on the order of 0.02–0.03 — comparable to the gap between
several reported "pass" values and their thresholds (e.g., Gate 1's 0.0108 vs 0.05 has real margin;
Gate 2's now-corrected ≈0.11 vs 0.07 does not). No confidence intervals were reported in the original
artifact for any gate; this is a reproducibility gap the full-scale run is intended to close (§17).

## 17. Reproducibility

- **Original failure:** exactly reproducible; git SHA `f1467c1` artifact, deterministic PCG64 seeding
  throughout (verified: re-running the harness at the recorded seed reproduces the recorded value, done
  for `trend_plus_noise` in §12).
- **Repair small-scale validation:** exactly reproducible (verified in §12). Cross-process determinism
  is separately asserted by `tests/phase4/test_reproducibility.py`.
- **Full 10,000/20,000-per-DGP validation:** **never run.** `scripts/phase4_repair_validation.py --full`
  exists and is documented but was not executed in this or any prior session (no artifact exists for
  it). This remains explicitly deferred, consistent with the Repair Contract's own stated scope.
- **Minor provenance note:** `results/phase4_repair_validation/results.json`'s `git_sha` field records
  `3412a67` (the commit *before* the repair modules were committed as `a0e07aa`) — the validation script
  was run against a working tree with uncommitted repair code, not a committed SHA. This does not affect
  the numerical result (the code was present, just not yet committed) but means the artifact's own
  provenance pointer is imprecise. Not corrected retroactively (would require re-running and is not
  scientifically material); flagged here for the record.

## 18. Engineering Verification

Run directly in this session (2026-08-13), not assumed from documentation:

```
uv run pytest -q                                       → 347 passed
uv run pytest --cov=src --cov-report=term-missing -q   → 347 passed, 98% branch coverage
uv run ruff check .                                    → All checks passed!
uv run ruff format --check .                           → 197 files already formatted
uv run mypy src                                         → Success: no issues found in 47 source files
```

Engineering status is clean and independently confirmed. **This is an engineering fact, not scientific
validation** — passing tests verify the code does what it is written to do; they do not verify that what
it is written to do (the repaired estimand) is itself sufficient to authorize a real-data claim, which
§11–§15 show it is not, yet.

## 19. Remaining Limitations

1. Granularity gate fails at coarse (10-tick) resolution — real, undocumented-away, no registered
   domain exclusion (§13).
2. Per-DGP FPR gate does not robustly pass for `trend_plus_noise` — newly demonstrated in this pass
   (§12); the existing artifact's "pass" was a boundary single-seed value.
3. φ-vs-5/8 specificity (the sharpest test of φ specialness) is implemented but validated only by one
   toy unit test, not the null-suite battery (§15).
4. Secondary/tertiary surrogate audits (GARCH, IAAFT) are implemented but not exercised in the
   validation battery — calibration is characterized against one surrogate family only (§15).
5. Positive-control power is characterized for one injection mechanism (a flagged approximation of the
   registered design) at one signal-strength level; no registered `δ_min` exists to calibrate power
   against a domain-justified effect size (§14).
6. Full-scale (10,000/20,000-per-DGP) validation has never been run (§17).
7. Numerical pre-registration (exact `C`, `δ_min`, Dataset A/B identities+hashes, block-length
   estimator config, RNG seed) remains unfrozen — a human/methodologist decision, not a coding task.
8. Bootstrap-coverage validation (an Arbiter gate from the original, pre-repair contract) was never
   demonstrated at scale for either the original or repaired estimand.
9. No real market data has ever been used anywhere in this repository.

## 20. What PHI Has Established

- A leakage-safe, deterministic, reproducible construction of φ-retracement features and matched
  controls (Phase 2), independently engineering-verified (§18).
- A rigorous, fail-closed confirmatory pipeline architecture that **cannot** silently run a forbidden
  statistic and refuses to execute without complete registration (verified in source, §9).
- A real, mathematically proven failure mode (Jensen bias) in the original estimand, caught by the
  project's own adversarial synthetic validation before any real-data exposure (§5–§7).
- A repair that **measurably and substantially** improves null calibration (aggregate FPR 1.0 → 0.011)
  and demonstrates the geometric bias is specifically neutralized (constant-sweep symmetry), with
  non-trivial power to detect an injected synthetic φ-signal.
- That the project's own falsification machinery works: it detected its own original failure and
  (partially) detected the repair's remaining weaknesses, rather than concealing them.

## 21. What PHI Has NOT Established

- That φ is empirically special in any real or synthetic time series beyond the one stylized positive
  control built to be detected.
- That the repaired estimand is calibrated at the resolution/DGP breadth its own gate set requires — it
  fails at coarse granularity and (per new evidence, §12) does not reliably meet its per-DGP FPR bound
  for at least one registered null process.
- That φ specifically outperforms its closest rational competitor, 5/8 — the mechanism to test this
  exists but has not been validated.
- Anything about real financial markets. No real data has been analyzed at any point.

## 22. Final Scientific Verdict

**B — NOT CLEARED — REPAIR REQUIRED.**

The original method is a confirmed, mathematically explained failure (Jensen bias) and is correctly
retired as forbidden. The arbitrated repair is a genuine, non-tuned, substantial improvement — not a
failed approach — but it does not currently pass its own registered five-part acceptance gate: the
granularity gate fails decisively, and this session's targeted replication shows the per-DGP FPR gate
also does not robustly pass for `trend_plus_noise`. Additional real gaps (rational-specificity vs 5/8
unvalidated at scale; secondary/tertiary surrogates unexercised in calibration; full-scale run never
performed; numerical pre-registration unfrozen) mean the confirmatory path is correctly and
appropriately still fail-closed. This is not scientific evidence against φ either — the question remains
open. Further repair work is a methodologist decision and is out of scope for this finalization pass
(Phase 4 of the operating brief: do not repair the method).

## 23. Real-Data Authorization

**NOT AUTHORIZED.** `RepairPreRegistration.is_confirmatory_authorized()` requires both complete
numerical registration (9 required fields, all `None` — verified in source, `registration.py`) and all
five validation gates passing (2 of 5 fail or do not robustly pass, per §11–§12). **No real market data
has been analyzed anywhere in this repository at any point.**
