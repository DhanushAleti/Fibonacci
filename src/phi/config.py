"""Deterministic configuration and secure secret handling for PHI.

Design goals:
- Configuration is explicit and reproducible (PRD-NFR-002): the same inputs produce
  the same behaviour, and the resolved config can be serialised into an experiment
  record (PRD-REPRO-001).
- Secrets (provider API keys, future broker credentials) come *only* from the
  environment or a local ``.env`` that is git-ignored — never hardcoded, never
  logged, never serialised into experiment records (PRD-SEC-001).

There is deliberately no network, database, or provider default here. Those are
open decisions (PRD-OPEN-001) and must be supplied explicitly by the caller.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def repo_root() -> Path:
    """Return the repository root (the directory containing ``pyproject.toml``)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    # Fallback: two levels up from src/phi/config.py
    return here.parents[2]


def load_dotenv(path: Path | None = None) -> dict[str, str]:
    """Load ``KEY=VALUE`` pairs from a local ``.env`` file into ``os.environ``.

    Existing environment variables are never overwritten (explicit env wins). Lines
    that are blank or start with ``#`` are ignored. Returns the keys that were newly
    set (names only — values are never returned or logged) for auditability.

    This is a minimal loader with no third-party dependency; it does not support
    quoting or interpolation, by design.
    """
    env_path = path or (repo_root() / ".env")
    newly_set: dict[str, str] = {}
    if not env_path.exists():
        return newly_set
    for raw in env_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip()
            newly_set[key] = "***"  # never expose the value
    return newly_set


class SecretNotConfiguredError(RuntimeError):
    """Raised when a required secret is absent from the environment."""


def get_secret(name: str, *, required: bool = True) -> str | None:
    """Fetch a secret from the environment.

    Never falls back to a hardcoded default and never logs the value. If a required
    secret is missing, raises with the variable *name* only (not any value).
    """
    value = os.environ.get(name)
    if value is None and required:
        raise SecretNotConfiguredError(
            f"Required secret '{name}' is not set. Provide it via the environment "
            f"or a git-ignored .env file — never hardcode it (PRD-SEC-001)."
        )
    return value


@dataclass(frozen=True)
class Paths:
    """Canonical on-disk locations, all under the repo root by default."""

    root: Path = field(default_factory=repo_root)

    @property
    def data(self) -> Path:
        return self.root / "data"

    @property
    def data_raw(self) -> Path:
        return self.data / "raw"

    @property
    def data_store(self) -> Path:
        return self.data / "store"

    @property
    def experiments(self) -> Path:
        return self.root / "experiments"


@dataclass(frozen=True)
class Settings:
    """Top-level runtime settings.

    Frozen and hashable so a resolved ``Settings`` can be recorded verbatim in an
    experiment log for reproducibility (PRD-REPRO-001). Contains no secrets.
    """

    log_level: str = "INFO"
    paths: Paths = field(default_factory=Paths)
    # Global deterministic seed used wherever randomness is unavoidable (controls,
    # permutation tests). Recorded in every experiment (PRD-REPRO-002).
    random_seed: int = 1618

    @classmethod
    def from_env(cls) -> Settings:
        """Build settings from the environment, applying safe defaults."""
        load_dotenv()
        return cls(
            log_level=os.environ.get("PHI_LOG_LEVEL", "INFO"),
            random_seed=int(os.environ.get("PHI_RANDOM_SEED", "1618")),
        )
