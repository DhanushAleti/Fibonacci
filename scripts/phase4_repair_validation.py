"""PHI Phase-4 REPAIR validation harness (synthetic only).

Runs the five-part acceptance gate of the repaired surrogate-standardized
methodology and writes a machine-readable artefact. Synthetic data only; no
real-world phi claim. This is NOT the final 10,000/20,000-per-DGP validation - it
is the small-scale run that discovers whether the repair passes.

    uv run python scripts/phase4_repair_validation.py [--full]

Absolute rule (Repair Contract): report whether PHI passes; never tune to pass.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from phi.phase4.repair.validation import run_repair_validation

OUT = Path("results/phase4_repair_validation/results.json")


def git_sha() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    cfg = (
        {"n_series": 1000, "series_length": 500, "n_surrogates": 999}
        if args.full
        else {"n_series": 100, "series_length": 400, "n_surrogates": 99}
    )
    start = time.time()
    v = run_repair_validation(base_seed=20260812, **cfg)
    result = {
        "metadata": {
            "generated_utc": datetime.now(UTC).isoformat(),
            "git_sha": git_sha(),
            "numpy_version": np.__version__,
            "python": sys.version.split()[0],
            "config": cfg,
            "note": "synthetic only; small-scale; no phi claim; not the final validation",
        },
        "gate_1_aggregate_fpr": {
            "value": round(v.aggregate_fpr, 4),
            "threshold": 0.05,
            "pass": v.aggregate_fpr_gate,
        },
        "gate_2_per_dgp_fpr": {
            "per_dgp": {k: round(x, 4) for k, x in v.per_dgp_fpr.items()},
            "max": round(v.max_per_dgp_fpr, 4),
            "threshold": 0.07,
            "pass": v.per_dgp_gate,
        },
        "gate_3_power_medium": {
            "value": round(v.positive_control_power_medium, 3),
            "threshold": 0.80,
            "pass": v.power_gate,
        },
        "gate_4_granularity": {
            "phi_fpr_by_tick": {
                str(k): round(x, 3) for k, x in v.granularity.phi_fpr_by_level.items()
            },
            "max_phi_fpr": round(v.granularity.max_phi_fpr, 3),
            "pass": v.granularity_gate,
        },
        "gate_5_constant_sweep_symmetry": {
            "fpr_by_focal": {
                str(round(k, 3)): round(x, 3) for k, x in v.constant_sweep_fpr.items()
            },
            "pass": v.symmetry_gate,
        },
        "overall_pass": v.passes,
        "proceed_to_real_data": v.passes,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    for name, gate in list(result.items())[1:-2]:
        print(f"  {name:34s} pass={gate['pass']}")
    print(f"\nOVERALL GATE PASSES: {v.passes}  |  proceed to real data: {v.passes}")
    print(f"elapsed {time.time() - start:.1f}s  ->  {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
