# Project PHI — Product Requirements Document

## 1. Document Control

- **Document:** PHI_PRD.md
- **Status:** Draft — Pending Review
- **Version:** 0.1.0
- **Owner:** TBD (Suggested: Founder / Solo Developer, acting as Product, Research & Engineering Lead)
- **Last Updated:** 2026-08-07
- **Scope:** Product-level requirements for Project PHI — what the platform must accomplish and what must be true for its research to be scientifically credible. This document does not define system architecture, module boundaries, or implementation detail; those are defined in [../03-architecture/SYSTEM_ARCHITECTURE.md](../03-architecture/SYSTEM_ARCHITECTURE.md) and are referenced, not duplicated, here (see [§37](#37-traceability-to-architecture)).

## 2. Executive Summary

Project PHI is a research-grade quantitative platform built to answer one specific, falsifiable question: do Golden Ratio (φ ≈ 1.6180339887) and Fibonacci-derived mathematical features carry statistically useful, out-of-sample predictive information about financial markets, once measured against realistic controls? PHI is not built to confirm that they do. It is built to find out, and to be equally credible whichever way the evidence points.

This PRD defines what PHI must accomplish as a product: a reproducible research workflow, a fair and mandatory comparison framework (Golden Ratio features vs. randomized, benchmark, conventional, and naive controls), a realistic event-driven backtesting standard, a rigorous statistical validation discipline, and an honest accounting of both success and failure that does not depend on the hypothesis being true. The platform is built by a solo developer, so requirements are scoped to prioritize scientific rigor, reproducibility, and simplicity over infrastructure that isn't yet justified.

This document does not redesign or restate [SYSTEM_ARCHITECTURE.md](../03-architecture/SYSTEM_ARCHITECTURE.md), which is now substantially drafted and committed. It defines the product requirements that architecture document was built to satisfy.

## 3. Product Vision

PHI exists to make it possible for a solo researcher to test a specific, historically under-rigorously-tested claim — that Golden Ratio/Fibonacci mathematics has predictive value in markets — with the same discipline a professional quantitative research desk would apply: point-in-time correctness, baseline-relative evaluation, placebo controls, walk-forward validation, and full reproducibility. The vision is not "a platform that finds a profitable Golden Ratio strategy." It is a platform that produces a *trustworthy answer*, positive or negative, and that is architected so the same rigor extends naturally to whatever research question comes after this one.

## 4. Problem Statement

Golden Ratio and Fibonacci relationships are widely referenced in retail and popular technical-analysis material as if their predictive value were established. In practice, most of this material does not test the claim against a baseline, does not control for the fact that *many* ratio-based rules will appear to "work" on a sufficiently large search over assets/periods/parameters, and does not report negative results. There is no accessible, end-to-end, reproducible framework that lets a solo researcher take this specific hypothesis from raw market data through a rigorous, bias-aware statistical conclusion. PHI is built to close that gap for this hypothesis — and, by construction, for any comparable quantitative hypothesis afterward.

## 5. Research Question

> Can Golden Ratio–derived features demonstrate statistically robust predictive information beyond appropriate placebo, benchmark, conventional technical, and naive baseline features across multiple assets, periods, and market regimes?

This is the single research question PHI's Phase 0–5 scope exists to answer. Every requirement in this document that touches data, features, backtesting, or validation exists in service of answering it credibly.

## 6. Scientific Hypothesis (H1)

Golden Ratio / Fibonacci-derived mathematical features (see [§17](#17-golden-ratio-feature-families)) contain statistically detectable, out-of-sample predictive information about future price or return behavior that is **not** already explained by: chance (randomized controls), arbitrary ratio structure in general (non-φ benchmark ratios), conventional technical analysis (baseline technical features), or naive forecasting (simple statistical baselines) — when evaluated across multiple assets, multiple time periods, and multiple market regimes under walk-forward validation.

## 7. Null Hypothesis (H0)

Golden Ratio / Fibonacci-derived features provide **no** statistically detectable predictive advantage over the control set defined in [§18](#18-control--placebo-framework), once evaluated under the same validation discipline. Any apparent edge observed in a single backtest, asset, period, or parameterization is presumed attributable to chance, selection effects, or leakage unless it survives the full falsification process in [§8](#8-falsification-criteria).

H0 is the default assumption PHI's architecture is built to hold until H1 earns rejection of H0 through evidence — not the reverse.

## 8. Falsification Criteria

PHI does not use a single hard metric threshold (e.g., a fixed Sharpe or IC cutoff) as a universal pass/fail gate — doing so creates an incentive to search for parameterizations that clear the gate, which is itself a form of data snooping (see [§21](#21-bias-prevention-requirements)). Instead, falsification is a **structural, process-based judgment**, made against the following conditions:

- **PRD-FALSIFY-001** — H1 is considered **not supported (effectively falsified)** for a given φ-feature family when, across the pre-defined set of assets, periods, and regimes tested for that family, the feature family fails to show an out-of-sample advantage over its strongest-performing control ([§18](#18-control--placebo-framework)) that is distinguishable from chance after accounting for the number of comparisons made ([§20](#20-statistical-validation-requirements)), and this failure is stable across the walk-forward windows tested rather than an artifact of one run.
- **PRD-FALSIFY-002** — H1 is considered **supported** for a given φ-feature family only when it shows a statistically distinguishable advantage over *all* control categories in [§18](#18-control--placebo-framework) (not just the weakest one), that advantage is stable across out-of-sample walk-forward windows and across more than one market regime, and the result survives the robustness/permutation checks in [§20](#20-statistical-validation-requirements).
- **PRD-FALSIFY-003** — A result that shows an advantage over some but not all controls, or that is unstable across regimes/windows, or that has not yet been tested across enough assets/periods to distinguish signal from chance, is recorded as **inconclusive**, not as support for H1.
- **PRD-FALSIFY-004** — Falsification (or support) is evaluated per φ-feature family (see [§17](#17-golden-ratio-feature-families)), not for "the Golden Ratio hypothesis" as a monolithic claim — different families may be falsified while others remain inconclusive or supported.
- **PRD-FALSIFY-005** — No single experiment run, asset, or time period is sufficient to declare H1 supported. A single run may contribute evidence toward falsification (a single strong negative result is informative) but requires the full replication set described in [§18](#18-control--placebo-framework)/[§20](#20-statistical-validation-requirements) to declare support.

## 9. Product Goals

- **PRD-GOAL-001** — Deliver an end-to-end, working research loop (data → features → controls → backtest → validation → conclusion) for at least the first cohort of Golden Ratio feature families defined in [§17](#17-golden-ratio-feature-families).
- **PRD-GOAL-002** — Make every research conclusion reproducible: re-running a logged experiment against its recorded code/data/config version must reproduce the same result.
- **PRD-GOAL-003** — Make the platform maintainable and extensible by a single developer, favoring simplicity and clear module boundaries over infrastructure scale.
- **PRD-GOAL-004** — Produce an honest, auditable research record regardless of outcome — a negative or inconclusive result is a valid, complete product deliverable.
- **PRD-GOAL-005** — Establish the falsification-first research workflow as a reusable capability, so future quantitative hypotheses beyond Golden Ratio can be tested with the same rigor without rebuilding the platform.

## 10. Non-Goals

- Live trading with real capital in the current or near-term phases (see [§33](#33-phase-plan), Phase 7–8).
- A multi-user, multi-tenant, or SaaS product.
- Enterprise-scale infrastructure (distributed streaming, container orchestration, microservices) — explicitly deferred; see [SYSTEM_ARCHITECTURE.md §29](../03-architecture/SYSTEM_ARCHITECTURE.md#29-architecture-decision-summary).
- A guarantee, promise, or expectation that Golden Ratio features will prove profitable or predictive. That is the open question this product exists to answer, not an assumed outcome.
- A general-purpose trading-signal product, dashboard, or subscription service. Any such thing is downstream of validated research, not a current goal.
- Defining exact data-provider selection, broker selection, or deployment target — these remain open ([§35](#35-open-questions)).

## 11. Target User

The primary user of PHI, across all currently scoped phases, is the **solo researcher/developer** building it — acting simultaneously as quantitative researcher, product owner, and engineer. There is no separate "customer" persona in this phase. Secondary, later-phase users (not currently scoped) may include:

- The same individual, later, operating PHI in a paper-trading capacity (Phase 7) — still a single user, not a multi-user product.
- A future reviewer or collaborator evaluating the credibility of PHI's research record, who consumes research outputs ([§23](#23-research-outputs)) but does not operate the platform directly.

## 12. Core User Jobs

Framed as jobs-to-be-done for the target user in [§11](#11-target-user):

- **PRD-JOB-001** — "I need to ingest and validate market data so that everything built downstream can be trusted, not just assumed clean."
- **PRD-JOB-002** — "I need to generate Golden Ratio feature candidates *and* equivalent baseline/placebo controls under identical conditions, so any comparison between them is fair."
- **PRD-JOB-003** — "I need to backtest candidate features/strategies with realistic frictions and zero look-ahead leakage, so a good-looking result actually means something."
- **PRD-JOB-004** — "I need statistically rigorous, multiple-testing-aware validation, so I don't fool myself into believing a result that is really noise."
- **PRD-JOB-005** — "I need every experiment to be reproducible, so I can trust a six-month-old conclusion as much as one from this morning."
- **PRD-JOB-006** — "I need a clear, honest way to know when I've reached support, falsification, or an inconclusive result — and to stop iterating once I have, rather than keep searching for a favorable number."

## 13. Product Scope

**In scope now (Phases 0–5, see [§33](#33-phase-plan)):** market data ingestion and validation; point-in-time-correct storage; Golden Ratio and baseline/placebo feature generation; event-driven backtesting; statistical validation and bias-prevention tooling; experiment reproducibility and tracking; research output generation (reports, conclusions).

**In scope later, contingent on earlier phases (Phases 6–8):** ML-based signal research (contingent on the rule-based research loop working and being trustworthy); paper trading (contingent on a strategy candidate surviving validation); a future API/UI (contingent on a real consumer need existing).

**Out of scope entirely for this document:** any implementation detail (schemas, endpoints, code structure) — see [§37](#37-traceability-to-architecture) for where that belongs once drafted.

## 14. Research Workflow

PHI's product requirement is to support the following workflow end-to-end, without permitting a shortcut around any stage:

```
Raw data
  → validation
  → point-in-time dataset
  → feature construction (Golden Ratio + baseline/placebo, in parallel, under identical conditions)
  → control construction
  → train / validation / test separation
  → backtesting (event-driven, realistic frictions)
  → walk-forward evaluation
  → statistical testing (with multiple-testing awareness)
  → robustness analysis
  → interpretation (support / inconclusive / falsified, per §8)
  → reproducible research record
```

- **PRD-WORKFLOW-001** — No stage in this workflow may be skipped for a result to be treated as a valid research conclusion; a result produced by skipping a stage (e.g., no walk-forward evaluation) is, at most, exploratory and must be labeled as such in research outputs ([§23](#23-research-outputs)).
- **PRD-WORKFLOW-002** — The workflow applies identically to Golden Ratio features and to every control category in [§18](#18-control--placebo-framework) — no stage may be applied more rigorously to one than to the other.

This workflow corresponds to the research loop defined architecturally in [SYSTEM_ARCHITECTURE.md §13](../03-architecture/SYSTEM_ARCHITECTURE.md#13-quantitative-research-architecture).

## 15. Data Requirements

- **PRD-DATA-001** — PHI must ingest historical price/volume (OHLCV) data, and any required reference data (e.g., corporate actions, delisting records), for a defined multi-asset universe. The final data provider is an open decision ([§35](#35-open-questions)) and is not fixed by this document.
- **PRD-DATA-002** — PHI must retain full history without destructive overwrites; corrected or restated data must be tracked alongside, not in place of, the original record.
- **PRD-DATA-003** — PHI must distinguish and be able to retrieve both adjusted and unadjusted price series, so that adjustment methodology is a visible, auditable choice rather than a silent default.
- **PRD-DATA-004** — PHI must detect and flag corporate actions (splits, dividends, mergers, ticker changes) that affect price continuity, rather than silently propagating discontinuities as if they were price moves.
- **PRD-DATA-005** — PHI must detect missing data (gaps) and must not silently interpolate or fill them without an explicit, logged, reversible policy.
- **PRD-DATA-006** — PHI must detect and reject or flag duplicate records.
- **PRD-DATA-007** — PHI must normalize all timestamps to a consistent, documented timezone convention and must be aware of each asset's trading calendar (sessions, holidays) rather than assuming continuous trading.
- **PRD-DATA-008** — PHI must track symbol changes (renames, re-listings) so that a time series is not silently discontinuous or silently merged across unrelated instruments.
- **PRD-DATA-009** — PHI must preserve delisted/inactive securities in its dataset rather than silently dropping them, so that survivorship bias ([§21](#21-bias-prevention-requirements)) can be measured and mitigated rather than structurally guaranteed.
- **PRD-DATA-010** — PHI must record data provenance (source, fetch timestamp, and — per [SYSTEM_ARCHITECTURE.md §12](../03-architecture/SYSTEM_ARCHITECTURE.md#12-time-semantics) — availability time distinct from event time) for every ingested record.
- **PRD-DATA-011** — PHI must validate volume data for consistency (e.g., non-negative, plausible relative to price move) as part of data validation, flagging rather than silently accepting implausible records.
- **PRD-DATA-012** — Selection of the final data provider, and of a survivorship-bias-free universe source, remain explicitly open decisions ([§35](#35-open-questions)) and must not be assumed or invented by this document or by downstream work.

## 16. Feature Engineering Requirements

- **PRD-FEATENG-001** — All feature computation (Golden Ratio and baseline/placebo alike) must use shared, leakage-safe computation infrastructure, so that no feature category receives implicit favorable treatment in how it accesses data.
- **PRD-FEATENG-002** — Every feature's observation window must end no later than the decision time it will be used at, per the time-ordering rule defined in [SYSTEM_ARCHITECTURE.md §12](../03-architecture/SYSTEM_ARCHITECTURE.md#12-time-semantics).
- **PRD-FEATENG-003** — Feature definitions must be versioned and deterministic: the same inputs, parameters, and code version must always produce the same output.
- **PRD-FEATENG-004** — Feature generation must record which version of which generator produced a given feature series, sufficient to trace any downstream result back to its exact generating logic.

## 17. Golden Ratio Feature Families

Golden Ratio / Fibonacci-derived features are a **research family of candidate mathematical transformations**, not a claimed or assumed trading indicator. No family listed here is asserted to be predictive; each is a candidate requiring the empirical process in [§14](#14-research-workflow) before any conclusion is drawn about it.

- **PRD-GRF-001** — φ-constant features: transformations referencing φ ≈ 1.6180339887 directly (e.g., price/time relationships expressed as multiples or fractions of φ).
- **PRD-GRF-002** — Reciprocal-φ features: transformations referencing 1/φ ≈ 0.6180339887.
- **PRD-GRF-003** — Power and inverse-power features: transformations referencing φ raised to integer or fractional powers (φ², φ⁻¹, etc.) and their inverses.
- **PRD-GRF-004** — Fibonacci-ratio features: transformations derived from ratios between terms of the Fibonacci sequence (which converge toward φ), including but not limited to conventional retracement/extension ratio sets.
- **PRD-GRF-005** — Fibonacci retracement relationships: price relationships to historical swing high/low retracement levels.
- **PRD-GRF-006** — Fibonacci extension relationships: projected price relationships beyond a prior move, based on standard Fibonacci ratios.
- **PRD-GRF-007** — φ-scaled distance features: normalized distances between observed price/time relationships and their nearest φ-derived reference value.
- **PRD-GRF-008** — φ-derived normalized relationships: ratio-based features scaled/normalized for comparability across instruments and regimes.
- **PRD-GRF-009** — Temporal φ transformations: relationships between the *timing* of market events (highs, lows, reversals) and φ-derived intervals, as distinct from price-based φ features.
- **PRD-GRF-010** — Regime-conditioned φ features: any of the above, explicitly conditioned on a market regime label, to test whether an effect (if any) is regime-dependent rather than universal.
- **PRD-GRF-011** — This list is illustrative and non-exhaustive; new families may be added, and existing families may be retired if falsified, without requiring a change to this document's scope or intent.
- **PRD-GRF-012** — No research output, commit message, documentation, or public communication may state or imply that any family in this section has been shown to be predictive prior to that family completing the full falsification process in [§8](#8-falsification-criteria).

This corresponds to the architecture's treatment of the same research family in [SYSTEM_ARCHITECTURE.md §14](../03-architecture/SYSTEM_ARCHITECTURE.md#14-golden-ratio-research-architecture).

## 18. Control / Placebo Framework

> **Canonical Phase 2 operationalization.** The concrete, frozen instantiation of this six-category framework for PHI's first φ feature — including how SYSTEM_ARCHITECTURE §15's "non-φ mathematical ratios" maps onto PRD-CONTROL-003 (as instantiation C2) — is specified in [ADR 0002](../18-decisions/0002-phase2-feature-and-control-design-lock.md) and the [feature & control contract](../05-mathematics/phi-retracement-feature-contract.md). The categories and IDs below are unchanged; the contract is the authoritative source for their exact construction.

The research question this platform answers is **not** "does φ make money?" It is: **does φ provide information that survives comparison against reasonable alternatives and statistical controls?** Every Golden Ratio feature evaluation must be accompanied by a comparison against all of the following, computed and evaluated under equivalent conditions:

| ID | Category | Purpose |
|---|---|---|
| PRD-CONTROL-001 | **A. Golden Ratio features** | The candidate under test (see [§17](#17-golden-ratio-feature-families)). |
| PRD-CONTROL-002 | **B. Random scalar controls** | Features with matched statistical shape (distribution, autocorrelation) but no φ-derived logic — tests whether an effect exceeds chance. |
| PRD-CONTROL-003 | **C. Fixed numerical benchmark controls** | Well-known, non-φ ratios (round numbers, arbitrary fixed percentages) — tests whether *any* ratio-based feature shows the effect, isolating whether φ specifically matters. |
| PRD-CONTROL-004 | **D. Conventional technical features** | Standard technical indicators — tests whether φ adds anything beyond what conventional technical analysis already captures. |
| PRD-CONTROL-005 | **E. Naive baselines** | Persistence/unconditional-mean-style forecasts — establishes the floor any feature must clear to be interesting at all. |
| PRD-CONTROL-006 | **F. Simple statistical baselines** | Basic statistical models (e.g., simple linear regression on price/volume) — a second, model-based floor distinct from the naive baseline. |

- **PRD-CONTROL-007** — All six categories must be evaluated on the same dataset, training window, test window, evaluation methodology, and transaction-cost assumptions within a given experiment. A difference in setup between categories invalidates the comparison for falsification purposes ([§8](#8-falsification-criteria)).
- **PRD-CONTROL-008** — A Golden Ratio feature family's evaluation is incomplete, and may not be used to claim support for H1, until it has been compared against all six categories for the relevant asset/period/regime set.
- **PRD-CONTROL-009** — Where a model (not just a raw feature) is being evaluated, the same model class and hyperparameter search budget must be used across all six categories.

This corresponds to the architecture's mandatory falsification/placebo architecture in [SYSTEM_ARCHITECTURE.md §15](../03-architecture/SYSTEM_ARCHITECTURE.md#15-falsification--placebo-architecture).

## 19. Backtesting Requirements

- **PRD-BACKTEST-001** — Backtesting must be event-driven: market data is replayed as discrete, time-ordered events, not evaluated via a pre-joined table that could implicitly contain future information.
- **PRD-BACKTEST-002** — Execution semantics must be deterministic: given the same inputs and configuration, a backtest run must produce the same result every time.
- **PRD-BACKTEST-003** — Every backtest must apply realistic, explicit, non-zero-by-default transaction costs (commissions).
- **PRD-BACKTEST-004** — Every backtest must apply realistic, explicit slippage assumptions between expected and realized fill price.
- **PRD-BACKTEST-005** — Where relevant to the instrument/frequency under test, backtests must apply realistic latency assumptions between decision and execution.
- **PRD-BACKTEST-006** — Backtests must enforce configurable position limits, not permit unbounded position sizing by default.
- **PRD-BACKTEST-007** — Backtests must maintain full cash accounting (available capital, realized/unrealized P&L) rather than an idealized "unlimited capital" assumption.
- **PRD-BACKTEST-008** — Backtests must maintain continuous portfolio state tracking (positions, exposure) through the full run, not just start/end snapshots.
- **PRD-BACKTEST-009** — No backtest may fill an order at a price or quantity the historical data does not support ("impossible fills" are prohibited).
- **PRD-BACKTEST-010** — No backtest may use same-bar information to both generate and execute a decision at a favorable price, except where explicitly documented as a realistic, justified assumption for the specific instrument/frequency.
- **PRD-BACKTEST-011** — Every backtest run must be reproducible from its logged configuration, code version, and data version ([§22](#22-experiment-reproducibility)).
- **PRD-BACKTEST-012** — A visually favorable equity curve or chart is explicitly **not** acceptable evidence of a working feature or strategy on its own; a result is only evidence once it has passed the statistical validation requirements in [§20](#20-statistical-validation-requirements).

This corresponds to [SYSTEM_ARCHITECTURE.md §16](../03-architecture/SYSTEM_ARCHITECTURE.md#16-backtesting-architecture).

## 20. Statistical Validation Requirements

PHI must compute, at minimum, the following categories of metrics as **evidence to be interpreted in context** — not as a checklist any single metric must individually clear:

- **PRD-VALIDATION-001** — Return-based metrics: total/annualized return, volatility.
- **PRD-VALIDATION-002** — Risk-adjusted metrics: Sharpe ratio, Sortino ratio, maximum drawdown.
- **PRD-VALIDATION-003** — Trading-behavior metrics: turnover, win rate, profit factor.
- **PRD-VALIDATION-004** — Predictive-quality metrics where appropriate: Information Coefficient, prediction error metrics (e.g., for regression-style model outputs).
- **PRD-VALIDATION-005** — No metric in PRD-VALIDATION-001 through 004 may be established as a universal hard success threshold (e.g., "Sharpe > 1.5") anywhere in this platform's requirements, documentation, or decision logic.

PHI must additionally support and require the following validation methodology before a conclusion may be drawn:

- **PRD-VALIDATION-006** — Out-of-sample testing on data not used in feature/model development for the given experiment.
- **PRD-VALIDATION-007** — Walk-forward testing across rolling/expanding windows.
- **PRD-VALIDATION-008** — Evaluation across multiple market regimes, not only in aggregate.
- **PRD-VALIDATION-009** — Cross-asset validation across more than one instrument, where the feature family is not asset-specific by design.
- **PRD-VALIDATION-010** — Placebo comparison against the full control set in [§18](#18-control--placebo-framework).
- **PRD-VALIDATION-011** — Permutation testing where appropriate, to check whether a result could plausibly arise from randomly permuted labels/features.
- **PRD-VALIDATION-012** — Multiple-testing awareness: the number of comparisons actually made (across feature families, parameterizations, and regimes) must be tracked and available for statistical interpretation.
- **PRD-VALIDATION-013** — Statistical corrections such as the Deflated Sharpe Ratio and Probability of Backtest Overfitting must be available and applied where appropriate as interpretive aids for results produced through iterative research — not as replacements for the judgment in [§8](#8-falsification-criteria).

This corresponds to [SYSTEM_ARCHITECTURE.md §17](../03-architecture/SYSTEM_ARCHITECTURE.md#17-validation-architecture).

## 21. Bias Prevention Requirements

| ID | Risk | Product Requirement |
|---|---|---|
| PRD-BIAS-001 | Confirmation bias | The platform must produce and retain evidence for outcomes that weaken or falsify H1 with the same completeness and visibility as evidence that supports it; no output format may suppress or de-emphasize negative results. |
| PRD-BIAS-002 | Hindsight selection | Feature families and evaluation parameters must be defined ([§17](#17-golden-ratio-feature-families)) before large-scale result review, not adjusted after seeing which parameterization "worked." |
| PRD-BIAS-003 | Cherry-picked assets | Evaluation must specify its asset universe in advance per experiment and must not silently narrow it post hoc to assets that produced favorable results. |
| PRD-BIAS-004 | Cherry-picked time periods | Evaluation must specify its time window(s) in advance and must include out-of-sample/walk-forward windows per [§20](#20-statistical-validation-requirements), not only the window that happened to look favorable. |
| PRD-BIAS-005 | Cherry-picked parameters | Every parameterization attempted must be logged ([§22](#22-experiment-reproducibility)), including unfavorable ones, so the full search is auditable rather than only the best result being visible. |
| PRD-BIAS-006 | Survivorship bias | The data universe must preserve delisted/inactive instruments where the provider supports it ([§15](#15-data-requirements)); sensitivity to survivorship effects must be checkable. |
| PRD-BIAS-007 | Look-ahead bias | No feature, signal, or execution may use information whose availability time is later than the decision time it is used at ([§16](#16-feature-engineering-requirements), [§19](#19-backtesting-requirements)). |
| PRD-BIAS-008 | Data / feature leakage | Feature computation must use shared, leakage-safe infrastructure ([§16](#16-feature-engineering-requirements)) rather than ad hoc per-feature data access. |
| PRD-BIAS-009 | Data snooping | The full history of experiments attempted, not only favorable ones, must be logged and available for review ([§22](#22-experiment-reproducibility)). |
| PRD-BIAS-010 | Repeated-testing bias | The number of tests/comparisons run must be tracked and factored into statistical interpretation ([§20](#20-statistical-validation-requirements), PRD-VALIDATION-012). |
| PRD-BIAS-011 | Regime overfitting | Regime-conditioned results must be evaluated and labeled as regime-specific, not silently generalized into an unconditional conclusion ([§17](#17-golden-ratio-feature-families), PRD-GRF-010). |
| PRD-BIAS-012 | Unrealistic transaction assumptions | Zero/favorable-by-default slippage or commissions are prohibited in backtesting ([§19](#19-backtesting-requirements), PRD-BACKTEST-003/004). |

This corresponds to [SYSTEM_ARCHITECTURE.md §18](../03-architecture/SYSTEM_ARCHITECTURE.md#18-bias-prevention-architecture).

## 22. Experiment Reproducibility

- **PRD-REPRO-001** — Every experiment (backtest, statistical evaluation, or model run) must be traceable to the exact code version (git commit), data version, and configuration that produced it.
- **PRD-REPRO-002** — Re-running a logged experiment against its recorded code/data/config version must reproduce the same result (determinism requirement).
- **PRD-REPRO-003** — Experiment logs must include unsuccessful and inconclusive experiments, not only favorable ones (see PRD-BIAS-005/009).
- **PRD-REPRO-004** — The runtime environment (dependency versions, and a container definition where used) must be pinned/versioned so that the same code version behaves the same way across machines.
- **PRD-REPRO-005** — Reproducibility must hold using the platform's current lightweight tooling in early phases and must not be assumed to require MLflow/DVC before those are actually adopted (see [§33](#33-phase-plan)).

This corresponds to [SYSTEM_ARCHITECTURE.md §21](../03-architecture/SYSTEM_ARCHITECTURE.md#21-reproducibility-architecture).

## 23. Research Outputs

- **PRD-OUTPUT-001** — Every completed experiment must produce a logged, structured record (configuration, data version, code version, computed metrics) sufficient to support [§22](#22-experiment-reproducibility).
- **PRD-OUTPUT-002** — Every φ-feature family that completes the process in [§14](#14-research-workflow) must produce a statistical evaluation report against the full control set in [§18](#18-control--placebo-framework).
- **PRD-OUTPUT-003** — Every φ-feature family must, at the conclusion of its evaluation, be assigned one of the outcome labels defined in [§30](#30-success-metrics)/[§8](#8-falsification-criteria): supported, inconclusive, or falsified — recorded, not left ambiguous.
- **PRD-OUTPUT-004** — Findings validated enough to be treated as durable conclusions should be promoted out of exploratory research material into the repository's research or decision records (`docs/04-research/`, `docs/18-decisions/`), consistent with existing repository convention.
- **PRD-OUTPUT-005** — Research outputs must state their own limitations (sample size, regime coverage, number of comparisons made) rather than presenting metrics without context.

## 24. Future ML Requirements

*(Phase 6 — not current scope; requirements below apply once this phase is entered.)*

- **PRD-ML-001** — Baseline, interpretable models must be evaluated before more complex models are considered, consistent with [§9](#9-product-goals) simplicity-first framing.
- **PRD-ML-002** — Any learned model must be evaluated under the same validation discipline as rule-based signals ([§20](#20-statistical-validation-requirements)) — no separate, weaker validation path for ML.
- **PRD-ML-003** — Deep learning approaches require documented justification (why simpler models are insufficient, and why sufficient data exists) before use — not a default choice.
- **PRD-ML-004** — No production-scale model-serving infrastructure is required for this phase; training and inference within the research process is sufficient.
- **PRD-ML-005** — Every trained model must record training data version, feature-set version, code version, and hyperparameters for reproducibility ([§22](#22-experiment-reproducibility)).

This corresponds to [SYSTEM_ARCHITECTURE.md §19](../03-architecture/SYSTEM_ARCHITECTURE.md#19-ml-architecture).

## 25. Future Paper-Trading Requirements

*(Phase 7 — not current scope; entry condition: a strategy candidate has survived the full validation/falsification process for at least one φ-feature family or baseline, per [§8](#8-falsification-criteria).)*

- **PRD-PAPER-001** — Any strategy considered for paper trading must remain broker-agnostic at the strategy/decision-logic level, so the same logic that was backtested is what gets paper-traded.
- **PRD-PAPER-002** — Paper trading must use simulated capital only; no real capital is placed at risk in this phase.
- **PRD-PAPER-003** — Paper-trading results must be logged with the same reproducibility discipline as backtests ([§22](#22-experiment-reproducibility)).
- **PRD-PAPER-004** — Broker selection for paper trading remains an open decision ([§35](#35-open-questions)) and is not fixed by this document.

This corresponds to [SYSTEM_ARCHITECTURE.md §24](../03-architecture/SYSTEM_ARCHITECTURE.md#24-paper-trading-boundary).

## 26. Future Product/UI Requirements

*(Phase 8 and beyond — not current scope; entry condition: a concrete consumer need exists, per [SYSTEM_ARCHITECTURE.md §29](../03-architecture/SYSTEM_ARCHITECTURE.md#29-architecture-decision-summary).)*

- **PRD-UI-001** — Any future UI must consume PHI only through the future API boundary, not access internal storage or research logic directly.
- **PRD-UI-002** — Any future UI must present research outcomes (including inconclusive/falsified results) with the same visibility as favorable ones — consistent with PRD-BIAS-001.
- **PRD-UI-003** — In the current phase, research notebooks serve as the interface; no dedicated UI is required or in scope.

This corresponds to [SYSTEM_ARCHITECTURE.md §23](../03-architecture/SYSTEM_ARCHITECTURE.md#23-api-boundary) and [§25](../03-architecture/SYSTEM_ARCHITECTURE.md#25-frontend-boundary).

## 27. Security / Data Integrity Requirements

- **PRD-SEC-001** — No credentials (data-provider API keys, broker credentials) may be hardcoded in source; secrets must be handled via environment configuration excluded from version control.
- **PRD-SEC-002** — Data integrity checks (validation, provenance, gap/duplicate detection per [§15](#15-data-requirements)) must run on every ingestion, not be optional or skippable in normal operation.
- **PRD-SEC-003** — Dependency versions must be pinned to reduce exposure to unreviewed upstream changes affecting research reproducibility.
- **PRD-SEC-004** — No authentication/authorization system is required while PHI has no network-facing interface (current phases); this requirement is revisited once an API boundary is activated ([§26](#26-future-productui-requirements)).

This corresponds to [SYSTEM_ARCHITECTURE.md §27](../03-architecture/SYSTEM_ARCHITECTURE.md#27-security).

## 28. Functional Requirements (Index)

The functional requirements of this product are the numbered requirements already defined in the sections below, indexed here rather than restated, to avoid duplicate or conflicting requirement text:

| Category | Section | Requirement IDs |
|---|---|---|
| Data | [§15](#15-data-requirements) | PRD-DATA-001 – PRD-DATA-012 |
| Feature Engineering | [§16](#16-feature-engineering-requirements) | PRD-FEATENG-001 – PRD-FEATENG-004 |
| Golden Ratio Feature Families | [§17](#17-golden-ratio-feature-families) | PRD-GRF-001 – PRD-GRF-012 |
| Control / Placebo Framework | [§18](#18-control--placebo-framework) | PRD-CONTROL-001 – PRD-CONTROL-009 |
| Backtesting | [§19](#19-backtesting-requirements) | PRD-BACKTEST-001 – PRD-BACKTEST-012 |
| Statistical Validation | [§20](#20-statistical-validation-requirements) | PRD-VALIDATION-001 – PRD-VALIDATION-013 |
| Bias Prevention | [§21](#21-bias-prevention-requirements) | PRD-BIAS-001 – PRD-BIAS-012 |
| Experiment Reproducibility | [§22](#22-experiment-reproducibility) | PRD-REPRO-001 – PRD-REPRO-005 |
| Research Outputs | [§23](#23-research-outputs) | PRD-OUTPUT-001 – PRD-OUTPUT-005 |
| Future ML *(Phase 6)* | [§24](#24-future-ml-requirements) | PRD-ML-001 – PRD-ML-005 |
| Future Paper Trading *(Phase 7)* | [§25](#25-future-paper-trading-requirements) | PRD-PAPER-001 – PRD-PAPER-004 |
| Future Product/UI *(Phase 8+)* | [§26](#26-future-productui-requirements) | PRD-UI-001 – PRD-UI-003 |
| Security / Data Integrity | [§27](#27-security--data-integrity-requirements) | PRD-SEC-001 – PRD-SEC-004 |

## 29. Non-Functional Requirements

- **PRD-NFR-001** — **Reproducibility.** Any research result must be re-derivable from its logged code, data, and configuration version ([§22](#22-experiment-reproducibility)).
- **PRD-NFR-002** — **Determinism.** Identical inputs and configuration must produce identical outputs across runs and machines.
- **PRD-NFR-003** — **Auditability.** The full history of experiments (including negative/unfavorable ones) must remain inspectable, not just the current "best" result.
- **PRD-NFR-004** — **Solo-developer maintainability.** The platform must remain operable and extensible by a single developer; complexity that requires a team to maintain is out of scope unless explicitly justified (see [§33](#33-phase-plan) entry conditions).
- **PRD-NFR-005** — **Local-first operation.** The platform must function fully on a single local machine without requiring cloud infrastructure, consistent with [SYSTEM_ARCHITECTURE.md §26 Phase 1](../03-architecture/SYSTEM_ARCHITECTURE.md#26-deployment-evolution).
- **PRD-NFR-006** — **No premature infrastructure.** Infrastructure (distributed processing, orchestration, feature stores) must not be introduced ahead of a demonstrated, current requirement — see [SYSTEM_ARCHITECTURE.md §29](../03-architecture/SYSTEM_ARCHITECTURE.md#29-architecture-decision-summary) for the specific deferred technologies and their triggers.
- **PRD-NFR-007** — **Data integrity.** No silent data mutation, interpolation, or correction may occur without an explicit, logged, reversible policy ([§15](#15-data-requirements)).
- **PRD-NFR-008** — **Documentation consistency.** Product and architecture documentation must not contradict one another; discrepancies must be corrected before either is treated as authoritative (see [§37](#37-traceability-to-architecture)).

## 30. Success Metrics

PHI's product success is defined independently of whether the Golden Ratio hypothesis turns out to be true — this separation is deliberate and load-bearing:

- **SUCCESS (research outcome):** The research framework demonstrates reproducible evidence for a φ-feature family that survives the full control comparison ([§18](#18-control--placebo-framework)) and validation discipline ([§20](#20-statistical-validation-requirements)), per PRD-FALSIFY-002.
- **INCONCLUSIVE (research outcome):** Evidence exists but is unstable, weak, regime-dependent, or has not yet been tested across enough assets/periods to be distinguished from chance, per PRD-FALSIFY-003.
- **FALSIFIED (research outcome):** A φ-feature family does not outperform its appropriate controls after rigorous validation, per PRD-FALSIFY-001. This is a **complete, legitimate, and valuable** outcome, not a project failure.
- **PRODUCT SUCCESS (independent of research outcome):** The platform reliably produces reproducible, auditable research — regardless of whether any given hypothesis survives. Concretely:
  - **PRD-SUCCESS-001** — At least one full research cycle (Phases 0–5) has been completed for at least one φ-feature family, ending in one of the three research-outcome labels above, not left in limbo.
  - **PRD-SUCCESS-002** — A previously logged experiment can be re-run from its recorded configuration and reproduces its original result (validates PRD-REPRO-002 in practice, not just as a stated requirement).
  - **PRD-SUCCESS-003** — The control framework ([§18](#18-control--placebo-framework)) has been exercised for every φ-feature family tested — no family has been evaluated in isolation.
  - **PRD-SUCCESS-004** — At least one negative or inconclusive result has been recorded and retained with the same visibility as any positive result, demonstrating PRD-BIAS-001 in practice.

## 31. Failure Conditions

Failure conditions are distinct from a **FALSIFIED** research outcome, which is not a failure (see [§30](#30-success-metrics)). PHI's product has failed if:

- **PRD-FAIL-001** — A previously logged experiment cannot be reproduced from its recorded code/data/config (violates PRD-REPRO-002).
- **PRD-FAIL-002** — A systematic, undetected leakage or look-ahead defect is discovered after results were treated as conclusive, invalidating those conclusions retroactively.
- **PRD-FAIL-003** — The platform cannot run a fair, controlled comparison between Golden Ratio features and the required control set ([§18](#18-control--placebo-framework)) — e.g., due to inconsistent evaluation conditions between categories.
- **PRD-FAIL-004** — Research is abandoned without a recorded outcome label (supported/inconclusive/falsified) for a feature family that was actively under test — leaving the question unanswered rather than answered negatively.
- **PRD-FAIL-005** — Documentation (this PRD, the architecture document, or research outputs) is found to assert that Golden Ratio features are proven predictive prior to completing the falsification process in [§8](#8-falsification-criteria).

## 32. Research Ethics / Scientific Integrity

- **PRD-ETHICS-001** — No p-hacking: parameters, assets, or time windows must not be adjusted after seeing results in order to manufacture a favorable outcome (see PRD-BIAS-002/003/004).
- **PRD-ETHICS-002** — No cherry-picking: all attempted experiments, favorable and unfavorable, are logged and remain visible (PRD-BIAS-005, PRD-REPRO-003).
- **PRD-ETHICS-003** — Negative and inconclusive results are reported with the same rigor and visibility as positive ones (PRD-BIAS-001, PRD-SUCCESS-004).
- **PRD-ETHICS-004** — No causal claims are made from correlational backtest results; language in research outputs must reflect statistical association and its limitations, not causation.
- **PRD-ETHICS-005** — No public or internal communication (documentation, commit messages, reports) may describe Golden Ratio features as "proven," "validated," or "working" ahead of the falsification process in [§8](#8-falsification-criteria) concluding that a specific family is supported.
- **PRD-ETHICS-006** — Assumptions, limitations, and open questions ([§35](#35-open-questions)) are stated explicitly in research outputs rather than left implicit.

## 33. Phase Plan

This PRD's phases are a finer-grained, research-delivery-oriented breakdown that nests within the five deployment phases already defined in [SYSTEM_ARCHITECTURE.md §26](../03-architecture/SYSTEM_ARCHITECTURE.md#26-deployment-evolution) (see the mapping in [§37](#37-traceability-to-architecture)). No phase below introduces live trading, dashboards, Kubernetes, distributed streaming, microservices, or high-frequency infrastructure ahead of its stated entry condition.

- **Phase 0 — Research Specification.** Deliverable: this PRD and the associated architecture document, reviewed. Entry condition: none (current phase). Explicitly deferred: everything below.
- **Phase 1 — Data Foundation.** Deliverable: ingestion, validation, and point-in-time-correct storage satisfying [§15](#15-data-requirements). Entry condition: Phase 0 reviewed.
- **Phase 2 — Golden Ratio Feature Laboratory.** Deliverable: feature engineering infrastructure and the first φ-feature families plus their matched controls, satisfying [§16](#16-feature-engineering-requirements)–[§18](#18-control--placebo-framework). Entry condition: Phase 1 complete.
- **Phase 3 — Event-Driven Backtester.** Deliverable: a backtesting engine satisfying [§19](#19-backtesting-requirements). Entry condition: Phase 2 complete (features must exist to backtest).
- **Phase 4 — Scientific Validation.** Deliverable: statistical validation and bias-prevention tooling satisfying [§20](#20-statistical-validation-requirements)–[§21](#21-bias-prevention-requirements). Entry condition: Phase 3 complete.
- **Phase 5 — Reproducible Experiment Platform.** Deliverable: experiment tracking/reproducibility tooling satisfying [§22](#22-experiment-reproducibility), sufficient to complete a full research cycle for at least one φ-feature family and reach a labeled outcome ([§8](#8-falsification-criteria)). Entry condition: Phase 4 complete.
- **Phase 6 — ML Research.** Deliverable: [§24](#24-future-ml-requirements). Entry condition: at least one full Phase 0–5 research cycle completed, and a documented reason classical/rule-based approaches are insufficient.
- **Phase 7 — Paper Trading.** Deliverable: [§25](#25-future-paper-trading-requirements). Entry condition: a strategy candidate has survived the falsification process ([§8](#8-falsification-criteria), PRD-FALSIFY-002).
- **Phase 8 — Production Platform.** Deliverable: [§26](#26-future-productui-requirements) and any live-capital operation. Entry condition: sufficient evidence from Phase 7 paper-trading performance to justify real capital, evaluated with the same non-hard-threshold discipline as [§20](#20-statistical-validation-requirements).

## 34. Acceptance Criteria

A phase in [§33](#33-phase-plan) is accepted as complete when:

- **PRD-ACCEPT-001** — All requirement IDs whose section maps to that phase (per [§33](#33-phase-plan)) are demonstrably satisfied, not merely documented.
- **PRD-ACCEPT-002** — For Phase 1: a reference dataset has passed validation ([§15](#15-data-requirements)) with logged data-quality results, and point-in-time correctness (availability time vs. decision time) is demonstrated on at least one worked example.
- **PRD-ACCEPT-003** — For Phase 2: at least one Golden Ratio feature family and its full matched control set ([§18](#18-control--placebo-framework)) can be generated deterministically from the same input dataset.
- **PRD-ACCEPT-004** — For Phase 3: a backtest run is reproducible (PRD-BACKTEST-011) and demonstrably rejects at least one deliberately-constructed impossible-fill or look-ahead scenario in testing.
- **PRD-ACCEPT-005** — For Phase 4: a walk-forward, multi-regime, placebo-compared evaluation has been run end-to-end for at least one φ-feature family.
- **PRD-ACCEPT-006** — For Phase 5: a previously logged experiment has been successfully reproduced from its recorded configuration (validates PRD-SUCCESS-002).
- **PRD-ACCEPT-007** — For Phase 6–8: acceptance criteria are deferred and will be defined when each phase is entered, consistent with not inventing requirements for capabilities not yet justified.

## 35. Open Questions

These mirror and do not duplicate the architectural open questions in [SYSTEM_ARCHITECTURE.md §32](../03-architecture/SYSTEM_ARCHITECTURE.md#32-open-architecture-questions); product-level open questions are:

- **PRD-OPEN-001** — Final data provider selection (affects [§15](#15-data-requirements) implementation, not this document's requirements).
- **PRD-OPEN-002** — Survivorship-bias-free universe source (affects PRD-DATA-009/PRD-BIAS-006 implementation).
- **PRD-OPEN-003** — The exact initial asset universe (which instruments, how many, which asset classes) to be tested in Phase 2 onward.
- **PRD-OPEN-004** — Exact walk-forward window sizing and regime-labeling methodology — left to research design, not fixed here.
- **PRD-OPEN-005** — The final, complete enumeration of φ-feature family parameterizations (the families in [§17](#17-golden-ratio-feature-families) are illustrative, not exhaustive).
- **PRD-OPEN-006** — Whether/when Phase 6 (ML) is justified — deferred to a documented decision at that time (PRD-ML-003).
- **PRD-OPEN-007** — Future broker selection for Phase 7 paper trading.
- **PRD-OPEN-008** — Exact deployment target for Phase 7+ (remains local vs. moves to cloud).

## 36. Risks and Mitigations

- **Solo-developer bandwidth risk.** A single developer maintaining data, research, and engineering work risks burnout or stalled progress. *Mitigation:* phase entry conditions ([§33](#33-phase-plan)) keep scope bounded per phase; non-functional requirement PRD-NFR-004 explicitly prioritizes maintainability.
- **Scope creep into premature infrastructure.** Temptation to build enterprise-scale tooling before it's needed. *Mitigation:* PRD-NFR-006 and the architecture's explicit deferral list ([SYSTEM_ARCHITECTURE.md §29](../03-architecture/SYSTEM_ARCHITECTURE.md#29-architecture-decision-summary)) provide a standing reference to push back against this.
- **Confirmation bias despite safeguards.** Even with placebo controls, a motivated researcher can unconsciously favor confirming evidence. *Mitigation:* PRD-ETHICS-001–006 and mandatory negative-result logging (PRD-REPRO-003, PRD-BIAS-001) create process friction against this, though no process fully eliminates it.
- **Data cost/access risk.** A suitable, affordable, survivorship-bias-free data source may not be readily available to a solo developer. *Mitigation:* provider selection is explicitly left open (PRD-OPEN-001) rather than assumed, so this is evaluated with real constraints in view rather than invented ones.
- **Motivation risk on a null result.** A researcher may be tempted to abandon or under-report a falsified hypothesis. *Mitigation:* [§30](#30-success-metrics) explicitly defines product success independent of research outcome, so a falsified hypothesis with a complete, reproducible research record is a full success by this document's own definition.
- **External credibility risk.** Without transparent methodology, any result (positive or negative) may not be trusted by outside reviewers. *Mitigation:* [§22](#22-experiment-reproducibility) and [§23](#23-research-outputs) require the research record to be reproducible and auditable by design, not only by the original researcher.

## 37. Traceability to Architecture

This PRD's requirements are downstream of, and must remain consistent with, [SYSTEM_ARCHITECTURE.md](../03-architecture/SYSTEM_ARCHITECTURE.md). All section references below point to sections that exist in that document as committed.

| PRD Section | Requirement IDs | Architecture Section |
|---|---|---|
| §14 Research Workflow | PRD-WORKFLOW-* | [§13 Quantitative Research Architecture](../03-architecture/SYSTEM_ARCHITECTURE.md#13-quantitative-research-architecture) |
| §15 Data Requirements | PRD-DATA-* | [§9.1–9.3 Data Ingestion / Validation / Storage](../03-architecture/SYSTEM_ARCHITECTURE.md#9-major-system-modules), [§12 Time Semantics](../03-architecture/SYSTEM_ARCHITECTURE.md#12-time-semantics) |
| §16 Feature Engineering Requirements | PRD-FEATENG-* | [§9.4 Feature Engineering](../03-architecture/SYSTEM_ARCHITECTURE.md#94-feature-engineering), [§12 Time Semantics](../03-architecture/SYSTEM_ARCHITECTURE.md#12-time-semantics) |
| §17 Golden Ratio Feature Families | PRD-GRF-* | [§14 Golden Ratio Research Architecture](../03-architecture/SYSTEM_ARCHITECTURE.md#14-golden-ratio-research-architecture) |
| §18 Control / Placebo Framework | PRD-CONTROL-* | [§15 Falsification / Placebo Architecture](../03-architecture/SYSTEM_ARCHITECTURE.md#15-falsification--placebo-architecture) |
| §19 Backtesting Requirements | PRD-BACKTEST-* | [§16 Backtesting Architecture](../03-architecture/SYSTEM_ARCHITECTURE.md#16-backtesting-architecture) |
| §20 Statistical Validation Requirements | PRD-VALIDATION-* | [§17 Validation Architecture](../03-architecture/SYSTEM_ARCHITECTURE.md#17-validation-architecture) |
| §21 Bias Prevention Requirements | PRD-BIAS-* | [§18 Bias Prevention Architecture](../03-architecture/SYSTEM_ARCHITECTURE.md#18-bias-prevention-architecture) |
| §22 Experiment Reproducibility | PRD-REPRO-* | [§21 Reproducibility Architecture](../03-architecture/SYSTEM_ARCHITECTURE.md#21-reproducibility-architecture) |
| §24 Future ML Requirements | PRD-ML-* | [§19 ML Architecture](../03-architecture/SYSTEM_ARCHITECTURE.md#19-ml-architecture) |
| §25 Future Paper-Trading Requirements | PRD-PAPER-* | [§24 Paper Trading Boundary](../03-architecture/SYSTEM_ARCHITECTURE.md#24-paper-trading-boundary) |
| §26 Future Product/UI Requirements | PRD-UI-* | [§23 API Boundary](../03-architecture/SYSTEM_ARCHITECTURE.md#23-api-boundary), [§25 Frontend Boundary](../03-architecture/SYSTEM_ARCHITECTURE.md#25-frontend-boundary) |
| §27 Security / Data Integrity Requirements | PRD-SEC-* | [§27 Security](../03-architecture/SYSTEM_ARCHITECTURE.md#27-security) |
| §33 Phase Plan | — | [§26 Deployment Evolution](../03-architecture/SYSTEM_ARCHITECTURE.md#26-deployment-evolution) — PRD Phases 0–2 nest within Architecture Phase 1 (Local Research); PRD Phases 3–5 span Architecture Phase 1–2 (Local Research → Reproducible Research Platform); PRD Phase 6 nests within Architecture Phase 2; PRD Phase 7 corresponds to Architecture Phase 3 (Paper Trading); PRD Phase 8 corresponds to Architecture Phase 4 (Production). |
| §35 Open Questions | PRD-OPEN-* | [§32 Open Architecture Questions](../03-architecture/SYSTEM_ARCHITECTURE.md#32-open-architecture-questions) |
| §36 Risks and Mitigations | — | [§30 Architecture Risks](../03-architecture/SYSTEM_ARCHITECTURE.md#30-architecture-risks), [§31 Scientific Risks](../03-architecture/SYSTEM_ARCHITECTURE.md#31-scientific-risks) |

No requirement in this document introduces a technology, module, or capability that contradicts [SYSTEM_ARCHITECTURE.md §29 Architecture Decision Summary](../03-architecture/SYSTEM_ARCHITECTURE.md#29-architecture-decision-summary).

## 38. Definition of Done

This PRD is considered complete enough for stakeholder review when:

- Every section from [§1](#1-document-control) through [§37](#37-traceability-to-architecture) contains real content — no remaining placeholder markers outside of [§35 Open Questions](#35-open-questions), which is deliberately left open by design.
- No statement in this document asserts that Golden Ratio / Fibonacci-derived features have been proven predictive; all such references are framed as an unproven, testable research family (per [§17](#17-golden-ratio-feature-families), PRD-GRF-012).
- No requirement establishes a hard universal profitability or statistical threshold as an automatic success gate (per PRD-VALIDATION-005).
- All requirement IDs are unique, and none are duplicated across sections.
- All relative Markdown links resolve to files that exist in the repository as of this document's last update.
- Every reference to [SYSTEM_ARCHITECTURE.md](../03-architecture/SYSTEM_ARCHITECTURE.md) points to a section that actually exists in that document, not an invented one.
- No fabricated data-provider claim, research result, or benchmark appears anywhere in the document.
- No implementation detail (schemas, endpoints, source code) has been introduced; such detail is deferred to the documents named in [§37](#37-traceability-to-architecture).
- The document has been reviewed by at least one stakeholder (per `docs/REFERENCE/MILESTONES.md` Phase B) and its `Status` field updated from "Draft — Pending Review" accordingly.
