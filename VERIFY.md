# VERIFY

Operational verification guide aligned with [docs/VISION_AND_PLAN.md](docs/VISION_AND_PLAN.md).

## Purpose
Run one repeatable verification flow after changes and before release decisions.

## Environment
Preferred:

```powershell
uv sync --all-groups
```

Fallback:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -U pip
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m pip install pytest pytest-cov ruff mypy
```

## Core Sanity Checks
```powershell
uv run pytest -q
uv run python -c "from unified_url_toolkit.core.extractors import extract_urls_from_text; print(extract_urls_from_text('visit https://example.com'))"
uv run python -c "from unified_url_toolkit.core.normalizers import clean_domain_list; print(clean_domain_list(['https://www.example.com','test.org']))"
uv run uut-clean-domains --help
uv run uut-extract-urls --help
uv run uut-check-links --help
```

## Full Quality Gate (Release Target)
```powershell
uv run pytest -q
uv run pytest --cov=. --cov-report=term-missing tests
uv run ruff check .
uv run ruff format --check .
uv run mypy --explicit-package-bases core io processing analysis config utils
```

## Decision Rule
- release-ready: all quality-gate commands pass
- not release-ready: any gate fails, or a public contract changed without docs/tests updates

## Latest Verification Snapshot (2026-03-04)
- `pytest -q`: pass
- CLI `--help` startup checks: pass
- `ruff check .`: fail (import ordering issue)
- `ruff format --check .`: fail (format drift)
- `mypy --explicit-package-bases core io processing analysis config utils`: fail (typing/import issues)

Treat this snapshot as branch-specific; always rerun commands on your current branch.

## If Verification Fails
1. Capture the exact command + error output.
2. Map failure to the owning module family.
3. Add or update regression tests with the fix.
4. Update docs when behavior or contracts change.

## Related Docs
- [Vision And Plan](docs/VISION_AND_PLAN.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Usage Guide](docs/USAGE.md)
