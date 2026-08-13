# PHI v0.3.0 Pre-Implementation Methodological Arbitration

**Role:** Read-only forensic audit and candidate methodological specification.
**Status:** CANDIDATE SPECIFICATION ONLY. No code was modified. No validation was
run. No real data was touched. No threshold, DGP, or test was changed. Nothing
in this document authorizes implementation, confirmatory validation, or real-data
analysis.
**Repository state at audit time:** `VERSION` = `0.2.0`; no `v0.3.0` identifier
exists anywhere else in the repository. This document is the first place that
label appears — it names a *candidate*, not an accepted release.
**Governs relative to:** [`docs/PHI_FINAL_SCIENTIFIC_STATUS.md`](../PHI_FINAL_SCIENTIFIC_STATUS.md)
remains the authoritative statement of v0.2.0's status. This document does not
supersede it; it extends the audit forward, read-only, toward a *candidate*
v0.3.0 that is explicitly **not yet authorized**.

---

## 0. Method note on this audit

The brief that initiated this audit ("the latest arbitration concluded…")
asserts fourteen claims, including two numeric ones — an information-resolution
lower bound of "approximately M ≥ 72" and a proposed conservative margin of
"M ≥ 100." **No document or artifact matching that exact prior arbitration
exists in this repository** (verified: `grep` across `docs/`, `src/`, root
markdown for "M ≥ 72", "information-resolution", "one additional validation
cycle", "governance rule" and related terms returns no hits outside this file).
Claims 1–4, 11, and 12 of the brief are independently and exactly verified
against `docs/PHI_FINAL_SCIENTIFIC_STATUS.md` and the underlying artifacts
(§1 below). Claims 5–10 and 13–14 are **not pre-existing repository record** —
they are treated here as hypotheses to be independently audited against code,
exactly as the brief instructs ("do not assume documentation matches
implementation"). Where this audit derives a number independently (§C) it
arrives at the same M ≥ 72 figure by an explicit, reproducible calculation —
that convergence is reported as a finding, not assumed.

---

## PART A — Reconstruction of the Actual v0.2.0 (and repair) Method

Legend: **CODE** = established by reading the implementation directly this
session. **DOC** = asserted in documentation; cross-checked against code where
noted. **GAP** = documented but not enforced in code. **UNKNOWN** = could not be
determined from repository evidence.

| # | Item | Status | Evidence |
|---|---|---|---|
| 1 | Estimand (original) | **CODE** | `Δ_φ = mean_{q∈C} E\|R−q\| − E\|R−q_φ\|`, paired per-excursion: [`src/phi/phase4/estimand.py:36-67`](../../src/phi/phase4/estimand.py). Permanently forbidden as confirmatory (Jensen bias, proven §6 below). |
| 1b | Estimand (repair) | **CODE** | `Z_φ = (Δ_obs − μ_null)/σ_null` over `n_surrogates` block-permutation surrogates of the *same* series: [`src/phi/phase4/repair/zscore.py:68-111`](../../src/phi/phase4/repair/zscore.py). |
| 2 | Test statistic / p-value | **CODE** | Surrogate-rank p-value `p = (1+#{Δ^(s) ≥ Δ_obs})/(S+1)`: [`zscore.py:100-102`](../../src/phi/phase4/repair/zscore.py). Reject `H0: Z_φ ≤ 0` iff `p < α`. |
| 3 | Null / alternative | **CODE** | Original: `H0: Δ_φ ≤ 0` vs `H1: Δ_φ>0` (one-sided, α=0.05) — [`phase4/constants.py:24,34`](../../src/phi/phase4/constants.py). Repair: `H0: Z_φ ≤ 0`, same α, same one-sidedness — inherited, not re-derived. |
| 4 | Surrogate generation | **CODE** | Three families, non-detrended: block-permutation (circular rotation + block shuffle, exact-marginal-preserving), GARCH(1,1)-matched increments, IAAFT — [`repair/surrogates.py:48-129`](../../src/phi/phase4/repair/surrogates.py). **No detrending step exists in any surrogate generator.** |
| 5 | Block-length rule | **CODE** | Politis–White (2004) automatic block length from the *increment* series' autocovariance, flat-top lag window — [`phase4/inference.py:49-87`](../../src/phi/phase4/inference.py), reused by the repair via [`repair/surrogates.py:40-45`](../../src/phi/phase4/repair/surrogates.py). Never a function of the test outcome (verified: no branch in the block-length code reads any test statistic). |
| 6 | Excursion / extrema definition | **CODE** | Deterministic three-point local extrema on run-length-compressed values; even-length plateaus dropped (no unique midpoint); no smoothing, no amplitude threshold — [`phase4/extrema.py:105-145`](../../src/phi/phase4/extrema.py). Retracement is the *terminal* value at the next extremum: `R_i = |X_{E_{i+1}}−X_{E_i}| / |X_{E_i}−X_{A_i}|` — [`phase4/retracement.py:1-27,76-102`](../../src/phi/phase4/retracement.py). This is flagged in the contract itself as an interpretation choice ("if the methodologist intends a different per-excursion reduction, only this module changes" — `retracement.py:15-21`), i.e. **DOC-flagged, not fully closed**. |
| 7 | Rational controls | **CODE** | `{1/2, 3/5, 5/8, 2/3}`, fixed dict, no dense grid — [`repair/rational.py:19-24`](../../src/phi/phase4/repair/rational.py). `dense_grid`/top-percentile machinery exists only in the *original* secondary landscape ([`estimand.py:99-111`](../../src/phi/phase4/estimand.py)) and is explicitly asserted absent from the repair namespace by test: [`tests/phase4/repair/test_contract.py:26-29`](../../tests/phase4/repair/test_contract.py). |
| 8 | p-value construction | **CODE** | Surrogate-rank (repair) vs null-recentred stationary-bootstrap (original) — both add-one-smoothed, both report MC/finite-sample structure. Original also reports `p_value_mc_se` — [`inference.py:109-172`](../../src/phi/phase4/inference.py); the repair's `standardized_null_score` does **not** report an analogous MC-error term for `surrogate_p` (**GAP** — no code computes it; only `n_surrogates` is retained). |
| 9 | Holm procedure | **CODE** | Standard Holm (1979) step-down, monotone-adjusted p-values via running max, single shared implementation reused by both original and repair — [`phase4/multiplicity.py:23-47`](../../src/phi/phase4/multiplicity.py). Read and re-derived by hand this session; matches the textbook algorithm exactly (sort ascending, multiply by `m-rank`, enforce monotonicity, clip at 1). No defect found. |
| 10 | Validation gates (repair) | **CODE** | Five gates, all fail-closed booleans on `RepairPreRegistration`: aggregate FPR ≤0.05, per-DGP FPR ≤0.07, power ≥0.80, granularity pass, constant-sweep symmetry — [`repair/registration.py:181-198`](../../src/phi/phase4/repair/registration.py). Gate *values* are not computed by the registration object itself; they must be supplied by the caller from `run_repair_validation()` output — the registration only checks thresholds. This is a real coupling risk (**GAP**, §G below): nothing in the type system prevents a caller from hand-supplying a gate value that was never actually produced by the harness. |
| 11 | Granularity implementation | **CODE** | Audited in depth, §C below. Summary: discretizes the *raw series* (not R directly) onto `n_levels` equal ticks spanning the series' own min–max range, then measures φ's surrogate-test FPR at each resolution — [`repair/granularity.py:41-103`](../../src/phi/phase4/repair/granularity.py). |
| 12 | Pre-registration fields | **CODE** | Original `Phase4PreRegistration`: 11 required numerical fields + a structurally-validated `comparison_set` — [`phase4/registration.py:148-161`](../../src/phi/phase4/registration.py). Repair `RepairPreRegistration`: **9** required fields — [`repair/registration.py:166-176`](../../src/phi/phase4/repair/registration.py). **Finding (new this session):** the repair schema *drops* `delta_min` and `falsification_criteria` as tracked fields entirely — they do not exist on `RepairPreRegistration` at all, whereas they were required, tracked blockers on the original. This is a silent narrowing of what "fully registered" means between the two schemas and is not called out in any existing document. |
| 13 | Real-data fail-closed mechanism | **CODE** | `is_confirmatory_authorized()` on both registration classes: `not missing_registrations() and not failed_gates()` (repair) / `... and comparison_set_is_valid() and not failed_validation_gates()` (original) — both fail closed on any single omission, verified by direct unit tests (`test_registration_repair.py::TestFailClosedGate`, exercised this session by re-reading, not re-running). `run_confirmatory_repair` additionally checks dataset role and content-hash match before executing — [`repair/registration.py:205-235`](../../src/phi/phase4/repair/registration.py). No path was found by which either confirmatory function can execute without passing through `is_confirmatory_authorized()` first (verified by reading every caller of `confirmatory_phi_test` / `run_confirmatory_repair` in `src/` and `tests/`). |

### Independently reproduced numeric claims (Part A cross-check with Part I of the brief)

Reproduced directly from `results/phase4_repair_validation/results.json` and
`results/phase4_repair_validation/trend_plus_noise_reverification.json` this
session (files read, not regenerated):

- Gate 2 (`trend_plus_noise`), grand-pooled across 8 seeds/1,200 series:
  **FPR = 0.1083**, approx. 95% CI **[0.0907, 0.1259]**, entirely above the
  0.07 threshold. Matches brief claim #2 exactly.
- Gate 4 (granularity), 10-tick resolution: **φ FPR = 0.22**, vs. 0.07
  threshold. Matches brief claim #3 exactly.
- `overall_pass: false`, `proceed_to_real_data: false` recorded directly in
  the artifact.

Claims #1 (v0.2.0 FAILED), #4 (`Δ_φ>0` invalid as confirmatory evidence), #5
(Zφ promising-but-not-validated), #11 (real-data blocked), #12 (any v0.3.0
change invalidates v0.2.0's evidentiary support — this is the direct,
necessary consequence of `content_hash()` binding every registration field,
`registration.py:200-202` / `repair/registration.py:200-202`) are all
independently confirmed by the same evidence.

---

## PART B — Audit of the Proposed "Detrended Block Permutation" Repair

**No implementation of detrended block permutation exists anywhere in this
repository** (confirmed by exhaustive `grep -rniI "detrend"` across `src/`,
`tests/`, `docs/` — zero hits). This section audits it purely as a *candidate
algorithm*, per the brief's request, without assuming it is correct.

### B.1 What the candidate would concretely mean

The most natural reading, matching the brief's sketch:

```
X_t = trend_hat_t + residual_t
1. fit trend_hat_t (some estimator) to X_t
2. residual_t = X_t − trend_hat_t
3. estimate block length L on residual_t (not X_t) via the existing
   Politis–White estimator (repair/surrogates.py:40-45 already operates on
   np.diff(x), so it would need to operate on the residual instead)
4. block-permute residual_t → residual*_t (reuse
   block_permutation_surrogate's block/rotation logic, applied to residuals)
5. reconstruct X*_t = trend_hat_t + residual*_t
6. run the existing three-point-extrema / retracement pipeline on X*_t
```

### B.2 Why this is plausible for exactly one DGP and unproven for the rest

`trend_plus_noise` is defined as `np.linspace(0, slope, n) + rng.standard_normal(n)`
— [`phase4/nulldgp.py:83-85`](../../src/phi/phase4/nulldgp.py), a literal
deterministic linear trend plus IID noise. For *this* DGP, OLS-linear
detrending recovers close to the true generative decomposition, and the
current (non-detrended) `block_permutation_surrogate` is a plausible root
cause of the observed Gate-2 failure: permuting blocks of a monotonically
increasing series creates discontinuities at block boundaries that the
original series does not have, so the surrogate's excursion/retracement
geometry is **not exchangeable** with the observed series under the null —
violating the exact property (`repair/surrogates.py:1-9` docstring:
"the observed series is exchangeable with its surrogates") the whole
standardization depends on. This is a mechanistically coherent explanation of
why `trend_plus_noise` specifically, and (per the artifact) *only*
`trend_plus_noise` among the 13, shows elevated FPR.

That coherence does **not** extend to the other 12 DGPs:

| DGP | Has a deterministic trend? | Effect of OLS-linear detrending |
|---|---|---|
| `iid_gaussian`, `iid_heavy_tailed` | No | Near-zero-slope fit; effectively a no-op | ESTABLISHED (trivially, by construction) |
| `random_walk`, `ar1`, `ar_p`, `market_like` | No — **stochastic/near-unit-root** trend | OLS-detrending a random walk is a classical spurious-regression hazard: a fitted line on a single realization does not remove non-stationarity, and the residual retains complex, near-unit-root dependence that the block-length estimator was never validated against | **HYPOTHESIS / REQUIRES EXPLORATORY TEST** |
| `regime_switching` | No — structural break, not a smooth trend | A single linear fit across a regime break is misspecified in both directions | **HYPOTHESIS / REQUIRES EXPLORATORY TEST** |
| `heteroskedastic`, `garch11`, `autocorr_heavy` | No (mean ≈ 0, variance varies) | Likely near-no-op on the mean, but detrending logic has never been tested against volatility-clustering residuals for its effect on block-length estimation | **UNKNOWN** |
| `seasonality` | Periodic, not linear | A *linear* trend estimator is misspecified for a sinusoid; would require a different (non-linear/periodic) estimator entirely, contradicting a single fixed "the trend estimator" | **HYPOTHESIS — likely wrong as stated** |
| `coarse_tick` | No | Interacts with granularity (§C); detrending a discretized AR(1) has not been analyzed at all | **UNKNOWN** |

### B.3 Direct answers to the brief's B-section questions

| Question | Classification | Basis |
|---|---|---|
| What trend estimator? | **NOT YET SPECIFIED** | No candidate implementation exists to inspect; "linear OLS" is the only reading consistent with matching `trend_plus_noise`'s own DGP, but the brief itself asks what happens for nonlinear/stochastic trends — see below. |
| Nonlinear true trend? | **HYPOTHESIS / REQUIRES EXPLORATORY TEST** | `seasonality` DGP is a direct nonlinear-trend counter-example already in the immutable 13-DGP suite (`repair/validation.py:59`); a linear estimator is provably misspecified for it. |
| Stochastic trend? | **HYPOTHESIS / REQUIRES EXPLORATORY TEST** | `random_walk`/`ar1`/`ar_p`/`market_like` are stochastic-trend/near-unit-root by construction; OLS-linear detrending of a random walk is a textbook-documented source of spurious structure, not a validated repair for this codebase. |
| Does it preserve the null being tested? | **UNKNOWN, DGP-dependent** | Depends entirely on whether `trend_hat_t` recovers the DGP's actual deterministic component; true only where a linear deterministic component exists (1 of 13 DGPs by construction). |
| Does reconstruction preserve excursion geometry? | **REQUIRES EXPLORATORY TEST** | `three_point_extrema` operates on absolute levels (`extrema.py:105-130`); reattaching `trend_hat_t` to *permuted* residual blocks was never run through the extrema detector in this repository — no evidence either way. |
| Preserves marginal distribution? | **PARTIALLY ESTABLISHABLE ANALYTICALLY, NOT VERIFIED IN CODE** | Block-permuting residuals preserves the residual multiset exactly (as the existing `block_permutation_surrogate` does for raw values — proven by `test_surrogates.py::test_preserves_the_exact_marginal`), but the *reconstructed series'* marginal (trend + permuted residual) is not the same object and has not been checked. |
| Preserves volatility clustering? | **LIKELY, FOR NON-TREND DGPs; UNTESTED** | If the trend fit is near-zero-slope for volatility-clustering DGPs (no deterministic mean trend), the residual ≈ the original series and behavior should reduce to the current method — but this reduction has not been demonstrated in code. |
| Introduces artifacts? | **UNKNOWN** | No implementation to test. |
| Creates a different null hypothesis? | **YES, for stochastic-trend DGPs — HYPOTHESIS graded as plausible** | Detrending a random walk changes what "no φ mechanism" means for that null: the surrogate reference distribution would no longer be built from the DGP's own generative process but from a linearly-detrended approximation of it — a different (and unvalidated) implicit null. |
| Appropriate for all 13 DGPs? | **NO — established by counter-example (`seasonality`), not merely unproven** | A single fixed linear-trend-and-permute algorithm is mathematically misspecified for at least one already-registered DGP. |
| Could one surrogate algorithm validly cover all 13 DGP classes? | **HYPOTHESIS, currently unsupported** | No evidence in this repository establishes this either way; the existing three-family hierarchy (block-permutation primary / GARCH secondary / IAAFT tertiary) already implies the project's own prior judgment was "no single family is sufficient," which cuts against assuming a fourth single family would be. |

**Conclusion of Part B:** Detrended block permutation is a **mechanistically
plausible, narrowly-targeted HYPOTHESIS** for repairing the `trend_plus_noise`
failure specifically. It is not established as a general repair, is
provably misspecified for at least one DGP already in the immutable suite
(`seasonality`) if implemented as a single linear-OLS detrend, and is
untested for the stochastic-trend DGPs where it carries real risk of
introducing new bias rather than removing it. It must not be described as a
"fix" — it is a candidate requiring exploratory validation against the full
13-DGP suite before any confirmatory role.

---

## PART C — Resolution Boundary Audit (M ≥ 50 vs 72 vs 100)

### C.1 What the code actually does

`granularity_audit` (`repair/granularity.py:68-103`) discretizes a **continuous
fBm path** (approximate spectral-synthesis fBm, itself flagged in the module
docstring as non-exact) onto `n_levels` (=`M`) equal-width ticks spanning
**that path's own min–max range**, via `discretize()` (`granularity.py:41-48`):

```
step = (hi − lo) / M
X_discretized = lo + round((X − lo) / step) * step
```

`M` here is the number of levels spanning the **entire series' price range**,
not a per-excursion or per-retracement resolution parameter, and not a
direct quantization of the retracement ratio `R ∈ [0,1]`. `R` is computed
*after* discretization, as a ratio of two differences of already-discretized
values: `R_i = |X_{E_{i+1}} − X_{E_i}| / |X_{E_i} − X_{A_i}|`.

Tested resolutions in the existing artifact: `M ∈ {1000, 100, 50, 10}`. Result:
φ FPR = 0.0 at 1000/100/50, **0.22 at 10**
(`results/phase4_repair_validation/results.json`, `gate_4_granularity`).

### C.2 Where "M ≥ 50" actually comes from

**M ≥ 50 is not derived from any criterion in the code.** It is exactly what
the brief already states: the smallest of the four *tested* values that
happened to show FPR = 0.0. No mathematical relationship between 50 and any
distinguishability criterion appears anywhere in `granularity.py`,
`validation.py`, or the surrounding documentation. **VERDICT: NOT
SCIENTIFICALLY JUSTIFIED — an empirical coincidence of the specific four test
points chosen, not a derived bound.** Nothing in the code or docs asserts a
monotonic relationship between `M` and φ's FPR either — only four points were
sampled, non-uniformly spaced on a log scale, with no interpolation or curve
fit attempted.

### C.3 Independently deriving a candidate M ≥ 72 bound

This audit independently derives a resolution criterion from first
principles, without assuming the brief's number, then checks where it lands.

The sharpest specificity question the project poses is φ vs. its closest
rational competitor, 5/8 (`repair/rational.py:26-27`, `FIVE_EIGHTHS = 0.625`):

```
q_φ = 1/φ ≈ 0.6180339887
5/8 = 0.625
gap = 5/8 − q_φ ≈ 0.0069660113
```

A standard half-tick distinguishability criterion — two values are
resolvable on a grid of spacing `s = 1/M` (over the unit interval `R∈[0,1]`)
only if `s ≤ gap`, i.e. `1/M ≤ gap`, i.e. `M ≥ 1/gap`; using the conservative
half-tick form `1/(2M) ≤ gap/2` gives the same bound `M ≥ 1/(2·gap)`:

```
M ≥ 1 / (2 × 0.0069660113) ≈ 71.78  ⇒  M ≥ 72
```

This *independently reproduces* the brief's "≈72" figure via an explicit,
reproducible calculation, using only `Q_PHI` and `FIVE_EIGHTHS` as already
defined in `repair/rational.py:16,27`. That convergence is worth taking
seriously as a **candidate exploratory criterion** — but §C.4 shows it does
not transfer cleanly onto the code's actual mechanism.

### C.4 Why this bound does not directly validate the implemented mechanism

The derivation in §C.3 assumes `M` directly quantizes `R` on `[0,1]` at
spacing `1/M`. **That is not what `discretize()` does.** It quantizes the
underlying price series `X` at spacing `(hi−lo)/M`, where `hi−lo` is the
*whole series' range*. The induced quantization step on `R` for a given
excursion `i` is not `1/M` — it is approximately:

```
effective step on R_i  ≈  (hi−lo) / (M · A_i)
```

where `A_i = |X_{E_i} − X_{A_i}|` is *that excursion's own swing magnitude*.
Equivalently, the number of ticks a given excursion actually spans is
`m_i = A_i · M / (hi−lo)`, and `R_i`'s effective resolution is governed by
`m_i`, **not** by the global `M`. Two consequences follow directly:

1. **A fixed global `M` does not guarantee a fixed resolution on `R`.**
   Small-magnitude excursions (common in any of the 13 null DGPs — fBm,
   random-walk, and AR-type paths all have heavy-tailed or highly variable
   swing-size distributions) can span far fewer than `M` ticks even when `M`
   is nominally "high resolution" (e.g. 1000). Those excursions' retracements
   are effectively coarse-grained regardless of the global setting.
2. **The §C.3 bound (`M ≥ 72`) is therefore, at best, a necessary condition
   for the *largest-swing* excursions in a series, not a sufficient
   condition for the population of excursions the estimand actually
   averages over.** No code in this repository computes or reports `m_i`
   per excursion, so this cannot currently be checked, let alone enforced.

**This directly answers the brief's C.9–C.10:** a scientifically defensible
resolution criterion should be keyed to **per-excursion swing-to-tick ratio
(`m_i`)**, e.g. an eligibility filter excluding excursions whose amplitude
spans fewer than some `m_min` ticks, layered on top of (not replacing) a
global grid-density parameter. **No such per-excursion criterion exists in
the code today** (verified: `retracement.py`'s `RetracementObservation` and
`RetracementResult` carry no ticks-per-swing or amplitude field at all).

### C.5 Verdicts

| Claim | Verdict |
|---|---|
| M ≥ 50 justified | **NO — not derived from any principle; an artifact of which four test points were chosen (§C.2).** |
| M ≥ 72 justified | **PARTIALLY — a valid necessary condition under an explicit, reproducible half-tick φ-vs-5/8 criterion (§C.3), but not shown sufficient for the actual per-excursion mechanism (§C.4). Classify: HYPOTHESIS, mathematically motivated, empirically untested.** |
| M ≥ 100 mathematically required | **NO — it is ~1.4× the derived 72 with no stated justification found anywhere in the repository; a safety margin, not a derived quantity.** |
| Should the criterion depend on excursion denominator, not just global M | **YES — established by the mechanism itself (§C.4), independent of any prior claim.** |
| Is a fixed global-M threshold alone scientifically defensible | **NO, not as currently specified — it must be paired with (or replaced by) a per-excursion ticks-spanned eligibility rule before any threshold, 72 or otherwise, can be called sufficient.** |

---

## PART D — Surrogate Null Coherence

### D.1 What the architecture already is (established, not proposed)

The current code **already treats the three surrogate families as a
hierarchy, not a merged composite null**: `repair/surrogates.py:10-22`
explicitly labels block-permutation PRIMARY, GARCH SECONDARY, IAAFT TERTIARY,
and states "these are the *only* surrogate families; the primary confirmatory
test uses block-permutation, with GARCH and IAAFT as the mandated
secondary/tertiary audit." `confirmatory_phi_test` (`repair/registration.py:65-100`)
hard-codes `standardized_null_score(..., surrogate_fn=block_permutation_surrogate)`
as its default and only path in the confirmatory function — GARCH and IAAFT
are never invoked by any confirmatory or validation-gate code path (verified:
`grep` for `garch_surrogate`/`iaaft_surrogate` usage outside `tests/` and their
own module returns zero call sites). **They exist only in unit tests
(`test_surrogates.py:37-42`), which check finiteness/shape, not statistical
calibration.**

### D.2 Direct answer

**They are not one coherent composite null today** — architecturally, they
are already three separate robustness analyses layered as
primary/secondary/tertiary, exactly matching the brief's recommended
"PRIMARY CONFIRMATORY TEST + SECONDARY ROBUSTNESS ANALYSES" structure. This is
a pre-existing, sound design choice (`ESTABLISHED BY CODE`), not something
that needs to be invented. The actual gap is not architectural — it is that
the secondary/tertiary legs are **implemented but never executed as
robustness analyses** (no gate, no report, no p-value ever computed from
GARCH or IAAFT surrogates on any of the 13 DGPs).

### D.3 Where a candidate detrended-block-permutation surrogate would fit

If validated per Part B, a detrended-block-permutation surrogate would
naturally replace or supplement the *primary* leg only (it targets the same
failure mode as plain block-permutation — non-exchangeability under trend —
not the variance or spectral properties GARCH/IAAFT target). It should **not**
be merged into a single p-value with GARCH/IAAFT; the existing hierarchy
already gives the correct shape for this. The concrete, minimum-scope
change (not yet authorized — see Part F) would be: (a) validate a detrended
variant of the primary surrogate specifically against the `trend_plus_noise`
and `seasonality` DGPs where non-exchangeability is suspected, while (b)
separately exercising GARCH and IAAFT as secondary/tertiary robustness checks
across the full 13-DGP suite, which is already-specified, already-coded work
that has simply never been run.

---

## PART E — φ-vs-5/8 Specificity Audit

| Question | Classification | Evidence |
|---|---|---|
| Is φ-vs-5/8 implemented? | **IMPLEMENTED — yes** | `confirmatory_phi_test` computes per-rational surrogate p-values (including `"5/8"`), Holm-adjusts them, and exposes `beats_five_eighths` — `repair/registration.py:83-99`. |
| Is Holm correctly applied? | **IMPLEMENTED CORRECTLY** | Re-derived the shared `holm_step_down` algorithm by hand this session against the textbook Holm (1979) procedure; matches exactly, including the monotonicity fix via running-max (`multiplicity.py:39-46`). No defect found in the multiplicity code itself. |
| Toy-test coverage only? | **CONFIRMED — yes, exactly one series** | `tests/phase4/repair/test_contract.py:16-25`, `TestOriginalDeltaPhiNotConfirmatory`, calls `confirmatory_phi_test` on a single `np.random.default_rng(0)` random-walk series, seed 20260812. This is the *only* call site of `confirmatory_phi_test` found anywhere in the repository outside its own module (verified by exhaustive grep of `tests/` and `src/`). |
| Validated across the 13-DGP null suite? | **NO — confirmed absent** | `null_suite_fpr` / `surrogate_fpr` (`repair/validation.py:62-105`), which *do* run all 13 DGPs, call `standardized_null_score` directly with the full rational set as a group (`constants=_RATIONALS`), never `confirmatory_phi_test`. The pairwise, Holm-adjusted φ-vs-individual-rational test has no FPR characterization on any DGP beyond the one toy series. |
| Is a "negative control" concept implemented? | **NOT IMPLEMENTED AS A DISTINCT LABELED MECHANISM** | No function, class, or test in the repository is named or documented as a negative control for φ-vs-5/8 specifically. The `coarse_tick` DGP and the granularity audit function as a *de facto* 5/8-confusion detector (by design intent, per `granularity.py:1-9`), but this is not the same instrument as a registered φ-vs-5/8 negative control, and is not described as one anywhere. |

**IMPLEMENTED vs VALIDATED vs SCIENTIFICALLY ESTABLISHED, explicitly
distinguished per the brief's instruction:**

- **IMPLEMENTED:** Yes — the mechanism exists, is type-correct, and is
  exercised by at least one passing test.
- **VALIDATED:** No — its own false-positive rate has never been measured on
  any null DGP beyond a single realization of one process.
- **SCIENTIFICALLY ESTABLISHED:** No — nothing in this repository supports a
  claim that φ is preferred over 5/8 specifically, under any conditions.

**What must be tested before any φ-vs-5/8 claim is possible:** run
`confirmatory_phi_test` (not just `standardized_null_score` against the
grouped rational set) across all 13 DGPs at adequate scale, characterize its
own per-DGP and aggregate false-positive rate on `beats_five_eighths`
specifically, and confirm that rate is ≤ the registered threshold before this
mechanism can contribute to any confirmatory claim. This is exploratory work,
not yet done.

---

## PART F — Candidate v0.3.0 Specification

Every parameter is explicitly labeled. **This is a specification of what
would need to be true, not a statement that it is true.**

| # | Parameter | Value | Label |
|---|---|---|---|
| 1 | Estimand | `Z_φ = (Δ_obs − μ_null)/σ_null`, surrogate-standardized | **FROZEN FROM v0.2.0** (repair contract) |
| 2 | Statistic | Surrogate-rank p-value, add-one-smoothed | **FROZEN FROM v0.2.0** |
| 3 | Null / alternative | `H0: Z_φ ≤ 0` vs `H1: Z_φ>0`, one-sided, α=0.05 | **FROZEN FROM v0.2.0** |
| 4 | Controls | `{1/2, 3/5, 5/8, 2/3}` | **FROZEN FROM v0.2.0** |
| 5 | Excursion definition | Deterministic three-point extrema, terminal retracement | **FROZEN FROM v0.2.0** (flagged interpretation, unchanged) |
| 6 | Primary surrogate family | Block-permutation | **FROZEN FROM v0.2.0**, *unless* §7 changes |
| 7 | Detrended-block-permutation variant | Candidate replacement/supplement to #6, targeted at `trend_plus_noise`/`seasonality` | **MUST BE EXPLORATORY** — Part B; not implemented, not validated, provably misspecified as a single linear estimator for `seasonality` |
| 8 | Trend estimator (if #7 proceeds) | Unspecified — plausibly *different estimators per DGP class* (linear for deterministic-trend DGPs, none/no-op for stationary DGPs, explicitly excluded for stochastic-trend DGPs pending further research) | **NOT YET JUSTIFIED** |
| 9 | Secondary/tertiary surrogates (GARCH, IAAFT) | Exercised across the full 13-DGP suite as independent robustness legs, not merged into the primary p-value | **PROPOSED CHANGE** (activation of already-implemented, currently-unused code — Part D) |
| 10 | Granularity eligibility | Global `M` grid density **plus** a new per-excursion ticks-spanned (`m_i`) minimum, `m_i` not yet defined | **MUST BE EXPLORATORY / NOT YET JUSTIFIED** — Part C; no fixed global `M` (50, 72, or 100) is validated as sufficient given §C.4 |
| 11 | φ-vs-5/8 specificity gate | `confirmatory_phi_test`'s `beats_five_eighths`, run and FPR-characterized across all 13 DGPs, new sixth acceptance-gate criterion | **PROPOSED CHANGE / MUST BE EXPLORATORY** — Part E; mechanism exists, evidence does not |
| 12 | Multiplicity | Holm step-down | **FROZEN FROM v0.2.0** — verified correct, no change proposed |
| 13 | Null DGP suite | The 13 immutable DGPs (`repair/validation.py:59`) | **FROZEN FROM v0.2.0** — brief's own instruction (#7) forbids treating M-threshold or repair changes as license to alter the suite; no DGP change is proposed here |
| 14 | Seeds | Deterministic PCG64, `SeedSequence`-spawned per series | **FROZEN FROM v0.2.0**, mechanism only — the *specific* registered seed remains **NOT YET JUSTIFIED / MUST BE PREREGISTERED** |
| 15 | Sample sizes (exploratory phase) | Not yet specified — must be large enough to resolve the ≈0.10 vs 0.07 Gate-2 gap and the `m_i` distribution question above sampling noise, without being the confirmatory-scale run | **MUST BE PREREGISTERED (for the exploratory phase itself — see Part H)** |
| 16 | Validation gates | The existing five, **plus** a candidate sixth (φ-vs-5/8 own-FPR gate, #11 above) | **PROPOSED CHANGE** |
| 17 | Stopping rule | One exploratory pass per candidate change (detrending, per-excursion granularity rule, φ-vs-5/8 battery), then freeze — no iterate-inspect-tweak-reiterate after any result is seen | **MUST BE PREREGISTERED** — this is a governance decision (Part H), not derivable from code |
| 18 | Provenance/hash requirements | `content_hash()` over the full registration dataclass, as already implemented for both v0.2.0 registration classes | **FROZEN FROM v0.2.0** |
| 19 | Real-data authorization state | Not authorized under v0.2.0; **cannot become authorized under a v0.3.0 that has not itself passed its own five (or six) gates** | **FROZEN — this is a logical consequence, not a policy choice** |

---

## PART G — Scientific Degrees-of-Freedom Audit

| Decision | Current value | Why this value? | Evidence | Post-hoc risk | What must be frozen? |
|---|---|---|---|---|---|
| Primary surrogate family | Block-permutation | Preserves marginal + local dependence + granularity while destroying long-range order | `surrogates.py:1-22` | Low today (pre-specified); **high if a detrended variant is swapped in after seeing the trend_plus_noise failure without exploratory validation across all 13 DGPs** | Whether detrending is adopted, and its exact estimator, before any confirmatory re-run |
| Block length | Politis–White automatic | Data-driven, "never tuned toward significance" (`inference.py:6-7`) | `inference.py:49-87` | Low — formulaic, no free parameter exposed to the researcher | No change proposed; already frozen |
| Granularity `M` threshold | Untested/unset — brief proposes 50, 72, or 100 | None derived in code; §C shows 72 is a defensible *necessary* condition, 50 is an artifact of test-point choice, 100 is an undocumented margin | `granularity.py:68-103`, this audit §C | **High** — picking a number now, after seeing the 10-tick failure and the 50-tick pass, without the per-excursion (`m_i`) analysis in §C.4, is close to the definition of a post-hoc threshold | The eligibility *rule* (global `M` + per-excursion `m_i` minimum), derived and exploratory-tested, before any number is registered |
| Surrogate family activation (GARCH/IAAFT) | Implemented, unused in any gate | No stated reason found for the gap; reads as an oversight, not a decision | `repair/validation.py` (no call sites) | Low to activate (code already exists and is unit-tested for basic correctness); risk is in *interpreting* disagreement between families after the fact | Whether disagreement among the three families blocks confirmation outright or is merely reported |
| Controls set | `{1/2,3/5,5/8,2/3}` | Pre-specified market-microstructure fractions, rejecting a dense grid as "testing optimization, not specialness" | `rational.py:1-9` | Low — fixed, small, symmetric-ish set chosen before any repair validation ran | Already frozen; no change proposed |
| Extrema definition | Deterministic three-point, no smoothing | Explicitly the frozen, lowest-degrees-of-freedom choice in the whole project's history (rejected discretionary swing detection as "the primary hidden p-hacking pathway" — ADR 0003) | `extrema.py:1-24`, `docs/18-decisions/0003-*.md:45` | Low | Already frozen; no change proposed |
| Excursion eligibility filters | `R∈[0,1]` eligible; `R>1` reported, not deleted; zero-denominator → NA | Explicit anti-p-hacking rule ("never epsilon-substituted") | `retracement.py:1-27` | Low | Already frozen |
| DGP parameters (e.g. `trend_plus_noise` slope=5.0) | Fixed defaults in function signatures | No registered alternative parameterization; Arbiter blocker explicitly names "DGP parameters" as still open (`phase4/nulldgp.py:11`) | `nulldgp.py:83-85` | Medium — a slope/parameter choice could itself be why `trend_plus_noise` fails; never varied to check | Exact DGP parameterization, pre-registered, before full-scale validation |
| Seed generation | `SeedSequence(base_seed).spawn(n)` per series, deterministic | Standard, reproducible, already re-verified this session by exact reproduction of a prior run | `validation.py:75-88`; independently reproduced in `trend_plus_noise_reverification.json` | Low mechanism risk; **the `base_seed` itself is an open registration field** (`random_seed: int | None = None`) | The specific registered `base_seed`, chosen *before* any exploratory result is seen |
| Simulation counts (`n_series`, `n_surrogates`) | 100–120 series / 99 surrogates in all validation-battery runs to date | Explicitly "reduced scale," full-scale (10k/20k) never run | `CHANGELOG.md`, `results.json` metadata | Medium — near-boundary gate values (Gate 2 at exactly 0.07 pre-replication) are exactly where small-`n` sampling noise can flip a verdict, as this session's own replication demonstrated | Full-scale run count, pre-registered, run only after all exploratory work above is frozen |
| Gate thresholds (0.05, 0.07, 0.80) | Fixed in `RepairPreRegistration.failed_gates()` | Carried over from the original repair contract; no re-derivation found in this audit | `repair/registration.py:181-194` | Low to change now (none proposed), **high if changed after seeing which gates fail** | Already frozen; this audit does not propose changing them |
| Stopping rule | Not formally coded anywhere; governance language in `CONTRIBUTING.md` ("no result-driven changes," Rule 3) is the closest existing analogue but is general, not specific to a fixed number of validation cycles | The brief's "one additional validation cycle" framing has no direct textual match in this repository; it is a reasonable **extension** of `CONTRIBUTING.md` Rule 3, not a pre-existing rule | `CONTRIBUTING.md:16-19` | High if left unstated — the exact failure mode `CONTRIBUTING.md` was written to prevent | Must be explicitly written down as part of any v0.3.0 preregistration (Part H) |

---

## PART H — Exploratory vs. Confirmatory Firewall

**EXPLORATORY (permitted next, per Part I):**

- Implement and unit-test a detrended-block-permutation surrogate variant.
- Run it (and the existing plain block-permutation surrogate, for
  comparison) against all 13 DGPs at the *existing* reduced scale
  (`n_series≈100-120`, `n_surrogates=99`) — the same scale already used for
  every other exploratory number in this project's history, so this is not a
  scale escalation.
- Compute per-excursion `m_i` (ticks spanned) distributions across the 13
  DGPs at several global `M` values, to characterize whether a per-excursion
  eligibility rule is workable at all before committing to one.
- Run `confirmatory_phi_test`'s `beats_five_eighths` across all 13 DGPs at
  reduced scale to characterize its own false-positive rate.
- Run GARCH and IAAFT surrogates through `null_suite_fpr`-equivalent
  harnesses across the 13 DGPs at reduced scale.

**Exploratory results may NOT, under any circumstance arising from this
audit, be used to:**

- Claim Type-I error control for any v0.3.0 candidate.
- Claim power.
- Claim φ-specificity vs. 5/8.
- Support any real-data claim.
- Directly overwrite `RepairPreRegistration`'s gate fields — those remain
  fail-closed booleans that must come from a **separate, later, full-scale**
  confirmatory-validation run, not from the exploratory pass.

**CONFIRMATORY (blocked until, in this exact order):**

1. Every candidate in Part F is fully specified (no "NOT YET JUSTIFIED" or
   "MUST BE EXPLORATORY" cells remain).
2. Every degree of freedom in Part G's rightmost column is frozen by a
   superseding ADR, per `CONTRIBUTING.md` Rule 3 — including, explicitly, the
   granularity eligibility rule, the detrending decision, and the stopping
   rule itself.
3. A complete numerical preregistration (all fields currently `None` on
   `RepairPreRegistration`, plus any new fields Part F introduces — e.g. a
   registered `m_min`) is filed and hashed.
4. `content_hash()` of that registration is recorded *before* the full-scale
   validation run, exactly as the existing infrastructure already requires
   (`repair/registration.py:200-202`).
5. The exploratory results from Part H's permitted list are sealed —
   referenced for hypothesis justification only, never re-run or cherry-picked
   after the confirmatory registration is frozen.

Only after all five conditions hold does `run_repair_validation` (at
full scale) become the correct next action, and only after *that* passes
does `is_confirmatory_authorized()` — already correctly fail-closed in code
today — become `True`.

---

## PART I — Final Decision

1. **Is v0.2.0 scientifically authorized?** **NO.** Confirmed directly from
   `results/phase4_repair_validation/results.json`: `overall_pass: false`,
   2 of 5 gates fail or fail under replication (granularity, per-DGP FPR).
2. **Is v0.3.0 currently scientifically authorized?** **NO — it does not yet
   exist as an implementation.** This document is the specification, not the
   validation, of a candidate.
3. **Is detrended block permutation proven?** **NO.** Not implemented at all;
   audited in Part B as a targeted hypothesis, plausible for exactly one of
   13 DGPs by construction, provably misspecified as a single linear
   estimator for at least one other (`seasonality`), unknown for the rest.
4. **Is M ≥ 50 justified?** **NO.** An artifact of which four test points
   happened to be sampled (§C.2), not a derived criterion.
5. **Is M ≥ 72 justified?** **PARTIALLY — as a necessary condition under an
   explicit, independently-reproduced half-tick φ-vs-5/8 criterion (§C.3),
   but not shown sufficient for the code's actual per-excursion mechanism
   (§C.4).** Classify as a validated-necessary, unvalidated-sufficient
   candidate, not a proven bound.
6. **Is M ≥ 100 mathematically required?** **NO.** An undocumented ~1.4×
   margin over the derived 72, not itself derived from any stated criterion.
7. **Can GARCH + IAAFT + block permutation form one null?** **They already
   don't, and shouldn't — the existing code already architects them as a
   primary/secondary/tertiary hierarchy of separate robustness analyses
   (Part D), which is the correct design; the gap is that two of the three
   legs are implemented but never executed.**
8. **Is φ-specificity established?** **NO.** Implemented (Part E), never
   validated beyond one toy series, not scientifically established.
9. **Is real-data confirmatory analysis authorized?** **NO.**
   `is_confirmatory_authorized()` returns `False` on both the original and
   repair registration objects today, and every path in this document that
   could change that requires exploratory work, then freezing, then a
   full-scale confirmatory run — none of which has happened.
10. **What is the SINGLE next action?**

    **Run the Part-H exploratory battery (detrended-permutation variant vs.
    all 13 DGPs; per-excursion `m_i` characterization; φ-vs-5/8 own-FPR
    check; GARCH/IAAFT activation) at the existing reduced scale, produce a
    single exploratory findings report, and stop — do not freeze, register,
    or run confirmatory validation in the same pass.** This is the audit
    → specify → exploratory-test step; freeze and confirmatory validation
    are each separate, later, human-gated actions, not bundled into this
    one.

No repair, threshold change, or confirmatory step is recommended in this
document. The default sequence **AUDIT → SPECIFY → EXPLORATORY TEST → FREEZE
→ CONFIRMATORY VALIDATION** is preserved; this document completes only the
first two stages.

---

## SCIENTIFIC STATUS

```
v0.2.0 = FAILED (2 of 5 gates fail or fail under replication; NOT CLEARED — REPAIR REQUIRED)
v0.3.0 = NOT YET IMPLEMENTED (candidate specification only; not authorized)
REAL DATA = NOT AUTHORIZED (no real-world data has ever been used anywhere in this repository)
```

## NEXT ACTION

Run the Part-H exploratory battery (detrended-block-permutation variant
across all 13 DGPs, per-excursion granularity characterization, φ-vs-5/8
own-FPR check, GARCH/IAAFT activation) at existing reduced scale; produce
one exploratory findings report; stop.

## IMPLEMENTATION AUTHORIZATION

**NO**

## CONFIRMATORY VALIDATION AUTHORIZATION

**NO**

## REAL-DATA AUTHORIZATION

**NO**
