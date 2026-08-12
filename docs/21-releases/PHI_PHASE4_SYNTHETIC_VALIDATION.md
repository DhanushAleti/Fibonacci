# PHI — Phase 4 Synthetic Validation Report (False-Positive Torture Test)

**Date:** 2026-08-12 · **Data:** synthetic only (no real-world analysis, no φ claim)
**Harness:** `scripts/phase4_synthetic_validation.py` · **Raw results:** `results/phase4_validation/results.json`
**Config:** 13 null processes × 150 series × length 400 × 199 bootstrap replicates; control set `{q_φ ± jδ, δ=0.05, j=1..4}` (**illustrative, not registered**).

## VERDICT — 🔴 FAIL. Do NOT proceed to real data.

PHI, run against processes with **no φ mechanism**, reports a false φ "positive" essentially **100% of the time**. The methodology as specified manufactures evidence. Per the brief, real-world confirmatory analysis must **not** proceed; the methodology must be fixed first (a methodologist decision — see §Root cause).

## Number of simulations
~2,100 full-pipeline runs: 1,950 null (section A/E) + 3 controls (B/C) + 150 pooled (D) + leakage/reproducibility probes.

## A + E. Null processes — false-positive rates

Expected FPR under every process ≈ α = 0.05. Observed:

| True process | FPR | 95% Wilson CI | mean Δ̂_φ | Status |
|---|---|---|---|---|
| IID Gaussian | **1.000** | [0.975, 1.0] | +0.0240 | FAIL |
| IID heavy-tailed (t) | **1.000** | [0.975, 1.0] | +0.0225 | FAIL |
| Random walk | **1.000** | [0.975, 1.0] | +0.0163 | FAIL |
| AR(1) | **1.000** | [0.975, 1.0] | +0.0212 | FAIL |
| AR(p) (AR(2)) | **1.000** | [0.975, 1.0] | +0.0210 | FAIL |
| Trend + noise | **1.000** | [0.975, 1.0] | +0.0241 | FAIL |
| Seasonal | **1.000** | [0.975, 1.0] | +0.0148 | FAIL |
| Heteroskedastic | **1.000** | [0.975, 1.0] | +0.0238 | FAIL |
| Volatility clustering (GARCH) | **1.000** | [0.975, 1.0] | +0.0243 | FAIL |
| Regime switching | **1.000** | [0.975, 1.0] | +0.0237 | FAIL |
| Autocorrelated heavy-tailed | **1.000** | [0.975, 1.0] | +0.0194 | FAIL |
| Market-like (AR+GARCH) | **1.000** | [0.975, 1.0] | +0.0228 | FAIL |
| Coarse-tick microstructure | **1.000** | [0.975, 1.0] | +0.0211 | FAIL |

**Pooled (E):** 1,950 null simulations, **1,950 rejections → pooled FPR = 1.000** (nominal α = 0.05). **0 / 13** processes calibrated. This is a **hard-gate failure** (spec §XLIV).

## D. Constant sweep — the decisive test (does PHI prefer φ *specifically*?)

Pooled N = 14,753 retracements from IID-Gaussian nulls. `Δ_c` computed for each focal constant with **its own** symmetric control grid:

| Focal constant `c` | 0.25 | 0.40 | 0.50 | **φ ≈ 0.618** | 0.75 |
|---|---|---|---|---|---|
| `Δ_c` (advantage vs its own controls) | +0.0233 | +0.0212 | +0.0192 | **+0.0164** | +0.0142 |

**Every constant "wins"** (`Δ_c > 0`) — because the symmetric-grid + convex-distance geometry favours *whatever center you pick*, not φ. And **φ is not preferred**: it ranks **4th of 5** (0.25, 0.40, 0.50 all beat it). The global landscape `M(q)=E|R−q|` minimises at **q ≈ 0.396** (the random-walk retracement's own occupancy mode), nowhere near φ. `phi_is_specifically_preferred = False`. This is direct proof that a positive `Δ_φ` is generic geometry, not φ specialness.

## B. Positive control (φ injected) — sensitivity / effect recovery

Injected swing ratio → q_φ. The **secondary landscape correctly recovers it**: `argmin M(q) = 0.626 ≈ φ`; `Δ̂_φ = +0.095` (much larger than the null ≈ +0.02); test fires. So the *landscape* has genuine sensitivity to a real φ signal.

## C. Negative control (non-φ injected) — does PHI mislabel it φ?

| Injected ratio | landscape argmin | `Δ̂_φ` | raw p | Interpretation |
|---|---|---|---|---|
| 0.50 | 0.506 (✓ correct) | **+0.033** | 0.005 | **PRIMARY FALSELY FIRES for φ** (Δ̂ > a typical δ_min=0.02) |
| 0.30 | 0.304 (✓ correct) | +0.000 | 0.005 (floor) | raw p floors on a near-degenerate variance; the δ_min effect-size gate correctly yields *indistinguishable* |

The **landscape** always localises the true attractor correctly (0.506, 0.304) — i.e. PHI's *secondary* analysis is sound. But the **primary `Δ_φ`-vs-0 test** labels a 0.5-clustered process as φ‑supporting. An effect-size (`δ_min`) gate rescues the 0.3 case but **not** the 0.5 case (its `Δ̂ = +0.033` exceeds a δ_min of 0.02), and several *null* processes have mean `Δ̂ ≈ 0.024 > 0.02` too — so even the effect-size gate does not fully repair the estimand.

## F. Temporal-leakage battery — clean

| Vector | Result |
|---|---|
| Look-ahead (append `X=1e12`) | earlier retracements bit-identical (max abs diff 0.0) → **leakage-free** |
| Preprocessing/normalization (×1000 scale) | retracements identical → **scale-invariant** |
| Normalization (+500 shift) | retracements identical → **shift-invariant** (no global normalization surface) |
| Overlapping windows | unit of inference is the completed excursion; stationary bootstrap resamples excursion blocks |
| Train/test contamination | discovery/confirmation/replication enforced by the fail-closed gate |

The **construction is leakage-safe**; the failure is purely the estimand's geometric bias, not leakage.

## G. Reproducibility — pass

Same process + same seed → identical (Δ̂, p, CI). Different seed → differs. Cross-process (fresh interpreter, unpinned hash seed) determinism is asserted by `tests/phase4/test_reproducibility.py`.

## Root cause and required fix (methodologist, not code)

By **Jensen's inequality**, for controls symmetric about `q_φ` and the convex `M(q)=E|R−q|`, `Δ_φ = mean_q M(q) − M(q_φ) ≥ 0` for **any** retracement distribution. So `Δ_φ > 0` tested against 0 is a mathematical property of the estimand + symmetric grid, not evidence about φ. The constant sweep confirms every center gets `Δ_c > 0` and φ is not special. **This must not be "fixed" in code to change the outcome.** Legitimate directions (a scientific decision): compare `Δ̂_φ` against its **null/surrogate distribution** rather than 0; or a **convexity-corrected** estimand (e.g. curvature of `M` at `q_φ` vs at matched controls); or replace the vs-0 test with the **rank of φ among a dense grid** as primary.

## Failures / limitations

- **Failure:** primary estimand-vs-0 test is not null-calibrated (FPR = 1.0 across all 13 processes); the negative-control 0.5 case is falsely labelled φ-supporting even with an effect-size gate.
- **Limitations:** reduced-scale run (150 series × 199 replicates); the false-positive signal is extreme so the CIs are already tight, but the full run (`--full`: 300 × 999) is available. Control set/δ_min here are **illustrative**, not registered. Positive-control power is characterised via the landscape, not a δ_min-calibrated Monte-Carlo power curve (that awaits a registered `δ_min`). No real data was used.

## Bottom line

PHI **can** fool itself under the estimand as specified — and this harness proves it does, on every null process, 100% of the time, while correctly showing (constant sweep + landscape) that φ is **not** the cause. The methodology is therefore **not** cleared for real data. The construction, leakage safety, determinism, and secondary landscape are sound; the primary estimand needs a methodologist revision before any confirmatory step. **No φ claim is made or implied.**
