# Phase 4 — Confirmatory Methodology Contract (implemented, not authorized to run)

**Status:** Methodology frozen (Chief Scientific Methodologist: GO-with-conditions); **confirmatory execution NOT authorized** (Final Arbiter: NO-GO until the pre-registration is complete and validation gates pass).
**Version:** 1.0.0 · **Last Updated:** 2026-08-12
**Implements:** `PHI — Phase 4 Scientific Specification` (methodology) and `Project PHI — Final Scientific Arbitration` (pre-registration gates). Package: `src/phi/phase4/`.

> **Scientific-claim boundary.** This layer implements the frozen confirmatory *methodology*. It has **not** been run on any real data and makes **no** φ claim. Running it is blocked in code (`Phase4PreRegistration.is_confirmatory_authorized()` fails closed) until a human freezes the numerical pre-registration and the validation gates pass — and, as documented in §7 below, **one validation gate does not currently pass**.

---

## 1. Frozen question, hypothesis, estimand

- **Question (spec §II):** Among pre-specified temporal excursions in eligible quantitative time series, is `q_φ = 1/φ` associated with greater normalized-retracement concentration than **scientifically matched non-φ constants**, after accounting for temporal dependence and multiplicity? (Tests φ *specialness*, not mere presence.)
- **Hypotheses (spec §III):** `H0: Δ_φ ≤ 0` vs `H1: Δ_φ > 0`, one-sided, `α = 0.05`.
- **Primary estimand (spec §XIX):** `Δ_φ = (1/K) Σ_{q∈C} E[ |R − q| − |R − q_φ| ]`, estimated by the paired, excursion-level statistic `Δ̂_φ = mean_i Z_i`, `Z_i = (1/K) Σ_{q∈C}(|R_i − q| − |R_i − q_φ|)`.

## 2. Frozen construction (implemented exactly)

| Component | Frozen rule (spec) | Module |
|---|---|---|
| Anchor | Deterministic three-point local extrema; odd-length plateau → midpoint, even → not an extremum; consecutive opposite-extrema pairing; no smoothing / amplitude threshold / fitted parameter (§V–§VII) | `phase4/extrema.py` |
| Retracement | `R_i = |X_{E_{i+1}} − X_{E_i}| / |X_{E_i} − X_{A_i}|` (terminal, per completed excursion); `R∈[0,1]` primary; `R>1` overshoot reported not deleted; zero denominator → NA (§XXII, §L) | `phase4/retracement.py` |
| φ-distance | Continuous `|R − q|`; **no `ε_φ`** in primary inference (§IX, §XIV) | `phase4/estimand.py` |
| Controls | Symmetric, equally-spaced, non-φ, q_φ excluded (§XXIV); dense `[0.05, 0.95]` global grid as secondary (§XXV) | `phase4/registration.py`, `phase4/estimand.py` |
| Inference | Stationary bootstrap (Politis–Romano) over excursion blocks; automatic block length (Politis–White); `B = 10,000`; 95% percentile CI; one-sided p-value with MC error (§XXX–§XXXVII) | `phase4/inference.py` |
| Multiplicity | Holm step-down FWER (§XXXIX) | `phase4/multiplicity.py` |
| Null-DGP suite | 10 DGPs + coarse-tick microstructure null + φ-biased positive control (§XLIII, §XLV) | `phase4/nulldgp.py` |
| Calibration / power | FPR harness (hard gate) + Monte-Carlo power (§XLIV, §XLII) | `phase4/calibration.py` |
| Separation | Discovery / confirmation (Dataset A) / external replication (Dataset B) (§XLVII) | `phase4/datasets.py`, `phase4/pipeline.py` |
| Interpretation | Four outcomes by CI vs `[−δ_min, +δ_min]` (§LIV–§LVII) | `phase4/verdict.py` |

## 3. Fail-closed confirmatory gate

`run_confirmatory` / `run_replication` refuse to run unless `is_confirmatory_authorized()` is `True`, which requires **all** of: the exact comparison set `C` (structurally valid), `δ_min`, Dataset A/B identities+hashes, sampling frequency, block-length config, RNG seed, code+environment provenance, falsification criteria — **and** the validation gates `bootstrap_coverage_validated`, `null_fpr_calibrated`, and `power_at_delta_min ≥ 0.80`. Any omission ⇒ refusal. This is the Arbiter's NO-GO expressed in code.

## 4. Documented interpretation decisions (flagged, not invented)

Two places where the spec is terse; each is implemented as the most defensible reading and flagged for methodologist confirmation before the confirmatory freeze:

1. **Per-excursion retracement = terminal value** at the next extremum (`retracement.py`), justified by the excursion being the unit (§XXI) and inter-extremum monotonicity. If a different per-excursion reduction is intended, only that module changes.
2. **Retracement formula orientation** follows the authoritative methodology spec §XXII (`|X_t − X_e|/|X_e − X_a|`), matching the existing frozen `features/retracement.py`; the arbitration/literature documents contain an inverted transcription, resolved in favour of the authoritative spec.

## 5. What is frozen numerically vs still open (Arbiter blockers)

**Open (must be human-registered before any run):** exact `C` (δ spacing and K), `δ_min` (domain-justified, never from data), Dataset A/B identities, block-length estimator configuration, DGP parameterisation, RNG seed.

## 6. Validation gates (Arbiter Gates 3–8)

Implemented as runnable **synthetic** harnesses; their *results* are the gate. Bootstrap coverage, null-FPR calibration, and power must be demonstrated on synthetic data before a confirmatory run.

## 7. HONEST FINDING — the primary estimand is not null-calibrated (blocker)

Running the null-calibration harness on the primary estimand **as specified** shows a false-positive rate **≈ 1.0** under pure-null DGPs (IID Gaussian, random walk, AR), with mean `Δ̂_φ ≈ +0.02 > 0`. This is not an implementation bug: by **Jensen's inequality**, for controls symmetric about `q_φ` and the convex functional `M(q) = E|R − q|`, `Δ_φ = mean_q M(q) − M(q_φ) ≥ 0` for **any** retracement distribution. So a positive `Δ̂_φ` tested against 0 is a **geometric artefact**, not evidence of φ specialness.

Consequence: the methodology **fails its own hard null-calibration gate (§XLIV)**. Confirmatory analysis is therefore correctly **doubly blocked** (unpassed calibration gate *and* unfrozen numerical pre-registration). Resolving this is a **methodologist decision, not an implementation change** — candidate directions include testing `Δ̂_φ` against its null/surrogate distribution rather than against 0, or a convexity-corrected estimand. It must **not** be silently "fixed" in code to make φ win or lose. The finding is locked as a regression test (`tests/phase4/test_calibration.py`, `test_estimand.py::TestJensenGeometricBias`).

## 8. Reproduce

```bash
uv run pytest tests/phase4 -q                    # 83 methodology tests
uv run pytest -m "reproducibility" -q            # in- and cross-process determinism
```
Synthetic validation (reduced scale; the finding in §7):
```python
from phi.phase4.calibration import null_calibration, all_nulls_calibrated
from phi.phase4.registration import ComparisonSet

C = ComparisonSet.build(delta=0.05, k_per_side=4).constants  # ILLUSTRATIVE, not registered
res = null_calibration(C, n_series=200, series_length=500, replicates=999, base_seed=20260812)
print({k: round(v.rejection_rate, 3) for k, v in res.items()}, all_nulls_calibrated(res))
```
There is **no confirmatory command** — it is gated NO-GO and there is no registered dataset.
