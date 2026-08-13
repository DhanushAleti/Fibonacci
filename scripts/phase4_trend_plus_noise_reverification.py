"""Targeted multi-seed re-verification of the trend_plus_noise per-DGP FPR gate.

The small-scale repair validation (results/phase4_repair_validation/results.json)
reported trend_plus_noise FPR = 0.07 at n_series=100, seed 20260812 -- exactly at
the Repair Contract's 0.07 per-DGP threshold. A value sitting precisely on its own
decision boundary from a single seed at n=100 carries substantial sampling
uncertainty, so this script re-estimates it via independent seeds using the
existing, unmodified surrogate_fpr() harness. No DGP, estimand, or threshold is
touched; this only adds replications. See docs/PHI_FINAL_SCIENTIFIC_STATUS.md §12.

    uv run python scripts/phase4_trend_plus_noise_reverification.py
"""

from __future__ import annotations

import json
from pathlib import Path

from phi.phase4.nulldgp import trend_plus_noise
from phi.phase4.repair.validation import surrogate_fpr

OUT = Path("results/phase4_repair_validation/trend_plus_noise_reverification.json")

# trend_plus_noise is index 7 of 13 in REPAIR_NULL_SUITE; null_suite_fpr() assigns
# it base_seed + 7, so base_seed=20260812 (the original run) used seed 20260819.
ORIGINAL_SEED = 20260819
SCALE_A = {"n_series": 100, "series_length": 400, "n_surrogates": 99}  # matches original
SCALE_B = {"n_series": 300, "series_length": 400, "n_surrogates": 99}  # tighter estimate


def main() -> int:
    runs: dict[str, dict[str, float | int]] = {}

    rate, valid = surrogate_fpr(trend_plus_noise, base_seed=ORIGINAL_SEED, **SCALE_A)
    runs["reproduce_original_seed20260819"] = {"fpr": rate, "valid": valid}

    for seed in (1007, 2007, 3007, 4007, 5007):
        rate, valid = surrogate_fpr(trend_plus_noise, base_seed=seed, **SCALE_A)
        runs[f"n100_seed{seed}"] = {"fpr": rate, "valid": valid}

    for seed in (1007, 2007):
        rate, valid = surrogate_fpr(trend_plus_noise, base_seed=seed, **SCALE_B)
        runs[f"n300_seed{seed}"] = {"fpr": rate, "valid": valid}

    n100_runs = [v for k, v in runs.items() if k.startswith(("n100", "reproduce"))]
    total_rej = sum(round(v["fpr"] * v["valid"]) for v in n100_runs)
    total_valid = sum(int(v["valid"]) for v in n100_runs)
    pooled_fpr = total_rej / total_valid
    se = (pooled_fpr * (1 - pooled_fpr) / total_valid) ** 0.5

    n300_runs = [v for k, v in runs.items() if k.startswith("n300")]
    total_rej_b = sum(round(v["fpr"] * v["valid"]) for v in n300_runs)
    total_valid_b = sum(int(v["valid"]) for v in n300_runs)
    pooled_fpr_b = total_rej_b / total_valid_b
    se_b = (pooled_fpr_b * (1 - pooled_fpr_b) / total_valid_b) ** 0.5

    grand_rej = total_rej + total_rej_b
    grand_valid = total_valid + total_valid_b
    grand_fpr = grand_rej / grand_valid
    grand_se = (grand_fpr * (1 - grand_fpr) / grand_valid) ** 0.5

    result = {
        "note": "synthetic only; re-verification of one borderline gate value; no phi claim",
        "threshold": 0.07,
        "runs": runs,
        "pooled_n100_scale": {
            "fpr": round(pooled_fpr, 4),
            "n": total_valid,
            "approx_95ci": [
                round(max(0.0, pooled_fpr - 1.96 * se), 4),
                round(pooled_fpr + 1.96 * se, 4),
            ],
        },
        "pooled_n300_scale": {
            "fpr": round(pooled_fpr_b, 4),
            "n": total_valid_b,
            "approx_95ci": [
                round(max(0.0, pooled_fpr_b - 1.96 * se_b), 4),
                round(pooled_fpr_b + 1.96 * se_b, 4),
            ],
        },
        "grand_pooled": {
            "fpr": round(grand_fpr, 4),
            "n": grand_valid,
            "approx_95ci": [
                round(max(0.0, grand_fpr - 1.96 * grand_se), 4),
                round(grand_fpr + 1.96 * grand_se, 4),
            ],
            "exceeds_threshold": grand_fpr - 1.96 * grand_se > 0.07,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
