# 0002 — Phase 2 Design Lock: Canonical First φ Feature and Six-Category Matched Control Set

**Status:** Accepted
**Last Updated:** 2026-08-10
**Supersedes:** none. **Superseded by:** none.
**Full contract:** [docs/05-mathematics/phi-retracement-feature-contract.md](../05-mathematics/phi-retracement-feature-contract.md)

## Context

Phase 0 forensic reconnaissance established that Phase 0/1 (engineering + data foundation) are genuinely implemented and tested (77/77 tests, 97% coverage, ruff/mypy clean, T-1 barrier enforced in code), but that the repository could **not** enter Phase 2 as-is:

1. **No canonical first φ feature exists** to implementation-grade precision. PRD [§17](../02-project/PHI_PRD.md#17-golden-ratio-feature-families) lists ten illustrative GRF families (PRD-GRF-001…010) as one-sentence descriptions with no formula, window, normalization, or edge-case rules — not implementable as written, and PRD-OPEN-005 explicitly leaves the enumeration open.
2. **The control/placebo framework is defined three inconsistent ways** — PRD [§18](../02-project/PHI_PRD.md#18-control--placebo-framework) (six categories A–F, with committed IDs PRD-CONTROL-001…006), SYSTEM_ARCHITECTURE [§15](../03-architecture/SYSTEM_ARCHITECTURE.md#15-falsification--placebo-architecture) (five controls, including a *"non-φ mathematical ratios"* category with no PRD counterpart), and RESEARCH_HYPOTHESES.md (a five-item lay list). PRD-CONTROL-008 requires *all* categories before any support claim, so an inconsistent definition blocks a fair Phase 2 comparison.
3. **A factual miscount** propagated into orientation docs: "12 named φ-feature families" (`ORGANIZATION_REPORT.md`, `PROJECT_MAP.md`) vs. the PRD's actual ten (PRD-GRF-011/012 are process rules, not families).

Phase 0.5 exists to resolve these as **scientific/architectural decisions before implementation**, without writing feature code.

## Decision

### Decision 1 — Canonical first φ feature: Fibonacci retracement-level proximity

The first φ feature is the **proximity of the current close's position within a deterministic prior-window price range to the golden-ratio retracement level `g_φ = 1/φ`**:

```
p_t   = (close_t − min_low[t−L, t))  /  (max_high[t−L, t) − min_low[t−L, t))
f_A(t) = | p_t − g_φ |            g_φ = 1/φ ≈ 0.6180339887,  L = 20
```

Primary home: **PRD-GRF-005** (Fibonacci retracement relationships), operationalized via the **PRD-GRF-007** (φ-scaled distance) framing. Full formula, temporal/normalization/edge-case contracts, and the six controls are frozen in the [feature contract](../05-mathematics/phi-retracement-feature-contract.md).

**Rationale.**
- It is *the* canonical, most-recognized Fibonacci market claim (retracement), so a null result is maximally informative against the strongest popular form of the hypothesis.
- A **single swappable φ constant** makes the ideal matched control: benchmarks C1/C2 differ from A by *exactly one constant*, directly isolating "φ specifically" — the crux of the research question.
- A **deterministic rolling-window range** (not discretionary swing/pivot detection) eliminates the classic ZigZag look-ahead trap → lowest leakage risk.
- The feature is **dimensionless/scale-invariant**, so no normalization (hence no fitting window, no extra leakage surface, no extra DoF) is needed.
- The `|·|` (proximity) form is **nonlinear**, so constant-swap controls are non-degenerate.

**Alternatives rejected.**
- **GRF-001 (abstract φ-constant multiples):** no single canonical operationalization; high researcher discretion.
- **GRF-005 with discretionary swing detection (ZigZag/pivots):** pivots are only confirmable in hindsight → high look-ahead risk, parameter-heavy, poorly reproducible.
- **GRF-006 (extensions):** requires a defined swing + direction → same discretion/leakage problems, plus unbounded outputs.
- **GRF-009 (temporal φ intervals):** requires event detection → discretionary and leakage-prone; hard to build clean matched controls.
- **Signed linear distance `p_t − g` instead of `|p_t − g|`:** makes every constant-swap control an affine shift of A → information-equivalent under any intercept-bearing evaluator → the φ-vs-benchmark comparison collapses. The proximity form is *required*.
- **Multi-level Fibonacci ladder (0.236/0.382/0.5/0.618/0.786):** more levels + a "nearest-level" rule = more DoF; deferred as a later family.

### Decision 2 — Canonical six-category matched control set

PRD [§18](../02-project/PHI_PRD.md#18-control--placebo-framework)'s six categories (committed IDs **PRD-CONTROL-001…006**) are adopted as the canonical framework, **not renumbered**. The conflicts are resolved by mapping, not by inventing a new taxonomy:

| ID | Category | This feature's instantiation |
|---|---|---|
| A · PRD-CONTROL-001 | Candidate φ | `\|p_t − g_φ\|` |
| B · PRD-CONTROL-002 | Deterministic temporal-alignment placebo | seeded circular rotation of the realized `f_A` series (not a null distribution — see contract §7.1) |
| C1 · PRD-CONTROL-003 | Fixed round-number benchmark | `\|p_t − 0.5\|` |
| C2 · PRD-CONTROL-003 | Non-φ mathematical-ratio benchmark | `\|p_t − 1/√2\|` |
| D · PRD-CONTROL-004 | Normalized rolling-range position baseline | `p_t` (the shared position primitive; not claimed equal to any named external indicator such as stochastic %K) |
| E · PRD-CONTROL-005 | Naive baseline | `p_{t−1}` (persistence) |
| F · PRD-CONTROL-006 | Simple statistical baseline | range-normalized OLS slope of prior-window closes (fully defined in contract §7.2) |

- **SYSTEM_ARCHITECTURE §15's "non-φ mathematical ratios" is folded into PRD-CONTROL-003 as instantiation C2** — it is a required benchmark, not a seventh category. This resolves the PRD-vs-architecture conflict without renumbering committed requirement IDs.
- **RESEARCH_HYPOTHESES.md's five-item "Required Comparisons" list is a lay summary and is superseded** by this six-category set.

Rationale for keeping PRD-CONTROL IDs stable rather than restructuring: those IDs are cross-referenced across the PRD, architecture, and database docs; renumbering a committed, drafted requirement set to match a convenient phrasing would create more inconsistency than it removes. Category C carrying two required instantiations (round-number + non-φ irrational) captures both the round-level and irrational-constant controls the research question needs.

### Decision 3 — Feature-family count is ten, not twelve

The PRD enumerates **ten** φ-feature families (PRD-GRF-001…010). PRD-GRF-011 ("illustrative, non-exhaustive") and PRD-GRF-012 ("no premature predictive claim") are process rules, not families. Orientation docs stating "12" are corrected to "10."

### Decision 4 — Feature and controls live in one contract document

Feature and controls are specified in a **single** contract ([phi-retracement-feature-contract.md](../05-mathematics/phi-retracement-feature-contract.md)) rather than two, because they must share the same temporal, normalization, and matching contracts. Splitting them across documents would reintroduce exactly the definition-drift this phase exists to eliminate.

## Consequences

- Phase 2 has an unambiguous, pre-registered target: one φ feature + six controls, all frozen (formula, window, temporal, normalization, edge cases, matching, seed). The mathematical definitions are exact; conforming implementations are held to the contract's [§5A reproducibility criterion](../05-mathematics/phi-retracement-feature-contract.md) — identical ordering/support/NULL masks, numeric values within a frozen tolerance (`atol = 1e-12`, `rtol = 1e-9`) — not to a "byte-identical" cross-implementation claim.
- Matching is **two-tier** (contract §8): strict constant-swap for A/C1/C2 (same function, one swapped constant), pipeline-matched for B/D/E/F (same data pipeline, genuinely different transforms). D/E/F are *not* claimed to be mere final transforms of `p_t`.
- The φ candidate receives no discretionary advantage over its controls (shared pipeline; single-constant swap for the benchmarks) — PRD-CONTROL-007/009 are satisfiable by construction.
- Phase 2 runs **no** predictive evaluation (no labels, no backtest, no statistics), structurally preventing result-driven selection; the multiple-testing ledger for Phase 4 is a fixed `1 × 6` comparison. Category B is a single deterministic realization for control validation, **not** a statistical null distribution — formal nulls, permutation inference, and significance belong to Phase 4.
- **Scientific claim boundary.** Implementing this contract establishes deterministic construction, temporal validity, reproducibility, and matched-control generation only. It establishes **no** predictive validity, statistical significance, market efficacy, or evidence that φ has explanatory/predictive power. The feature is a *candidate operationalization* of the φ hypothesis, not evidence for it (PRD-GRF-012, PRD-ETHICS-005).
- This ADR must be **superseded, not edited,** if the first feature, the control taxonomy, `L`, or the frozen constants change.

## Alternatives considered (taxonomy)

- **Restructure the PRD's six into the "non-φ ratio as its own category + merge naive/statistical" shape.** Rejected: renumbers committed requirement IDs and drops the PRD's deliberate naive-vs-simple-statistical distinction for no scientific gain at this stage; the same coverage is achieved by C2 + the existing E/F split.
- **Pick a discretionary-swing retracement to match retail TA faithfully.** Rejected: faithful reproduction of a discretionary indicator imports its look-ahead and reproducibility problems; the research goal is a *fair, leakage-safe* test of the φ level, not fidelity to retail charting.

## Traceability

| Section | Derived From |
|---|---|
| Decision 1 | PRD-GRF-005/007; SYSTEM_ARCHITECTURE §12, §14; `phi.data.time` |
| Decision 2 | PRD-CONTROL-001…009; SYSTEM_ARCHITECTURE §15; RESEARCH_HYPOTHESES.md |
| Decision 3 | PRD §17 (PRD-GRF-001…012) |
| Decision 4 | PRD-NFR-008 (documentation consistency) |
| Frozen contract | [phi-retracement-feature-contract.md](../05-mathematics/phi-retracement-feature-contract.md) |
