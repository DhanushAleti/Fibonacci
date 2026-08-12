# PHI Research & Development Log

Canonical, chronological research and development log for Project PHI. This consolidates entries that were previously split across three locations — `docs/logs/`, `docs/research/`, and `docs/04-research/RESEARCH_LOG.md` — into one running log. All content below is preserved verbatim from those sources; each entry notes its original location for traceability. New entries should be appended below in chronological order.

## 2026-08-05 — Development Log

*(originally `docs/logs/2026-08-05.md`)*

### Work Completed

- Continued PHI system planning.
- Improved documentation structure.
- Reviewed architecture and roadmap.

### Tomorrow

- Continue system architecture.
- Begin backend implementation.
- Define database schema.
- Added GitHub contribution workflow.

## 2026-08-08 — Research Log

*(originally `docs/04-research/RESEARCH_LOG.md`)*

### Repository State

- Product requirements are defined.
- System architecture is substantially drafted.
- Research protocol is established.
- Current research direction is focused on falsifiable evaluation of
  Golden Ratio/Fibonacci-derived market features.

### Next Research Priorities

1. Define the canonical dataset contract.
2. Define feature-generation rules without look-ahead bias.
3. Establish baseline and placebo implementations.
4. Define the minimum backtesting and statistical evaluation protocol.
5. Build reproducible experiments only after these contracts are fixed.

## 2026-08-09 — Research Log

*(originally `docs/research/2026-08-09.md`)*

### Focus

Continued documenting the PHI AcademicOS architecture and implementation direction.

### Progress

- Reviewed the current documentation structure.
- Continued separating product requirements from implementation details.
- Maintained the repository as the source of truth for PHI development decisions.

### Next

- Continue backend integration work.
- Expand academic data ingestion documentation.
- Keep implementation decisions traceable through version-controlled documentation.

## 2026-08-11 — Development Log

### Focus

Implemented Phase 2 (`src/phi/features/`) to the frozen [feature & control contract](../05-mathematics/phi-retracement-feature-contract.md) — the canonical φ retracement feature and its full six-category matched control set — following the design lock recorded in [ADR 0002](../18-decisions/0002-phase2-feature-and-control-design-lock.md).

### Progress

- `phi.features.pipeline`: the shared §2 computation (eligibility filter, prior window, prior range, position-in-range) used identically by the candidate and every control, plus input-sequence validation (duplicate/non-monotonic/mixed-symbol rejection per §6 case 5 and the §1 ordering precondition).
- `phi.features.candidate`: Category A, `f_A(t) = |p_t - g_phi|`.
- `phi.features.controls`: C1, C2 (constant-swap benchmarks), D (position baseline), E (naive persistence), F (range-normalized OLS slope, §7.2), and B (seeded circular rotation placebo, §7.1).
- `phi.features.engine`: whole-series computation producing one aligned row per bar, keyed by `(symbol, event_time, availability_time)`.
- Full §11 test contract: mathematical worked examples, single-implementation determinism, temporal-leakage invariants, window-boundary exactness, insufficient-history and late-availability NULL handling, invalid-input rejection, a real (non-mocked) non-finite-output guard for `p_t`, Tier-1/Tier-2 matching parity, parameter parity, and metamorphic invariants (non-negativity, scale-invariance, translation-invariance, swap-constant identities) — 150 tests passing project-wide (73 new), 98% coverage, ruff/mypy clean.

### Scope boundary held

No real-market data, no labels, no backtest, no statistical/predictive claim — per the contract's §0A scientific claim boundary, this establishes deterministic construction, temporal validity, reproducibility, and matched-control generation only. See the acceptance-gate status note in the [feature & control contract](../05-mathematics/phi-retracement-feature-contract.md#12-phase-2-acceptance-gate) for the two honest caveats (cross-implementation reproducibility not yet applicable with a single implementation; Category F's non-finite-output guard is unexercised, believed but not proven unreachable).

### Next

- Phase 3 — Event-Driven Backtester (PRD §19). Entry condition (Phase 2 complete) is now satisfied; Phase 3 itself has not been started.
- Real market-data provider selection remains open (PRD-OPEN-001).

## 2026-08-12 — Development Log (external-review remediation + ship)

### Focus

Turned the three external reviews (Authoritative Contract, Perplexity, Gemini), the independent repository audit, and the hostile final peer review into a concrete, scientifically-bounded ship — fixing flagged defects and recording decisions **without** inventing any of the blocked science.

### Progress

- Recorded the **feature-authority decision** ([ADR 0003](../18-decisions/0003-phase2-external-review-nogo-and-feature-authority.md) → Accepted, Option B): rolling-window `p_t` authoritative; excursion arithmetic retained as Phase-4 guidance. Updated `features/__init__.py` and `retracement.py` from "open decision" to "decided."
- Verified the prior session's three HIGH code fixes are present and green: non-finite price rejection at construction (`allow_inf_nan=False`), a strengthened confirmatory-readiness gate (multiplicity / confidence level / controls now required), and a real cross-process determinism test.
- Added **code + environment provenance** to the manifest (`code_version`, `environment_lock_hash`) plus a reproducible `phi.experiment.provenance` capture helper (audit I-5; contract §26, §36).
- Enforced **window ≥ 2** at the pipeline boundary, making Category F's zero-denominator edge unrepresentable (audit I-11).
- Corrected stale/contradictory documentation (README no longer claims "no application code"; test counts de-brittled), added `REPRODUCIBILITY.md` and `CONTRIBUTING.md`, and committed the previously-uncommitted Phase-2 implementation to a branch (audit I-4).

### Scope boundary held

No anchor algorithm, no `ε_φ`, no primary estimand, no inference layer, no φ claim. The reviews' NO-GO on confirmatory analysis stands and is enforced in code by `ExperimentManifest.is_confirmatory_ready()`. What shipped is construction + reproducibility + honest documentation — **not** scientific validation.

### Next

- Blockers 1–4 (causal anchor algorithm, `ε_φ`, primary estimand, dependence-aware inference) remain the gate to any Phase-4 confirmatory experiment — a human decision, not a coding task.

## 2026-08-12 — Development Log (Phase 4 confirmatory methodology)

### Focus

Implemented the now-frozen Phase-4 confirmatory methodology (Chief Scientific Methodologist: GO-with-conditions; Final Arbiter: NO-GO to *run* until gates pass) exactly, without reinterpreting or optimizing for φ. New package `src/phi/phase4/`.

### Progress

- Anchor (`extrema.py`): deterministic three-point extrema with the plateau-midpoint parity rule; excursion pairing. Retracement (`retracement.py`): per-excursion terminal `R`, `R∈[0,1]` primary, `R>1` overshoot reported. Estimand (`estimand.py`): paired `Z_i`, `Δ̂_φ`, secondary landscape/rank. Inference (`inference.py`): Politis–White automatic block length + Politis–Romano stationary bootstrap, percentile CI, one-sided p-value with MC error. Multiplicity (`multiplicity.py`): Holm. Null-DGP suite + calibration + power (`nulldgp.py`, `calibration.py`). Replication separation (`datasets.py`), four-outcome verdict (`verdict.py`), and a fail-closed confirmatory gate (`registration.py`, `pipeline.py`). 83 methodology tests; project-wide gates green.

### Honest finding (locked as a regression)

The primary estimand *as specified* is **not null-calibrated**: by Jensen's inequality, symmetric controls make `Δ_φ ≥ 0` on pure noise, so the empirical false-positive rate is ≈ 1.0 under IID/random-walk/AR nulls. It fails the contract's own hard gate (§XLIV), which correctly keeps confirmatory analysis blocked. This is surfaced, not hidden or "fixed"; resolving it (e.g., testing `Δ̂_φ` against its null/surrogate distribution, or a convexity-corrected estimand) is a methodologist decision.

### Scope boundary held

No real data, no confirmatory run, no φ claim. Numerical pre-registration (`C`, `δ_min`, Dataset A/B, block-length config, seed) remains for a human to freeze; the code fails closed until then.

### Next

- Methodologist: resolve the estimand null-calibration finding; then freeze the numerical pre-registration and pass the validation gates.

---

*New entries: append a `## YYYY-MM-DD — <Research Log | Development Log>` section below, following the format above.*
