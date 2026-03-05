"""Contract tests for CLI behavior and output formats."""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLI_DIR = PROJECT_ROOT / "cli"


def _run_cli(args: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    """Run a CLI script via the project Python executable."""
    return subprocess.run(
        [sys.executable, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
        cwd=str(PROJECT_ROOT),
    )


def test_clean_domains_output_contract(tmp_path: Path) -> None:
    """clean_domains should write normalized domains one per line."""
    input_file = tmp_path / "raw.txt"
    output_file = tmp_path / "cleaned.txt"
    input_file.write_text(
        "\n".join(
            [
                "https://WWW.Example.com/path?a=1",
                "www.example.com",
                "test.org",
                "# comment",
                "",
            ]
        ),
        encoding="utf-8",
    )

    proc = _run_cli(
        [
            str(CLI_DIR / "clean_domains.py"),
            str(input_file),
            "-o",
            str(output_file),
            "--strip-www",
            "--sort",
        ]
    )

    output = proc.stdout + proc.stderr
    assert proc.returncode == 0, output
    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8") == "example.com\ntest.org\n"


def test_extract_urls_output_contract(tmp_path: Path) -> None:
    """extract_urls should write one URL per line in text output mode."""
    input_file = tmp_path / "sample.txt"
    output_file = tmp_path / "urls.txt"
    input_file.write_text(
        "One: https://example.com/path\nTwo: http://test.org?q=1\n",
        encoding="utf-8",
    )

    proc = _run_cli(
        [
            str(CLI_DIR / "extract_urls.py"),
            str(input_file),
            "-o",
            str(output_file),
            "-e",
            "txt",
        ]
    )

    output = proc.stdout + proc.stderr
    assert proc.returncode == 0, output
    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8") == "https://example.com/path\nhttp://test.org?q=1\n"


def test_check_links_missing_input_exit_code_contract(tmp_path: Path) -> None:
    """check_links should return exit code 2 for missing input path."""
    missing = tmp_path / "missing-urls.txt"

    proc = _run_cli([str(CLI_DIR / "check_links.py"), str(missing)])
    output = proc.stdout + proc.stderr

    assert proc.returncode == 2, output
    assert "input file not found" in output.lower(), output
