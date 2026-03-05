# Architecture

## Role In The Project
This document defines implementation boundaries that support the strategy in [Vision And Plan](VISION_AND_PLAN.md).

## Design Principles
- business logic lives in reusable modules, not CLI scripts
- one responsibility per module family
- package-first imports (`unified_url_toolkit.*`) for public/docs examples
- explicit, testable contracts for user-visible behavior

## Module Boundaries

### `core/`
URL/domain logic primitives:
- `patterns.py`: regex patterns and pattern helpers
- `validators.py`: URL/domain validation rules
- `extractors.py`: text/file URL and domain extraction
- `normalizers.py`: canonicalization and cleanup
- `checkers.py`: async URL reachability/status checks

### `io/`
Persistence and serialization:
- `readers.py`: file and CSV ingestion helpers
- `writers.py`: text/CSV/JSON output helpers

### `processing/`
Execution orchestration:
- `parallel.py`: batch/parallel processing utilities

### `analysis/`
Aggregation and categorization:
- `categorizers.py`: domain/TLD grouping and suspicious-pattern analysis

### `specialized/`
Advanced HTTP/content/security/cache/DOM workflows for deeper analysis.

### `cli/`
Thin command adapters:
- parse args
- call library modules
- format user-facing summaries

### `config/`
Central defaults and tunables (`settings.py`).

### `utils/`
Cross-cutting support (progress and error utilities).

## Data Flow
1. Inputs are read from text/files/streams.
2. Core extraction and normalization produce canonical URL/domain data.
3. Validation/checking/analysis enriches results.
4. Writers persist outputs in text/CSV/JSON contracts.

## Packaging Model (Current)
- Distribution name: `unified-url-toolkit`
- Import namespace: `unified_url_toolkit`
- Console scripts:
  - `uut-clean-domains`
  - `uut-extract-urls`
  - `uut-check-links`

## Testing Model
- unit tests for deterministic logic
- CLI smoke and contract tests for entrypoint stability
- integration tests for file and pipeline behavior

## Architecture Rules
- avoid cross-module duplication
- avoid hidden environment-based behavior
- keep CLI and specialized layers from reimplementing core logic

## Related Docs
- [Vision And Plan](VISION_AND_PLAN.md)
- [Usage Guide](USAGE.md)
- [Contributing](../CONTRIBUTING.md)
