# Excursion-Retracement Contract → Machine-Checkable Rules Map

**Status:** Frozen subset implemented; unfrozen subset BLOCKED (see [ADR 0003](../18-decisions/0003-phase2-external-review-nogo-and-feature-authority.md)).
**Last Updated:** 2026-08-11
**Governs:** the external "PHI — Phase 2 Authoritative Scientific Contract" (excursion-retracement feature).

This document is the traceability bridge required by Phase B ("convert the
approved scientific contract into explicit machine-checkable rules; no
scientific decision should remain implicit"). Each **frozen** rule maps to the
code that enforces it and the test that proves it. Each **unfrozen** rule is
marked **BLOCKED** and is deliberately *not* implemented — implementing it would
be inventing methodology (contract §44; Gemini five-blocker verdict).

## A. Frozen rules — implemented and tested

| Contract rule | § | Enforced in | Proven by |
|---|---|---|---|
| φ constant `φ = (1+√5)/2` | §3, §43 | `phi.PHI` (`src/phi/__init__.py`) | `tests/features/test_retracement.py::TestQPhi` |
| `q_φ = 1/φ = φ − 1 ≈ 0.61803…` | §3, §43 | `phi.features.retracement.Q_PHI` | `TestQPhi::test_q_phi_is_reciprocal_of_phi` |
| `R_t = \|X_t − X_e\| / \|X_e − X_a\|` | §4, §43 | `retracement_ratio` | `TestRetracementRatioWorkedExamples` |
| `D_φ,t = \|R_t − q_φ\|` | §4 | `phi_distance` | `TestPhiDistance` |
| φ-hit ⇔ `D_φ,t ≤ ε_φ` (rule; **not** the value) | §4 | `is_phi_hit` | `TestIsPhiHit` |
| Zero excursion `\|X_e − X_a\|=0` → **NA**, no epsilon substitution | §8 | `retracement_ratio` (returns `None`) | `test_zero_excursion_returns_na_not_epsilon` |
| Negative input values allowed | §9 | `retracement_ratio` (abs magnitudes) | `test_negative_values_allowed` |
| Overshoot `R_t > 1` **not clamped** (no Winsorizing) | Attack V.8 | `retracement_ratio` (returns raw ratio) | `test_overshoot_beyond_one_not_clamped` |
| Non-finite ratio never returned silently | §31 analogue | `NonFiniteRetracementError` | `test_overflow_raises_not_silent_inf` |
| No default / data-driven threshold (anti-fishing) | §14, AV.7 | `is_phi_hit(*, epsilon)` required kw, no default | `test_epsilon_is_required_keyword_only` |
| Scale-invariance of the ratio | §15 | (property of formula) | `TestScaleInvarianceProperty` (Hypothesis) |
| **Leakage**: future `X_{T+1}` cannot change feature at `T` | §16, §37 | shared `phi.features.pipeline` barrier | `tests/features/test_pipeline.py::TestAdversarialFutureInjection` |
| Immutable, content-hashed experiment manifest | §29, AV.7 | `phi.experiment.manifest.ExperimentManifest` | `tests/experiment/test_manifest.py` |
| Manifest cannot be confirmatory-ready while science unfrozen | §29, §31 | `is_confirmatory_ready` / `unfrozen_blockers` | `TestConfirmatoryReadinessGate` |
| Exclusion accounting: raw / excluded / valid / reasons / missingness | §7, §35 | `phi.experiment.exclusions` | `tests/experiment/test_exclusions.py` |
| No silent drop (named reason required; over-exclusion raises) | §7, AV.5 | `ExclusionAccountant.record` / `.summary` | `TestFailureModes` |

## B. Unfrozen rules — **BLOCKED** (not implemented, by design)

| Contract requirement | § | Blocker | Why not implemented |
|---|---|---|---|
| Causal anchor/excursion **selection** algorithm `(X_a, X_e)` | §5, §12, §44 | **1** | Free swing-detection parameters are the primary p-hacking pathway (Gemini dim 3; AV 1, 9). Only a no-behaviour `ExcursionAnchorSelector` Protocol boundary exists. |
| Exact `ε_φ` **value** | §4, §44 | **2** | Must be registered before confirmatory analysis; choosing it here = threshold fishing. Left as a required manifest field. |
| Single primary **estimand/statistic** (`Δp` vs `Δμ` vs survival) | §20, §44 | **3** | Designating one is a scientific decision; the code computes no comparative statistic and no pass/fail gate. |
| Dependence-aware **inference** (block bootstrap, block length, #resamples, CI) | §20-§22, §44 | **4** | "Use a block bootstrap" is under-specified (Gemini dims 6, 19). No statistical layer implemented. |
| IAAFT / GARCH surrogate nulls, multiplicity correction, robustness battery | §17-§25 | 3-4 | Phase-E work; depends on Blockers 1-4 and the primary estimand. |

## C. How to reproduce the frozen-rule checks

```bash
source .venv/bin/activate
python -m pytest tests/features/test_retracement.py tests/experiment -q   # frozen rules
python -m pytest -q --cov=src/phi --cov-report=term-missing               # full suite
ruff check . && mypy src/phi
```

## D. Explicit non-claims

Implementing Section A establishes **construction and reproducibility of the
frozen arithmetic and the experiment infrastructure only**. It establishes no
predictive validity, no statistical significance, and no evidence about φ
(contract §33; PRD-GRF-012). A passing test suite here is *not* scientific
support for the hypothesis.
