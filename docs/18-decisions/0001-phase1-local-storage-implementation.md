# 0001 — Phase 1 Market Data Storage: Local Parquet Repository Behind the Storage Interface

**Status:** Accepted
**Last Updated:** 2026-08-10

## Context

[SYSTEM_ARCHITECTURE.md §22](../03-architecture/SYSTEM_ARCHITECTURE.md#22-storage-architecture) and [DATABASE_ARCHITECTURE.md](../03-architecture/DATABASE_ARCHITECTURE.md) commit to PostgreSQL + the TimescaleDB extension as the canonical Market Data Storage engine (module 3, [SYSTEM_ARCHITECTURE.md §9.3](../03-architecture/SYSTEM_ARCHITECTURE.md#93-market-data-storage)). That decision is not being revisited here.

The current development environment has neither a running PostgreSQL/TimescaleDB instance nor a running Docker daemon available to stand one up (`psql`/`pg_ctl`/`postgres` are not installed; `docker` the CLI is present but its daemon is not running, and pulling images would require network access this session should not assume). Standing up a database server is itself infrastructure work with its own risk (credentials, a running service, data durability) that [PHI_PRD.md PRD-NFR-006](../02-project/PHI_PRD.md#29-non-functional-requirements) and [SYSTEM_ARCHITECTURE.md §5](../03-architecture/SYSTEM_ARCHITECTURE.md#5-architectural-principles) principle 5 caution against introducing ahead of a concrete, current requirement — and Phase 1 has no real data volume yet to justify it.

## Decision

Implement Market Data Storage (module 3) behind a small repository interface (`PriceBarRepository` protocol in `src/phi/data/storage.py`) whose contract — append validated `PriceBar` records, query by `(instrument, time range)`, never destructively overwrite — matches exactly what [DATABASE_ARCHITECTURE.md §7.2](../03-architecture/DATABASE_ARCHITECTURE.md#72-time-series-entities-timescaledb-hypertables) and [§8 Indexing Strategy](../03-architecture/DATABASE_ARCHITECTURE.md#8-indexing-strategy) already specify a TimescaleDB-backed implementation would need to satisfy.

Ship one concrete implementation for Phase 1: `ParquetPriceBarRepository`, a local-first, content-hashed, append-only Parquet store queried via Polars. This is not a new architectural decision — Parquet is already a named, approved component of the storage architecture ([SYSTEM_ARCHITECTURE.md §22](../03-architecture/SYSTEM_ARCHITECTURE.md#22-storage-architecture), [§29](../03-architecture/SYSTEM_ARCHITECTURE.md#29-architecture-decision-summary)) — this ADR only elevates it from "portable exchange/versioning format" to "the Phase 1 storage backend behind the module-3 interface," specifically because the intended primary backend is unavailable in the current environment.

## Consequences

- Phase 1 can be built, tested, and validated end-to-end without a database server dependency, keeping the environment local-first and reproducible on any machine that can run this repository's test suite ([PHI_PRD.md PRD-NFR-005](../02-project/PHI_PRD.md#29-non-functional-requirements)).
- A future `TimescalePriceBarRepository` implementing the same `PriceBarRepository` protocol is a boundary swap, not a rewrite — exactly the migration path [SYSTEM_ARCHITECTURE.md §33](../03-architecture/SYSTEM_ARCHITECTURE.md#33-future-evolution) already anticipates ("Storage can migrate ... without changing the query interface Feature Engineering and Event-Driven Backtesting depend on").
- Content-hashing of each ingested Parquet snapshot is required so the repository still satisfies the data-versioning requirement PostgreSQL/TimescaleDB would otherwise carry via row-level provenance ([PHI_PRD.md PRD-DATA-010](../02-project/PHI_PRD.md#15-data-requirements), [PRD-REPRO-001](../02-project/PHI_PRD.md#22-experiment-reproducibility)).
- This ADR must be revisited (superseded, not edited) once PostgreSQL/TimescaleDB is actually available and real ingestion volume exists — it is an environment-driven implementation choice for Phase 1, not a claim that Parquet replaces the committed architecture.

## Alternatives Considered

- **Start a local Postgres/TimescaleDB via Docker now.** Rejected for this session: Docker daemon is not running and starting it, pulling images, and provisioning a database are operational actions with their own blast radius that should be a deliberate, confirmed step, not a side effect of writing Phase 1 code.
- **In-memory only storage (no persistence).** Rejected: fails PRD-DATA-002 (retain full history) and PRD-REPRO-002 (a logged experiment must be re-derivable) outright — there would be nothing to re-derive from between process runs.
- **SQLite as a stand-in relational/time-series store.** Rejected: not part of the already-decided storage architecture, and would itself need replacing later; Parquet is *already* the architecture's named portable format, so it introduces no new technology.

## Traceability

| Section | Derived From |
|---|---|
| Storage interface contract | [DATABASE_ARCHITECTURE.md §7.2](../03-architecture/DATABASE_ARCHITECTURE.md#72-time-series-entities-timescaledb-hypertables), [§8](../03-architecture/DATABASE_ARCHITECTURE.md#8-indexing-strategy) |
| Parquet as approved component | [SYSTEM_ARCHITECTURE.md §22](../03-architecture/SYSTEM_ARCHITECTURE.md#22-storage-architecture), [§29](../03-architecture/SYSTEM_ARCHITECTURE.md#29-architecture-decision-summary) |
| No premature infrastructure | [PHI_PRD.md PRD-NFR-006](../02-project/PHI_PRD.md#29-non-functional-requirements) |
| Local-first operation | [PHI_PRD.md PRD-NFR-005](../02-project/PHI_PRD.md#29-non-functional-requirements) |
| Future migration path | [SYSTEM_ARCHITECTURE.md §33](../03-architecture/SYSTEM_ARCHITECTURE.md#33-future-evolution) |
