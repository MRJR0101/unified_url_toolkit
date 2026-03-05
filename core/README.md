# Core Module

Shared URL/domain business logic aligned with [Vision And Plan](../docs/VISION_AND_PLAN.md).

## Responsibilities
- regex pattern handling
- validation
- extraction from text/files
- normalization/canonicalization
- async reachability checks

## Main Files
- `patterns.py`
- `validators.py`
- `extractors.py`
- `normalizers.py`
- `checkers.py`

## Usage Example
```python
from unified_url_toolkit.core.extractors import extract_urls_from_text
from unified_url_toolkit.core.normalizers import clean_domain_list

text = "Visit https://example.com and http://test.org"
urls = extract_urls_from_text(text)
print(clean_domain_list(urls, strip_www=True))
```

## Boundaries
- no CLI argument parsing in `core/`
- keep persistence in `io/`
- keep orchestration in `processing/` or callers

## Related Docs
- [Architecture](../docs/ARCHITECTURE.md)
- [Usage Guide](../docs/USAGE.md)
