# Contributing to Project PHI

PHI is a falsifiability-first research platform. Its entire value depends on making it **impossible for
the researcher or the software to quietly change what "φ is present" means after seeing data.** The
rules below are not bureaucracy — they are the experiment's integrity controls. Contributions that
weaken them will be rejected regardless of code quality.

## Scientific-integrity rules (non-negotiable)

1. **Do not invent the blocked scientific decisions.** Four decisions are deliberately unfrozen and must
   be set by a human via a superseding ADR before *any* confirmatory code:
   the causal anchor/excursion algorithm, the φ-hit threshold `ε_φ`, the primary estimand, and the
   dependence-aware inference protocol. Do not hardcode a value, default, or "reasonable" choice for any
   of them. `is_phi_hit` refusing a default `epsilon`, and `ExperimentManifest.is_confirmatory_ready()`
   returning `False` until these are registered, are features — do not "fix" them.
2. **Make no φ claim.** Nothing may state or imply that the golden ratio is predictive, present,
   validated, or special. Passing tests and coverage are engineering facts, not scientific validation
   (see the [contract](docs/05-mathematics/phi-retracement-feature-contract.md) §0A, §33; PRD-GRF-012).
3. **No result-driven changes.** Do not tune windows, thresholds, controls, or seeds toward any outcome.
   The frozen parameters (`L = 20`, `seed = 1618`, the six controls, the constants) may change **only**
   by a logged, superseding ADR — never by editing an existing ADR in place.
4. **Preserve the leakage barrier.** Feature values at time `T` must be invariant to any data with
   `availability_time > T`. The adversarial future-injection test
   (`tests/features/test_pipeline.py::TestAdversarialFutureInjection`) must stay green and must not be
   weakened.
5. **Account for every exclusion.** Dropped observations must be recorded against a named
   `ExclusionReason` — never silently filtered.

## Engineering workflow

- **Environment:** `uv sync --extra dev`. Run everything via `uv run …`.
- **TDD:** write the test first; hand-verify mathematical claims against the contract rather than against
  the implementation's own output.
- **Quality gates (all must pass before a PR):**
  ```bash
  uv run pytest -q --cov=phi --cov-report=term-missing
  uv run ruff check .
  uv run ruff format --check .
  uv run mypy
  ```
  Do not lower coverage, `# noqa`/`# type: ignore` to pass a gate, or silence a warning without a
  written justification (the suite runs with `filterwarnings = ["error"]`).
- **Commits:** Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:`). Keep the
  documentation set consistent — `PRD = Architecture = Contract = Code = Tests = Research Log`.
- **Decisions:** record architectural/scientific decisions as ADRs under
  [`docs/18-decisions/`](docs/18-decisions/). **Supersede, never edit** an accepted ADR.

## What is welcome right now

Science-neutral engineering that helps under any eventual feature/inference decision: reproducibility
and provenance hardening, additional adversarial/leakage tests, documentation accuracy, and Phase-3
backtester scaffolding that operates on the frozen features **without** reopening their definitions or
starting predictive/statistical claim work.
