"""Strict discovery / confirmation / external-replication separation (spec §X, §XLVII).

The confirmatory experiment runs **once** on Dataset A; replication runs the exact
same frozen contract on an independently-assigned Dataset B; anything else is
discovery/exploratory and can never produce a confirmatory claim (spec §XLVII-
§XLVIII). This module names those roles and provides the guards the pipeline uses
so the separation is enforced in code, not just documentation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DataRole(StrEnum):
    DISCOVERY = "discovery"  # write/debug/tune the pipeline; NO confirmatory claim
    CONFIRMATION = "confirmation"  # Dataset A: primary inference, executed once
    EXTERNAL = "external"  # Dataset B: independent replication, same contract


class DataSeparationError(RuntimeError):
    """A dataset was used in a role that violates the replication separation rules."""


@dataclass(frozen=True)
class RegisteredDataset:
    """An immutable dataset identity bound to a role and a content hash (spec §XLIX)."""

    dataset_id: str
    content_hash: str
    role: DataRole
