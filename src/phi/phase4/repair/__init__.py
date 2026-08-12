"""PHI Phase-4 post-failure scientific repair (Repair Contract).

The original ``Delta_phi > 0`` confirmatory test FAILED synthetic validation
(FPR = 1.0 across 13 null DGPs) and is **permanently forbidden** as confirmatory
evidence. This subpackage implements the arbitrated repair:

* **Standardized null score ``Z_phi``** (:mod:`~phi.phase4.repair.zscore`) - the
  observed advantage standardized against a surrogate ensemble of the same series,
  neutralizing the geometric/convexity bias.
* **Rational-fraction controls** (:mod:`~phi.phase4.repair.rational`) - phi vs
  ``{1/2, 3/5, 5/8, 2/3}``; phi must specifically beat ``5/8``.
* **Surrogate ensemble** (:mod:`~phi.phase4.repair.surrogates`) - block-permutation
  (primary), GARCH (secondary), IAAFT (tertiary).
* **phi-attractor GARCH positive control** + **granularity audit**
  (:mod:`~phi.phase4.repair.positive_control`, :mod:`~phi.phase4.repair.granularity`).
* **Five-part validation gate** (:mod:`~phi.phase4.repair.validation`) and a
  **fail-closed** repaired registration (:mod:`~phi.phase4.repair.registration`).

Status: IMPLEMENTATION of the frozen repair. No real data has been run; the
confirmatory path fails closed until the full validation passes on synthetic data.
No phi claim is made or implied.
"""

from __future__ import annotations

from phi.phase4.repair.granularity import GranularityAudit, granularity_audit
from phi.phase4.repair.positive_control import phi_attractor_garch
from phi.phase4.repair.rational import FIVE_EIGHTHS, Q_PHI, RATIONAL_CONSTANTS
from phi.phase4.repair.registration import (
    ConfirmatoryNotAuthorizedError,
    ConfirmatoryResult,
    RepairPreRegistration,
    SecondaryProfile,
    confirmatory_phi_test,
    run_confirmatory_repair,
    run_secondary_profile,
)
from phi.phase4.repair.surrogates import (
    PRIMARY_SURROGATE,
    SURROGATES,
    block_permutation_surrogate,
    garch_surrogate,
    iaaft_surrogate,
)
from phi.phase4.repair.validation import (
    REPAIR_NULL_SUITE,
    RepairValidation,
    constant_sweep_symmetry,
    null_suite_fpr,
    positive_control_power,
    run_repair_validation,
    surrogate_fpr,
)
from phi.phase4.repair.zscore import (
    RepairScore,
    eligible_retracements,
    phi_advantage,
    standardized_null_score,
)

__all__ = [
    "FIVE_EIGHTHS",
    "PRIMARY_SURROGATE",
    "Q_PHI",
    "RATIONAL_CONSTANTS",
    "REPAIR_NULL_SUITE",
    "SURROGATES",
    "ConfirmatoryNotAuthorizedError",
    "ConfirmatoryResult",
    "GranularityAudit",
    "RepairPreRegistration",
    "RepairScore",
    "RepairValidation",
    "SecondaryProfile",
    "block_permutation_surrogate",
    "confirmatory_phi_test",
    "constant_sweep_symmetry",
    "eligible_retracements",
    "garch_surrogate",
    "granularity_audit",
    "iaaft_surrogate",
    "null_suite_fpr",
    "phi_advantage",
    "phi_attractor_garch",
    "positive_control_power",
    "run_confirmatory_repair",
    "run_repair_validation",
    "run_secondary_profile",
    "standardized_null_score",
    "surrogate_fpr",
]
