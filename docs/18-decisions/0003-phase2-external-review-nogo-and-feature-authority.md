# 0003 — Phase 2 External Review: NO-GO Verdict, Excursion-vs-Rolling-Window Feature Contradiction, and Required Scientific Freezes

**Status:** **Accepted** — the feature-authority decision (item 1) was made by the architect on 2026-08-12 (Option B; see [§ Decision made](#decision-made-2026-08-12)). Blockers 1–4 remain **UNFROZEN** and continue to gate any confirmatory (Phase-4) work.
**Last Updated:** 2026-08-12
**Supersedes:** none. **Superseded by:** none.
**Relates to:** [ADR 0002](0002-phase2-feature-and-control-design-lock.md), [feature & control contract](../05-mathematics/phi-retracement-feature-contract.md)

## Context

Three external review documents were received on 2026-08-11 and are treated here as inputs, not as instructions to implement:

1. **"PHI — Phase 2 Authoritative Scientific Contract"** (Chief Scientific Architect / Research Methodologist). Verdict: **🔴 NO-GO.** Explicitly *"Scope: Scientific specification only; no implementation code"* and *"All implementation work on Phase 2 must remain FROZEN"* until five blockers are frozen.
2. **"Perplexity — Literature & Prior-Art Intelligence."** Conclusion: the research question is testable and meaningful, but there is **no strong prior** that φ structure should appear in arbitrary series; PHI's contribution is expected to be *methodological*, and "no convincing evidence" is the most likely honest outcome.
3. **"Gemini — Independent Statistical Red Team"** (32-dimension adversarial audit). Verdict: **FAIL** as of current architecture, same five blockers, plus a detailed defense/verification matrix and a proposed superiority-based statistical protocol.

All three agree: **engineering rigor (150 tests, ~98% coverage, ruff/mypy clean, T-1 barrier) is real but is not scientific validity**, and Phase 2 scientific implementation is not authorized until specific scientific choices are frozen *by a human decision*, not invented during coding.

This ADR records that verdict, the contradiction it exposes with already-implemented work, and the exact decisions required. It deliberately **does not** resolve the science — doing so by fiat would itself be the p-hacking pathway PHI exists to prevent (contract §14, §28 of ADR 0002's principles; the review's own Blocker 1).

## The core contradiction (must be resolved before any Phase 2 feature is "authoritative")

The new contract defines a **different scientific object** from the one currently implemented.

| | **Implemented (ADR 0002 + feature contract, `src/phi/features/`)** | **New authoritative contract** |
|---|---|---|
| Feature | Rolling-window **position**: `p_t = (close_t − min_low[t−L,t)) / (max_high[t−L,t) − min_low[t−L,t))` | Excursion **retracement**: `R_t = \|X_t − X_e\| / \|X_e − X_a\|` |
| φ statistic | `f_A(t) = \|p_t − 1/φ\|` (continuous distance) | `D_φ,t = \|R_t − 1/φ\|`, with a **φ-hit** when `D_φ,t ≤ ε_φ` |
| Anchoring | **Deterministic rolling window; no swing/anchor detection** (ADR 0002 explicitly *rejected* ZigZag/pivot detection as look-ahead-prone) | **Requires** a causal anchor/excursion `(X_a, X_e)` selection algorithm — i.e. swing detection |
| Threshold | none (continuous) | `ε_φ` (a registered scientific parameter) |
| Controls | A/B/C1/C2/D/E/F (constant-swap + pipeline-matched) | Family A strict matched ratios `{0.500, 0.583, 0.667}`, IAAFT surrogates, GARCH, circular-shift placebo |
| Phase-2 scope | generation + validation only | same *intent* (construction/reproducibility), but via the excursion feature |

The new contract's feature **cannot be implemented without a swing/anchor algorithm**, which is exactly what ADR 0002 rejected on leakage grounds and what the review flags as **Blocker 1 (unfrozen)**. Therefore:

- The implemented rolling-window feature is **not** what the new contract describes.
- The new contract is **not** implementable as written (its anchor algorithm, threshold, estimand, and inference protocol are unfrozen).
- Running both side-by-side would create **duplicate feature architectures** and inflate multiplicity — forbidden without a pre-registered, counted decision.

**This is an architectural decision only the architect/researcher can make.** It is stated as a required decision in the "Decision required" section below, not resolved here.

## The five blockers (verbatim intent), and their status

| # | Blocker | Status | Why it cannot be invented in code |
|---|---|---|---|
| 1 | Exact **causal anchor/extremum** selection algorithm (lookback `k`, tie-breaking, min-excursion `δ_min`) | **UNFROZEN** | Free swing-detection parameters are the primary hidden p-hacking pathway (Gemini dim 3; Attack Vectors 1, 9). Choosing them during implementation = inventing methodology. |
| 2 | Exact primary threshold **`ε_φ`** | **UNFROZEN** | Selecting `ε_φ` from observed `R_t` density is threshold-fishing (Gemini dim 14; Attack Vector 7). Must be registered before confirmatory analysis. |
| 3 | Single primary **estimand/statistic** (hit-frequency vs continuous distance vs conditional survival) | **UNFROZEN** | Leaving it open creates an unmonitored multiple-comparison space (Gemini dim 20). |
| 4 | Exact **dependence-aware inference** protocol (block definition, block-length rule, #resamples, CI method, overlap handling) | **UNFROZEN** | "Use a block bootstrap" is under-specified; wrong block length severely mis-estimates variance in autocorrelated data (Gemini dims 6, 19; Blocker 4). |
| 5 | Final **cross-document scientific consistency** audit | **PARTIALLY RESOLVED** (see below) | Several items were already reconciled in the last-session contract; the excursion-vs-rolling-window conflict (this ADR) is the remaining open item. |

### Blocker 5 — what is already resolved vs still open

The feature contract authored in the previous session already pre-empted several Blocker-5 items the reviews flagged from the *older* architecture:

- **"Byte-identical" reproducibility claim** — already corrected: the contract's [§5A](../05-mathematics/phi-retracement-feature-contract.md) explicitly states equivalence means identical ordering/support/NULL masks with values within `atol=1e-12, rtol=1e-9`, and *"never byte-identical."*
- **Circular-shift labeled as a formal null** — already corrected: Category B is defined as a *"deterministic temporal-alignment placebo, **not** a statistical null distribution."*
- **Stochastic-%K mischaracterization** — already corrected: contract §7 note explicitly declines to equate Category D with textbook %K.
- **Under-specified OLS-slope control** — already resolved: contract §7.2 fully specifies Category F.
- **Strict vs pipeline-matched control families** — already resolved: contract §8 two-tier matching.

**Still open (this ADR):** the excursion-vs-rolling-window feature identity, and the fact that a *new* control taxonomy (Family A `{0.500, 0.583, 0.667}`, IAAFT, GARCH) is proposed that does not match the implemented A/B/C1/C2/D/E/F set. `PRD = Architecture = Contract = Code = Tests = Research Log` cannot be asserted until the feature-authority decision is made.

## What is NOT authorized to implement under this ADR

Per the reviews' NO-GO and the project's "do not invent methodology" principle, the following MUST NOT be written until frozen by a human decision:

- the excursion anchor/extremum selection algorithm (Blocker 1);
- any hardcoded `ε_φ` value or default (Blocker 2);
- a designated primary estimand or its pass/fail gate (Blocker 3);
- the statistical/inference layer — bootstrap, CIs, effect sizes, multiplicity, IAAFT/GARCH surrogates (Blocker 4) — this is Phase 4 work in the PRD phase plan and depends on Blockers 1–3;
- any predictive, significance, or "φ detected/validated" claim (contract §33; PRD-GRF-012, PRD-ETHICS-005).

## What IS legitimately implementable now — and what was implemented (2026-08-11, round 2)

The frozen arithmetic of the excursion contract, and its science-neutral infrastructure, require none of the unfrozen decisions. These were implemented, with full tests, without inventing any unfrozen methodology (traceability: [frozen-rules map](../05-mathematics/phi-excursion-frozen-rules-map.md)):

- **Frozen excursion-retracement math** — `src/phi/features/retracement.py`: `retracement_ratio` (`R_t = |X_t−X_e|/|X_e−X_a|`, zero→NA with no epsilon substitution §8, negatives allowed §9, overshoot unclamped, overflow raises not silent-`inf`), `phi_distance`, `is_phi_hit` (**`epsilon` is a required kwarg with no default** — Blocker 2 cannot be silently defaulted). The anchor selector is a **no-behaviour `Protocol` only** (Blocker 1 not implemented).
- **Immutable experiment manifest** — `src/phi/experiment/manifest.py`: §29 fields, canonical-JSON SHA-256 hash, frozen/immutable, and `is_confirmatory_ready()` that returns `False` while any of Blockers 1–4 is unset — a machine-checkable encoding of this ADR's NO-GO.
- **Exclusion accounting** — `src/phi/experiment/exclusions.py`: raw/excluded/valid counts, named reasons, missingness rate; over-exclusion raises (§7, §35; AV 5).
- **Adversarial T+1 leakage invariant** — `tests/features/test_pipeline.py::TestAdversarialFutureInjection`: inject `X_{T+1}=1e10`, assert the feature at `T` is bit-for-bit unchanged (§16, §37; Gemini dim 26).

Explicitly still **not** built (needs the feature-authority decision and/or Blockers 1–4): the anchor algorithm, any `ε_φ` value, the primary estimand, and the entire statistical/inference layer (bootstrap, CIs, effect sizes, multiplicity, IAAFT/GARCH surrogates, robustness battery).

## Decision required (from the architect/researcher, not from implementation)

1. **Feature authority.** Choose one:
   - (A) Adopt the excursion-based `R_t` contract as authoritative and **supersede ADR 0002's feature** — then freeze Blockers 1–4 before any confirmatory code.
   - (B) Keep the implemented rolling-window `p_t` feature as the Phase-2 artifact; treat the new contract as Phase-4 statistical guidance.
   - (C) Run both as explicitly pre-registered, multiplicity-counted feature families.
   - (D) Hold Phase 2; build only science-neutral infrastructure until (1) is decided.
2. **Freeze Blockers 1–4** with exact, registered values/algorithms (or authorize drafting *proposals* for human approval — explicitly not confirmatory implementation).

## Decision made (2026-08-12)

**1. Feature authority — Option (B) selected by the architect.** The implemented rolling-window position feature `f_A(t) = |p_t − 1/φ|` (frozen by [ADR 0002](0002-phase2-feature-and-control-design-lock.md) and the [feature contract](../05-mathematics/phi-retracement-feature-contract.md)) is the **authoritative Phase-2 feature.** The excursion-retracement contract (`R_t = |X_t−X_e|/|X_e−X_a|`) is **not** adopted as the Phase-2 feature; its frozen arithmetic core (`src/phi/features/retracement.py`) is retained as **Phase-4 statistical guidance only** — explicitly subordinate, and deliberately **not wired into** the authoritative compute path (`engine.py` / `candidate.py` do not import it). This supersedes the "open decision" framing above.

**Rationale.** The rolling-window feature is deterministic and swing-detection-free, so it carries the **lowest** look-ahead / researcher-degrees-of-freedom risk — ADR 0002 rejected discretionary swing detection precisely because it is the primary hidden p-hacking pathway (Gemini dim 3; Attack Vectors 1, 9). Adopting the excursion feature would first require freezing Blocker 1 (the causal anchor algorithm), which the reviews say must not be invented during coding. Option (B) keeps a defensible, leakage-safe construction artifact now while deferring the excursion feature's confirmatory science to a properly-frozen Phase 4.

**2. Blockers 1–4 remain UNFROZEN.** This decision resolves *which feature is the Phase-2 construction artifact* — nothing more. It does **not** freeze the causal anchor algorithm, `ε_φ`, the primary estimand, or the dependence-aware inference protocol. Any confirmatory (Phase-4) evaluation — of *either* feature — remains **NO-GO** until a human freezes those four, and `phi.experiment.manifest.ExperimentManifest.is_confirmatory_ready()` continues to enforce that in code. This decision therefore closes the feature-authority half of Blocker 5, but does **not** lift the reviews' overall NO-GO on confirmatory φ analysis.

## Consequences

- The engineering baseline stays green and untouched; no working code is discarded on the strength of a NO-GO document.
- Phase 2 is **not** declared scientifically complete. ADR 0002's acceptance gate covered *construction/reproducibility of the rolling-window feature*; it never asserted the excursion feature or any statistics, so no prior claim is retracted — but the new contract's scope is explicitly **not met** and must not be represented as met.
- The feature-authority decision is now **recorded above** (Option B, 2026-08-12): `PRD = Architecture = Contract = Code` can be asserted for the *rolling-window* feature. A **separate** superseding ADR is still required if/when Blockers 1–4 are frozen to authorize any confirmatory (Phase-4) analysis; until then the reviews' NO-GO on confirmatory φ claims stands and is enforced by `is_confirmatory_ready()`.

## Traceability

| Section | Derived from |
|---|---|
| NO-GO verdict | "Authoritative Scientific Contract" §0, §44, Final Decision; "Gemini Red Team" §4 Verdict |
| Feature contradiction | New contract §3–§4, §43 vs [ADR 0002](0002-phase2-feature-and-control-design-lock.md) Decision 1 |
| Blockers 1–5 | New contract §44; "Gemini Red Team" §4 (five blockers) |
| Blocker-5 partial resolution | [feature & control contract](../05-mathematics/phi-retracement-feature-contract.md) §5A, §7, §7.2, §8 |
| Adversarial leakage invariant | New contract §16, §37; "Gemini Red Team" dim 26 / Attack Vector 9 |
| Prohibited claims | New contract §33; PRD-GRF-012, PRD-ETHICS-005 |
