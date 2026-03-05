# Config Module

Centralized defaults and tunable settings.

## Main File
- `settings.py`

## Responsibilities
- store shared defaults (timeout, retries, formats, behavior flags)
- avoid magic numbers scattered across modules

## Usage Example
```python
from unified_url_toolkit.config.settings import DEFAULT_ALLOWED_SCHEMES, DEFAULT_HTTP_TIMEOUT

print(DEFAULT_HTTP_TIMEOUT)
print(DEFAULT_ALLOWED_SCHEMES)
```

## Change Guidance
- add shared settings here rather than hardcoding in feature modules
- document behavior impacts when defaults change

## Related Docs
- [Architecture](../docs/ARCHITECTURE.md)
- [Vision And Plan](../docs/VISION_AND_PLAN.md)
