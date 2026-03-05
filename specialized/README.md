# Specialized Module

Advanced analyzers for HTTP/content/security/cache/DOM workflows.

## Included Modules
- `http_inspector.py`
- `security_analyzer.py`
- `redirect_mapper.py`
- `content_inspector.py`
- `metadata_extractor.py`
- `cache_analyzer.py`
- `link_checker.py`
- `dom_parser.py`
- `http_analyzer.py`

## Typical Use Cases
- security-header audits
- redirect-chain mapping
- metadata extraction for SEO/content
- cache policy analysis
- deep DOM extraction

## Usage Example
```python
from unified_url_toolkit.specialized import fetch_http_response, get_missing_security_headers

response = fetch_http_response("https://example.com")
print(response.status_code)
print(get_missing_security_headers(response.headers))
```

## Notes
- specialized modules target advanced workflows and may require extra runtime dependencies
- keep shared parsing/normalization logic in core modules where possible

## Related Docs
- [Usage Guide](../docs/USAGE.md)
- [Architecture](../docs/ARCHITECTURE.md)
- [Vision And Plan](../docs/VISION_AND_PLAN.md)
