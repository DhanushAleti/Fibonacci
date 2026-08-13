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

**The single authoritative statement of PHI's scientific status** — including the Phase-4 confirmatory
methodology, its synthetic falsification, the post-failure repair, and why the repair also does not
currently clear its own validation gates — is
[docs/PHI_FINAL_SCIENTIFIC_STATUS.md](docs/PHI_FINAL_SCIENTIFIC_STATUS.md), with the full narrative in
[docs/PHI_FINAL_RESEARCH_REPORT.md](docs/PHI_FINAL_RESEARCH_REPORT.md). Every headline number in those
two documents is reproduced by a command in this file.

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

### Phase-4 methodology (frozen; confirmatory execution blocked)

```bash
uv run pytest tests/phase4 -q                    # confirmatory methodology tests
uv run pytest -m "reproducibility" -q            # in- and cross-process determinism
```

There is **no confirmatory command**: `phi.phase4` fails closed until a human completes the numerical
pre-registration and the validation gates pass, and one gate (null-FPR calibration of the estimand *as
specified*) does not currently pass — see the [Phase-4 contract](docs/05-mathematics/phi-phase4-scientific-contract.md) §7. The
synthetic false-positive/power harnesses (`phi.phase4.calibration`) are runnable and deterministic.

### Phase-4 original synthetic falsification (FAIL — provenance for the headline numbers)

```bash
uv run pytest tests/phase4 -q                                # 83 methodology tests, git SHA f1467c1
uv run python scripts/phase4_synthetic_validation.py          # regenerates results/phase4_validation/results.json
```

Headline numbers (aggregate FPR = 1.000 across 1,950 null trials; φ ranks 4th of 5 in the constant
sweep) come directly from `results/phase4_validation/results.json` (git SHA `f1467c1`, config
`n_series=150, series_length=400, replicates=199, base_seed=20260812`). Report:
[docs/21-releases/PHI_PHASE4_SYNTHETIC_VALIDATION.md](docs/21-releases/PHI_PHASE4_SYNTHETIC_VALIDATION.md).

### Phase-4 repair validation (small-scale — does not pass its own gate)

```bash
uv run pytest tests/phase4/repair -q                          # 39 repair tests
uv run python scripts/phase4_repair_validation.py              # small-scale 5-part gate (~90s)
uv run python scripts/phase4_repair_validation.py --full       # heavier run (1000x999); not yet run
```

Headline numbers (aggregate FPR 1.0 → 0.011; power 0.82; granularity FPR 0.22 at 10-tick resolution)
come from `results/phase4_repair_validation/results.json`, `n_series=100, series_length=400,
n_surrogates=99, base_seed=20260812`. **Provenance note:** this artifact's own `git_sha` field records
`3412a67` (the commit immediately before the repair modules were committed as `a0e07aa`) — the script
ran against a working tree that already had the repair code but had not yet committed it. The numeric
result is unaffected; only the artifact's self-reported provenance pointer is one commit behind where
the code actually landed. The final 10,000/20,000-per-DGP validation (`--full`) has never been run.

### Trend-plus-noise per-DGP gate re-verification (new in this finalization pass)

The small-scale artifact above reports the `trend_plus_noise` null process at FPR = 0.07 — **exactly**
the Repair Contract's 0.07 per-DGP threshold, from a single seed at `n_series=100`. Because a value
sitting precisely on its decision boundary at that scale carries meaningful sampling uncertainty, this
was re-checked with independent seeds using the existing, unmodified harness (no DGP, estimand, or
threshold changed):

```bash
uv run python scripts/phase4_trend_plus_noise_reverification.py
```

Output: `results/phase4_repair_validation/trend_plus_noise_reverification.json`. Method: an exact
reproduction of the original run (`base_seed=20260819`, the seed `null_suite_fpr` assigns to
`trend_plus_noise` at harness `base_seed=20260812`, since it is index 7 of 13 in `REPAIR_NULL_SUITE`)
confirms determinism (reproduces 0.07 exactly); six further independent seeds (five at `n_series=100`,
two at `n_series=300`) give FPRs of 0.11, 0.13, 0.16, 0.12, 0.11, 0.1067, 0.0933. Grand-pooled across
all 8 runs (1,200 total simulated series): **FPR ≈ 0.108, approximate 95% CI [0.091, 0.126]** —
decisively above the 0.07 threshold. **Conclusion: the per-DGP FPR gate does not robustly pass for
trend_plus_noise; the originally reported 0.07 was the low tail of sampling variability at small n, not
a representative estimate.** See [docs/PHI_FINAL_SCIENTIFIC_STATUS.md](docs/PHI_FINAL_SCIENTIFIC_STATUS.md) §12 for
full interpretation.

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
