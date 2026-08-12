# PHI Next Steps

**Status:** Canonical roadmap for Project PHI. (`docs/19-roadmap/README.md` is a navigation index that points here — it does not duplicate this content.) **Last Updated:** 2026-08-12.

## Done

- System architecture and PRD drafted and internally consistent (`docs/02-project/PHI_PRD.md`, `docs/03-architecture/SYSTEM_ARCHITECTURE.md`, `docs/03-architecture/DATABASE_ARCHITECTURE.md`).
- **Phase 0 — Engineering Foundation:** `pyproject.toml` (uv/hatchling, pytest/ruff/mypy), `src/phi/{config,logging,cli}.py`. Tested, lint-clean, type-checked.
- **Phase 1 — Data Foundation** (`src/phi/data/`): time semantics + T-1 information barrier (`time.py`), domain schemas (`schemas.py`), a minimal weekday trading calendar (`calendar.py`), Data Validation — gap/duplicate/monotonicity/volume checks (`validation.py`), a synthetic (test-only, clearly labeled) OHLCV provider (`providers/synthetic.py`), a local Parquet-backed `PriceBarRepository` (`storage.py`, see [ADR 0001](../18-decisions/0001-phase1-local-storage-implementation.md) for why Parquet instead of PostgreSQL/TimescaleDB in this environment), ingestion orchestration (`ingestion.py`), and a point-in-time worked example satisfying PRD-ACCEPT-002 (`tests/data/test_point_in_time_worked_example.py`).
- **Phase 0.5 — Design Lock:** the canonical first φ feature and its six-category matched control set frozen to implementation-grade precision — [ADR 0002](../18-decisions/0002-phase2-feature-and-control-design-lock.md) and the [feature & control contract](../05-mathematics/phi-retracement-feature-contract.md).
- **Phase 2 — Golden Ratio Feature Laboratory** (`src/phi/features/`): implemented exactly to the frozen contract above and its [acceptance gate](../05-mathematics/phi-retracement-feature-contract.md#12-phase-2-acceptance-gate) — shared leakage-safe pipeline (`pipeline.py`), the canonical φ retracement feature (`candidate.py`), the full six-category matched control set (`controls.py`, `engine.py`). Generation + validation only, as scoped: no labels, no backtest, no real-market data, no predictive claim made or implied (contract §0A, §9–§10).
- **Feature-authority decision recorded** ([ADR 0003](../18-decisions/0003-phase2-external-review-nogo-and-feature-authority.md), 2026-08-12, Option B): the rolling-window `p_t` feature is authoritative; the excursion-retracement arithmetic (`features/retracement.py`) is retained as **Phase-4 guidance only**. Blockers 1–4 remain **unfrozen** — confirmatory φ analysis stays NO-GO.
- **Science-neutral experiment infrastructure** (`src/phi/experiment/`): immutable content-hashed pre-registration manifest with an `is_confirmatory_ready()` gate that enforces the NO-GO in code, exclusion accounting, and code/environment provenance capture.
- **Phase 4 — confirmatory methodology** (`src/phi/phase4/`): implemented exactly to the now-frozen Phase-4 Specification (three-point extrema anchor, Δ_φ vs matched constants, stationary-bootstrap inference, Holm multiplicity, null-DGP calibration + power, replication separation, fail-closed gate). **Confirmatory execution is NOT authorized** — blocked in code pending the numerical pre-registration and validation gates. Documented blocker: the estimand as specified is not null-calibrated (Jensen bias); see [Phase-4 contract](../05-mathematics/phi-phase4-scientific-contract.md) §7 and [readiness report](../21-releases/PHI_PHASE4_READINESS.md).

**Project-wide test status: full suite passing at ~98% branch coverage, Ruff- and mypy-clean. Run `uv run pytest` for the live count (see [REPRODUCIBILITY.md](../../REPRODUCIBILITY.md)).**

## Not Done / Explicitly Deferred

- No real market-data provider is wired up (PRD-OPEN-001 remains open by design) — everything validated so far uses clearly-labeled synthetic fixtures, never presented as market evidence.
- `InstrumentAlias`, `CorporateAction`, and a real exchange-specific `TradingCalendar` are not modeled yet (Phase 1 used a minimal weekday-only calendar as a documented simplification).
- PostgreSQL/TimescaleDB is not stood up (no local Postgres, Docker daemon unavailable in this environment) — see ADR 0001.
- Phase 2's cross-implementation reproducibility criterion (contract §5A) is asserted only as single-implementation determinism plus hand-verified worked examples — no second independent implementation exists yet to compare against. Category F's non-finite-output guard (contract §6 case 8) is implemented but, unlike the candidate's equivalent guard, not exercised by a forced-overflow test (believed, not proven, structurally unreachable). See the acceptance-gate status note in the contract for detail.
- No predictive, statistical, or market-efficacy claim has been made about the φ feature — Phase 2 establishes construction, temporal validity, reproducibility, and matched-control generation only (contract §0A).

## Next Milestone — Phase 3: Event-Driven Backtester

Per PRD §19 (backtesting requirements) / PRD's phase plan §33. **Entry condition (Phase 2 complete) is now satisfied — Phase 3 itself has not been started.** No backtest engine, order/fill simulation, or labeled evaluation exists in this repository yet.

- Deliverable: a backtesting engine satisfying PRD §19, operating on the Phase 2 features (candidate + six controls) without reopening their frozen definitions.
- Must not begin any predictive/statistical claim work out of order — PRD-ACCEPT-004 (reproducible backtest, demonstrably rejects at least one deliberately-constructed impossible-fill/look-ahead scenario) gates Phase 3 completion; PRD-ACCEPT-005's walk-forward/placebo-compared evaluation is Phase 4, not Phase 3.
- Do not select a real market-data provider opportunistically mid-implementation — PRD-OPEN-001 is a standing open decision, not something to resolve as a side effect of backtester work.
