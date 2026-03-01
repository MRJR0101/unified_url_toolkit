# cli

**Category:** <!-- TODO: Add category (e.g., 06_URLs) -->
**Status:** Production

> Check URL status with async parallel requests.

## Overview

**What it does:**
BEFORE: 8+ separate implementations (CheckLinks, ValidateLinks, MyUrlChecker, etc.)
AFTER: One clean implementation using unified checker

Replaces:
- CheckLinks/
- ValidateLinks/
- MyUrlChecker/
- Linkchecker/
- LinkCheckerv2/
- URLToolkit url_validator and link_checker functions

**What it does NOT do:**
<!-- TODO: Describe boundaries to prevent wrong-tool confusion -->

## Use Cases

<!-- TODO: Add 2-4 concrete scenarios -->
- 

## Features

- CheckLinks/
- ValidateLinks/
- MyUrlChecker/
- Linkchecker/
- LinkCheckerv2/
- URLToolkit url_validator and link_checker functions

## Requirements

- Python 3.8+
- Windows 10/11
- Third-party: core

## Quick Start

```powershell
cd C:\Dev\PROJECTS\00_PyToolbelt\06_URLs\unified_url_toolkit\cli
python check_links.py --help
```

**First run:**
```powershell
python check_links.py --dry-run
```

## Usage

```powershell
# Basic usage
python check_links.py --dry-run

# <!-- TODO: Add real usage examples -->
```

## Options

| Argument | Default | Description |
|----------|---------|-------------|
| `input` | -- |  |
| `--output` | -- | Output CSV file for results |
| `--json` | -- | Output JSON file for results |
| `--concurrency` | 50 |  |
| `--timeout` | 15.0 |  |
| `--retries` | 2 |  |
| `--no-redirects` | -- | Don\ |
| `--show-ok` | -- | Show successful URLs in output |
| `--show-all` | -- |  |

## Input / Output

**Expects:**
<!-- TODO: Describe input format and sources -->

**Creates:**
<!-- TODO: Describe output files and locations -->

## Pipeline Position

**Fed by:** <!-- TODO: Upstream tools -->
**Feeds into:** <!-- TODO: Downstream tools -->

## Hardcoded Paths

| Line | Current Value | Purpose |
|------|---------------|---------|
| 94 | `C:\\path\\to\\yourfile` | <!-- TODO: Describe purpose --> |

## Files

| File | Lines | Purpose |
|------|-------|---------|
| `check_links.py` | 184 | Python script |
| `clean_domains.py` | 124 | Python script |
| `extract_urls.py` | 186 | Python script |
| `pyproject.toml` | 20 | Project configuration and dependencies |
| `requirements.txt` | 7 | Python dependencies |
| `uv.lock` | 706 |  |

## Safety & Reliability

<!-- TODO: Describe dry-run mode, backup behavior, failure handling -->

## License & Contact

Internal tool. Maintainer: MR

---
*Part of PyToolbelt -- Zero-dependency Windows utilities*

<!-- ReadmeForge: The following sections were auto-appended. Move them to the correct position per the 21-section blueprint. -->

## How It Works

<!-- TODO: Add a ## How It Works section with numbered steps describing the internal processing flow from input to output. -->


## Example Output

<!-- TODO: Add a ## Example Output section with a fenced code block showing realistic console output from a typical run. -->


## Logging & Observability

<!-- TODO: Add a ## Logging section describing: where logs are written, log format, verbosity flags, and any run artifacts produced. -->


## Troubleshooting / FAQ

<!-- TODO: Add a ## Troubleshooting section with Problem/Fix pairs for the most common errors. Include known limitations. -->


## Versioning / Roadmap

<!-- TODO: Add a ## Versioning section with the current version number and a roadmap of planned features. -->
