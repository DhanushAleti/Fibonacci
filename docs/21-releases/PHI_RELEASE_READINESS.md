# PHI — Release Readiness Report

**Date:** 2026-08-12
**Prepared by:** Principal engineer / research implementation lead (final ship pass)

> **Honest framing.** PHI is **not** "perfect" and is **not** scientifically validated. This report
> attests to the readiness of what actually exists — leakage-safe φ-feature *construction* and
> science-neutral reproducibility infrastructure — and is explicit about what does not exist (any
> confirmatory φ result) and what is deliberately withheld (the blocked scientific decisions).

## Status summary

| Field | Value |
|---|---|
| **Project version** | 0.2.0 |
| **Git commit** | `7747ddd0b426c49fafc6bc24e794dc44ea957467` (branch `feat/phase2-feature-lab-and-experiment-infra`, not pushed) |
| **Test count** | 210 passed |
| **Coverage** | 98% branch (757 stmts, 10 missed) |
| **Lint status** | Ruff `check` clean; `format --check` clean |
| **Type-check status** | mypy clean (25 source files) |
| **Reproducibility status** | Single-implementation + cross-process determinism demonstrated; provenance binds git SHA + lockfile hash. Cross-*implementation* equivalence not demonstrable (one implementation). No confirmatory experiment exists to reproduce. |
| **Scientific validation status** | **None — by design.** No φ claim is made anywhere; confirmatory analysis is gated NO-GO in code. |
| **Experiment status** | No confirmatory experiment has been run. `ExperimentManifest.is_confirmatory_ready()` returns `False` until a human freezes the four blocked decisions. |

## What is ready (in scope)

- **Phase 0/1** — engineering + data foundation: deterministic settings, secret-safe logging, the T-1
  information barrier, schemas that reject non-finite prices at construction, validation, a labeled
  synthetic provider, Parquet storage, ingestion, point-in-time queries.
- **Phase 2 — φ-feature construction** — the authoritative rolling-window candidate
  `f_A(t) = |p_t - 1/φ|` and its six matched controls (A/B/C1/C2/D/E/F) over one shared leakage-safe
  pipeline (`L = 20`), with an adversarial future-injection leakage invariant.
- **Experiment infrastructure** (science-neutral) — immutable content-hashed pre-registration manifest
  with a machine-checkable confirmatory-readiness gate; exclusion accounting; code/environment
  provenance capture.

## What is NOT ready (deliberately gated NO-GO)

Three external reviews (Authoritative Contract, Perplexity, Gemini) plus an independent audit and a
hostile peer review agree these are **human decisions that must not be invented in code**, and they are
unimplemented:

1. The causal anchor/excursion selection algorithm (Blocker 1).
2. The φ-hit threshold `ε_φ` (Blocker 2).
3. The single primary estimand (Blocker 3).
4. The dependence-aware inference protocol — bootstrap, CIs, effect sizes, multiplicity, IAAFT/GARCH
   surrogates (Blocker 4).

Until all four are frozen by a superseding ADR, no confirmatory φ analysis is authorized.

## Known limitations

- **No scientific result.** Passing tests and 98% coverage are engineering facts, not evidence about φ.
- **Synthetic data only.** All data is a labeled Gaussian random walk; it cannot support any real-world
  φ claim (PRD-OPEN-001 open by design).
- **Construct validity is an open question.** The rolling-window position `p_t` is a defensible,
  low-leakage operationalization of retracement-level proximity, but it is *not* the folkloric
  swing-based retracement; the peer review's central scientific ask — "does 0.618 beat *equivalent
  constants* under one frozen protocol?" — is a Phase-4 experiment that has not been run.
- **Base-rate geometry.** Under a random walk, `p_t` is arcsine/U-shaped, not uniform; any future
  inference must use the constant-swap superiority design (already the intended Family-A comparison),
  never "0.618 appears often."
- **Cross-implementation reproducibility** (contract §5A) is asserted only as single-implementation +
  cross-process determinism; a second independent implementation would be needed to exercise it.
- **Provenance of history.** Eight earlier "record PHI research progress" commits are empty heartbeat
  commits on `main`; they are left untouched (rewriting published history is out of scope) but noted.

## Known risks

- **Feature-authority is settled but blockers are not.** ADR 0003 records Option B (rolling-window
  authoritative). The risk is treating "Phase 2 construction complete" as scientific progress — the
  README and this report guard against that explicitly.
- **Multiplicity / researcher-degrees-of-freedom** remain the dominant scientific risk for any future
  Phase 4; the manifest + exclusion ledger + NO-GO gate exist to constrain them but are only as good as
  the eventually-registered plan.

## Exact reproduction commands

```bash
git clone <this-repo> && cd project-phi
git checkout feat/phase2-feature-lab-and-experiment-infra   # or the merged commit
uv sync --extra dev
uv run pytest -q --cov=phi --cov-report=term-missing
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest -m "reproducibility or leakage" -q            # targeted scientific-invariant checks
uv run python -c "import phi, phi.features, phi.experiment; print('import OK', phi.__version__)"
```

There is **no experiment command** — Phase 2 runs no labels, backtest, or statistics by design. The
commands above verify construction, determinism, and the quality gates. See
[REPRODUCIBILITY.md](../../REPRODUCIBILITY.md).

## Bottom line

A researcher can clone PHI, run it, inspect the exact frozen methodology, reproduce the construction and
its determinism, and independently see that **no φ claim is being made** and that the machinery is built
to keep a future result honest. Whether the golden ratio matters in markets is **undetermined here and
deliberately so** — that verdict awaits a registered Phase-4 experiment that freezes the four blocked
decisions first.
