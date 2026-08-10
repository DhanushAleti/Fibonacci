"""Phase 0 foundation tests: package sanity, config, logging, CLI, secrets."""

from __future__ import annotations

import dataclasses
import io
import json
import logging
import math
import os

import pytest

from phi import PHI, __version__
from phi.config import SecretNotConfiguredError, Settings, get_secret, load_dotenv
from phi.logging import JsonFormatter, configure_logging, get_logger


@pytest.mark.unit
def test_phi_constant_is_golden_ratio() -> None:
    # φ satisfies φ² = φ + 1; this is the defining invariant of the golden ratio.
    assert math.isclose(PHI * PHI, PHI + 1.0, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(PHI, 1.618033988749895, abs_tol=1e-15)


@pytest.mark.unit
def test_version_is_exposed_and_consistent() -> None:
    assert __version__ == "0.2.0"


@pytest.mark.unit
def test_settings_from_env_defaults() -> None:
    settings = Settings.from_env()
    assert settings.random_seed == 1618  # φ-derived default seed
    assert (settings.paths.root / "pyproject.toml").exists()


@pytest.mark.unit
def test_settings_are_frozen_and_hashable() -> None:
    # Frozen so a resolved config can be recorded verbatim in an experiment log.
    s = Settings()
    with pytest.raises(dataclasses.FrozenInstanceError):
        s.log_level = "DEBUG"  # type: ignore[misc]
    assert isinstance(hash(s), int)


@pytest.mark.unit
def test_get_secret_missing_raises_without_leaking_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PHI_TEST_SECRET", raising=False)
    with pytest.raises(SecretNotConfiguredError) as exc:
        get_secret("PHI_TEST_SECRET")
    # The error names the variable but never a value.
    assert "PHI_TEST_SECRET" in str(exc.value)


@pytest.mark.unit
def test_get_secret_optional_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PHI_TEST_SECRET", raising=False)
    assert get_secret("PHI_TEST_SECRET", required=False) is None


@pytest.mark.unit
def test_load_dotenv_does_not_overwrite_existing_env(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("PHI_TEST_KEY=from_file\n# a comment\n\nBLANKLINE\n")
    monkeypatch.setenv("PHI_TEST_KEY", "from_env")
    newly = load_dotenv(env_file)
    # Existing env wins; the file value is ignored and never reported.
    assert os.environ["PHI_TEST_KEY"] == "from_env"
    assert "PHI_TEST_KEY" not in newly


@pytest.mark.unit
def test_load_dotenv_masks_values(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("PHI_NEW_SECRET=supersecret\n")
    monkeypatch.delenv("PHI_NEW_SECRET", raising=False)
    newly = load_dotenv(env_file)
    # The loader reports the key was set but masks the value.
    assert newly["PHI_NEW_SECRET"] == "***"
    assert "supersecret" not in json.dumps(newly)


@pytest.mark.unit
def test_json_logging_is_structured_and_parseable() -> None:
    stream = io.StringIO()
    configure_logging(level=logging.INFO, stream=stream)
    log = get_logger("phi.test")
    log.info("ingested", extra={"rows": 42, "symbol": "TEST"})

    line = stream.getvalue().strip()
    record = json.loads(line)  # must be valid JSON
    assert record["msg"] == "ingested"
    assert record["rows"] == 42
    assert record["symbol"] == "TEST"
    assert record["level"] == "INFO"
    assert record["ts"].endswith("+00:00")  # UTC


@pytest.mark.unit
def test_json_formatter_excludes_reserved_keys() -> None:
    formatter = JsonFormatter()
    rec = logging.LogRecord("phi", logging.INFO, __file__, 1, "hi", None, None)
    out = json.loads(formatter.format(rec))
    assert set(out) >= {"ts", "level", "logger", "msg"}
    assert "args" not in out and "pathname" not in out
