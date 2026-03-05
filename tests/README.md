# Tests

Test suite for smoke, contract, and focused module validation.

## Current Test Files
- `test_smoke.py`
- `test_dom_parser.py`
- `test_cli_smoke.py`
- `test_cli_contracts.py`

## Run Tests
```powershell
uv sync --all-groups
uv run pytest -q
```

## Priority Expansion Areas
- core validators/extractors/normalizers edge cases
- async checker success/failure/retry paths
- additional contract coverage for text/CSV/JSON outputs

## Quality Gates
```powershell
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
uv run mypy --explicit-package-bases core io processing analysis config utils
```

## Related Docs
- [Vision And Plan](../docs/VISION_AND_PLAN.md)
- [Project VERIFY](../VERIFY.md)
