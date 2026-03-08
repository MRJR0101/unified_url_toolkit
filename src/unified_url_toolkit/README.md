# src/unified_url_toolkit

This directory is a stale artifact from an earlier src-layout attempt.

## Active Package Root

The active package root is the project root directory, not this folder.

`pyproject.toml` configures setuptools with:

```toml
[tool.setuptools.package-dir]
unified_url_toolkit = "."
```

This maps `unified_url_toolkit` directly to the project root. All subpackages
(`core/`, `io/`, `analysis/`, etc.) resolve from there. The `__init__.py` in
this folder is NOT imported during install or normal use.

## Authoritative File

The real package init is: `<project_root>/__init__.py`

## Resolution

No migration needed. The package structure is intentional and functional.
This `src/` directory can be removed in a future cleanup pass once the
dual-structure concern is formally closed in MISSINGMORE.txt.
