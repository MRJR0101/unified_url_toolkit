# Contributing

## Canonical Project Direction
Before making changes, review [docs/VISION_AND_PLAN.md](docs/VISION_AND_PLAN.md).  
All contributions should support that roadmap.

## Setup
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

## PR Expectations
1. keep module boundaries clean (`core`, `io`, `processing`, `analysis`, `specialized`, `cli`)
2. run verification commands from [VERIFY.md](VERIFY.md)
3. update docs for any behavior or contract changes
4. add tests for user-visible changes

## Required Local Checks
```powershell
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
uv run mypy --explicit-package-bases core io processing analysis config utils
```

## Engineering Rules
- Prefer package-first imports in docs/examples: `unified_url_toolkit.*`
- Keep CLI thin; reusable logic belongs in library modules.
- Avoid duplicate implementations when an existing helper already exists.
- Any API/CLI contract change requires:
  - tests
  - changelog entry
  - migration/update notes when relevant

## Documentation Rule
For non-trivial behavior changes, update:
- [README.md](README.md)
- [docs/USAGE.md](docs/USAGE.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) when boundaries change
- [docs/VISION_AND_PLAN.md](docs/VISION_AND_PLAN.md) when roadmap status changes
