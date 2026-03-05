# Processing Module

Parallel and batch execution primitives for high-volume workflows.

## Responsibilities
- parallel map/filter processing
- batch slicing helpers
- progress-aware execution wrappers

## Main File
- `parallel.py`

## Usage Example
```python
from unified_url_toolkit.processing.parallel import process_parallel

items = ["https://example.com", "https://test.org"]
results = process_parallel(items, lambda x: x.upper(), use_threads=True)
print(results)
```

## Boundaries
- orchestration primitives only
- domain logic stays in `core/`
- persistence stays in `io/`

## Related Docs
- [Architecture](../docs/ARCHITECTURE.md)
- [Vision And Plan](../docs/VISION_AND_PLAN.md)
