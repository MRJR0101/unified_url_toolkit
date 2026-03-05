# Utils Module

Cross-cutting helpers for error handling and progress reporting.

## Main Files
- `errors.py`
- `progress.py`

## Responsibilities
- centralized error collection/formatting
- reusable progress callbacks and helpers

## Usage Example
```python
from unified_url_toolkit.utils.errors import ErrorCollector

collector = ErrorCollector()
try:
    raise ValueError("example")
except Exception as exc:
    collector.add(exc, context="demo")

print(collector.summary())
```

## Boundaries
- utility layer only
- no module-specific business logic

## Related Docs
- [Usage Guide](../docs/USAGE.md)
- [Architecture](../docs/ARCHITECTURE.md)
