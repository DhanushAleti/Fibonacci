"""PHI Phase-4 synthetic validation and false-positive torture test.

Runs the frozen Phase-4 pipeline against synthetic processes whose true generating
mechanism is KNOWN, to determine whether PHI can fool itself. **Synthetic data
only — no real-world confirmatory analysis.** Emits machine-readable JSON and a
console summary. Nothing here makes a real-world φ claim.

Sections (A-G) mirror the validation brief:
    A. Null processes (12) -> false-positive rate + Wilson CI
    B. Positive control (injected φ) -> sensitivity / effect recovery
    C. Negative control (injected non-φ) -> does PHI mislabel it φ?
    D. Constant sweep (φ vs nearby vs far) -> does PHI prefer φ specifically?
    E. Multiple testing -> pooled FPR across all null simulations
    F. Temporal-leakage battery
    G. Reproducibility

Run:  uv run python scripts/phase4_synthetic_validation.py [--full]
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from phi.phase4.analysis import analyze_series
from phi.phase4.calibration import CalibrationResult, estimate_rejection_rate
from phi.phase4.constants import ALPHA, Q_PHI
from phi.phase4.estimand import dense_grid, grid_landscape, paired_z
from phi.phase4.extrema import build_excursions, three_point_extrema
from phi.phase4.inference import bootstrap_delta_phi
from phi.phase4.nulldgp import NULL_DGPS
from phi.phase4.registration import ComparisonSet
from phi.phase4.retracement import excursion_retracements

Generator = np.random.Generator
DGP = Callable[[Generator, int], np.ndarray]

OUT_DIR = Path("results/phase4_validation")


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #
def wilson_ci(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Wilson score interval for a binomial rate (robust near 0 and 1)."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, center - half), min(1.0, center + half))


def retracements_of(series: np.ndarray) -> np.ndarray:
    """Eligible (R in [0,1]) per-excursion retracements of a raw series."""
    result = excursion_retracements(build_excursions(three_point_extrema(list(series))))
    return np.array([o.r for o in result.eligible], dtype=np.float64)


def delta_for_constant(r: np.ndarray, c: float, *, delta: float, k_per_side: int) -> float:
    """Δ_c for an arbitrary focal constant ``c`` with a symmetric grid around it.

    Lets us ask the decisive question: does the method 'prefer' q_φ specifically,
    or does it 'prefer' whatever constant you centre the symmetric controls on?
    """
    controls = tuple(c - j * delta for j in range(k_per_side, 0, -1)) + tuple(
        c + j * delta for j in range(1, k_per_side + 1)
    )
    z = paired_z(r, controls, q_phi=c)
    return float(z.mean()) if z.size else float("nan")


# --------------------------------------------------------------------------- #
# Extra DGPs required by the brief (AR(p), autocorrelated heavy-tailed)
# --------------------------------------------------------------------------- #
def ar_p(rng: Generator, n: int, *, coeffs: tuple[float, ...] = (0.5, 0.3)) -> np.ndarray:
    x = np.zeros(n, dtype=np.float64)
    eps = rng.standard_normal(n)
    for t in range(n):
        val = eps[t]
        for j, a in enumerate(coeffs, start=1):
            if t - j >= 0:
                val += a * x[t - j]
        x[t] = val
    return x


def autocorr_heavy(rng: Generator, n: int, *, rho: float = 0.6, df: float = 4.0) -> np.ndarray:
    x = np.empty(n, dtype=np.float64)
    eps = rng.standard_t(df, size=n)
    x[0] = eps[0]
    for t in range(1, n):
        x[t] = rho * x[t - 1] + eps[t]
    return x


def biased_zigzag(rng: Generator, n: int, *, target: float, noise: float = 0.04) -> np.ndarray:
    """A zig-zag whose successive swing ratio -> ``target`` (so R clusters at target).

    Used as the positive control (target=q_φ) and the negative controls
    (target != q_φ). The injected structure is in the *retracement ratio*, exactly
    the quantity PHI measures.
    """
    x = np.empty(n, dtype=np.float64)
    x[0] = 0.0
    swing = 1.0
    direction = 1.0
    for t in range(1, n):
        x[t] = x[t - 1] + direction * swing
        ratio = target + noise * rng.standard_normal()
        swing = abs(swing * max(ratio, 1e-3))
        direction = -direction
    return x


def _result_dict(r: CalibrationResult) -> dict[str, object]:
    lo, hi = wilson_ci(r.n_rejected, r.n_valid)
    return {
        "dgp": r.dgp_name,
        "n_series": r.n_series,
        "n_valid": r.n_valid,
        "n_rejected": r.n_rejected,
        "false_positive_rate": round(r.rejection_rate, 4),
        "fpr_wilson_ci95": [round(lo, 4), round(hi, 4)],
        "mean_delta_hat": round(r.mean_delta_hat, 5),
        "expected": f"~alpha ({ALPHA})",
        "status": "PASS" if r.is_calibrated() else "FAIL (over-rejects)",
    }


# --------------------------------------------------------------------------- #
# Sections
# --------------------------------------------------------------------------- #
def section_a_nulls(comparison_set: tuple[float, ...], cfg: dict[str, int]) -> dict[str, object]:
    dgps: dict[str, DGP] = {**NULL_DGPS, "ar_p": ar_p, "autocorr_heavy": autocorr_heavy}
    rows: list[dict[str, object]] = []
    for i, (name, dgp) in enumerate(dgps.items()):
        res = estimate_rejection_rate(
            dgp,
            comparison_set,
            n_series=cfg["n_series"],
            series_length=cfg["series_length"],
            replicates=cfg["replicates"],
            base_seed=cfg["base_seed"] + i,
            dgp_name=name,
        )
        rows.append(_result_dict(res))
        r = rows[-1]
        print(
            f"  {name:20s} FPR={r['false_positive_rate']:.3f} "
            f"CI{r['fpr_wilson_ci95']} meanD={r['mean_delta_hat']:+.4f} {r['status']}"
        )
    return {"per_dgp": rows}


def section_bc_controls(
    comparison_set: tuple[float, ...], cfg: dict[str, int]
) -> dict[str, object]:
    grid = dense_grid(step=0.002)
    out: dict[str, object] = {}
    for label, target in [("positive_phi", Q_PHI), ("negative_0.5", 0.5), ("negative_0.3", 0.3)]:
        rng = np.random.default_rng(cfg["base_seed"])
        r = retracements_of(biased_zigzag(rng, cfg["series_length"] * 3, target=target))
        if r.size < 2:
            out[label] = {"note": "too few eligible retracements"}
            continue
        land = grid_landscape(r, grid)
        argmin_q = float(grid[int(np.argmin(land))])
        z = paired_z(r, comparison_set)
        boot = bootstrap_delta_phi(z, replicates=cfg["replicates"], seed=cfg["base_seed"])
        out[label] = {
            "injected_target_ratio": round(target, 5),
            "n_eligible": int(r.size),
            "mean_R": round(float(r.mean()), 4),
            "landscape_argmin_q": round(argmin_q, 4),
            "landscape_localises_injection": bool(abs(argmin_q - target) < 0.05),
            "primary_delta_hat_vs_phi": round(boot.delta_hat, 5),
            "primary_p_value": round(boot.p_value, 5),
            "primary_rejects_h0_favouring_phi": bool(boot.p_value < ALPHA),
        }
        print(
            f"  {label:14s} injected={target:.3f} argmin(M(q))={argmin_q:.3f} "
            f"Δ_φ={boot.delta_hat:+.4f} p={boot.p_value:.3f} "
            f"fires={out[label]['primary_rejects_h0_favouring_phi']}"
        )
    return out


def section_d_constant_sweep(cfg: dict[str, int]) -> dict[str, object]:
    grid = dense_grid(step=0.002)
    delta, k = 0.05, 4
    focal = {"phi": Q_PHI, "0.5": 0.5, "0.4": 0.4, "0.75": 0.75, "0.25": 0.25}
    rng = np.random.default_rng(cfg["base_seed"])
    # Pool retracements from several IID-Gaussian nulls for a stable landscape.
    pool: list[np.ndarray] = []
    for _ in range(cfg["n_series"]):
        pool.append(retracements_of(np.cumsum(rng.standard_normal(cfg["series_length"]))))
    r = np.concatenate([p for p in pool if p.size]) if pool else np.empty(0)
    land = grid_landscape(r, grid)
    deltas = {
        name: round(delta_for_constant(r, c, delta=delta, k_per_side=k), 5)
        for name, c in focal.items()
    }
    argmin_q = float(grid[int(np.argmin(land))])
    print(f"  pooled N={r.size}  argmin(M(q))={argmin_q:.3f}  Δ_c per focal constant:")
    for name, d in deltas.items():
        print(f"    Δ_{name:5s} = {d:+.5f}")
    return {
        "pooled_n": int(r.size),
        "landscape_argmin_q": round(argmin_q, 4),
        "delta_by_focal_constant": deltas,
        "phi_is_specifically_preferred": bool(
            deltas["phi"] > max(v for k2, v in deltas.items() if k2 != "phi") + 1e-6
        ),
    }


def section_f_leakage(comparison_set: tuple[float, ...], cfg: dict[str, int]) -> dict[str, object]:
    rng = np.random.default_rng(cfg["base_seed"])
    series = np.cumsum(rng.standard_normal(cfg["series_length"]))
    r_base = retracements_of(series)
    # Look-ahead: append a spectacular future value; earlier retracements must not change.
    r_future = retracements_of(np.append(series, 1e12))
    m = min(r_base.size, r_future.size)
    lookahead_max_diff = (
        float(np.max(np.abs(r_base[: m - 1] - r_future[: m - 1]))) if m > 1 else 0.0
    )
    # Normalization/preprocessing: retracement is a ratio of differences -> scale & shift invariant.
    r_scaled = retracements_of(series * 1000.0)
    r_shifted = retracements_of(series + 500.0)
    scale_max_diff = float(np.max(np.abs(r_base - r_scaled))) if r_base.size else 0.0
    shift_max_diff = float(np.max(np.abs(r_base - r_shifted))) if r_base.size else 0.0
    out = {
        "lookahead_earlier_retracements_max_abs_diff": lookahead_max_diff,
        "lookahead_leakage_free": bool(lookahead_max_diff < 1e-9),
        "scale_invariance_max_abs_diff": scale_max_diff,
        "shift_invariance_max_abs_diff": shift_max_diff,
        "normalization_leakage_free": bool(scale_max_diff < 1e-9 and shift_max_diff < 1e-9),
        "overlapping_window_note": (
            "unit of inference is the completed excursion; stationary bootstrap resamples "
            "excursion blocks, so overlapping intra-excursion points are not treated as independent"
        ),
        "train_test_separation_note": (
            "discovery/confirmation/replication roles enforced by the fail-closed gate "
            "(phi.phase4.pipeline)"
        ),
    }
    print(
        f"  look-ahead leakage-free: {out['lookahead_leakage_free']} "
        f"(max diff {lookahead_max_diff:.2e})"
    )
    print(
        f"  normalization leakage-free (scale+shift invariant): {out['normalization_leakage_free']}"
    )
    return out


def section_g_reproducibility(
    comparison_set: tuple[float, ...], cfg: dict[str, int]
) -> dict[str, object]:
    series = np.cumsum(np.random.default_rng(777).standard_normal(cfg["series_length"]))
    a = analyze_series(series, comparison_set, replicates=cfg["replicates"], seed=20260812)
    b = analyze_series(series, comparison_set, replicates=cfg["replicates"], seed=20260812)
    c = analyze_series(series, comparison_set, replicates=cfg["replicates"], seed=1)
    same = (
        a.bootstrap is not None
        and b.bootstrap is not None
        and (
            a.delta_hat == b.delta_hat
            and a.bootstrap.p_value == b.bootstrap.p_value
            and a.bootstrap.ci_low == b.bootstrap.ci_low
        )
    )
    diff_seed_changes = (
        c.bootstrap is not None
        and a.bootstrap is not None
        and (c.bootstrap.p_value != a.bootstrap.p_value or c.bootstrap.ci_low != a.bootstrap.ci_low)
    )
    out = {
        "same_seed_identical": bool(same),
        "different_seed_differs": bool(diff_seed_changes),
        "cross_process_test": "tests/phase4/test_reproducibility.py",
    }
    print(
        f"  same-seed identical: {out['same_seed_identical']}  "
        f"different-seed differs: {out['different_seed_differs']}"
    )
    return out


def git_sha() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description="PHI Phase-4 synthetic validation")
    parser.add_argument("--full", action="store_true", help="larger, slower run")
    args = parser.parse_args()
    cfg = (
        {"n_series": 300, "series_length": 500, "replicates": 999, "base_seed": 20260812}
        if args.full
        else {"n_series": 150, "series_length": 400, "replicates": 199, "base_seed": 20260812}
    )
    # ILLUSTRATIVE control set — NOT a registered confirmatory value.
    comparison_set = ComparisonSet.build(delta=0.05, k_per_side=4).constants

    start = time.time()
    print(f"PHI Phase-4 synthetic validation  (config={cfg})")
    print("\n[A] NULL PROCESSES")
    a = section_a_nulls(comparison_set, cfg)
    print("\n[B/C] POSITIVE & NEGATIVE CONTROLS")
    bc = section_bc_controls(comparison_set, cfg)
    print("\n[D] CONSTANT SWEEP")
    d = section_d_constant_sweep(cfg)
    print("\n[F] TEMPORAL-LEAKAGE BATTERY")
    f = section_f_leakage(comparison_set, cfg)
    print("\n[G] REPRODUCIBILITY")
    g = section_g_reproducibility(comparison_set, cfg)

    # E: pooled multiple-testing FPR across all null DGPs.
    total_valid = sum(int(row["n_valid"]) for row in a["per_dgp"])  # type: ignore[index]
    total_rej = sum(int(row["n_rejected"]) for row in a["per_dgp"])  # type: ignore[index]
    lo, hi = wilson_ci(total_rej, total_valid)
    e = {
        "total_null_simulations": total_valid,
        "total_rejections": total_rej,
        "pooled_false_positive_rate": round(total_rej / total_valid, 4) if total_valid else None,
        "pooled_fpr_wilson_ci95": [round(lo, 4), round(hi, 4)],
        "nominal_alpha": ALPHA,
    }
    n_pass = sum(1 for row in a["per_dgp"] if row["status"] == "PASS")  # type: ignore[index]
    n_dgp = len(a["per_dgp"])  # type: ignore[arg-type]
    verdict = (
        "PASS"
        if (
            n_pass == n_dgp
            and e["pooled_false_positive_rate"] is not None
            and e["pooled_false_positive_rate"] <= 2 * ALPHA
        )
        else "FAIL"
    )

    results: dict[str, object] = {
        "metadata": {
            "generated_utc": datetime.now(UTC).isoformat(),
            "git_sha": git_sha(),
            "numpy_version": np.__version__,
            "python": sys.version.split()[0],
            "config": cfg,
            "comparison_set": [round(x, 6) for x in comparison_set],
            "note": "synthetic data only; no real-world phi claim",
        },
        "A_nulls": a,
        "BC_controls": bc,
        "D_constant_sweep": d,
        "E_multiple_testing": e,
        "F_leakage": f,
        "G_reproducibility": g,
        "verdict": {
            "nulls_calibrated": f"{n_pass}/{n_dgp}",
            "pooled_fpr": e["pooled_false_positive_rate"],
            "overall": verdict,
            "proceed_to_real_data": verdict == "PASS",
        },
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "results.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print("\n[E] MULTIPLE TESTING")
    print(
        f"  pooled null simulations={total_valid}  rejections={total_rej}  "
        f"pooled FPR={e['pooled_false_positive_rate']}  (nominal alpha={ALPHA})"
    )
    print(
        f"\nVERDICT: {verdict}  |  nulls calibrated {n_pass}/{n_dgp}  |  "
        f"proceed to real data: {verdict == 'PASS'}"
    )
    print(f"elapsed {time.time() - start:.1f}s  ->  {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
