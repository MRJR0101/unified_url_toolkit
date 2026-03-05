# CLI Module

Command adapters for domain cleanup, URL extraction, and link checking.

## Scripts
- `clean_domains.py`
- `extract_urls.py`
- `check_links.py`

## Responsibilities
- parse CLI arguments
- call reusable library modules
- emit user-facing summaries and outputs

## Preferred Commands
```powershell
uv run uut-clean-domains input.txt -o cleaned.txt --strip-www --sort
uv run uut-extract-urls . -r -e txt,md,html --csv extracted.csv
uv run uut-check-links urls.txt -o results.csv --timeout 20 --concurrency 100
```

## Script Fallback
```powershell
uv run python cli\clean_domains.py input.txt -o cleaned.txt --strip-www --sort
uv run python cli\extract_urls.py . -r -e txt,md,html --csv extracted.csv
uv run python cli\check_links.py urls.txt -o results.csv --timeout 20 --concurrency 100
```

## Roadmap Alignment
CLI should remain thin and package-first (`unified_url_toolkit.*`) per [Vision And Plan](../docs/VISION_AND_PLAN.md).

## Related Docs
- [Usage Guide](../docs/USAGE.md)
- [Architecture](../docs/ARCHITECTURE.md)
