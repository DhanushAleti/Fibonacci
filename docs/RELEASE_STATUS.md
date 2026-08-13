PROJECT: PHI

SCIENTIFIC VERDICT:
B — NOT CLEARED — REPAIR REQUIRED. The original confirmatory estimand is a confirmed, mathematically
explained failure (Jensen bias; aggregate false-positive rate 1.0 across 13 null processes, 1,950
simulations) and is permanently forbidden as confirmatory evidence. The arbitrated repair substantially
improves calibration (aggregate FPR 1.0 → 0.011) but does not currently pass its own five-part
acceptance gate: the granularity audit fails (φ FPR 0.22 at coarse tick resolution vs. a 0.07 threshold)
and a targeted multi-seed re-verification performed during this finalization pass shows the per-DGP FPR
gate also does not robustly pass for `trend_plus_noise` (pooled FPR ≈0.108, 95% CI [0.091, 0.126], vs.
threshold 0.07). Full detail: [docs/PHI_FINAL_SCIENTIFIC_STATUS.md](PHI_FINAL_SCIENTIFIC_STATUS.md).

ENGINEERING STATUS:
Clean, independently re-verified 2026-08-13: 347 tests passed; 98% branch coverage; `ruff check` and
`ruff format --check` clean; `mypy src` clean (47 source files). Not a scientific claim — see the
verdict above.

ORIGINAL METHOD:
FAILED synthetic validation. Aggregate false-positive rate 1.000 across all 13 registered null
data-generating processes (1,950 simulations), against nominal α = 0.05. Root cause proven
mathematically (Jensen's inequality on a convex distance functional against a symmetric control set —
`Δ_φ ≥ 0` for any distribution, null or not). Constant sweep confirms φ is not preferred over other
constants (ranks 4th of 5). `Δ_φ > 0` vs. 0 is now permanently forbidden as confirmatory evidence
(retained only as a labeled, non-confirmatory descriptive statistic).

REPAIR:
IMPLEMENTATION COMPLETE / VALIDATION FAILED (2 of 5 gates). Surrogate-standardized `Z_φ` estimand
neutralizes the geometric bias (aggregate FPR 0.011, constant-sweep symmetry restored, positive-control
power 0.82 at small scale) but does not clear its own acceptance gate. Full-scale (10,000/20,000-per-DGP)
validation has never been run. Numerical pre-registration remains unfrozen.

MANDATORY GATES:

| Gate | Threshold | Result | Status |
|---|---|---|---|
| 1. Aggregate FPR | ≤ 0.05 | 0.0108 (single small-scale run) | PASS |
| 2. Per-DGP FPR (max) | ≤ 0.07 | reported 0.07 (trend_plus_noise, single seed); replicated pooled ≈0.108, 95% CI [0.091, 0.126] | **FAIL (does not survive replication)** |
| 3. Positive-control power (medium) | ≥ 0.80 | 0.82 (single small-scale run) | PASS |
| 4. Granularity (φ FPR by tick) | ≤ 0.07 at every resolution | 0.0 / 0.0 / 0.0 / **0.22** (at 1000/100/50/10 ticks) | **FAIL** |
| 5. Constant-sweep symmetry | φ within tolerance of 0.382, 0.5 | all 0.0 | PASS |

Overall: FAILS (2 of 5 gates fail; both without a registered exception).

REAL-DATA AUTHORIZATION:
NO. `RepairPreRegistration.is_confirmatory_authorized()` requires complete numerical registration (9
required fields, all currently unset) AND all five gates passing. Neither condition is met.

REAL DATA ANALYZED:
NO. No real-world market data has been used anywhere in this repository at any point. All data in every
test, validation, and calibration run is synthetic and explicitly labeled as such.

FINAL CLAIM:
PHI has established a rigorous, fail-closed confirmatory pipeline that correctly detected a severe,
mathematically explained defect in its own originally specified method before any real-data exposure,
and has implemented a substantial, non-tuned repair that measurably improves null calibration. PHI has
NOT established that the golden ratio is empirically special in any real or synthetic time series: the
repair does not yet meet its own pre-registered validation bar (granularity and per-DGP false-positive
checks both fail or fail under replication), rational-fraction specificity against the closest
competing constant (5/8) is implemented but statistically uncharacterized, and no real data has been
analyzed. The question of whether φ-retracement structure exists in real markets remains open and
unanswered by this project as it currently stands.

REMAINING BLOCKERS:
1. Granularity gate failure at coarse tick resolution — unresolved, no registered domain exclusion.
2. Per-DGP FPR gate failure for `trend_plus_noise` under replication — newly demonstrated, unresolved.
3. Numerical pre-registration unfrozen (exact comparison set `C`, `δ_min`, Dataset A/B identities and
   hashes, block-length estimator configuration, RNG seed) — human/methodologist decision.
4. Full-scale (10,000/20,000-per-DGP) validation never run.
5. Bootstrap-coverage validation (an original Arbiter gate) never demonstrated at scale for either
   estimand.

FUTURE WORK:
- Methodologist resolution of the granularity artefact (e.g. exact Cholesky/Davies–Harte fBm and exact
  GARCH/IAAFT surrogates in place of the current documented approximations, and/or a registered
  minimum-tick-resolution eligibility rule).
- Methodologist investigation of why `trend_plus_noise` specifically shows elevated false-positive rate
  under the surrogate-standardized test, and whether a structural fix (vs. a data artefact) is needed.
- Exercise the mandated secondary (GARCH) and tertiary (IAAFT) surrogate families in the validation
  battery, not only in unit tests.
- Characterize φ-vs-5/8 rational specificity (Holm-adjusted) against the full null-DGP suite, not a
  single toy series.
- Freeze the numerical pre-registration, then run the full-scale validation, before any confirmatory
  step is considered.

No further action is planned in this session. PROJECT FINALIZED AS A SCIENTIFIC INVESTIGATION.
