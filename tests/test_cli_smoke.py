"""Smoke tests for CLI entry scripts."""

import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLI_DIR = PROJECT_ROOT / "cli"


@pytest.mark.parametrize(
    "script_name",
    ["clean_domains.py", "extract_urls.py", "check_links.py"],
)
def test_cli_help(script_name: str) -> None:
    """Each CLI should provide help output without crashing."""
    script_path = CLI_DIR / script_name
    proc = subprocess.run(
        [sys.executable, str(script_path), "--help"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    output = (proc.stdout + "\n" + proc.stderr).lower()
    assert proc.returncode == 0, output
    assert "usage:" in output, output


@pytest.mark.parametrize(
    "module_name",
    [
        "unified_url_toolkit.cli.clean_domains",
        "unified_url_toolkit.cli.extract_urls",
        "unified_url_toolkit.cli.check_links",
    ],
)
def test_cli_help_via_module(module_name: str) -> None:
    """CLI modules should be runnable via the package namespace."""
    proc = subprocess.run(
        [sys.executable, "-m", module_name, "--help"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
        cwd=str(PROJECT_ROOT),
    )

    output = (proc.stdout + "\n" + proc.stderr).lower()
    assert proc.returncode == 0, output
    assert "usage:" in output, output
