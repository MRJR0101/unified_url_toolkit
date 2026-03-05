# Unified URL Toolkit

Unified URL Toolkit consolidates 42+ legacy URL/domain utilities into one maintainable Python toolkit.

## Canonical Direction
Project strategy, sequencing, and current status live in:
- [docs/VISION_AND_PLAN.md](docs/VISION_AND_PLAN.md)

This README is an entry point, not the roadmap source of truth.

## What The Toolkit Provides
- URL/domain extraction from text and files
- normalization and canonicalization utilities
- validation helpers for URLs and domains
- async URL checking
- categorization/summarization analysis
- specialized HTTP/content/security/cache/DOM analysis modules

## Quick Start
### 1) Environment
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

### 2) Library example
```python
from unified_url_toolkit.core.extractors import extract_urls_from_text
from unified_url_toolkit.core.normalizers import clean_domain_list

text = "Visit https://example.com and http://test.org"
urls = extract_urls_from_text(text)
domains = clean_domain_list(urls, strip_www=True, remove_duplicates=True)
print(urls)
print(domains)
```

### 3) CLI examples
```powershell
uv run uut-clean-domains input.txt -o cleaned.txt --strip-www --sort
uv run uut-extract-urls . -r -e txt,md,html --csv extracted.csv
uv run uut-check-links urls.txt -o results.csv --timeout 20 --concurrency 100
```

## Documentation Map
- Strategy and roadmap: [docs/VISION_AND_PLAN.md](docs/VISION_AND_PLAN.md)
- Architecture and boundaries: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Usage patterns: [docs/USAGE.md](docs/USAGE.md)
- Verification workflow: [VERIFY.md](VERIFY.md)
- Contribution workflow: [CONTRIBUTING.md](CONTRIBUTING.md)
- Migration guidance: [MIGRATION.md](MIGRATION.md)

## Package And Layout
Primary import namespace: `unified_url_toolkit`.

Main module families:
- `core/`
- `io/`
- `processing/`
- `analysis/`
- `specialized/`
- `cli/`
- `config/`
- `utils/`

## License
MIT License. See [LICENSE](LICENSE).
