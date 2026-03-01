"""
File reading utilities for URLs and domains.

Consolidated from 30+ implementations across legacy projects.
"""

from pathlib import Path
from typing import Iterator, List, Optional, Set
import csv


# =============================================================================
# BASIC FILE READING
# =============================================================================

def read_lines_from_file(filepath: Path,
                        skip_comments: bool = True,
                        skip_empty: bool = True,
                        strip: bool = True,
                        encoding: str = 'utf-8') -> Iterator[str]:
    """
    Read lines from file with common filtering.

    Args:
        filepath: Path to file
        skip_comments: Skip lines starting with #
        skip_empty: Skip empty lines
        strip: Strip whitespace from lines
        encoding: File encoding

    Yields:
        Processed lines from file
    """
    try:
        with filepath.open('r', encoding=encoding, errors='ignore') as f:
            for line in f:
                if strip:
                    line = line.strip()

                if skip_empty and not line:
                    continue

                if skip_comments and line.startswith('#'):
                    continue

                yield line
    except Exception as e:
        raise IOError(f"Error reading {filepath}: {e}")


def read_urls_from_file(filepath: Path,
                       skip_comments: bool = True,
                       skip_empty: bool = True,
                       encoding: str = 'utf-8') -> List[str]:
    """
    Read URLs from file, one per line.

    Args:
        filepath: Path to file
        skip_comments: Skip lines starting with #
        skip_empty: Skip empty lines
        encoding: File encoding

    Returns:
        List of URLs

    Example:
        >>> urls = read_urls_from_file(Path('urls.txt'))
    """
    return list(read_lines_from_file(
        filepath,
        skip_comments=skip_comments,
        skip_empty=skip_empty,
        encoding=encoding
    ))


# =============================================================================
# MULTI-FILE READING
# =============================================================================

def read_urls_from_multiple_files(filepaths: List[Path],
                                  unique: bool = True) -> List[str]:
    """
    Read URLs from multiple files.

    Args:
        filepaths: List of file paths
        unique: Return only unique URLs

    Returns:
        List of URLs from all files
    """
    all_urls = []
    seen = set() if unique else None

    for filepath in filepaths:
        try:
            urls = read_urls_from_file(filepath)

            if unique:
                for url in urls:
                    if url not in seen:
                        seen.add(url)
                        all_urls.append(url)
            else:
                all_urls.extend(urls)

        except Exception:
            continue

    return all_urls


def find_and_read_files(directory: Path,
                       pattern: str = '*.txt',
                       recursive: bool = False) -> dict[Path, List[str]]:
    """
    Find files matching pattern and read their contents.

    Args:
        directory: Directory to search
        pattern: Glob pattern (e.g., '*.txt', '*.csv')
        recursive: Search subdirectories

    Returns:
        Dictionary mapping filepath -> list of lines
    """
    glob_pattern = f'**/{pattern}' if recursive else pattern
    results = {}

    for filepath in directory.glob(glob_pattern):
        if filepath.is_file():
            try:
                lines = read_urls_from_file(filepath)
                results[filepath] = lines
            except Exception:
                continue

    return results


# =============================================================================
# CSV READING
# =============================================================================

def read_urls_from_csv(filepath: Path,
                      url_column: str | int = 0,
                      has_header: bool = True,
                      encoding: str = 'utf-8') -> List[str]:
    """
    Read URLs from a CSV file.

    Args:
        filepath: Path to CSV file
        url_column: Column containing URLs (name or index)
        has_header: Whether CSV has a header row
        encoding: File encoding

    Returns:
        List of URLs
    """
    urls = []

    with filepath.open('r', encoding=encoding, errors='ignore') as f:
        reader = csv.reader(f)

        # Skip header if present
        if has_header:
            next(reader, None)

        for row in reader:
            if not row:
                continue

            try:
                if isinstance(url_column, int):
                    url = row[url_column].strip()
                else:
                    # If column name provided, use DictReader
                    pass  # TODO: Implement DictReader version

                if url:
                    urls.append(url)
            except IndexError:
                continue

    return urls


# =============================================================================
# SPECIALIZED READERS
# =============================================================================

def read_domains_from_file(filepath: Path,
                          encoding: str = 'utf-8') -> List[str]:
    """
    Read domains from file (alias for read_urls_from_file).

    Args:
        filepath: Path to file
        encoding: File encoding

    Returns:
        List of domains
    """
    return read_urls_from_file(filepath, encoding=encoding)


def read_file_pairs(filepath: Path,
                   separator: str = ',',
                   encoding: str = 'utf-8') -> List[tuple[str, str]]:
    """
    Read pairs of values from file (key, value per line).

    Args:
        filepath: Path to file
        separator: Separator between key and value
        encoding: File encoding

    Returns:
        List of (key, value) tuples
    """
    pairs = []

    for line in read_lines_from_file(filepath, encoding=encoding):
        if separator in line:
            parts = line.split(separator, 1)
            if len(parts) == 2:
                pairs.append((parts[0].strip(), parts[1].strip()))

    return pairs
