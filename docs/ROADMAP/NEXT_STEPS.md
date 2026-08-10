# PHI Next Steps

**Status:** Canonical roadmap for Project PHI. (`docs/19-roadmap/README.md` is a navigation index that points here — it does not duplicate this content.) **Last Updated:** 2026-08-10.

## Done

- System architecture and PRD drafted and internally consistent (`docs/02-project/PHI_PRD.md`, `docs/03-architecture/SYSTEM_ARCHITECTURE.md`, `docs/03-architecture/DATABASE_ARCHITECTURE.md`).
- **Phase 0 — Engineering Foundation:** `pyproject.toml` (uv/hatchling, pytest/ruff/mypy), `src/phi/{config,logging,cli}.py`. Tested, lint-clean, type-checked.
- **Phase 1 — Data Foundation** (`src/phi/data/`): time semantics + T-1 information barrier (`time.py`), domain schemas (`schemas.py`), a minimal weekday trading calendar (`calendar.py`), Data Validation — gap/duplicate/monotonicity/volume checks (`validation.py`), a synthetic (test-only, clearly labeled) OHLCV provider (`providers/synthetic.py`), a local Parquet-backed `PriceBarRepository` (`storage.py`, see [ADR 0001](../18-decisions/0001-phase1-local-storage-implementation.md) for why Parquet instead of PostgreSQL/TimescaleDB in this environment), ingestion orchestration (`ingestion.py`), and a point-in-time worked example satisfying PRD-ACCEPT-002 (`tests/data/test_point_in_time_worked_example.py`). 77 tests passing, 97% coverage, ruff/mypy clean.

## Not Done / Explicitly Deferred

- No real market-data provider is wired up (PRD-OPEN-001 remains open by design) — everything validated so far uses clearly-labeled synthetic fixtures, never presented as market evidence.
- `InstrumentAlias`, `CorporateAction`, and a real exchange-specific `TradingCalendar` are not modeled yet (Phase 1 used a minimal weekday-only calendar as a documented simplification).
- PostgreSQL/TimescaleDB is not stood up (no local Postgres, Docker daemon unavailable in this environment) — see ADR 0001.

## Next Milestone — Phase 2: Golden Ratio Feature Laboratory

- Shared, leakage-safe feature-computation primitives (rolling windows, normalization) built on top of `phi.data.time`'s T-1 barrier.
- The first Golden Ratio/Fibonacci feature family (`PRD-GRF-*`, PRD §17) plus its full matched control set (`PRD-CONTROL-*`, PRD §18) — this is a hard requirement of Phase 2, not a follow-up.
- Leakage tests proving feature computation cannot access future observations, following the same TDD discipline as Phase 1.
- Entry condition satisfied: Phase 1 (data foundation) is complete and tested.
