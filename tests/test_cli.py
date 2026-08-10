"""Phase 0 CLI tests."""

from __future__ import annotations

import pytest

from phi import __version__
from phi.cli import main


@pytest.mark.unit
def test_cli_version(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["version"])
    assert code == 0
    assert capsys.readouterr().out.strip() == __version__


@pytest.mark.unit
def test_cli_info_reports_settings_without_secrets(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["info"])
    assert code == 0
    out = capsys.readouterr().out
    assert "phi constant: 1.6180339887" in out
    assert "random seed: 1618" in out


@pytest.mark.unit
def test_cli_no_command_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    code = main([])
    assert code == 0
    assert "usage: phi" in capsys.readouterr().out
