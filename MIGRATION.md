# Migration Guide

Transition from legacy URL utilities to Unified URL Toolkit, aligned with [docs/VISION_AND_PLAN.md](docs/VISION_AND_PLAN.md).

## Migration Principle
Migrate behavior into shared, testable modules and remove duplicated script logic.

## Legacy-To-Unified Mapping

### Domain cleaning tools
Legacy examples:
- `CleanDomains`
- `CleanDomainsv2`
- `cleanup_domains`

Unified replacements:
- `unified_url_toolkit.core.normalizers.clean_domain_list`
- `unified_url_toolkit.core.normalizers.normalize_domain`
- `uut-clean-domains` (or `cli/clean_domains.py`)

### URL extraction tools
Legacy examples:
- `ExtractUrls`
- `URLExtractor`
- `SimpleUrlExtractor`
- `DreamExtractor`

Unified replacements:
- `unified_url_toolkit.core.extractors.extract_urls_from_text`
- `unified_url_toolkit.core.extractors.extract_from_files`
- `unified_url_toolkit.core.extractors.extract_from_directory`
- `uut-extract-urls` (or `cli/extract_urls.py`)

### Link checking tools
Legacy examples:
- `CheckLinks`
- `ValidateLinks`
- `Linkchecker`
- `MyUrlChecker`

Unified replacements:
- `unified_url_toolkit.core.checkers.URLChecker`
- `unified_url_toolkit.core.checkers.check_urls`
- `uut-check-links` (or `cli/check_links.py`)

## Recommended Migration Sequence
1. Replace legacy script calls with `unified_url_toolkit.*` APIs.
2. Move all file input/output handling to `io.readers` and `io.writers`.
3. Lock output formats (text/CSV/JSON) with tests.
4. Switch automation/pipelines to unified CLI entry points.
5. Remove legacy wrappers only after parity verification.

## Parity Checklist
- representative legacy fixtures match expected outputs
- edge-case URL/domain behavior is covered
- retry/timeout/failure behavior meets operational expectations
- downstream consumers accept output contracts without adaptation regressions

## Transitional Risks
- mixed import styles (`core.*` vs `unified_url_toolkit.core.*`)
- branch drift in output contract assumptions
- docs and implementation diverging during active refactors

## Related Docs
- [Vision And Plan](docs/VISION_AND_PLAN.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Usage Guide](docs/USAGE.md)
- [Project VERIFY](VERIFY.md)
