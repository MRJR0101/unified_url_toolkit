# Analysis Module

Categorization and summarization utilities for URL/domain datasets.

## Responsibilities
- group domains by TLD/base domain
- detect suspicious domain patterns
- compute top-domain and top-TLD summaries

## Main File
- `categorizers.py`

## Usage Example
```python
from unified_url_toolkit.analysis.categorizers import get_top_domains, get_top_tlds

urls = ["https://example.com/a", "https://example.com/b", "https://test.org"]
print(get_top_domains(urls, top_n=5))
print(get_top_tlds(urls, top_n=5))
```

## Boundaries
- aggregation and categorization only
- parsing/extraction should happen before analysis

## Related Docs
- [Usage Guide](../docs/USAGE.md)
- [Architecture](../docs/ARCHITECTURE.md)
