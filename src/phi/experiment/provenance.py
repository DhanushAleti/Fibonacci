"""Reproducible capture of code + environment provenance (external contract §26, §36).

A registered experiment must bind not only its scientific parameters but the exact
code commit and dependency environment that will execute it, so that *"same manifest
hash"* implies *"same executable experiment"* (external audit finding I-5). This
module captures that provenance **reproducibly** — from git and the lockfile —
instead of relying on hand-typed, drift-prone values.

It makes no scientific decision and computes no feature; it only records what code
and environment are present.
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

#: Explicit, greppable sentinel for "provenance could not be determined." Used
#: instead of an empty string so an unbound provenance field is never mistaken
#: for a real (blank) value.
UNKNOWN = "unknown"


def current_git_sha(*, repo_root: Path | None = None) -> str:
    """Full git commit SHA of ``repo_root`` (default: cwd), or :data:`UNKNOWN`.

    Never raises: a missing ``git`` executable, a non-repository directory, or any
    git error resolve to :data:`UNKNOWN` so that capturing provenance cannot itself
    abort an experiment. A real 40-hex SHA is always preferred when available.
    """
    root = repo_root or Path.cwd()
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return UNKNOWN
    return result.stdout.strip() or UNKNOWN


def hash_file(path: str | Path) -> str:
    """SHA-256 hex digest of the file at ``path``.

    Raises :class:`FileNotFoundError` if the file is absent — an environment that
    cannot be pinned must fail loudly rather than silently record a blank hash.
    """
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def capture(*, repo_root: Path | None = None, lockfile: str = "uv.lock") -> tuple[str, str]:
    """Capture ``(code_version, environment_lock_hash)`` for a manifest.

    ``code_version`` is the current git SHA (:func:`current_git_sha`).
    ``environment_lock_hash`` is the SHA-256 of ``repo_root/lockfile`` when it
    exists, else :data:`UNKNOWN` — a missing lockfile is recorded as explicitly
    unknown rather than hard-failing capture, so provenance can still be attached
    in environments without one.
    """
    root = repo_root or Path.cwd()
    lock_path = root / lockfile
    lock_hash = hash_file(lock_path) if lock_path.is_file() else UNKNOWN
    return current_git_sha(repo_root=root), lock_hash
