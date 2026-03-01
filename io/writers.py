"""
File writing utilities for URLs and domains.

Consolidated from 20+ CSV/file writing implementations.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import csv
import json
from datetime import datetime


# =============================================================================
# BASIC FILE WRITING
# =============================================================================

def write_lines_to_file(lines: List[str],
                       filepath: Path,
                       deduplicate: bool = False,
                       sort: bool = False,
                       encoding: str = 'utf-8') -> int:
    """
    Write lines to file.

    Args:
        lines: Lines to write
        filepath: Output file path
        deduplicate: Remove duplicates
        sort: Sort lines alphabetically
        encoding: File encoding

    Returns:
        Number of lines written
    """
    if deduplicate:
        seen = set()
        unique_lines = []
        for line in lines:
            if line not in seen:
                seen.add(line)
                unique_lines.append(line)
        lines = unique_lines

    if sort:
        lines = sorted(lines)

    # Write to file
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text('\n'.join(lines) + '\n' if lines else '', encoding=encoding)

    return len(lines)


def write_urls_to_file(urls: List[str],
                      filepath: Path,
                      deduplicate: bool = True,
                      sort: bool = False,
                      encoding: str = 'utf-8') -> int:
    """
    Write URLs to file, one per line.

    Args:
        urls: URLs to write
        filepath: Output file path
        deduplicate: Remove duplicate URLs
        sort: Sort alphabetically
        encoding: File encoding

    Returns:
        Number of URLs written

    Example:
        >>> urls = ['https://example.com', 'https://test.org']
        >>> count = write_urls_to_file(urls, Path('output.txt'))
    """
    return write_lines_to_file(urls, filepath, deduplicate=deduplicate,
                              sort=sort, encoding=encoding)


# =============================================================================
# CSV WRITING
# =============================================================================

def write_to_csv(data: List[Dict[str, Any]],
                filepath: Path,
                fieldnames: Optional[List[str]] = None,
                encoding: str = 'utf-8') -> int:
    """
    Write data to CSV file.

    Args:
        data: List of dictionaries to write
        filepath: Output CSV path
        fieldnames: CSV column names (auto-detect if None)
        encoding: File encoding

    Returns:
        Number of rows written

    Example:
        >>> data = [
        ...     {'url': 'https://example.com', 'status': 200},
        ...     {'url': 'https://test.org', 'status': 404}
        ... ]
        >>> write_to_csv(data, Path('results.csv'))
    """
    if not data:
        return 0

    # Auto-detect fieldnames from first row
    if fieldnames is None:
        fieldnames = list(data[0].keys())

    # Ensure parent directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Write CSV
    with filepath.open('w', newline='', encoding=encoding) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    return len(data)


def write_urls_to_csv(urls: List[str],
                     filepath: Path,
                     url_column: str = 'url',
                     add_index: bool = False,
                     encoding: str = 'utf-8') -> int:
    """
    Write URLs to CSV file.

    Args:
        urls: URLs to write
        filepath: Output CSV path
        url_column: Name of URL column
        add_index: Add index column
        encoding: File encoding

    Returns:
        Number of URLs written
    """
    data = []
    for i, url in enumerate(urls, 1):
        row = {url_column: url}
        if add_index:
            row['index'] = i
        data.append(row)

    fieldnames = ['index', url_column] if add_index else [url_column]
    return write_to_csv(data, filepath, fieldnames=fieldnames, encoding=encoding)


def write_check_results_to_csv(results: List[Any],
                               filepath: Path,
                               encoding: str = 'utf-8') -> int:
    """
    Write URL check results to CSV.

    Args:
        results: List of CheckResult objects or dicts
        filepath: Output CSV path
        encoding: File encoding

    Returns:
        Number of results written
    """
    # Convert CheckResult objects to dicts if needed
    data = []
    for result in results:
        if hasattr(result, 'to_dict'):
            data.append(result.to_dict())
        elif isinstance(result, dict):
            data.append(result)
        else:
            continue

    return write_to_csv(data, filepath, encoding=encoding)


# =============================================================================
# JSON WRITING
# =============================================================================

def write_to_json(data: Any,
                 filepath: Path,
                 indent: int = 2,
                 encoding: str = 'utf-8') -> None:
    """
    Write data to JSON file.

    Args:
        data: Data to serialize (must be JSON-serializable)
        filepath: Output JSON path
        indent: Indentation level
        encoding: File encoding
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with filepath.open('w', encoding=encoding) as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def write_results_to_json(results: List[Any],
                         filepath: Path,
                         include_summary: bool = True,
                         encoding: str = 'utf-8') -> None:
    """
    Write results to JSON with optional summary.

    Args:
        results: List of results
        filepath: Output JSON path
        include_summary: Include summary statistics
        encoding: File encoding
    """
    # Convert results to dicts
    data_list = []
    for result in results:
        if hasattr(result, 'to_dict'):
            data_list.append(result.to_dict())
        elif isinstance(result, dict):
            data_list.append(result)

    output = {
        'results': data_list,
        'count': len(data_list),
        'generated_at': datetime.now().isoformat()
    }

    if include_summary:
        # Calculate summary statistics
        status_counts = {}
        for item in data_list:
            if 'status' in item:
                status = item['status']
                status_counts[status] = status_counts.get(status, 0) + 1

        output['summary'] = {
            'total': len(data_list),
            'by_status': status_counts
        }

    write_to_json(output, filepath, encoding=encoding)


# =============================================================================
# SPECIALIZED WRITERS
# =============================================================================

def write_domains_to_file(domains: List[str],
                         filepath: Path,
                         deduplicate: bool = True,
                         sort: bool = False,
                         encoding: str = 'utf-8') -> int:
    """
    Write domains to file (alias for write_urls_to_file).

    Args:
        domains: Domains to write
        filepath: Output file path
        deduplicate: Remove duplicates
        sort: Sort alphabetically
        encoding: File encoding

    Returns:
        Number of domains written
    """
    return write_urls_to_file(domains, filepath, deduplicate=deduplicate,
                             sort=sort, encoding=encoding)


def append_to_file(lines: List[str],
                  filepath: Path,
                  encoding: str = 'utf-8') -> int:
    """
    Append lines to an existing file.

    Args:
        lines: Lines to append
        filepath: File path
        encoding: File encoding

    Returns:
        Number of lines appended
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with filepath.open('a', encoding=encoding) as f:
        for line in lines:
            f.write(line + '\n')

    return len(lines)


# =============================================================================
# REPORT GENERATION
# =============================================================================

def generate_report_file(summary: dict,
                        filepath: Path,
                        title: str = "URL Processing Report",
                        encoding: str = 'utf-8') -> None:
    """
    Generate a formatted text report file.

    Args:
        summary: Summary dictionary with statistics
        filepath: Output file path
        title: Report title
        encoding: File encoding
    """
    lines = []
    lines.append("=" * 70)
    lines.append(title)
    lines.append("=" * 70)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    for key, value in summary.items():
        if isinstance(value, dict):
            lines.append(f"\n{key.upper()}:")
            for sub_key, sub_value in value.items():
                lines.append(f"  {sub_key}: {sub_value}")
        else:
            lines.append(f"{key}: {value}")

    lines.append("")
    lines.append("=" * 70)

    write_lines_to_file(lines, filepath, encoding=encoding)
