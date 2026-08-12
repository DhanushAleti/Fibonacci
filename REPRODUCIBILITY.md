# Reproducibility Guide

This guide lets an independent researcher clone PHI, run everything, and verify every claim the
repository makes. Please read the **scientific-claim boundary** first — it determines what "reproduce"
means here.

## Scientific-claim boundary (what there is to reproduce)

PHI currently implements the **leakage-safe construction** of one candidate φ feature and its six
matched controls, plus science-neutral pre-registration/reproducibility infrastructure. It has **not**
run any confirmatory experiment and makes **no** claim about whether the golden ratio matters in
markets. There is therefore **no φ result to reproduce** — only the construction, its determinism, and
the test/quality gates. The confirmatory science (anchor algorithm, `ε_φ`, primary estimand,
dependence-aware inference) is deliberately **not implemented** and is gated NO-GO in code
(`ExperimentManifest.is_confirmatory_ready()`). See the
[feature & control contract](docs/05-mathematics/phi-retracement-feature-contract.md) §0A and
[ADR 0003](docs/18-decisions/0003-phase2-external-review-nogo-and-feature-authority.md).

## Environment

- **Python:** ≥ 3.11 (developed and type-checked under 3.13).
- **Dependency manager:** [`uv`](https://github.com/astral-sh/uv). Exact versions are pinned in
  [`uv.lock`](uv.lock); reproduce the environment with `uv sync --extra dev`.
- **Runtime deps:** `polars`, `numpy`, `pydantic`. **Dev deps:** `pytest`, `pytest-cov`, `hypothesis`,
  `ruff`, `mypy`.

## Reproduce the full verification

```bash
git clone <this-repo> && cd project-phi
uv sync --extra dev                              # create .venv from the pinned lockfile
uv run pytest -q --cov=phi --cov-report=term-missing   # full suite + coverage
uv run ruff check .                              # lint
uv run ruff format --check .                     # formatting
uv run mypy                                      # static types
uv run python -c "import phi, phi.features, phi.experiment; print('import OK', phi.__version__)"
```

Expected: the full suite passes at ~98% branch coverage, with `ruff` and `mypy` clean. (Test counts
grow over time — trust the live number the command prints over any number written in prose.)

## What "reproducible" means here — precisely

- **Single-implementation determinism (demonstrated).** The feature computation is a pure function of
  its inputs with all randomness seeded (`random.Random(1618)`, matching `Settings.random_seed`) and
  all constants pinned by *expression* (`PHI = (1 + 5**0.5) / 2`, `g_φ = 1/PHI`). The same input yields
  bit-identical output across repeated runs **and across process restarts** — the latter is asserted by
  `tests/features/test_determinism.py::TestCrossProcessDeterminism`, which recomputes the output in a
  fresh interpreter with an unpinned hash seed and compares SHA-256 digests.
- **Cross-implementation equivalence (NOT yet demonstrable).** The contract's §5A criterion (two
  independent implementations agreeing within `atol=1e-12, rtol=1e-9`) cannot be exercised — only one
  implementation exists. This is stated, not glossed. PHI does **not** claim "byte-identical
  reproducibility" of any whole-pipeline artifact.
- **Provenance.** `phi.experiment.provenance.capture()` records the git commit SHA and a SHA-256 of
  `uv.lock`; an `ExperimentManifest` binds both, so an equal manifest hash implies the *same executable
  experiment*, not merely the same parameters.

## Data

All data used anywhere in the tests is **synthetic** — a deterministic Gaussian random walk from
`phi.data.providers.synthetic`, clearly labeled `synthetic:` and never presented as market evidence. No
real market-data provider is connected (PRD-OPEN-001 is open by design). Per the contract, synthetic
data can validate engineering properties but **cannot** support any scientific claim about real-world φ
structure.
