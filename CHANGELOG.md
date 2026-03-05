# Changelog

All notable changes to this project are documented here.

## Unreleased
- Completed documentation alignment with `docs/VISION_AND_PLAN.md` as canonical strategy source.
- Updated root/docs/module READMEs to use package-namespace examples (`unified_url_toolkit.*`) and consistent CLI workflow guidance.
- Replaced stale verification success claims with a dated verification snapshot and release-target gate definitions in `VERIFY.md`.
- Refreshed migration, contribution, and Definition of Done docs to match current roadmap phases and contract-hardening priorities.
- Documentation overhaul aligned to a vision-first roadmap.
- Added project strategy and delivery plan in `docs/VISION_AND_PLAN.md`.
- Added architecture map in `docs/ARCHITECTURE.md`.
- Added consolidated usage guide in `docs/USAGE.md`.
- Rewrote module README files to remove template placeholders.
- Updated contributor guidance to match practical local workflows.
- Clarified migration, verification, and readiness documentation.
- Fixed CLI startup by importing via `unified_url_toolkit.*` namespace bootstrap.
- Added CLI smoke tests (`tests/test_cli_smoke.py`) to catch startup regressions.
- Added `pyproject.toml` with dependency groups and `uv` workflow support.
- Added generated `uv.lock` for reproducible dependency sync.
- Added installable package mapping and CLI entry points (`uut-clean-domains`, `uut-extract-urls`, `uut-check-links`).
- Added CLI contract tests for text output and missing-input exit-code behavior.
- Replaced Unicode-only CLI status glyphs with ASCII-safe markers for Windows console compatibility.
- Cleared Ruff lint debt and normalized formatting with Ruff formatter.
- Made `mypy --explicit-package-bases core io processing analysis config utils` pass with targeted typing fixes.

## 0.1.0 - Initial release
- Initial project scaffolding.
