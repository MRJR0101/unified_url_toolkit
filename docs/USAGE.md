# Usage Guide

## Purpose
Practical usage for library imports and CLI workflows, aligned with [Vision And Plan](VISION_AND_PLAN.md).

## Environment Setup
Preferred:

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

## Library Usage

### Extract URLs
```python
from unified_url_toolkit.core.extractors import extract_urls_from_text

text = "Visit https://example.com and http://test.org"
print(extract_urls_from_text(text))
```

### Extract domains
```python
from unified_url_toolkit.core.extractors import extract_domains_from_text

text = "user@example.com and https://api.test.org/path"
print(extract_domains_from_text(text))
```

### Normalize and clean
```python
from unified_url_toolkit.core.normalizers import clean_domain_list, normalize_url

print(normalize_url("Example.com/path?b=2&a=1", sort_query_params=True))
print(clean_domain_list(["https://www.Example.com", "www.example.com.", "test.org"], strip_www=True))
```

### Validate
```python
from unified_url_toolkit.core.validators import validate_domain, validate_url

print(validate_domain("example.com"))
print(validate_url("https://example.com/path"))
```

### Async link checking
```python
from unified_url_toolkit.core.checkers import URLChecker

checker = URLChecker(timeout=10, retries=1, concurrency=20)
checker.check_sync(["https://example.com", "https://nonexistent.invalid"])
print(checker.get_summary())
```

## CLI Usage
Installed scripts (recommended):

```powershell
uv run uut-clean-domains input.txt -o cleaned.txt --strip-www --sort
uv run uut-extract-urls . -r -e txt,md,html --csv extracted.csv
uv run uut-extract-urls . -r --domains -o domains.txt
uv run uut-check-links urls.txt -o results.csv --timeout 20 --concurrency 100
```

Repository script fallback:

```powershell
uv run python cli\clean_domains.py input.txt -o cleaned.txt --strip-www --sort
uv run python cli\extract_urls.py . -r -e txt,md,html --csv extracted.csv
uv run python cli\check_links.py urls.txt -o results.csv --timeout 20 --concurrency 100
```

## Output Contracts
- text: one item per line
- CSV: structured rows for tabular analysis
- JSON: machine-readable payloads for automation

## Verification Commands
Core verification:

```powershell
uv run pytest -q
uv run python -c "from unified_url_toolkit.core.extractors import extract_urls_from_text; print(extract_urls_from_text('visit https://example.com'))"
uv run python -c "from unified_url_toolkit.core.normalizers import clean_domain_list; print(clean_domain_list(['https://www.example.com','test.org']))"
```

Quality gate target:

```powershell
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
uv run mypy --explicit-package-bases core io processing analysis config utils
uv run uut-clean-domains --help
uv run uut-extract-urls --help
uv run uut-check-links --help
```

For release-readiness interpretation of these commands, use [Project VERIFY](../VERIFY.md).
