# PHI v0.3.0 — Exploratory Battery Specification

**Status:** SPECIFICATION ONLY. Nothing in this document has been executed.
**Scope of this pass:** design only. No source file was modified, no simulation
was run, no validation gate was evaluated, no real data was touched, nothing
was committed.
**Builds on:** [`docs/05-mathematics/PHI_V030_PREIMPLEMENTATION_ARBITRATION.md`](PHI_V030_PREIMPLEMENTATION_ARBITRATION.md)
(the prior read-only audit). Every candidate below traces back to a specific
open question raised there (Parts B, C, D, E, G of that document).
**Absolute rule, inherited from `CONTRIBUTING.md` Rule 3 ("no result-driven
changes") and restated here for this specific battery:** nothing computed by
this battery may be tuned, re-run-until-favorable, or silently promoted to
confirmatory status. Section 12 and Part Q6 make this an explicit, checkable
firewall.

---

## 0. How to read this document

Sections 1–4 (scientific questions, hypotheses, fixed inputs, candidate
methods) are given once, up front, then Q1–Q4 each supply their own exact
experimental matrix, simulation counts, seed protocol, metrics, diagnostics,
and evidence-interpretation rule (items 5–10 of the requested output,
answered per-question because the four questions are methodologically
distinct). Q5 is an audit table, not a simulation. Items 11–15 of the
requested output (what exploratory results may/may not change,
preregistration fields, stopping rules, real-data confirmation) are answered
once, centrally, in Parts Q6–Q8, because they apply identically across Q1–Q4.

---

## 1. Scientific questions (restated from the prior audit)

| Q | Question | Source |
|---|---|---|
| Q1 | Does a detrended block-permutation surrogate improve exchangeability/calibration generally, or does it only patch `trend_plus_noise` while leaving (or harming) the other 12 DGPs? | Arbitration Part B |
| Q2 | What is the actual, code-grounded relationship between global tick-count `M`, per-excursion effective resolution, retracement quantization error, φ-vs-5/8 distinguishability, and false-positive rate — and do M≥72 / M≥100 survive contact with that relationship? | Arbitration Part C |
| Q3 | Does the existing φ-vs-5/8 pairwise Holm test (`confirmatory_phi_test`) have acceptable false-positive behavior across the full null suite, and does it correctly *decline* to prefer φ when the true injected structure favors 5/8 instead? | Arbitration Part E |
| Q4 | Can the already-implemented GARCH and IAAFT surrogate families be activated as independent robustness checks without merging their evidence into the primary p-value? | Arbitration Part D |
| Q5 | What preregistration-schema fields are missing, decorative, or silently unconsumed, beyond the two (`delta_min`, `falsification_criteria`) already found? | Arbitration Part G |
| Q6 | What must the exploratory/confirmatory firewall forbid, precisely, for this specific battery? | Arbitration Part H |

---

## 2. Hypotheses under test

Each is stated so it can fail — none is stated as something this battery is
expected to confirm.

- **H1 (Q1):** A single, fixed, uniformly-applied detrending rule reduces
  `trend_plus_noise`'s surrogate FPR toward the nominal band **without**
  degrading calibration (raising FPR beyond a symmetric noise band) on any of
  the other 12 DGPs. **Falsified if** any other DGP's FPR rises materially
  under the candidate relative to the current mechanism.
- **H2 (Q2):** φ-vs-5/8 distinguishability, and the granularity FPR effect,
  are governed by the *per-excursion* ticks-spanned quantity `m_i`, not by
  the *global* `M` alone. **Falsified if** FPR and distinguishability track
  global `M` well even after controlling for the realized `m_i` distribution
  (i.e., if per-excursion resolution turns out not to add explanatory power
  beyond global M).
- **H3 (Q2, numeric):** Neither `M≥72` nor `M≥100` is a sufficient condition
  for φ-vs-5/8 distinguishability once realistic (heavy-tailed) per-excursion
  swing-size distributions are accounted for. **Falsified if** the measured
  `m_i`-conditional FPR stays at or below the nominal band for essentially
  all excursions once global `M≥72` (respectively `100`).
- **H4 (Q3):** `confirmatory_phi_test`'s `beats_five_eighths` mechanism has a
  per-DGP false-positive rate in a scientifically plausible range (i.e., not
  wildly miscalibrated) across the 13-DGP suite. **Falsified if** any DGP
  shows a `beats_five_eighths` FPR far above the nominal band, or if the
  negative-control experiment shows the mechanism attributing "φ wins" when
  the injected ground truth is 5/8.
- **H5 (Q4):** GARCH- and IAAFT-surrogate FPR broadly agree with the existing
  block-permutation FPR across the 13 DGPs (i.e., the primary result is not
  an artifact specific to one surrogate family). **Falsified if** GARCH or
  IAAFT diverges materially from block-permutation on any DGP.

---

## 3. Fixed inputs (unmodified for every question below)

- **Null DGP suite:** all 13 members of `REPAIR_NULL_SUITE`
  (`src/phi/phase4/repair/validation.py:59`) — `iid_gaussian`,
  `iid_heavy_tailed`, `random_walk`, `ar1`, `heteroskedastic`, `garch11`,
  `regime_switching`, `trend_plus_noise`, `seasonality`, `market_like`,
  `coarse_tick`, `ar_p`, `autocorr_heavy`. **None deleted, none
  reparameterized.**
- **Rational control set:** `{1/2, 3/5, 5/8, 2/3}`
  (`src/phi/phase4/repair/rational.py:19-24`) — unchanged.
- **α:** 0.05 (`phase4/constants.py:24`) — unchanged.
- **Series length:** 400, matching every existing artifact
  (`results/phase4_repair_validation/results.json` metadata).
- **Extrema/retracement construction:** `three_point_extrema` +
  `excursion_retracements`, unchanged (`phase4/extrema.py`,
  `phase4/retracement.py`).
- **Block-length estimator:** `politis_white_block_length`
  (`phase4/inference.py:49-87`), unchanged; reused, not reimplemented, in
  every candidate below.
- **Holm procedure:** `holm_step_down` (`phase4/multiplicity.py:23-47`),
  unchanged.
- **RNG:** `numpy.random.Generator` (PCG64) via `SeedSequence`/`spawn`,
  exactly the pattern already used throughout `repair/validation.py`,
  `repair/granularity.py`, and `phase4/calibration.py`.

---

## 4. Candidate methods (precise, pre-registered-before-execution specifications)

None of the four functions below exist in the repository today. Each is
specified completely here, before any run, per the brief's requirement.
Writing them into `src/` is explicitly **out of scope for this pass** (see
Q7/next action) — they are given as exact pseudocode so a future
implementation is a transcription, not a design decision made after seeing
results.

### 4.1 Candidate B — `detrended_block_permutation_surrogate` (Q1)

```
def detrended_block_permutation_surrogate(series, rng, *, block_length=None):
    x = asarray(series, dtype=float64)
    n = x.size
    if n < 2:
        return x.copy()
    t = arange(n, dtype=float64)
    b, a = polyfit(t, x, deg=1)            # OLS: x ≈ a + b*t (intercept a, slope b)
    trend_hat = a + b * t
    residual = x - trend_hat
    length = block_length_for(residual) if block_length is None else block_length
    permuted_residual = block_permutation_surrogate(residual, rng, block_length=length)
    return trend_hat + permuted_residual
```

Exact specification, item by item (as required before execution):

- **Trend estimator:** ordinary least squares, degree-1 polynomial in the
  integer time index `t = 0..n-1`. **Fixed and uniform across all 13 DGPs —
  no DGP-conditional dispatch.** This is a deliberate choice, not an
  oversight: letting the trend estimator vary by DGP would itself be a
  researcher degree of freedom of exactly the kind `CONTRIBUTING.md` Rule 3
  and ADR 0003 forbid ("free swing-detection parameters are the primary
  hidden p-hacking pathway"). The uniform rule is expected, and permitted, to
  fail on some DGPs — that failure is the finding (H1).
- **Residual construction:** `residual = x − (a + b·t)`, additive only. No
  multiplicative/log-detrending variant is included in this minimal battery.
- **Block-length estimation:** the existing `politis_white_block_length`
  (`phase4/inference.py:49-87`), applied to `np.diff(residual)` — the exact
  analogue of how the current `block_length_for` applies it to
  `np.diff(series)` (`repair/surrogates.py:40-45`). Not reimplemented; reused
  unchanged, on a different input array.
- **Surrogate reconstruction:** `trend_hat + block_permutation_surrogate(residual, rng, block_length=length)`.
  Reuses the existing, tested block/rotation logic
  (`repair/surrogates.py:48-67`) unchanged — the only change from today's
  method is *what array gets shuffled* (residual, not raw series) and *what
  gets added back* (trend_hat).
- **Treatment of the intercept:** included in the fit (`a`), but analytically
  inert for the retracement ratio: `R_i = |X_{E_{i+1}}−X_{E_i}| /
  |X_{E_i}−X_{A_i}|` is a ratio of *differences*, so a constant additive
  shift to the whole reconstructed series cancels exactly. This is not
  assumed — it follows directly from the retracement formula in
  `phase4/retracement.py:9`, and is consistent with the project's own
  existing scale/shift-invariance leakage check (`PHI_FINAL_RESEARCH_REPORT.md`
  §3). Fitting the intercept is retained anyway (standard OLS practice, and
  required for `trend_hat` to sit at the correct level for the *reattachment*
  step, even though it doesn't affect `R`).
- **Treatment of endpoints:** the OLS fit uses the full series with no
  windowing, truncation, or edge-tapering, and is never extrapolated beyond
  `t=0..n−1`, so detrending itself introduces no boundary artifact.
  Circular-rotation wrap-around (`np.roll`, `repair/surrogates.py:64`) is a
  **pre-existing** property of the reused block-permutation logic, unchanged
  by this candidate, and is explicitly *not* being re-audited here — it
  applies identically to variant A and variant B.
- **Treatment of stochastic trends** (`random_walk`, `ar1`, `ar_p`,
  `market_like`, `regime_switching`): the same OLS-linear fit is applied
  blind, with no adaptation. **Pre-registered prediction (not fact):** likely
  neutral-to-harmful, because a single-realization linear fit of a
  near-unit-root process captures sampling-specific drift, not a
  reproducible structural trend, and detrending changes the residual's
  dependence structure in a way this battery is designed to detect, not
  assume away.
- **Treatment of seasonality:** same blind OLS-linear fit. **Pre-registered
  prediction:** likely close to a no-op (a sinusoid over a window that is not
  an exact integer number of periods has a small but generally non-zero OLS
  slope/intercept contribution) — but this is an empirical question the
  battery measures, not an assumption. `seasonality`'s deterministic
  component is periodic, not linear, so a linear estimator is provably
  misspecified for it *in principle*; whether that misspecification is large
  enough to matter *in practice* at `n=400` is exactly what Q1's experiment
  measures.
- **Deterministic random-seed protocol:** see §Q1.5 below — the critical
  design choice is that variant A and variant B consume the **same** `rng`
  seed per series, so the block/rotation random draws are identical between
  them and the comparison isolates the effect of detrending, not
  re-randomization noise.

### 4.2 Candidate — per-excursion effective-resolution instrumentation (Q2)

No new surrogate function is needed; this is a measurement instrument to be
added to `granularity.py`'s existing pipeline. Precise definitions:

```
step(M)      = (hi − lo) / M                          # discretize()'s own tick size, granularity.py:47
m_i(M)       = A_i / step(M)  =  A_i · M / (hi − lo)   # ticks spanned by excursion i's raw amplitude A_i
eps_i(M)     = | R_i^discretized(M) − R_i^raw |        # empirically measured retracement quantization error
```

`hi, lo` are the discretized path's own min/max, exactly as `discretize()`
computes them today (`granularity.py:44`); `A_i = |X_{E_i} − X_{A_i}|` is
computed from the **raw, undiscretized** fBm path, using the existing
`Excursion.magnitude` property (`phase4/extrema.py:69-70`) applied to
extrema located on the raw path. No change to `discretize()` itself is
proposed — this only adds bookkeeping (recording `A_i`, `m_i`, `eps_i`
alongside each retracement observation) that does not exist today.

### 4.3 Candidate — `five_eighths_attractor_garch` (Q3 negative control)

```
def five_eighths_attractor_garch(rng, n, *, inject_prob=0.15, seg_bars=6, noise=0.02):
    # Exact structural copy of phi_attractor_garch (repair/positive_control.py:46-72),
    # with the single substitution FIVE_EIGHTHS in place of Q_PHI on the injection line:
    #     mags[i] = FIVE_EIGHTHS * mags[i - 1]   instead of   mags[i] = Q_PHI * mags[i - 1]
    # Nothing else changes: same GARCH(1,1) magnitude skeleton, same seg_bars/noise defaults,
    # same three injection levels (Small=0.05, Medium=0.15, Large=0.30).
    ...
```

This does **not** touch `RATIONAL_CONSTANTS` or any comparison-set constant
(per the brief's explicit instruction) — it only changes what ratio is
*injected into the synthetic data-generating process*, a property of the DGP,
not of the inference method.

### 4.4 Minimal code change to activate GARCH/IAAFT (Q4)

```
# repair/validation.py — additive, default-preserving signature change only:
def surrogate_fpr(dgp, *, focal=Q_PHI, constants=_RATIONALS, n_series, series_length,
                   n_surrogates, base_seed, alpha=ALPHA,
                   surrogate_fn: Surrogate = block_permutation_surrogate):   # NEW, defaulted
    ...
    score = standardized_null_score(series, constants=constants, focal=focal,
                                     n_surrogates=n_surrogates, seed=boot_seed,
                                     surrogate_fn=surrogate_fn)              # NEW arg threaded
    ...

def null_suite_fpr(*, n_series, series_length, n_surrogates, base_seed,
                    surrogate_fn: Surrogate = block_permutation_surrogate):  # NEW, defaulted
    ...
```

No existing call site changes behavior (the new parameter defaults to
today's `block_permutation_surrogate`, so `results/phase4_repair_validation/results.json`
remains reproducible byte-for-byte under the same call pattern). This is the
entire code change Q4 requires — `standardized_null_score` already accepts
`surrogate_fn` (`repair/zscore.py:75`); only `validation.py`'s wrapper
functions fail to expose it today.

---

## Q1 — Trend Surrogate Exploratory Battery

**Q1.5 Experimental matrix.** Paired design: for every (DGP, series index),
draw **one** series realization and evaluate **both** variants on it, so the
comparison isolates the surrogate mechanism, not sampling noise.

| Axis | Values |
|---|---|
| DGP | all 13, `REPAIR_NULL_SUITE` order (index 0–12) |
| Variant | A = `block_permutation_surrogate` (existing, unmodified) · B = `detrended_block_permutation_surrogate` (§4.1) |
| `n_series` (primary block) | 150 per DGP |
| `n_surrogates` | 99 (matches every existing artifact) |
| `series_length` | 400 |

**Q1.6 Exact simulation counts.** Primary block: 13 DGPs × 2 variants × 150
series × 99 surrogates ≈ **386,100** surrogate-generation + retracement
evaluations, order-of-magnitude comparable to the existing `null_suite_fpr`
battery (13×100×99≈128,700) times ~3 for the added variant and series count
— proportionate, not a scale escalation. A conditional replicate block
(same size) is permitted **only** under the stopping rule in §Q7 — not run
by default.

**Q1.7 Seed protocol.**

```
EXPLORATORY_Q1_BASE_SEED = 20260814                      # concrete, exploratory-only
for dgp_index, (name, dgp) in enumerate(REPAIR_NULL_SUITE.items()):
    child_seeds = SeedSequence(EXPLORATORY_Q1_BASE_SEED + dgp_index).spawn(150)
    for cs in child_seeds:
        gen = default_rng(cs)                             # generates the DGP realization
        series = dgp(gen, 400)
        boot_seed = int(cs.generate_state(1, dtype=uint32)[0])
        score_A = standardized_null_score(series, constants=_RATIONALS, n_surrogates=99,
                                           seed=boot_seed, surrogate_fn=block_permutation_surrogate)
        score_B = standardized_null_score(series, constants=_RATIONALS, n_surrogates=99,
                                           seed=boot_seed, surrogate_fn=detrended_block_permutation_surrogate)
```

Using the identical `boot_seed` for A and B means both draw the same
sequence of block-rotation/permutation random choices — the *only* thing
that differs between `score_A` and `score_B` is whether the raw series or
the detrended residual is what gets shuffled. `Δ_obs` is identical between A
and B by construction (both call `phi_advantage` on the same `eligible_retracements(series)`);
only `mu_null`, `sigma_null`, `z_phi`, `surrogate_p` can differ. This exact
pairing is the mechanism, not an incidental detail — restated in §Q1.9.

Exchangeability-diagnostic sub-experiment (cheap, additive): for each DGP,
draw `K=30` **fresh, independent** realizations from
`SeedSequence(EXPLORATORY_Q1_BASE_SEED + 1000 + dgp_index).spawn(30)`,
compute `Δ` directly on each (no surrogates needed — a true independent draw
from the same null), forming an empirical "true-null-Δ" reference
distribution.

**Q1.8 Metrics.**

- Per-DGP, per-variant surrogate FPR: `rejected/valid` at `α=0.05`, exactly
  as `surrogate_fpr` already computes it.
- Paired McNemar test per DGP: among the 150 paired series, count
  `(A rejects, B rejects)`, `(A rejects, B doesn't)`, `(A doesn't, B rejects)`,
  `(A doesn't, B doesn't)`; exact binomial test on the two discordant cells.
  This is the correct test for *paired* binary outcomes and is far more
  powerful than comparing two independent FPRs at this sample size.
- `ΔFPR = FPR_B − FPR_A` per DGP, with an approximate normal-difference CI as
  a secondary, more interpretable summary alongside McNemar's exact p-value.

**Q1.9 Diagnostics.**

- KS two-sample test (`scipy.stats.ks_2samp`, standard library, no new code)
  comparing the pooled surrogate-`Δ` distribution (variant A, then
  separately variant B) against the `K=30` fresh-independent-draw-`Δ`
  reference distribution from §Q1.7, per DGP. This directly tests the
  underlying property the whole standardization depends on — "the observed
  series is exchangeable with its surrogates" (`repair/surrogates.py:7`) —
  rather than only its downstream symptom (FPR).

**Q1.10 Evidence interpretation.**

| Outcome | Interpretation |
|---|---|
| B's FPR moves toward 0.05 on `trend_plus_noise` (McNemar significant) **and** no other DGP's FPR rises materially (no McNemar-significant increase) | Supports H1 partially — detrending is a viable *candidate* for the primary surrogate, worth a preregistration proposal. **Still not sufficient for adoption** — full-scale replication and a superseding ADR remain required (Part F/H of the arbitration). |
| B fixes `trend_plus_noise` but degrades ≥1 other DGP | **H1 falsified.** The uniform-rule hypothesis fails; conclude explicitly, in the write-up, that "no single detrending rule survives all 13 DGPs at this scale," per the brief's explicit instruction to say so if true. Do **not** attempt a DGP-conditional patch in the same pass — that would be exactly the p-hacking pathway this project's own governance forbids. |
| B changes little on any DGP (McNemar non-significant everywhere) | Inconclusive at this scale — report as such; do not interpret a null result as either confirmation or refutation without the KS diagnostic's corroboration. |
| KS diagnostic shows variant A's surrogate-Δ distribution already diverges from the fresh-draw reference on `trend_plus_noise` specifically (and B's does not) | Direct mechanistic confirmation of the non-exchangeability explanation in the prior audit (Part B.2) — strengthens the case for B on the mechanism-level grounds the project requires, not merely on "it scored better." |

---

## Q2 — Granularity Resolution Battery

**Q2.5 Experimental matrix.**

| Axis | Values |
|---|---|
| Global `M` (tick levels) | `{5, 7, 10, 15, 20, 30, 50, 72, 100, 150, 200, 300, 500, 1000}` — 14 log-ish-spaced points. **72 and 100 are included as measurement points, not as presupposed thresholds**; the point of including them is to test them, which is the opposite of assuming them. |
| Amplitude ratio `ρ = A/(hi−lo)` (deterministic sub-experiment only) | `{0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0}` — 7 points spanning "excursion is a tiny fraction of the path's range" to "excursion spans the whole range" |
| DGP for the Monte Carlo sub-experiment | `coarse_tick_fbm_null` (Hurst=0.5), unchanged from the existing `granularity_audit` |

**Q2.6 Exact simulation / evaluation counts.**

- **Deterministic tick-collapse sweep** (§4.2-adjacent, no RNG): for every
  `(ρ, M)` pair (7×14=98 combinations), construct the synthetic two-outcome
  scenario described below and check whether `discretize()` maps `q_φ`- and
  `5/8`-implied endpoints to the same tick or different ticks. Zero
  simulations — a closed-form evaluation of the existing `discretize()`
  formula (`granularity.py:41-48`), reused unchanged. Produces a sharp
  boundary curve `m*(ρ)`: the minimum ticks-spanned at which the two
  constants remain distinguishable under this pipeline's actual rounding
  rule.

  *Construction:* WLOG (by the shift/scale invariance already established in
  §4.1) fix the series range to `[0,1]` so `hi−lo=1`, an anchor at `0`, an
  end-of-excursion at `A=ρ`. The two hypothesized next-extrema are
  `A + A·q_φ` and `A + A·(5/8)`. Apply `discretize()` at resolution `M` to
  the three points `{0, A, A+A·q_φ}` and `{0, A, A+A·(5/8)}` separately,
  recompute `R = |disc(next) − disc(A)| / |disc(A) − disc(0)|` for each, and
  record whether the two discretized `R` values are equal (collapsed) or
  distinct (resolved).

- **Combined Monte Carlo sweep** (retracement error + FPR from the same
  runs, to avoid duplicate simulation): 14 `M` values × `n_series=60`
  (matches `granularity_audit`'s existing default, `granularity.py:73`) ×
  `n_surrogates=99` ≈ **83,160** surrogate evaluations — about 3.5× the
  existing 4-point sweep's 23,760, proportionate to going from 4 to 14
  points, not a scale escalation.

**Q2.7 Seed protocol.**

```
EXPLORATORY_Q2_BASE_SEED = 20260815
for M in tick_grid:
    child_seeds = SeedSequence(EXPLORATORY_Q2_BASE_SEED + M).spawn(60)   # mirrors granularity_audit's
                                                                          # existing base_seed+level pattern exactly
    for cs in child_seeds:
        gen = default_rng(cs)
        raw_path = fbm(gen, 400, hurst=0.5)                 # BEFORE discretization — needed for A_i, m_i, eps_i
        disc_path = discretize(raw_path, n_levels=M)
        # extrema/excursions computed on BOTH raw_path and disc_path;
        # for each excursion i present in disc_path's excursion set:
        #   A_i   = magnitude on raw_path at the matching anchor/end indices
        #   m_i   = A_i * M / (raw_path.max() - raw_path.min())
        #   eps_i = |R_i(disc_path) - R_i(raw_path)|
        boot_seed = int(cs.generate_state(1, dtype=uint32)[0])
        score = standardized_null_score(disc_path, constants=_RATIONALS, n_surrogates=99, seed=boot_seed)
```

**Q2.8 Metrics.** Per `M`: φ surrogate FPR (as today), plus the pooled
`{m_i, eps_i}` pairs across all 60 paths' excursions at that `M` — reported
as, at minimum, `median(m_i)`, `p10(m_i)` (the tail that matters most, since
a global "high" `M` can still leave many small excursions poorly resolved),
and `mean(eps_i | m_i-bin)` binned into `m_i ∈ {<10, 10–30, 30–72, 72–150,
>150}`.

**Q2.9 Diagnostics.** Re-express the existing FPR-vs-`M` relationship as
FPR-vs-`median(m_i)` and FPR-vs-`p10(m_i)`. If these re-expressed curves are
materially tighter (less scatter at fixed x-value) than the raw FPR-vs-`M`
curve, that is direct, data-grounded confirmation of H2 (resolution is
excursion-level, not global). If they are not tighter, H2 is not supported at
this scale and the global-`M`-only framing should not be abandoned without
further justification.

**Q2.10 Evidence interpretation — explicit falsification criteria for M≥72 / M≥100.**

| Outcome | Interpretation |
|---|---|
| The deterministic sweep's boundary curve shows `q_φ` and `5/8` remain **collapsed** (indistinguishable) for excursions with `m_i` at or above 72 (respectively 100), for some realistic `ρ` | **M≥72 (respectively M≥100) is falsified** as a sufficient global threshold — report exactly which `(ρ, M)` combinations still collapse. |
| The Monte Carlo sweep shows φ's surrogate FPR remains at or below the nominal band even where `p10(m_i)` is well below 72 | Suggests the naive half-tick bound (arbitration §C.3) is conservative in practice for this specific DGP/mechanism — worth noting, but does **not** by itself justify lowering any threshold; a single DGP's behavior is not sufficient grounds for a general claim. |
| The Monte Carlo sweep shows φ's surrogate FPR exceeds the nominal band even at global `M` well above 100, whenever `p10(m_i)` is low (many small excursions) | Directly confirms H3 and the arbitration's Part C.4 conclusion: no fixed *global* `M` is sufficient on its own; a per-excursion `m_i`-eligibility rule is required, and its own minimum value (`m_min`) becomes the thing to preregister — not a bare `M`. |

---

## Q3 — φ-vs-5/8 Null Battery and Negative Control

**Q3.5–Q3.7 Null-suite battery.**

- **Statistic:** `confirmatory_phi_test`'s `beats_five_eighths` (boolean) and
  `supports_phi` (composite boolean) — `repair/registration.py:56-62,83-99`
  — unchanged, called directly (not the grouped `standardized_null_score`
  path that `null_suite_fpr` currently uses, which is the exact gap
  identified in the prior audit, Part E).
- **Holm procedure:** `holm_step_down` over the 4 per-rational surrogate
  p-values, `α=0.05`, exactly as `confirmatory_phi_test` already implements
  it (`repair/registration.py:91`) — unchanged.
- **Simulation counts:** `n_series=120` per DGP (matches `run_repair_validation`'s
  existing default, `repair/validation.py:196`), `n_surrogates=99`. Primary
  block only, one seed block, per §Q7's conditional-replicate stopping rule.
- **Seed protocol:** `EXPLORATORY_Q3_BASE_SEED = 20260816`,
  `SeedSequence(EXPLORATORY_Q3_BASE_SEED + dgp_index).spawn(120)`, identical
  pattern to Q1/Q2 and to the existing `null_suite_fpr`.
- **Metrics, per DGP and pooled:** `beats_five_eighths` FPR,
  `supports_phi` FPR, and the per-rational Holm-adjusted p-value
  distribution's median and 90th percentile (diagnostic only).
- **Pass/fail interpretation (exploratory screening band, explicitly distinct
  from any future confirmatory gate):** flag any DGP with `beats_five_eighths`
  FPR `> 0.15` for mechanism review before any further validation investment
  in this mechanism. **0.15 is a screening threshold for this exploratory
  pass only** — it is not proposed as, and must not be mistaken for, the
  eventual confirmatory gate value, which remains unset and must be
  preregistered separately (§Q7.3).

**Q3.8 Negative control.**

- **DGP:** `five_eighths_attractor_garch` (§4.3), injection levels
  `{0.05, 0.15, 0.30}` (Small/Medium/Large, matching the existing convention,
  `positive_control.py:9-11`), `n_series=100` per level (matches project
  convention), `n_surrogates=99`.
- **Seed:** `EXPLORATORY_Q3_NEGCTRL_BASE_SEED = 20260817`, spawned per
  injection level.
- **Metric:** rate at which `confirmatory_phi_test` returns
  `beats_five_eighths=True` on data whose *true* injected structure favors
  5/8, not φ.
- **Diagnostic — dose-response comparison:** plot this false-attribution
  rate against injection strength alongside the *genuine* positive control's
  power curve (`phi_attractor_garch`, already characterized at Medium in the
  existing artifact, `power=0.82`). The correctly-behaving signature is a
  **flat, low** false-attribution rate across injection strength, in
  contrast to the genuine control's rate *rising* with injection strength.
  **A rate that itself rises with injection strength is a serious structural
  finding** — it would mean the mechanism is not measuring φ-specificity at
  all but something both constants share, and would block any further use of
  `beats_five_eighths` until resolved, regardless of what the null-suite
  battery above shows.
- **Explicit limitation, noted in the design rather than discovered later:**
  the current `confirmatory_phi_test` is structurally asymmetric — it only
  ever tests "does φ beat the rationals," never "does a rational beat φ" or
  "does a rational beat the other rationals." The negative control above
  probes this asymmetry indirectly (via false attribution) but does not
  fully close it. Building a symmetric test is out of scope for this minimal
  battery and is noted here as a candidate for a *separate* future
  exploratory proposal, not silently folded into this one.

---

## Q4 — GARCH / IAAFT Activation

**Q4.5–Q4.7 Battery.**

- **Prerequisite:** the minimal, additive signature change in §4.4
  (`surrogate_fn` parameter on `surrogate_fpr`/`null_suite_fpr`) — not yet
  implemented; this battery cannot run before it exists.
- **Runs:** `null_suite_fpr(..., surrogate_fn=garch_surrogate)` and
  `null_suite_fpr(..., surrogate_fn=iaaft_surrogate)`, each across all 13
  DGPs, `n_series=120`, `n_surrogates=99`.
- **Seed:** reuse `base_seed=20260812` — **the same base seed the existing
  `results/phase4_repair_validation/results.json` block-permutation run
  used** — so the underlying null-series realizations are identical across
  all three surrogate families (block-permutation, GARCH, IAAFT); only the
  surrogate mechanism differs. This makes the three-way comparison a true
  paired design, exactly as in Q1, and means the existing artifact can be
  reused directly as variant A's reference row rather than regenerated.

**Q4.8 Metrics and interpretation — what each family may support.**

| Family | Role | May support | May NOT support |
|---|---|---|---|
| Block-permutation | **PRIMARY** | The only family whose FPR/power/p-value may ever feed a confirmatory `Z_φ` claim, once and if authorized. | — |
| GARCH(1,1) | **SECONDARY** | "The primary result is not merely a volatility-clustering/heavy-tail artifact," if its FPR broadly agrees with primary across the 13 DGPs. | Independently authorizing a φ claim; substituting for the primary gate; explaining away a primary-gate failure. |
| IAAFT | **TERTIARY** | "The primary result is not merely a linear-autocorrelation/marginal-distribution artifact," under the same agreement condition. | Same restrictions as GARCH. |

No merged/combined p-value across the three families is proposed or
computed anywhere in this battery — confirmed against the repository
(§ Arbitration Part D.1: no unification formula exists in code). Per-DGP
disagreement (non-overlapping approximate Wilson 95% CIs between any two
families) is flagged as "requires investigation" and **must be reported, not
averaged away or silently dropped**, exactly as the prior audit's Part D
specified.

---

## Q5 — Preregistration Schema Gap Audit

Comparison baseline: **three** registration-shaped classes exist in this
repository, not two — `ExperimentManifest` (Phase 0–2,
`src/phi/experiment/manifest.py`), `Phase4PreRegistration` (original Phase 4,
`src/phi/phase4/registration.py`), and `RepairPreRegistration` (repair,
`src/phi/phase4/repair/registration.py`). `ExperimentManifest` is included
below only as context establishing the project's own baseline for "what a
registration should track" — the requested comparison is the latter two.

**Consumption was checked, not assumed**, by tracing every field from its
declaration through `pipeline.py::_run_registered` (original) and
`repair/registration.py::run_confirmatory_repair` (repair) to
`analysis.py::analyze_series` / `repair/registration.py::confirmatory_phi_test`,
and by an exhaustive `grep` for `registration\.<field>` across `src/` and
`tests/` (zero hits outside declaration/hashing for every field marked "NO"
below).

| Field | Exists in schema? | Consumed by code (controls execution)? | Required for scientific reproduction? | Current default | Recommended action |
|---|---|---|---|---|---|
| `experiment_id` / `experiment_version` / `research_question` / `primary_hypothesis` | Both | NO (identity/labels only; included in `content_hash()`) | Yes — human-readable identity | none (required) | No change |
| `comparison_set` (original) | Original only | **YES** — passed directly to `analyze_series` (`pipeline.py:87`) | Yes | `()` (must be set) | No change |
| `rational_constants` (repair) | Repair only | **NO** — `confirmatory_phi_test` hardcodes `_RATIONALS` from the module constant, never reads `registration.rational_constants` (verified: zero call sites) | Yes, if the field is ever meant to be overridable; if it is meant to always equal the module constant, the field is redundant | `_RATIONALS` (= `RATIONAL_CONSTANTS.values()`) | **Thread it through** `run_confirmatory_repair → confirmatory_phi_test(..., constants=registration.rational_constants)`, or remove the field and document that the control set is a hardcoded project constant, not a per-experiment registration |
| `focal_constant` (repair) | Repair only | **NO** — `confirmatory_phi_test`/`standardized_null_score` hardcode `focal=Q_PHI` | Only if a non-φ focal is ever intended (it isn't, currently) | `Q_PHI` | Low priority; document as decorative, or remove |
| `primary_surrogate` (repair) | Repair only | **NO** — `run_confirmatory_repair` never selects a surrogate function from this string; `confirmatory_phi_test` always uses `block_permutation_surrogate` via its default | **Yes, materially** — this is exactly the field that should govern which surrogate family a confirmatory run uses, and today it cannot | `"block_permutation"` (string) | **Thread it through** — resolve the string against the existing `SURROGATES` registry (`repair/surrogates.py:133-138`) and pass the resolved function into `confirmatory_phi_test` |
| `primary_estimand` (repair) | Both (different meaning in each) | NO in both — identifier label only, no branch reads it (there is only one estimand implementation per schema, so nothing to select) | Documentation-only; acceptable | fixed string | No change — this one is a benign hash-binding label, unlike the three above which *do* correspond to real alternatives in code |
| `alpha` (repair) | Both | **PARTIAL** — repair: consumed by `failed_gates()`'s Gate-1 threshold check (`self.aggregate_fpr > self.alpha`, `repair/registration.py:184`), but **not** passed into `confirmatory_phi_test`'s Holm call in `run_confirmatory_repair` (which uses the module-level `ALPHA` default). Original: **not consumed anywhere** — `analyze_series`/`SeriesAnalysis.rejected_h0` hardcodes the literal `0.05` (`phase4/analysis.py:50`), never reading `registration.alpha`. | Yes, materially, if ever set to a non-default value | `0.05` (`ALPHA`) on both | **Repair:** thread `registration.alpha` into the `confirmatory_phi_test(..., alpha=registration.alpha)` call so Gate-1's threshold and the actual test's significance level cannot silently diverge. **Original:** either thread `registration.alpha` into `analyze_series`'s decision, or remove the field. |
| `n_surrogates` (repair) | Repair only | **YES** — threaded correctly (`run_confirmatory_repair` passes `registration.n_surrogates`) | Yes | 999 | No change — this one is done right; included here to show the audit checked positives, not only negatives |
| `bootstrap_replicates` (original) | Original only | **YES** — passed correctly (`pipeline.py:88`) | Yes | 10,000 | No change |
| `confidence_level` (original) | Original only | **YES** — passed correctly (`pipeline.py:90`) | Yes | 0.95 | No change |
| `q_phi` (original) | Original only | **YES** — passed correctly (`pipeline.py:91`) | Yes | `Q_PHI` | No change |
| `delta_min` | **Original only — absent from repair** | Original: NO (used only in `classify_outcome`, a downstream/reporting function, not gated inside `is_confirmatory_authorized`) | **Yes** — without it, no equivalence-region interpretation is possible on a repaired result | `None` (original) | Add to `RepairPreRegistration`, or explicitly document why the repair's binary reject/fail-to-reject framing makes an equivalence margin unnecessary — currently neither is done |
| `falsification_criteria` | **Original only — absent from repair** | Original: NO (documentation field; required for registration completeness but not read by any decision function) | Yes — required by the project's own stated anti-p-hacking discipline | `None` (original) | Add to `RepairPreRegistration` for consistency, even though it is documentation-only in the original too |
| `bootstrap_coverage_validated` (original gate) | **Original only — no repair equivalent gate exists at all** | Original: YES, gates `is_confirmatory_authorized()` | Yes — CI-coverage validation is a distinct claim from FPR calibration | `False` (original) | **Add an equivalent gate field to `RepairPreRegistration`** — today there is no way to even *record* that surrogate-CI coverage was checked for the repaired estimand, let alone require it; this is a missing field, not just missing evidence (extends arbitration §19 item 8 from "evidence gap" to "schema gap") |
| `dataset_a_id`/`hash`, `dataset_b_id`/`hash` | Both | YES in both — checked in `run_confirmatory`/`run_confirmatory_repair`'s dataset-role/hash comparison | Yes | `None` | No change |
| `sampling_frequency` | Both | NO in both (declared, required for "fully registered," but never read by any decision function) | Yes, for documentation/audit purposes even if not computationally load-bearing | `None` | No change — acceptable as a documentation-only required field |
| `block_length_config` | Both | NO in both (the actual block length is *always* computed automatically by `politis_white_block_length`; this field records the *configuration label*, not a parameter that changes behavior) | Yes, for documentation | `None` | No change — consistent with the project's "never tuned toward significance" design; this field exists to record that fact, not to control it |
| `random_seed` | Both | YES in both | Yes | `None` | No change |
| `code_version` / `environment_lock_hash` | Both | NO in both, in the specific sense that **neither registration class calls** `phi.experiment.provenance.capture()` — the exact function that exists to populate these fields reproducibly (`src/phi/experiment/provenance.py:55-67`) is exported, unit-tested (`tests/experiment/test_provenance.py`), and used by neither `Phase4PreRegistration` nor `RepairPreRegistration`. Both fields are populated only by a human typing a value. | Yes, materially — this is the field that turns "same hash" into "same executable experiment" per the module's own docstring | `None` | Wire both registration classes to call `provenance.capture()` when these fields are set, rather than accepting hand-typed values that can drift from the actual commit/lockfile |
| `granularity_passes`, `constant_sweep_symmetric`, `max_per_dgp_fpr`, `positive_control_power_medium`, `aggregate_fpr` (repair gates) | Repair only | YES — all five gate `is_confirmatory_authorized()` via `failed_gates()` | Yes | `False`/`None` (fail-closed) | No change — correctly implemented; note (as in the arbitration) that nothing prevents a caller from hand-supplying a value here that was never actually produced by `run_repair_validation` — a type-level, not value-level, gap |

**Additional missing fields found this session, beyond `delta_min` and
`falsification_criteria`:** a bootstrap/surrogate-coverage validation gate
(above), and — functionally, not by name — a genuinely-consumed comparison-set
override (`rational_constants` exists but is inert). No further fields
present on `ExperimentManifest` but absent from both Phase-4 schemas (e.g.
`dataset_version`, `missing_data_policy`) are flagged as *required*, since
Phase 4's narrower synthetic-only scope may not need them — but their
absence is noted for a methodologist to confirm, not silently assumed
correct.

---

## Q6 — Exploratory / Confirmatory Firewall for This Battery

### ALLOWED TO INFORM v0.3.0 DESIGN

- Whether detrended block permutation shows a directionally consistent
  improvement (or harm) on `trend_plus_noise` vs. the other 12 DGPs —
  informs whether to propose it as a *candidate* primary-surrogate change at
  all (Part F label: MUST BE EXPLORATORY → CANDIDATE FOR PREREGISTRATION, or
  → DROPPED).
- Whether a single uniform detrending rule survives all 13 DGPs, or must be
  reported as not generalizing (per H1's falsification branch).
- The empirical relationship among global `M`, per-excursion `m_i`,
  retracement quantization error, and φ-vs-5/8 tick-collapse — informs
  *what kind* of granularity eligibility rule to propose (global-only vs.
  per-excursion-gated), and whether 72/100/some other value is even the
  right kind of number to preregister.
- Whether `beats_five_eighths`'s own FPR is in a plausible range at all —
  informs whether the mechanism is worth carrying into a future confirmatory
  design as specified, or needs a redesign (e.g., the symmetry gap noted in
  §Q3.8) before that.
- Whether GARCH/IAAFT roughly agree or sharply disagree with
  block-permutation — informs whether explicit disagreement-handling must be
  written into the v0.3.0 spec.
- Which `RepairPreRegistration` fields are genuinely inert (§Q5) — informs
  which fields to thread through vs. remove before any future confirmatory
  freeze.
- Downgrading or upgrading a candidate's Part-F label (e.g.
  "MUST BE EXPLORATORY" → "CANDIDATE FOR PREREGISTRATION" or → "NOT VIABLE,
  DROPPED"). **Never** upgrading a label directly to "VALIDATED" or
  "SCIENTIFICALLY ESTABLISHED" — that requires the full-scale confirmatory
  process (arbitration Part H), not this battery.

### FORBIDDEN FROM BEING USED AS CONFIRMATORY EVIDENCE

- No FPR, power, symmetry, or distinguishability number produced by this
  battery may be written into `RepairPreRegistration`'s gate fields
  (`aggregate_fpr`, `max_per_dgp_fpr`, `positive_control_power_medium`,
  `granularity_passes`, `constant_sweep_symmetric`) or any future
  v0.3.0-equivalent gate field.
- No result here may be used to claim Type-I error control, power, or
  φ-specificity for real data, or to change `is_confirmatory_authorized()`'s
  outcome in any way.
- No candidate (detrending method, `M`/`m_min` value, surrogate family) may
  be adopted **because** it produced a more favorable number on this
  specific run. Any adoption must cite the mechanism-level reasoning (Parts
  B/C/D of the arbitration, and the diagnostics in Q1.9/Q2.9 above), never
  "it scored best."
- The battery may not be silently re-run with different parameters after an
  unfavorable result, with only the more-favorable re-run reported. If a
  conditional replicate (§Q7) is triggered, **both** runs are reported,
  pooled, never one in place of the other.
- No result here authorizes editing `VERSION`, proposing a v0.3.0 release,
  or beginning a full-scale/confirmatory run.
- No result here may change any of the five (or, if later adopted, six)
  gate **thresholds** (0.05, 0.07, 0.80, or any new φ-vs-5/8 threshold) —
  threshold changes require a superseding ADR, never an exploratory outcome.
- No real data is introduced anywhere in this battery, for any purpose,
  under any condition.

---

## Q7 — Stopping Rules, Preregistration Fields to Eventually Freeze, and Compute Scope

**Q7.1 Stopping rules.**

1. Each of Q1–Q4's batteries runs **exactly once** at its specified
   configuration before any interpretation.
2. A **single, pre-authorized** conditional replicate (same size as the
   primary block) is permitted per question, and only when a result lands
   "near a decision-relevant boundary," defined precisely and in advance —
   not left to post-hoc judgment — as: `|observed_rate − reference| ≤ 2·SE`,
   where `SE = sqrt(p̂(1−p̂)/n)` and `reference` is `α=0.05` (Q1, Q4) or the
   stated screening band (Q3, 0.15). This mirrors, exactly, what this
   session's own prior audit already did for Gate 2 (`trend_plus_noise` sat
   ~1.4 SE from its replicated estimate) — one extra block, pooled and
   reported alongside the first, never substituted for it.
3. No candidate's *definition* (trend estimator, `M`/`ρ` grid, seed,
   `n_series`) may change after seeing a result and then be re-run under the
   same "exploratory battery" label to chase a better number. A genuinely new
   idea surfaced while interpreting results becomes a **separate, freshly
   labeled** follow-on proposal — not a silent substitution into this
   battery's own reported results.
4. Once Q1–Q4 have each completed their pre-registered run (plus at most one
   conditional replicate), and Q5's audit and Q6's firewall are written up,
   **exploration stops.** The next step is human/methodologist review and a
   superseding ADR for whatever is adopted — not further exploratory
   iteration.

**Q7.2 Compute scope, stated for planning, not as a request to run it:**
order-of-magnitude totals — Q1 ≈386K surrogate evaluations (≈772K if the
conditional replicate fires for every DGP, which is not expected), Q2
≈83K + 98 closed-form evaluations, Q3 ≈13×120×99≈154K (null battery) +
3×100×99≈30K (negative control), Q4 ≈2×13×120×99≈309K (two new families
against the existing block-permutation reference). All individually smaller
than or comparable to existing "small-scale" artifacts already in this
repository; none approaches the deferred full-scale (10,000/20,000-per-DGP)
run.

**Q7.3 Preregistration fields that must eventually be frozen** (before any
confirmatory step, regardless of what this battery finds):

- Whichever candidate(s) from Q1/Q2/Q3/Q4 are adopted, named exactly, with
  version-pinned code.
- If a detrending candidate is adopted: nothing further to freeze beyond the
  fixed specification in §4.1 (it has no free parameters by design).
- If a granularity eligibility rule is adopted: the specific `m_min` value
  and its derivation, replacing (or supplementing) any bare `M` threshold.
- If `beats_five_eighths` is adopted as a sixth confirmatory gate: its own
  threshold, derived the same way the existing five were meant to be —
  not selected because it happens to pass on this battery's data.
- `RepairPreRegistration.rational_constants`, `.primary_surrogate`, `.alpha`
  either wired to actually control execution (§Q5) or removed — a schema
  fix, independent of any exploratory outcome, that should happen regardless
  of which candidates above are adopted.
- A `bootstrap_coverage_validated`-equivalent field, added to
  `RepairPreRegistration` (§Q5), and actual evidence for it, before any
  confirmatory authorization.
- All fields already required by `RepairPreRegistration.REQUIRED_REGISTRATIONS`
  today, unchanged.

**Q7.4 Confirmation that no real-data analysis is authorized.** Nothing in
this document changes `is_confirmatory_authorized()`'s result on either
registration class (both remain `False` by construction — no field on
either object is touched by this specification). No real-world data source
is named, referenced, or required by any experiment above. This document
does not authorize, and cannot authorize, real-data analysis; only a human
methodologist, after the full arbitration → specify → exploratory-test →
freeze → confirmatory-validation sequence, can.

---

## EXPLORATORY BATTERY DESIGNED: YES
## SOURCE CODE MODIFIED: NO
## SIMULATIONS RUN: NO
## CONFIRMATORY VALIDATION RUN: NO
## REAL DATA RUN: NO

## NEXT SINGLE ACTION

Human/methodologist review and sign-off on this specification, followed by
implementation of the four minimal, additive, default-preserving code
changes it specifies (§4.1–§4.4: the detrended-permutation surrogate
function, the per-excursion `m_i`/`eps_i` instrumentation, the
five-eighths-attractor negative-control DGP, and the `surrogate_fn`
parameter threading in `repair/validation.py`) as one reviewable change that
adds new functions without altering any existing frozen behavior — only
after which Q1–Q4's batteries may actually be run.
