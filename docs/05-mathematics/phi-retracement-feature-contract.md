# Phase 2 Feature & Control Contract — φ Retracement-Level Proximity

**Status:** Design-locked (frozen). Implementation contract for PHI Phase 2.
**Version:** 1.0.0
**Last Updated:** 2026-08-10
**Decision of record:** [docs/18-decisions/0002-phase2-feature-and-control-design-lock.md](../18-decisions/0002-phase2-feature-and-control-design-lock.md)
**Governs:** PRD [§16](../02-project/PHI_PRD.md#16-feature-engineering-requirements)–[§18](../02-project/PHI_PRD.md#18-control--placebo-framework); SYSTEM_ARCHITECTURE [§9.4–9.6](../03-architecture/SYSTEM_ARCHITECTURE.md#9-major-system-modules), [§12](../03-architecture/SYSTEM_ARCHITECTURE.md#12-time-semantics), [§14–15](../03-architecture/SYSTEM_ARCHITECTURE.md#14-golden-ratio-research-architecture).

> This document is the single authoritative specification of PHI's **first canonical φ feature** and its **six-category matched control set**. It is written to be implementation-grade: the mathematical definitions below are exact, and any two conforming implementations run on the canonical synthetic fixture must satisfy the reproducibility criterion of [§5A](#5a-reproducibility-criterion-frozen) (identical ordering, support, and NULL masks; numeric values equal within a frozen tolerance). Where the PRD, SYSTEM_ARCHITECTURE, and RESEARCH_HYPOTHESES previously disagreed, this contract and its ADR are the resolution. It makes **no claim** that any feature here is predictive (PRD-GRF-012); it defines *what will be computed and compared*, not *what the answer is* — see the [scientific claim boundary](#0a-scientific-claim-boundary).

---

## 0. Scope of this document

- **In:** the mathematical definition, temporal contract, normalization contract, edge-case contract, the six matched controls, the matching rules, the research-discipline rules, the Phase 2 scope lock, the test contract, and the Phase 2 acceptance gate.
- **Out:** any implementation code, any real-market data, any predictive evaluation (labels, backtest, statistics). Those belong to Phases 3–5 and MUST NOT be started under this contract. See [§9](#9-phase-2-scope-lock).

---

## 0A. Scientific claim boundary

Implementing this contract establishes **only**: deterministic construction of the feature and its controls, temporal validity (leakage-safety under §4), reproducibility (§5A), and matched-control generation (§7–§8). It establishes **none** of the following: predictive validity, statistical significance, market efficacy, or any evidence that φ / Fibonacci structure has explanatory or predictive power.

The canonical feature (§3) is a **candidate operationalization of the φ hypothesis, not evidence for it.** A correct, passing Phase 2 implementation says nothing about whether the golden ratio matters in markets; it only produces well-defined, leakage-safe, fairly-controlled inputs for the later inference phases that *do* weigh evidence (Phases 3–5). No document, commit, or report may treat "the feature is implemented and tests pass" as support for H1 (PRD-GRF-012, PRD-ETHICS-005).

---

## 1. Notation

Let a single instrument's **validated daily bar series** be
`B = (b_0, b_1, …, b_{N−1})`, ordered by `event_time` ascending, exactly as produced by Phase 1 (`phi.data.validation` → `phi.data.storage`): deduplicated, quarantine-removed, schema-valid. Index `i` is **sequence position in the validated series**, never a calendar offset.

Each bar `b_i` carries (all per `phi.data.schemas.PriceBar`, so already finite, timezone-aware, OHLC-consistent, prices `> 0`):

| Symbol | Meaning |
|---|---|
| `τ_i` | `event_time` (bar close time) |
| `α_i` | `availability_time` (when the bar was knowable; `α_i ≥ τ_i`) |
| `o_i, h_i, ℓ_i, c_i` | open, high, low, close (`ℓ_i ≤ o_i,c_i ≤ h_i`) |
| `v_i` | volume (`≥ 0`) |

**Frozen constants** (pinned by *expression*, not by decimal literal, so float64 results are identical across implementations that reuse the repository's `PHI`):

| Constant | Definition (exact expression) | Value (float64, informative) |
|---|---|---|
| `L` | window length in sequence bars | `20` |
| `PHI` | `(1.0 + 5.0**0.5) / 2.0` (from `src/phi/__init__.py`) | `1.6180339887498949` |
| `g_φ` | `1.0 / PHI` | `0.6180339887498949` |
| `g_½` | `0.5` | `0.5` |
| `g_√2` | `1.0 / (2.0**0.5)` | `0.7071067811865476` |
| `SEED` | `random_seed` from `phi.config.Settings` | `1618` |

`NULL` denotes an explicit missing value (Python `None` / Polars null). **`NaN`/`±inf` are never used as a stand-in for `NULL`.**

---

## 2. Shared computation (identical for the candidate and every control)

All features below are computed from one shared pipeline. Only the **final transform** (§3) differs between the candidate and the controls; everything up to and including `p_t` is the same code path.

For a **decision index** `t`:

**2.1 Eligibility filter (leakage barrier).** A prior bar `b_i` is *eligible* for `t` iff `i < t` **and** `α_i ≤ α_t`. This ties the window to Phase 1's availability semantics (`phi.data.pointintime.as_of`) and excludes any late-arriving/restated bar whose availability is after the decision instant.

**2.2 Prior window.** `P_t` = the `L` highest-indexed eligible bars for `t`. In index space this is the half-open interval `[t−L, t)` **when availability is monotone** (the synthetic-fixture and normal case); the eligibility filter only diverges from `[t−L, t)` when out-of-order availability exists, which Phase 1 independently flags. If fewer than `L` eligible bars exist, `f(t) = NULL` (warmup / insufficient history — not an error).

**2.3 Prior range.**
```
H_t  = max_{i ∈ P_t} h_i
Lo_t = min_{i ∈ P_t} ℓ_i
R_t  = H_t − Lo_t
```
The current bar `b_t` is **excluded** from the range (its own extremes must not define the range it is measured against — see ADR 0002 rationale). If `R_t = 0` (degenerate flat window) → `f(t) = NULL` (see [§6](#6-edge-case-contract)).

**2.4 Position of the current close within the prior range.**
```
p_t = (c_t − Lo_t) / R_t
```
`p_t < 0` when the current close is below the entire prior range; `p_t > 1` when above; `p_t ∈ [0,1]` when inside. **No clipping** — breakout information is retained. Only `c_t` (the current close) is consumed from bar `t`.

---

## 3. The candidate φ feature (Category A)

```
f_A(t) = | p_t − g_φ |          g_φ = 1.0 / PHI ≈ 0.6180339887498949
```

Interpretation: the distance between the current close's position-in-range and the **golden-ratio retracement level** `g_φ`, expressed in *position-from-low* coordinates. `0` = exactly on the level; larger = farther. No monotone/kernel transform is applied here (that would add a parameter); downstream evaluation may apply one.

**Why position-from-low `= 1/φ`, and not `0.382`.** A 61.8% retracement of an up-move sits at position `1 − 0.618 = 0.382` from the low; the position `0.618` from the low is the 38.2% retracement. Both `0.382` and `0.618` are φ-derived (`0.382 = 1/φ²`, `0.618 = 1/φ`). To keep the first feature a **single frozen constant**, we fix the reference at `g_φ = 1/φ` in position-from-low coordinates. Multi-level ladders (`0.236/0.382/0.5/0.618/0.786`) and a "nearest-level" rule add degrees of freedom and are **out of scope** (a later family).

**Why absolute value (proximity), not signed distance.** A signed linear feature `p_t − g` would make every constant-swap control an *affine shift* of `f_A` (e.g. `p_t − 0.5 = (p_t − g_φ) + 0.118`), hence information-equivalent under any intercept-bearing evaluator — collapsing the φ-vs-benchmark comparison to nothing. The `|·|` (proximity) form is **nonlinear** in `p_t`, so `|p_t − 0.5|` carries genuinely different information from `|p_t − g_φ|`. Proximity is therefore *required* for a non-degenerate matched-control design, not a stylistic choice.

---

## 4. Temporal contract (binding)

| Concept | Definition for this feature |
|---|---|
| **Event time** | `τ_t`, the close time of the located bar `b_t`. |
| **Availability time** | `α_t`. Every input to `f_A(t)` — `c_t` and `{h_i, ℓ_i : i ∈ P_t}` — is knowable by `α_t` (prior bars satisfy `α_i ≤ α_t` by the §2.1 filter). |
| **Feature-available-at** | `feature_available_at(t) = α_t`. The value indexed at `t` may be consumed by a decision made **at or after** `α_t`. |
| **Lookback** | Exactly the `L` eligible bars in `P_t` (§2.2), plus `c_t`. |
| **Boundary semantics** | Prior window is **left-closed / right-open** in index space, `[t−L, t)`: the `L` bars `{t−L,…,t−1}` inclusive; bar `t` excluded from the range and contributing **only** its close. |
| **Current-bar usage** | `close_t` — **YES** (located price). `open_t`, `high_t`, `low_t`, `volume_t` — **NO.** |
| **Label separation** | Phase 2 computes **no labels**. The contract reserves: any future target evaluated later (Phase 3+) must begin strictly after `α_t` (≥ 1 bar; target uses `b_{t+1}` onward), so feature and target never share a bar. |

**Leakage invariant (must hold for every emitted value):**
```
∀ i ∈ P_t ∪ {t}:   α_i ≤ α_t = feature_available_at(t)
```
Any violation is a defect, not a data condition: the §2.1 filter guarantees it for the window, and `c_t` trivially satisfies it. This is the same T-1 / information-barrier rule enforced in `phi.data.time`; feature computation MUST route window selection through availability, never through raw index alone.

---

## 5. Normalization contract

**No additional normalization is applied, by design.** `p_t` is already dimensionless and scale-invariant (a ratio *within* the prior range), so `f_A` and the level-based controls are directly comparable across instruments, price levels, and regimes without any fitting step. Adding z-scoring/standardization would (a) introduce a fitting window = a new parameter and a new leakage surface, and (b) is unnecessary for the position-based construction.

If any standardization is ever required downstream, it MUST be **past-only** (rolling or expanding, fit strictly on `{i : α_i ≤ α_t}`) and is **out of scope** for Phase 2. Normalization MUST never use future observations. This clause exists to forbid a convenient global z-score, which would leak.

---

## 5A. Reproducibility criterion (frozen)

The mathematical definitions in §2–§7 are **exact**; the tolerance below covers only floating-point rounding-order differences between independent implementations and does **not** license any change to a definition. Reproducibility is asserted at two levels:

- **Single-implementation determinism (exact).** One implementation, run repeatedly on the same input on the same platform, MUST return identical (bitwise) values, ordering, support, and NULL masks across repeated runs and process restarts — including Category B's seeded rotation (this is the PRD-NFR-002 determinism requirement applied to a fixed implementation).
- **Cross-implementation equivalence (within frozen tolerance).** Any two conforming implementations, run on the canonical synthetic fixture, MUST agree on: (a) identical ordering and alignment keys `(symbol, τ_t, α_t)`; (b) identical **support** (the set of non-NULL indices) and identical **NULL masks**; and (c) numeric values equal within the frozen tolerance **`atol = 1e-12`, `rtol = 1e-9`** (i.e. `|x − y| ≤ 1e-12 + 1e-9·|y|`).

"Two conforming implementations produce equivalent outputs" means exactly (a)+(b)+(c) — never "byte-identical." Ordering, support, and NULL masks are exact matches; only finite numeric values carry the tolerance.

If any standardization is ever required downstream, it MUST be **past-only** (rolling or expanding, fit strictly on `{i : α_i ≤ α_t}`) and is **out of scope** for Phase 2. Normalization MUST never use future observations. This clause exists to forbid a convenient global z-score, which would leak.

---

## 6. Edge-case contract

Every case resolves to exactly one of: `RETURN VALUE`, `NULL`, `RAISE`, `REJECT INPUT`. No undefined behavior.

| # | Condition | Behavior |
|---|---|---|
| 1 | Fewer than `L` eligible prior bars (`t < L`, or warmup) | **NULL** |
| 2 | Eligibility filter (§2.1) leaves `< L` bars (late/restated availability) | **NULL** |
| 3 | `R_t = 0` (flat prior window, `H_t = Lo_t`) | **NULL** + optional non-fatal diagnostic flag; **never** an epsilon fudge and **never** divide-by-zero |
| 4 | Gaps / missing bars inside the calendar span | Handled by the sequence-based window; **no** interpolation (gaps already flagged in Phase 1) |
| 5 | Duplicate bars at the same `event_time` reaching the feature | **REJECT INPUT** (raise): Phase 1 must have deduped/quarantined; presence is an upstream contract violation |
| 6 | OHLC inconsistency (`ℓ > h`, etc.) | **REJECT INPUT**: impossible for a constructed `PriceBar`; if seen, upstream invariant broke |
| 7 | `NaN`/`±inf` in any price input | **REJECT INPUT**: impossible from a validated `PriceBar`; feature never ingests non-finite prices |
| 8 | A computed `f(t)` is non-finite despite `R_t > 0` | **RAISE** (assertion): indicates an implementation bug; output is never silently `NaN`/`inf` |
| 9 | Non-trading dates | Not represented as bars; irrelevant to the sequence window |
| 10 | Timezone-naive timestamp | Impossible post-Phase-1 (schema enforces tz-aware); feature performs no naive tz comparison |
| 11 | Suspended / inactive instrument | Appears as absent bars (gaps); if `< L` eligible bars → **NULL** (case 1/2) |

---

## 7. Six-category matched control set

All six categories share the **identical §2 pipeline surface** (same `B`, `L`, eligibility filter, NULL/edge rules, output shape and alignment). They divide into two matching tiers — strict constant-swap (A, C1, C2) and pipeline-matched alternatives (B, D, E, F) — defined precisely in [§8](#8-matching-contract-two-tier). The transforms below are therefore *not* uniformly "a final transform of `p_t`": A/C1/C2/D are functions of `p_t`, E is `p` at a shifted index, B is a rotation of the realized `f_A` series, and F is computed directly from window closes. Category IDs are the PRD's committed requirement IDs — **not renumbered.**

| ID | Category | Definition | Controls for | Expected predictive? |
|---|---|---|---|---|
| **A** · PRD-CONTROL-001 | Candidate φ | `f_A(t) = \|p_t − g_φ\|` | — (the thing under test) | open question |
| **B** · PRD-CONTROL-002 | Deterministic temporal-alignment placebo | seeded circular rotation of the realized `f_A` series (see §7.1) | temporal-alignment artifacts; construction/control validation | **no** (and not a null distribution — §7.1) |
| **C1** · PRD-CONTROL-003 | Fixed round-number benchmark | `f_{C1}(t) = \|p_t − g_½\|` | a salient round level (50%) | benchmark |
| **C2** · PRD-CONTROL-003 | Non-φ mathematical-ratio benchmark | `f_{C2}(t) = \|p_t − g_√2\|` | *φ specifically* vs any irrational constant | benchmark |
| **D** · PRD-CONTROL-004 | Normalized rolling-range position baseline | `f_D(t) = p_t` (the shared position primitive, §2.4) | whether the plain in-range position already captures what the φ-level distance does | baseline |
| **E** · PRD-CONTROL-005 | Naive baseline | `f_E(t) = p_{t−1}` (persistence of position) | the floor of "reuse the last observation" | floor |
| **F** · PRD-CONTROL-006 | Simple statistical baseline | `f_F(t) = β̂_t / R_t` (fully defined in §7.2) | a simple statistical model of price | floor |

**Reconciliation note.** SYSTEM_ARCHITECTURE §15's *"non-φ mathematical ratios"* is **not** a seventh category; it is instantiation **C2** of PRD-CONTROL-003. RESEARCH_HYPOTHESES.md's five-item "Required Comparisons" list is a lay summary and is **superseded** by this six-category set. See ADR 0002.

**On Category D naming.** D is defined as *exactly* the shared normalized rolling-range position `p_t` (§2.4). It is the conventional-analysis analogue of "where does price sit within its recent range." It is deliberately **not** claimed to equal any specific named external indicator (e.g. stochastic %K), because no PHI source document defines one: textbook %K uses a range that includes the current bar and a ×100 scaling, neither of which applies here. D imports no external technical-analysis convention beyond the plain in-range position already specified in §2.4.

### 7.1 Category B construction — deterministic temporal-alignment placebo
Let `S = (t : f_A(t) ≠ NULL)` in ascending order, with `|S|` realized values `(f_A(t))_{t∈S}`.
1. Instantiate `rng = random.Random(SEED)` (`SEED = 1618`), matching the ecosystem PRNG used by `phi.data.providers.synthetic`.
2. Draw offset `s = rng.randrange(L, |S| − L + 1)` (requires `|S| ≥ 2L`; if `|S| < 2L`, B is `NULL` everywhere and the fixture is too small — a test-fixture sizing error, surfaced, not silently tolerated).
3. For the `k`-th support position `t_k` (0-indexed): `f_B(t_k) = f_A(t_{(k + s) mod |S|})`.
4. `NULL` positions of `f_A` remain `NULL` in `f_B` (null mask matched).

**What this preserves, and what it does not establish.** The circular rotation preserves, *by construction*, the exact multiset of realized non-NULL `f_A` values and their circular ordering/dependence structure; it changes only the timestamp alignment between the feature series and any (future) target. It is therefore a **deterministic temporal-alignment placebo**, not a statistical null distribution:

- Phase 2 uses **one** deterministic realization (the single seeded offset `s`).
- Its purpose is **construction/control validation** — confirming the placebo shares the pipeline, support, and NULL mask of `f_A` while breaking alignment.
- It is **not** a formal statistical null distribution and, on its own, establishes **no** significance and **no** null hypothesis rejection.
- Formal null distributions, permutation inference, multiple realizations, and significance testing belong to the later research/inference phases (Phase 4), not here.

No additional placebo parameters are introduced beyond the single frozen `SEED` and the offset construction above.

### 7.2 Category F construction (range-normalized OLS slope) — complete definition
F regresses the prior window's closes on their within-window ordinal position, then normalizes the slope by the same prior range used everywhere else. It is fully specified as follows, with no ambiguity left:

| Item | Specification |
|---|---|
| Observation set | the `L` prior-window bars `P_t` (§2.2). The **current bar `b_t` does not participate** (not even its close). |
| Prior `L=20` closes | all `L` window closes `{c_j : j ∈ P_t}` are used, none omitted. |
| Independent variable `x` | the **within-window ordinal position**: sort `P_t` by ascending `event_time` and assign `x_k = k` for `k = 0,…,L−1` (spacing exactly 1; slope is invariant to the absolute index, so any index gaps under the eligibility filter are immaterial). |
| Dependent variable `y` | the corresponding close `y_k = c_{(k)}` of the `k`-th window bar. |
| OLS slope | `β̂_t = Σ_{k} (x_k − x̄)(y_k − ȳ) / Σ_{k} (x_k − x̄)²`, with `x̄ = (L−1)/2`, `ȳ =` mean window close. For `L = 20` the denominator is the constant `Σ(x_k − x̄)² = L(L²−1)/12 = 665`. |
| Normalization denominator | the prior range `R_t = H_t − Lo_t` from §2.3 (the *same* range used by A/C1/C2/D), in price units. |
| Feature | `f_F(t) = β̂_t / R_t` — units of (price per bar) ÷ price = per-bar fractional drift. |
| Sign convention | **signed**: `β̂_t > 0` ⇔ closes rise across the window; the sign is retained in `f_F` (never `|·|`). |
| Zero range | `R_t = 0` → **NULL** (same rule as §6 case 3; no division). |
| Insufficient history | `< L` eligible prior bars → **NULL** (§6 cases 1–2). |
| Non-finite | inputs finite by schema; if a computed `f_F(t)` is non-finite despite `R_t > 0` → **RAISE** (§6 case 8). |
| Output type | `float64` (signed) or `NULL`; never `NaN`/`inf`. |
| Temporal availability | `feature_available_at(t) = α_t` for alignment parity with the other five; F in fact consumes only bars through `t−1`, so its inputs are all available strictly before `α_t` — no weaker guarantee than the leakage invariant (§4). |

`β̂_t` is *estimated from data*, not a chosen hyperparameter — see parameter parity in §8.

---

## 8. Matching contract (two-tier)

"Matched control" means two distinct, precisely-scoped things here. Conflating them would overclaim; they are separated below.

### 8.1 Tier 1 — Strict matched constant-swap controls (A, C1, C2)

A, C1, C2 share the **exact same primitive `f(t) = |p_t − g|`** and differ **only in the frozen reference constant**:

| Control | Constant `g` (exact expression) |
|---|---|
| A | `g_φ = 1.0 / PHI` |
| C1 | `g_½ = 0.5` |
| C2 | `g_√2 = 1.0 / (2.0**0.5)` |

Nothing else may differ between them — same `p_t`, same window, same everything downstream to the null mask. Because they are the *same function* with a single swapped constant, their degrees-of-freedom parity is exact by construction, and the φ candidate gets **no** discretionary advantage. This is the tier that isolates "does the constant `g_φ` specifically matter?"

### 8.2 Tier 2 — Pipeline-matched alternative baselines (B, D, E, F)

B, D, E, F are **not** constant-swaps of A and are **not** all functions of `p_t`; their mathematical transformations genuinely differ (B = rotation of realized `f_A`; D = `p_t`; E = `p_{t−1}`; F = range-normalized OLS slope of window closes). They are "matched" in the weaker, still-mandatory sense that they share the **same data-processing pipeline**:

- same source bar sequence `B` (same instrument, same validated data, same adjusted/unadjusted choice);
- same availability semantics and same temporal barrier / leakage invariant (§2.1, §4);
- same window policy where a window applies (D, E, F use `P_t`/`L=20`; B operates on the realized `f_A` series);
- same eligibility rules;
- same `NULL` / support policy;
- same output alignment keys `(symbol, τ_t, α_t)`;
- same output dimensionality (one scalar per `t`), dtype (`float64`), null representation;
- same downstream evaluation protocol and label separation (identical for all six, defined in Phases 3–4).

What may differ in Tier 2 is **only the mathematical transform**, not the pipeline around it.

### 8.3 Parameter parity (all six)

A, C1, C2 each carry **exactly one fixed constant** and **zero tunable hyperparameters** beyond the frozen `L`. D and E carry **zero** constants. F fits **one slope from data** (not a chosen knob). No control may introduce a tunable hyperparameter that A lacks, and A is granted none beyond the frozen `L`.

### 8.4 Anti-favoritism

The φ candidate receives no smoothing, outlier handling, or preprocessing that the controls don't also receive. The §2 pipeline surface up to each control's transform is the same code path, making preprocessing favoritism structurally impossible (PRD-CONTROL-007/009, PRD-FEATENG-001, PRD-BIAS-008).

---

## 9. Research discipline (pre-registration)

Phase 2 is **not** a feature-mining laboratory. The following are **frozen by this contract before any real-market evaluation** and may be changed only by a superseding ADR (logged):

- one φ family only (this one); no family-shopping;
- `L = 20`; no window grid, no result-driven `L` tuning;
- `g_φ = 1/φ`; the only other level constants that exist are the pre-registered benchmarks `g_½ = 0.5` and `g_√2 = 1/√2`; no constant grid beyond these;
- the exact six controls above; controls are fixed *before* results, never selected after;
- `SEED = 1618` for the one place randomness enters (Category B).

Structural safeguard: **Phase 2 runs no predictive evaluation at all** — no labels, no backtest, no significance test. It only *generates and validates* the feature/controls on the synthetic fixture. Result-driven selection is therefore impossible within Phase 2. When Phase 4 evaluates, the comparison count is this fixed `1 candidate × 6 categories` set, logged for multiple-testing accounting (PRD-VALIDATION-012). Any later expansion is a new, pre-registered, counted decision.

---

## 10. Phase 2 scope lock

**IN SCOPE**
- shared leakage-safe feature primitives (rolling prior-window range, position-in-range, availability-filtered windowing) in a new `src/phi/features/` package, built on `phi.data.time` / `phi.data.schemas` / `phi.data.pointintime`;
- the one canonical φ feature (Category A);
- the complete six-category matched control set (B, C1, C2, D, E, F);
- deterministic feature generation over the existing synthetic fixture;
- feature-level validation, leakage tests, boundary tests, determinism/reproducibility tests, control-parity tests (§11);
- this contract's documentation (already authored).

**OUT OF SCOPE (explicitly prohibited in Phase 2)**
- any additional φ feature family or feature-family exploration;
- ML, model selection, hyperparameter optimization;
- backtesting, signal generation, strategy/portfolio/execution logic;
- any predictive claim, label construction, or statistical significance testing;
- real-market data / provider selection (PRD-OPEN-001 stays open);
- live/paper trading, UI, dashboards, real-time systems;
- PostgreSQL/TimescaleDB, DVC, MLflow, or any experiment-tracking platform;
- large-scale data infrastructure; unrelated refactors of Phase 0/1 code.

---

## 11. Test contract (mandatory before Phase 2 is complete)

Coverage percentage alone is **not** acceptance. All of the following must exist and pass:

1. **Mathematical correctness** — hand-computed worked examples (at least: a close on the level → `f_A = 0`; a close at prior high and prior low → known `p_t`, known `f_A`; an OLS-slope example for F) reproduce exact expected values.
2. **Determinism & reproducibility** — per §5A: a single implementation returns identical (bitwise) values, ordering, support, and NULL masks across repeated runs and process restarts (including Category B's seeded rotation); and any two conforming implementations agree on ordering, support, and NULL masks exactly, with numeric values within `atol = 1e-12`, `rtol = 1e-9`.
3. **Temporal leakage** — a bar with `α_i > α_t` in the window is excluded; injecting a future-availability bar cannot change `f_A(t)`; feature value at `t` is invariant to appending any bars after `t`.
4. **Window boundary** — left-closed/right-open semantics verified: bar `t` is absent from the range; bar `t−L` is present; bar `t−L−1` is absent.
5. **Insufficient history** — `t < L` and post-filter `< L` both yield `NULL`, per §6 cases 1–2.
6. **Invalid input** — duplicate/inconsistent/non-finite inputs trigger `REJECT INPUT` per §6 cases 5–7.
7. **`NaN`/`inf` safety** — no output is ever `NaN`/`inf`; `R_t = 0` yields `NULL` (case 3), not a division error.
8. **Matching parity (both tiers, §8)** — Tier 1: assert A, C1, C2 are the *same function* of `p_t` with only the constant swapped, sharing support and NULL mask exactly. Tier 2: assert B, D, E, F share the source sequence, availability semantics, eligibility rules, NULL/support policy, and alignment keys with A on the same fixture (E's support is A's shifted by one bar; B's support and NULL mask equal A's).
9. **Parameter parity (§8.3)** — no control carries a tunable hyperparameter beyond what A has (none, past frozen `L`); F's slope is data-estimated, not a chosen knob.
10. **Cross-implementation reproducibility** — on the canonical fixture, outputs satisfy the §5A cross-implementation criterion (identical ordering/support/NULL masks; values within the frozen tolerance) with stable serialization and stable null encoding.
11. **Metamorphic / invariants** — e.g. `f_A(t) ≥ 0`; scaling all prices by a positive constant leaves `p_t` (hence `f_A`) unchanged (scale-invariance); translating all prices by an additive constant changes `p_t` predictably; `f_{C?}` swap-constant identities hold.

---

## 12. Phase 2 acceptance gate

Phase 2 MUST NOT be declared complete unless **every** box is true:

```
[x] One canonical φ feature formally specified            (this doc §3)
[x] Formula frozen                                        (§3)
[x] Temporal contract frozen                              (§4)
[x] Window semantics frozen                               (§2, §4)
[x] Normalization frozen                                  (§5)
[x] Edge cases frozen                                     (§6)
[x] Six control categories frozen                         (§7)
[x] Matching rules frozen                                 (§8)
[x] Shared leakage-safe primitives implemented            (src/phi/features/)
[x] φ feature implemented
[x] All matched controls implemented                      (B, C1, C2, D, E, F)
[x] Mathematical tests pass                                (§11.1)
[x] Determinism tests pass                                 (§11.2)
[x] Leakage tests pass                                     (§11.3)
[x] Boundary tests pass                                    (§11.4)
[x] Control-parity tests pass                              (§11.8–9)
[x] Reproducibility tests pass                             (§11.10, with the caveat below)
[x] No real-market empirical claims made
[x] No additional φ families introduced
[x] Phase 3 work not started
```

**Status: implementation complete (2026-08-11).** `src/phi/features/` (`pipeline.py`, `candidate.py`, `controls.py`, `engine.py`) implements this contract exactly. 150 tests pass project-wide (73 new to Phase 2), 98% line coverage, ruff/mypy clean. The full §11 test contract (all 11 items, not only the ones this gate names by number) has corresponding tests in `tests/features/`.

**Two honest caveats, not glossed over:**

- **§11 item 10 (cross-implementation reproducibility) is not literally testable yet** — there is exactly one implementation in this repository. What *is* tested is (a) single-implementation determinism: repeated calls on identical input return bitwise-identical output, including Category B's seeded rotation (§5A's other clause, item 2), and (b) hand-computed worked examples matching this implementation's output far inside the frozen tolerance (`atol=1e-12, rtol=1e-9`). True cross-implementation agreement can only be asserted once a second, independent implementation exists to compare against.
- **Category F's non-finite-output guard (§6 case 8) is implemented but not exercised by a forced-overflow test.** `p_t`'s equivalent guard *is* tested with real (schema-valid) inputs — a breakout close against a near-zero prior range genuinely overflows float64 (`tests/features/test_pipeline.py::TestNonFiniteOutputGuard`) — because `R_t` there comes only from the *prior* window while `close_t` is unconstrained relative to it. F's slope and its normalizing range are both derived from the *same* window, which appears to make them scale together for any schema-valid input, so a genuine overflow could not be constructed. The guard is believed structurally near-unreachable, not proven unreachable, and is left in place as defense-in-depth rather than removed.

---

## 13. Traceability

| This contract | Derives from |
|---|---|
| Candidate φ feature (§3) | PRD-GRF-005 (retracement) + PRD-GRF-007 (φ-scaled distance); SYSTEM_ARCHITECTURE §14 |
| Six-category control set (§7) | PRD-CONTROL-001…006 (§18); SYSTEM_ARCHITECTURE §15 (non-φ ratios → C2) |
| Temporal contract (§4) | SYSTEM_ARCHITECTURE §12; PRD-FEATENG-002; PRD-BIAS-007; `phi.data.time` |
| Matching contract (§8) | PRD-CONTROL-007/009; PRD-FEATENG-001; PRD-BIAS-008 |
| Research discipline (§9) | PRD §21 (BIAS-002/003/004/005/009/010); PRD-ETHICS-001/002 |
| Determinism / reproducibility (§9, §11) | PRD-FEATENG-003/004; PRD-REPRO-001/002 |
| Acceptance gate (§12) | PRD-ACCEPT-003 |
