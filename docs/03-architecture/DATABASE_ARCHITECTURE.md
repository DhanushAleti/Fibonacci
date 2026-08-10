# Database Architecture

## 1. Document Control

- **Document:** DATABASE_ARCHITECTURE.md
- **Status:** Draft — Pending Review
- **Version:** 0.1.0
- **Document Type:** Architecture Specification
- **Owner:** TBD (Suggested: Engineering Lead)
- **Last Updated:** 2026-08-10

## 2. Purpose

Define the database-level architecture for Project PHI: what entities the system's databases must represent, how PostgreSQL and TimescaleDB divide responsibility, and the schema-design, indexing, migration, backup, and scaling principles that govern them. This document exists to make PHI's persistence layer support — not undermine — the reproducibility and point-in-time-correctness requirements already established for the platform.

## 3. Scope

Covers database-level structure only: conceptual entities, their relationships, and schema-design/operational principles for PostgreSQL and TimescaleDB. It does **not** cover:

- Broader data pipeline, ingestion mechanics, or lineage — that belongs to [DATA_ARCHITECTURE.md](DATA_ARCHITECTURE.md) (currently a skeleton).
- Exact SQL DDL, column types, or a finalized migration tool choice — those are implementation decisions made when Phase 1 (Data Foundation) is actually built, not invented here.
- Parquet/DuckDB usage in detail beyond how they relate to the databases described here — their conceptual role is defined in [SYSTEM_ARCHITECTURE.md §22](SYSTEM_ARCHITECTURE.md#22-storage-architecture) and is not restated.
- API-level access to this data — that belongs to [API_ARCHITECTURE.md](API_ARCHITECTURE.md) (currently a skeleton).

## 4. Relationship to Other Documents

This document implements the conceptual storage roles already decided in [SYSTEM_ARCHITECTURE.md §22 Storage Architecture](SYSTEM_ARCHITECTURE.md#22-storage-architecture) and [§9.3 Market Data Storage](SYSTEM_ARCHITECTURE.md#93-market-data-storage), and exists to satisfy the data requirements in [PHI_PRD.md §15](../02-project/PHI_PRD.md#15-data-requirements) and the reproducibility requirements in [PHI_PRD.md §22](../02-project/PHI_PRD.md#22-experiment-reproducibility). It does not revisit or override any decision already made in those documents (see [§14 Traceability](#14-traceability)).

## 5. Overview

PHI's persistence layer splits across two database engines, per the already-committed architecture decision (not re-litigated here):

- **PostgreSQL** — relational, non-time-series data: instrument reference data, corporate actions, experiment/run metadata, feature definitions, statistical evaluation results, and any entity with normal relational structure.
- **TimescaleDB** (a PostgreSQL extension) — time-series market data: price/volume bars and, where applicable, tick data, stored in hypertables partitioned by time.

Because TimescaleDB extends PostgreSQL directly, both roles can be served by a single running PostgreSQL instance with the TimescaleDB extension enabled — PHI does not require two separate database servers. Parquet snapshots and DuckDB analytical queries (per [SYSTEM_ARCHITECTURE.md §22](SYSTEM_ARCHITECTURE.md#22-storage-architecture)) sit alongside this database, not inside it — they are portable exports/analytical views, not additional schema-level structure defined here.

## 6. Schema Design Principles

- **PRD-traceable structure.** Every entity described in [§7](#7-entity-relationship-overview) exists to satisfy a specific requirement already defined in [PHI_PRD.md](../02-project/PHI_PRD.md) or [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) — no entity is added speculatively.
- **Point-in-time correctness by construction.** Any table holding time-relevant data must be able to distinguish *event time* from *availability time*, per [SYSTEM_ARCHITECTURE.md §12 Time Semantics](SYSTEM_ARCHITECTURE.md#12-time-semantics). A schema that only records event time is insufficient.
- **No destructive overwrites.** Corrected or restated data is recorded alongside the original, not in place of it, consistent with [PHI_PRD.md PRD-DATA-002](../02-project/PHI_PRD.md#15-data-requirements).
- **Provenance is mandatory, not optional.** Every ingested record must be traceable to its source and fetch time (PRD-DATA-010); this is a schema-level requirement, not something bolted on later.
- **Survivorship-safe by default.** Instrument records are never hard-deleted on delisting; they are marked inactive and retained (PRD-DATA-009, PRD-BIAS-006).
- **Reproducibility-first for research entities.** Experiment, feature-definition, and evaluation-result records must carry enough versioning information (code version, data version/hash, configuration) to satisfy [PHI_PRD.md §22](../02-project/PHI_PRD.md#22-experiment-reproducibility) directly from the schema, not as an afterthought.
- **No premature normalization for scale that doesn't exist.** Schema design targets a single researcher's local-first workload ([PHI_PRD.md PRD-NFR-005](../02-project/PHI_PRD.md#29-non-functional-requirements)), not a multi-tenant or high-concurrency system.

## 7. Entity Relationship Overview

This section describes conceptual entities and their relationships — not SQL DDL, column types, or a finalized schema. It is the input to that later work, not a substitute for it.

### 7.1 Reference / Relational Entities (PostgreSQL)

- **Instrument** — A tradable security: symbol, exchange, asset class, currency, listing date, delisting date (nullable), and status (active/inactive). Never hard-deleted (schema design principle above).
- **InstrumentAlias** — Tracks symbol/ticker changes and re-listings over time, so a time series is not silently discontinuous or silently merged across unrelated instruments (PRD-DATA-008). Relates to exactly one `Instrument`.
- **CorporateAction** — A split, dividend, merger, or similar event affecting an instrument's price continuity: instrument reference, action type, effective date, and adjustment factor/details (PRD-DATA-004). Relates to one `Instrument`; used to derive adjusted price series without destructively rewriting raw data.
- **TradingCalendar** — Session and holiday definitions per exchange, used to distinguish genuine data gaps from expected non-trading periods (PRD-DATA-007).
- **DataProvenance** — Records source, fetch timestamp, and provider identifiers for a batch of ingested data, including the availability-time metadata required by [SYSTEM_ARCHITECTURE.md §12](SYSTEM_ARCHITECTURE.md#12-time-semantics) (PRD-DATA-010).
- **DataQualityFlag** — A record of a validation failure or anomaly (gap, duplicate, implausible volume, provider disagreement) raised during Data Validation (module 2, [SYSTEM_ARCHITECTURE.md §9.2](SYSTEM_ARCHITECTURE.md#92-data-validation)); routes to a quarantine/review path rather than being silently dropped.

### 7.2 Time-Series Entities (TimescaleDB hypertables)

- **PriceBar** — The canonical OHLCV time series: instrument reference, event time, availability time, open/high/low/close/volume, an explicit adjusted-vs-unadjusted flag (PRD-DATA-003), and a reference to the `DataProvenance` record it came from. Partitioned by time per [§8 Indexing Strategy](#8-indexing-strategy).
- **FeatureValue** *(time-series; may live in TimescaleDB or as Parquet output depending on volume — see [§13 Open Questions](#13-open-questions))* — A computed feature's value for an instrument at a point in time, referencing the `FeatureDefinition` that produced it and bound by the observation-window rule in [SYSTEM_ARCHITECTURE.md §12](SYSTEM_ARCHITECTURE.md#12-time-semantics).

### 7.3 Research / Reproducibility Entities (PostgreSQL)

- **FeatureDefinition** — A versioned, deterministic feature generator: name, family (a Golden Ratio family per [PHI_PRD.md §17](../02-project/PHI_PRD.md#17-golden-ratio-feature-families), or a control category per [§18](../02-project/PHI_PRD.md#18-control--placebo-framework)), parameters, and a reference to the exact code version that implements it (PRD-FEATENG-003/004).
- **Experiment** — A single research run: code version (git commit), data version/hash, configuration, and timestamp (PRD-REPRO-001). Logged whether the run was favorable or not (PRD-REPRO-003, PRD-BIAS-005/009) — there is no schema-level distinction that would make it easier to record only favorable runs.
- **ControlAssignment** — Links an `Experiment` to which control category (A–F, [PHI_PRD.md §18](../02-project/PHI_PRD.md#18-control--placebo-framework)) it evaluated, and confirms the shared conditions (dataset, window, model class) required for a fair comparison (PRD-CONTROL-007).
- **BacktestRun** — A specific execution of an `Experiment` through the event-driven backtester: market-clock configuration, position-limit configuration, and the transaction-cost/slippage assumptions used (PRD-BACKTEST-003/004/006), referencing [SYSTEM_ARCHITECTURE.md §16](SYSTEM_ARCHITECTURE.md#16-backtesting-architecture).
- **BacktestFill** — A single simulated fill within a `BacktestRun`: instrument, timestamp, price, quantity, commission, slippage — the accounting record behind position tracking (PRD-BACKTEST-007/008), corresponding to the `FillEvent` concept in [SYSTEM_ARCHITECTURE.md §11](SYSTEM_ARCHITECTURE.md#11-event-model).
- **StatisticalEvaluationResult** — The computed metrics (per [PHI_PRD.md §20](../02-project/PHI_PRD.md#20-statistical-validation-requirements)) for a `BacktestRun` or `Experiment`, including which regime and walk-forward window they apply to, and the outcome label (supported / inconclusive / falsified, per [PHI_PRD.md §8](../02-project/PHI_PRD.md#8-falsification-criteria) and PRD-OUTPUT-003).

### 7.4 Relationship Summary

```
Instrument ──< InstrumentAlias
Instrument ──< CorporateAction
Instrument ──< PriceBar (via DataProvenance)
Instrument ──< TradingCalendar (via exchange)

FeatureDefinition ──< FeatureValue (per Instrument, per timestamp)

Experiment ──< ControlAssignment (one per control category evaluated)
Experiment ──< BacktestRun
BacktestRun ──< BacktestFill
Experiment ──< StatisticalEvaluationResult
FeatureDefinition ──< Experiment (an experiment tests one or more feature definitions)
```

No entity above implies a specific table name, column type, or storage engine beyond what is stated in [§7.1–7.3](#71-reference--relational-entities-postgresql). Finalizing those is implementation work, not architecture.

## 8. Indexing Strategy

- **Time-series data** (`PriceBar`, and `FeatureValue` if it lives in TimescaleDB) must support efficient range queries by `(instrument, time range)` — the dominant access pattern for both backtesting and feature computation. TimescaleDB's hypertable chunking (time-based partitioning) is the intended mechanism, consistent with [SYSTEM_ARCHITECTURE.md §29](SYSTEM_ARCHITECTURE.md#29-architecture-decision-summary)'s choice of TimescaleDB.
- **Relational lookup entities** (`Instrument`, `FeatureDefinition`) must support efficient lookup by their natural identifiers (symbol, feature name/version) — standard relational indexing, not specified further here.
- **Reproducibility lookups** (`Experiment`, `BacktestRun`) must support efficient lookup by code version and data version/hash, since re-deriving a past result (PRD-REPRO-002) starts from exactly that lookup.
- Exact index definitions (composite indexes, partial indexes, chunk interval sizing) are deferred to implementation; this section defines the access patterns an implementation must serve, not the SQL to serve them.

## 9. Migration Strategy

- Schema changes must be **versioned and forward-only**: every change to the database structure is captured as a sequential, reviewable migration, not as an ad hoc manual `ALTER`.
- A migration must never silently alter the meaning of a past `Experiment` record — if a schema change would change how an old record should be interpreted, the migration must document that explicitly rather than leave it ambiguous, consistent with the reproducibility principle in [§6](#6-schema-design-principles).
- Migrations run against a local database in Phase 1; no separate staging/production migration pipeline is required until a deployment target beyond local research exists ([SYSTEM_ARCHITECTURE.md §26 Phase 1](SYSTEM_ARCHITECTURE.md#26-deployment-evolution)).
- The specific migration tooling (e.g., a Python migration library) is **not selected in this document** — no such dependency exists yet in the project's dependency manifest, and selecting one prematurely would contradict [PHI_PRD.md PRD-NFR-006](../02-project/PHI_PRD.md#29-non-functional-requirements) (no premature infrastructure). It is tracked as an open question ([§13](#13-open-questions)).

## 10. Backup and Recovery

- In Phase 1 (local research), backup requirements are intentionally minimal: periodic local database dumps are sufficient, consistent with [PHI_PRD.md PRD-NFR-005](../02-project/PHI_PRD.md#29-non-functional-requirements) (local-first operation) and [SYSTEM_ARCHITECTURE.md §26 Phase 1](SYSTEM_ARCHITECTURE.md#26-deployment-evolution).
- Because raw market data can, in principle, be re-ingested from the original provider, the database's price-history tables are not the *only* copy of that data — but `Experiment`, `FeatureDefinition`, `BacktestRun`, and `StatisticalEvaluationResult` records are **not** re-derivable from an external source if lost, since they represent the research history itself. Backup priority follows from this distinction: research/reproducibility entities are higher priority to protect than re-ingestable market data.
- Parquet snapshots (per [SYSTEM_ARCHITECTURE.md §22](SYSTEM_ARCHITECTURE.md#22-storage-architecture)) provide an independent, portable copy of dataset state and double as a practical recovery path for market data specifically.
- No automated offsite/cloud backup is required until a deployment phase beyond local research is entered; introducing one earlier would be infrastructure ahead of a demonstrated need (PRD-NFR-006).
- Exact backup frequency, retention, and restore-testing procedure are deferred to implementation and are not fixed by this document.

## 11. Scaling Considerations

- This document does not assume a scale beyond what a single researcher's local machine can handle, consistent with [SYSTEM_ARCHITECTURE.md §4 Non-Goals](SYSTEM_ARCHITECTURE.md#4-non-goals) and [§26 Phase 1](SYSTEM_ARCHITECTURE.md#26-deployment-evolution).
- The specific trigger for reconsidering the PostgreSQL/TimescaleDB choice is already defined in [SYSTEM_ARCHITECTURE.md §29](SYSTEM_ARCHITECTURE.md#29-architecture-decision-summary): "Query latency or ingestion volume genuinely exceeds what a PostgreSQL-based engine can sustain." This document does not restate or invent a new numeric threshold for that trigger — doing so would risk the same kind of premature hard-gating [PHI_PRD.md §20](../02-project/PHI_PRD.md#20-statistical-validation-requirements) explicitly warns against for statistical metrics.
- If that trigger is ever reached, the already-identified alternatives (kdb+, InfluxDB, ClickHouse) remain the reference set to evaluate — this document does not add new candidates.
- Read-heavy analytical workloads that would otherwise stress the transactional database are intended to be offloaded to DuckDB against Parquet exports, per [SYSTEM_ARCHITECTURE.md §22](SYSTEM_ARCHITECTURE.md#22-storage-architecture), rather than solved by scaling PostgreSQL/TimescaleDB itself.

## 12. Security and Secrets Handling

- Database connection credentials are secrets and must be supplied via environment configuration, never hardcoded — consistent with [PHI_PRD.md PRD-SEC-001](../02-project/PHI_PRD.md#27-security--data-integrity-requirements) and the existing `phi.config.get_secret` convention already established in the codebase (`src/phi/config.py`), which raises rather than silently falling back to a default when a required secret is missing.
- No network-facing database access is required in Phase 1 (local-only); this section is revisited if/when a deployment target beyond local research introduces network exposure ([SYSTEM_ARCHITECTURE.md §27 Security](SYSTEM_ARCHITECTURE.md#27-security)).
- Research data itself (market prices, computed features, backtest results) is not personal or sensitive data; this document does not define PII-handling requirements because none of the currently scoped entities in [§7](#7-entity-relationship-overview) contain PII.

## 13. Open Questions

- **Exact migration tooling.** No migration library is currently a project dependency; selection is deferred to Phase 1 implementation (see [§9](#9-migration-strategy)).
- **FeatureValue storage engine.** Whether computed feature time series live in TimescaleDB (queryable, indexed) or are generated on demand from Parquet/DuckDB (cheaper to store, recomputed as needed) is not decided — both are consistent with [SYSTEM_ARCHITECTURE.md §22](SYSTEM_ARCHITECTURE.md#22-storage-architecture) and the choice depends on feature-recomputation cost, which is not yet known.
- **TimescaleDB version/edition and exact hypertable chunk-interval defaults** are implementation decisions deferred until real ingestion volume is observed.
- **Exact backup frequency and restore-testing cadence** (see [§10](#10-backup-and-recovery)) are left to implementation.
- **Whether `BacktestFill` records are retained at full granularity indefinitely or summarized after a retention window** is an open data-volume/reproducibility trade-off not yet resolved.
- This document inherits, and does not attempt to re-resolve, the data-provider and survivorship-bias-free-universe-source open questions already recorded in [SYSTEM_ARCHITECTURE.md §32](SYSTEM_ARCHITECTURE.md#32-open-architecture-questions) and [PHI_PRD.md §35](../02-project/PHI_PRD.md#35-open-questions).

## 14. Traceability

| Section | Derived From |
|---|---|
| §5 Overview, §7.1–7.2 storage engine split | [SYSTEM_ARCHITECTURE.md §22 Storage Architecture](SYSTEM_ARCHITECTURE.md#22-storage-architecture), [§29 Architecture Decision Summary](SYSTEM_ARCHITECTURE.md#29-architecture-decision-summary) |
| §6 Point-in-time correctness principle | [SYSTEM_ARCHITECTURE.md §12 Time Semantics](SYSTEM_ARCHITECTURE.md#12-time-semantics) |
| §7.1 Instrument, InstrumentAlias, CorporateAction, TradingCalendar, DataProvenance, DataQualityFlag | [PHI_PRD.md §15 Data Requirements](../02-project/PHI_PRD.md#15-data-requirements) (PRD-DATA-001–012) |
| §7.2 PriceBar | [SYSTEM_ARCHITECTURE.md §9.3 Market Data Storage](SYSTEM_ARCHITECTURE.md#93-market-data-storage) |
| §7.3 FeatureDefinition | [PHI_PRD.md §16 Feature Engineering Requirements](../02-project/PHI_PRD.md#16-feature-engineering-requirements), [§17 Golden Ratio Feature Families](../02-project/PHI_PRD.md#17-golden-ratio-feature-families) |
| §7.3 Experiment | [PHI_PRD.md §22 Experiment Reproducibility](../02-project/PHI_PRD.md#22-experiment-reproducibility) |
| §7.3 ControlAssignment | [PHI_PRD.md §18 Control / Placebo Framework](../02-project/PHI_PRD.md#18-control--placebo-framework) |
| §7.3 BacktestRun, BacktestFill | [SYSTEM_ARCHITECTURE.md §16 Backtesting Architecture](SYSTEM_ARCHITECTURE.md#16-backtesting-architecture), [PHI_PRD.md §19 Backtesting Requirements](../02-project/PHI_PRD.md#19-backtesting-requirements) |
| §7.3 StatisticalEvaluationResult | [PHI_PRD.md §20 Statistical Validation Requirements](../02-project/PHI_PRD.md#20-statistical-validation-requirements), [§8 Falsification Criteria](../02-project/PHI_PRD.md#8-falsification-criteria) |
| §11 Scaling Considerations | [SYSTEM_ARCHITECTURE.md §29 Architecture Decision Summary](SYSTEM_ARCHITECTURE.md#29-architecture-decision-summary) |
| §12 Security and Secrets Handling | [PHI_PRD.md §27 Security / Data Integrity Requirements](../02-project/PHI_PRD.md#27-security--data-integrity-requirements), [SYSTEM_ARCHITECTURE.md §27 Security](SYSTEM_ARCHITECTURE.md#27-security) |

## 15. Definition of Done

This document is considered complete enough for stakeholder review when:

- Every section from [§1](#1-document-control) through [§14](#14-traceability) contains real content, with no remaining `(Placeholder)` markers.
- No entity or field described in [§7](#7-entity-relationship-overview) has been fixed as literal SQL DDL — this remains architecture, not schema code.
- No migration tool, exact index definition, or backup schedule has been asserted as decided where [§13 Open Questions](#13-open-questions) marks it open.
- No numeric scaling threshold has been invented beyond the one already established in [SYSTEM_ARCHITECTURE.md §29](SYSTEM_ARCHITECTURE.md#29-architecture-decision-summary).
- All relative Markdown links resolve to files and headings that exist in the repository as of this document's last update.
- Nothing in this document contradicts a decision already made in [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) or [PHI_PRD.md](../02-project/PHI_PRD.md).
- The document has been reviewed by at least one stakeholder and its `Status` field updated from "Draft — Pending Review" accordingly.
