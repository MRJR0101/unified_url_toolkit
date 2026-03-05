# IO Module

Input/output utilities for reading URL/domain data and writing results.

## Responsibilities
- read line-based and CSV inputs
- aggregate content across multiple files/directories
- write text, CSV, and JSON outputs
- serialize checker/analysis results

## Main Files
- `readers.py`
- `writers.py`

## Usage Example
```python
from pathlib import Path
from unified_url_toolkit.io import read_urls_from_file, write_urls_to_file

urls = read_urls_from_file(Path("urls.txt"))
write_urls_to_file(urls, Path("cleaned_urls.txt"), deduplicate=True)
```

## Boundaries
- keep persistence and serialization here
- keep extraction/validation logic in `core/`

## Related Docs
- [Usage Guide](../docs/USAGE.md)
- [Architecture](../docs/ARCHITECTURE.md)
