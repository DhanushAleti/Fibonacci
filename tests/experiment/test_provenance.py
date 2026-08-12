"""Reproducible code + environment provenance capture (contract §26, §36; audit I-5)."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from phi.experiment.provenance import UNKNOWN, capture, current_git_sha, hash_file


class TestHashFile:
    def test_hash_matches_sha256_of_contents(self, tmp_path: Path) -> None:
        f = tmp_path / "data.bin"
        f.write_bytes(b"phi-provenance")
        assert hash_file(f) == hashlib.sha256(b"phi-provenance").hexdigest()

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        # A pinnable environment must fail loudly, never record a blank hash.
        with pytest.raises(FileNotFoundError):
            hash_file(tmp_path / "does-not-exist")


class TestGitSha:
    def _is_valid(self, sha: str) -> bool:
        return sha == UNKNOWN or (len(sha) == 40 and all(c in "0123456789abcdef" for c in sha))

    def test_returns_unknown_or_40_hex_in_repo(self) -> None:
        assert self._is_valid(current_git_sha(repo_root=Path(__file__).resolve().parent))

    def test_never_raises_and_stays_valid_off_repo(self, tmp_path: Path) -> None:
        # Capture must not abort even outside a repository (worst case: UNKNOWN).
        assert self._is_valid(current_git_sha(repo_root=tmp_path))


class TestCapture:
    def test_returns_two_strings(self) -> None:
        code, lock = capture(repo_root=Path.cwd())
        assert isinstance(code, str) and isinstance(lock, str)

    def test_missing_lockfile_recorded_as_unknown(self, tmp_path: Path) -> None:
        _code, lock = capture(repo_root=tmp_path, lockfile="uv.lock")
        assert lock == UNKNOWN

    def test_present_lockfile_is_hashed(self, tmp_path: Path) -> None:
        (tmp_path / "uv.lock").write_bytes(b"locked==1.0")
        _code, lock = capture(repo_root=tmp_path, lockfile="uv.lock")
        assert lock == hashlib.sha256(b"locked==1.0").hexdigest()
