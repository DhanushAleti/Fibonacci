# PHI: A Falsifiable Test of Golden-Ratio Retracement Specificity in Time Series — Final Research Report

**Status:** Confirmatory analysis not authorized. No claim about φ in real markets is made or supported.
**Date:** 2026-08-13

## Abstract

We pre-specified a confirmatory procedure to test whether the golden-ratio constant `q_φ = 1/φ ≈
0.618` is associated with excursion retracements in eligible time series to a degree distinguishable
from scientifically matched non-φ constants, under dependence-aware inference and multiplicity control.
Before any real-data use, we subjected the frozen procedure to an adversarial synthetic validation: 13
null data-generating processes (no φ mechanism present) with 1,950 total simulated trials. The procedure
rejected the null in **100% of trials**, an aggregate false-positive rate of 1.0 against a nominal 0.05.
We show analytically that this is not an implementation defect but a consequence of Jensen's inequality
applied to a convex distance functional against a control set symmetric about `q_φ`: the test statistic
is mechanically non-negative for any distribution. We implemented a pre-arbitrated repair that
standardizes the statistic against a surrogate-data null distribution rather than against zero. The
repair reduces the aggregate false-positive rate from 1.0 to approximately 0.01 at small scale, and a
constant-sweep check confirms the geometric bias is specifically removed. However, the repair's own
five-part acceptance gate does not pass: a granularity audit shows φ's false-positive rate rises to 0.22
at coarse (10-level) tick discretization, and a targeted multi-seed replication performed for this
report shows the per-DGP false-positive-rate bound is also not reliably met for a trend-plus-noise null
(pooled estimate ≈0.11 against a 0.07 threshold, where the single seed originally reported sat exactly
at the threshold). We conclude that PHI's confirmatory path is correctly not authorized to run on real
data. This is a negative-but-informative result: the falsification apparatus performed as designed,
catching a severe defect in its own primary method before any real-world exposure, and then correctly
declining to certify its own repair as sufficient.

## 1. Research Question

Financial and other time series are informally observed to exhibit "retracements" — partial reversals
of a directional swing — that some practitioners associate with golden-ratio-derived fractions (most
commonly `0.618` and `0.382`). This claim is usually asserted without a falsifiable procedure: no
pre-specified null, no matched controls, no correction for the fact that any constant in `(0,1)` will
appear to "fit" some fraction of observed retracements by chance. PHI's research question was
constructed specifically to close that gap: **is `q_φ` associated with retracement concentration to a
degree that survives comparison against symmetric, scientifically matched alternative constants, after
accounting for temporal dependence in the underlying series and multiplicity across the constants
tested?** This is a test of φ *specialness*, not of φ *presence* — a procedure that merely detects
"some" retracement clustering near 0.618 without checking whether nearby non-φ constants cluster just as
well answers a different, much weaker question.

## 2. Pre-Specified Method

The method was frozen before any validation was run (`docs/05-mathematics/phi-phase4-scientific-
contract.md`; implementation `src/phi/phase4/`, 14 modules, 83 dedicated tests at the time of freezing).
Construction: excursions are identified by a deterministic three-point local-extrema rule (no smoothing,
no fitted parameters); each completed excursion yields a terminal retracement ratio `R ∈ [0,1]`
(overshoots `R>1` are reported, not discarded). The primary estimand was

```
Δ_φ = mean_{q∈C} E[|R−q|] − E[|R−q_φ|]
```

for a control set `C` of constants symmetric about and equally spaced around `q_φ`, tested one-sided
against `H0: Δ_φ ≤ 0` at `α = 0.05`, using a stationary bootstrap over excursion blocks with an
automatic (Politis–White) block-length estimator and Holm step-down multiplicity correction across
constants. A fail-closed gate (`is_confirmatory_authorized()`) was built to refuse execution on real
data unless a complete numerical pre-registration (exact `C`, minimum meaningful effect size `δ_min`,
dataset identities, seed, code/environment provenance) was frozen **and** a battery of synthetic
validation gates (null-calibration, power, bootstrap coverage) had passed. At the time of freezing, none
of the numerical registration was complete and none of the validation gates had been demonstrated — the
method was implemented but not yet authorized to run, by design.

## 3. Synthetic Falsification

Before any registration was attempted, the frozen procedure was run against synthetic data with known
generating mechanisms and *no φ structure whatsoever* — the standard falsification move of asking
whether a test rejects its own null too often when the null is, by construction, true.

**Design.** Thirteen null data-generating processes were registered in advance: IID Gaussian, IID
heavy-tailed (Student-t), random walk, AR(1), AR(2), trend-plus-noise, seasonal, heteroskedastic,
GARCH(1,1) volatility clustering, regime-switching, autocorrelated heavy-tailed, a market-like
AR+GARCH composite, and a coarse-tick-discretized microstructure null. Each was simulated 150 times at
length 400 with 199 bootstrap replicates (1,950 total null trials), plus positive- and negative-control
injections and a constant-sweep check. The harness and its raw output are preserved at
`scripts/phase4_synthetic_validation.py` and `results/phase4_validation/results.json`.

**Result.** Every one of the 13 null processes produced a false-positive rate of **1.000** (Wilson 95%
CI `[0.975, 1.0]` in each case), against a nominal 0.05. Pooled across all 1,950 null trials: 1,950
rejections, aggregate FPR 1.000. The mean observed `Δ̂_φ` under pure noise was consistently positive
(≈+0.016 to +0.024 depending on the process) — small in absolute terms, but reliably on the wrong side
of zero for a test calibrated at `α=0.05`.

A **constant sweep** — the decisive diagnostic — computed the same statistic for five different focal
constants (0.25, 0.40, 0.50, `q_φ≈0.618`, 0.75), each against its own symmetric control set, on pooled
IID-Gaussian null data. Every constant showed a positive "advantage" over its own controls; φ ranked
**fourth of five**, and the global landscape of mean absolute distance minimized near `q ≈ 0.396` — a
value with no known relationship to φ. This directly demonstrates that the original failure is a
property of the test's geometry, not of the data having any special relationship to φ.

A temporal-leakage battery (look-ahead injection, scale/shift invariance) and a reproducibility check
(same seed → identical output; different seed → different output) both passed cleanly, isolating the
defect to the estimand itself rather than to data handling or non-determinism.

## 4. Failure Diagnosis

The mechanism is a direct consequence of Jensen's inequality. Let `M(q) = E|R−q|`, a convex function of
`q` for any fixed distribution of `R`. If `C` is symmetric about `q_φ` — for every `q_φ+δ` in `C` there
is a matched `q_φ−δ` — then by convexity `mean_{q∈C} M(q) ≥ M(q_φ)` for **any** distribution of `R`,
with equality only in degenerate cases. Therefore `Δ_φ = mean_{q∈C} M(q) − M(q_φ) ≥ 0` unconditionally.
Testing a quantity that is mechanically non-negative against a null of "equals zero" produces a test
that rejects essentially always, regardless of whether the data contains any φ-related structure. This
is not a bug in the code; it is a mathematical property of the estimand paired with a symmetric control
set, and it would reproduce in any correct implementation of the same specification. It is recorded as a
permanent regression test (`tests/phase4/test_estimand.py::TestJensenGeometricBias`) precisely so that
no future change can silently reintroduce a symmetric-control comparison against zero as a confirmatory
test.

## 5. Repair

An arbitrated repair (pre-specified separately from this report; implemented in `src/phi/phase4/
repair/`) replaces the zero-referenced test with a **surrogate-standardized** score:

```
Z_φ = (Δ_obs − μ_null) / σ_null
```

where `μ_null, σ_null` are the mean and standard deviation of the same `Δ` statistic computed on
surrogate resamples of the *same observed series* — primarily block-permutation surrogates, which
preserve local dependence, tick granularity, and volatility clustering while destroying long-range
φ-specific alignment (GARCH-parametric and IAAFT surrogates are also implemented as a mandated
secondary/tertiary check; see §7 for their validation status). Under this construction, a null series is
exchangeable with its own surrogates, so `E[Z_φ] ≈ 0` under the null regardless of the Jensen bias, which
affects the observed and surrogate statistics identically and cancels in standardization. The original
`Δ_φ`-vs-zero statistic is retained only as an explicitly labeled, non-confirmatory descriptive
statistic; `run_confirmatory_repair` is structurally incapable of invoking it. The repair also replaces
the dense-grid comparison set with four pre-specified rational fractions used in technical-analysis
practice (`1/2, 3/5, 5/8, 2/3`) — chosen specifically because `5/8 = 0.625` is numerically close to
`q_φ ≈ 0.618`, making it the sharpest available test of whether φ is distinguishable from a
microstructure-plausible neighbor rather than merely from "a generic constant."

## 6. Adversarial Validation of the Repair

The repair carries its own five-part acceptance gate, run at reduced scale (`n_series=100`,
`series_length=400`, `n_surrogates=99`, single base seed `20260812`) before any larger commitment of
compute: (1) aggregate false-positive rate ≤ 0.05 across the null suite; (2) per-DGP false-positive rate
≤ 0.07, any single failing process blocking the study; (3) positive-control power ≥ 0.80 at a medium
injection rate; (4) a granularity audit requiring φ's false-positive rate to stay ≤ 0.07 as the data is
discretized onto coarser grids; (5) constant-sweep symmetry, confirming φ is no longer preferentially
favored over nearby constants under the null.

At this scale, gates 1, 3, and 5 pass with room to spare: aggregate FPR fell from 1.0 to 0.0108, power
was 0.82, and the constant sweep showed φ, 0.382, and 0.5 all producing FPR 0.0 under the null — direct
confirmation that surrogate standardization removes the geometric bias identified in §4. Gate 4
(granularity) fails: φ's false-positive rate is 0.0 at tick resolutions of 1000, 100, and 50, but rises
to **0.22** at a resolution of 10 — the predicted signature of the `5/8 ≈ q_φ` discretization artefact
the audit exists to detect. No pre-registered rule excludes coarse-resolution data from the confirmatory
domain, so this stands as a genuine, unresolved vulnerability rather than an out-of-scope edge case.

Gate 2 (per-DGP FPR) was reported as passing at the reduced scale, with the maximum across all 13 null
processes — trend-plus-noise — landing at exactly 0.07, the threshold itself. Because a value sitting
precisely on its own decision boundary at `n=100` carries substantial sampling uncertainty (binomial
standard error ≈0.025 at that scale), this report performed a targeted, moderate replication rather than
accepting the single-seed value at face value: the trend-plus-noise false-positive rate was re-estimated
using the same unmodified harness at six additional independent seeds (five at the original `n=100`
scale, two at a larger `n=300` scale), plus an exact reproduction of the original seed as a determinism
check. The reproduction matched exactly (0.07), confirming the harness is deterministic and the original
number was not a transcription error. But the six independent replications produced 0.11, 0.13, 0.16,
0.12, 0.11 (at `n=100`) and 0.1067, 0.0933 (at `n=300`) — pooling all eight runs (1,200 total simulated
series) gives a false-positive rate estimate of **≈0.108**, with an approximate 95% confidence interval
of **[0.091, 0.126]**, entirely above the 0.07 threshold. The single value originally reported was the
low tail of sampling variability, not a representative estimate. **Gate 2, like Gate 4, does not
robustly pass.**

A further review of the repair's own code, undertaken for this report, surfaces two additional
unresolved gaps that had not previously been documented as such. First, the mandated secondary and
tertiary surrogate families (GARCH-parametric and IAAFT) exist and are unit-tested for basic correctness
but are not invoked anywhere in the validation-gate battery — every gate above was computed using only
the primary block-permutation surrogate, so the repair's calibration has been characterized against one
null-generating mechanism for the surrogates themselves, not the full mandated hierarchy. Second, the
specific pairwise test of φ against its closest rational competitor (`5/8`, via Holm-adjusted surrogate
p-values — the sharpest available test of φ specificity, per §5) is implemented but has been exercised
exactly once, in a single unit test on one synthetic series with one seed; it has never been run against
the 13-process null suite to characterize its own false-positive behavior, the way the aggregate `Z_φ`
statistic has.

## 7. Residual Limitations

- The granularity failure (§6) is real, reproducible from the existing artifact, and not excluded by any
  registered domain boundary.
- The per-DGP false-positive bound for trend-plus-noise does not robustly hold under replication (§6, a
  new finding from this report, produced without modifying the DGP, estimand, or threshold).
- Rational-fraction specificity against `5/8` — the comparison that would most directly demonstrate φ is
  not just "a constant that fits" but *the* constant that fits — is implemented but statistically
  uncharacterized.
- Calibration evidence for the repair rests on one surrogate family; the two other mandated families are
  unused in validation.
- The positive control's injection mechanism is an acknowledged simplification of the originally
  specified construction, and power has been measured at only one signal-strength level against a
  synthetic effect of unknown relationship to any real-world retracement magnitude.
- No full-scale (10,000/20,000-per-DGP) validation run has ever been executed; all evidence above comes
  from reduced-scale runs plus this report's own moderate-scale replication.
- The numerical pre-registration (exact comparison set, minimum effect size, dataset identities, block-
  length configuration, random seed) remains unfrozen, a decision reserved for a human methodologist and
  explicitly out of scope for automated resolution.
- No real market data has been used at any point in this research program.

## 8. Final Scientific Decision

The evidence supports three separable conclusions. First, the original confirmatory method was
definitively falsified before real-data exposure, for a reason that is mathematically understood rather
than merely observed — this is the falsification apparatus working as intended. Second, the repair is a
genuine and substantial improvement, not a failed patch: it demonstrably neutralizes the specific bias
identified in §4, with clean evidence on three of five acceptance-gate dimensions. Third, the repair does
not yet meet its own bar for confirmatory use: two of five gates fail or do not survive replication, and
two further validation gaps (surrogate-family coverage, rational-specificity characterization) were
identified in the course of preparing this report. The correct and only scientifically defensible
disposition is to leave the confirmatory path fail-closed, as it already is in code, and to treat further
repair — resolving the granularity and per-DGP findings, exercising the full surrogate hierarchy,
characterizing φ-vs-5/8 specificity at scale, and only then running the deferred full-scale validation —
as necessary future work for a methodologist, not as something to be resolved by adjusting thresholds or
selecting a more favorable seed. No claim that golden-ratio retracements are, or are not, a real property
of any time series is made by this report. The question remains open.
