"""
File reading utilities for URLs and domains.

Consolidated from 30+ implementations across legacy projects.
"""

import csv
from pathlib import Path
from typing import Iterator, List

# =============================================================================
# BASIC FILE READING
# =============================================================================


def read_lines_from_file(
    filepath: Path, skip_comments: bool = True, skip_empty: bool = True, strip: bool = True, encoding: str = "utf-8"
) -> Iterator[str]:
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
        with filepath.open("r", encoding=encoding, errors="ignore") as f:
            for line in f:
                if strip:
                    line = line.strip()

                if skip_empty and not line:
                    continue

                if skip_comments and line.startswith("#"):
                    continue

                yield line
    except Exception as e:
        raise IOError(f"Error reading {filepath}: {e}")


def read_urls_from_file(
    filepath: Path, skip_comments: bool = True, skip_empty: bool = True, encoding: str = "utf-8"
) -> List[str]:
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
    return list(read_lines_from_file(filepath, skip_comments=skip_comments, skip_empty=skip_empty, encoding=encoding))


# =============================================================================
# MULTI-FILE READING
# =============================================================================


def read_urls_from_multiple_files(filepaths: List[Path], unique: bool = True) -> List[str]:
    """
    Read URLs from multiple files.

    Args:
        filepaths: List of file paths
        unique: Return only unique URLs

    Returns:
        List of URLs from all files
    """
    all_urls: list[str] = []
    seen: set[str] = set()

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


def find_and_read_files(directory: Path, pattern: str = "*.txt", recursive: bool = False) -> dict[Path, List[str]]:
    """
    Find files matching pattern and read their contents.

    Args:
        directory: Directory to search
        pattern: Glob pattern (e.g., '*.txt', '*.csv')
        recursive: Search subdirectories

    Returns:
        Dictionary mapping filepath -> list of lines
    """
    glob_pattern = f"**/{pattern}" if recursive else pattern
    results = {}

    try:
        for filepath in sorted(directory.glob(glob_pattern)):
            try:
                if not filepath.is_file():
                    continue
                lines = read_urls_from_file(filepath)
                results[filepath] = lines
            except Exception:
                continue
    except OSError:
        return results

    return results


# =============================================================================
# CSV READING
# =============================================================================


def read_urls_from_csv(
    filepath: Path, url_column: str | int = 0, has_header: bool = True, encoding: str = "utf-8"
) -> List[str]:
    """
    Read URLs from a CSV file.

    Args:
        filepath: Path to CSV file
        url_column: Column containing URLs (name or index)
        has_header: Whether CSV has a header row
        encoding: File encoding

    Returns:
        List of URLs

    Raises:
        ValueError: If `url_column` is a string and headers are unavailable,
            or if the named column does not exist.
    """
    urls: list[str] = []

    with filepath.open("r", encoding=encoding, errors="ignore", newline="") as f:
        if isinstance(url_column, str):
            if not has_header:
                raise ValueError("String url_column requires has_header=True")

            dict_reader = csv.DictReader(f)
            fieldnames = dict_reader.fieldnames or []
            column_name = url_column

            if column_name not in fieldnames:
                normalized_to_original = {
                    name.strip().lower(): name for name in fieldnames if name and name.strip()
                }
                fallback = normalized_to_original.get(column_name.strip().lower())
                if fallback:
                    column_name = fallback

            if not fieldnames or column_name not in fieldnames:
                available = ", ".join(fieldnames)
                raise ValueError(f"CSV column '{url_column}' not found. Available columns: {available}")

            for row in dict_reader:
                if not row:
                    continue
                raw_url = row.get(column_name, "")
                if raw_url is None:
                    continue
                url = raw_url.strip()
                if url:
                    urls.append(url)
        else:
            reader = csv.reader(f)

            # Skip header if present
            if has_header:
                next(reader, None)

            for row in reader:
                if not row:
                    continue

                try:
                    url = row[url_column].strip()
                    if url:
                        urls.append(url)
                except IndexError:
                    continue

    return urls


# =============================================================================
# SPECIALIZED READERS
# =============================================================================


def read_domains_from_file(filepath: Path, encoding: str = "utf-8") -> List[str]:
    """
    Read domains from file (alias for read_urls_from_file).

    Args:
        filepath: Path to file
        encoding: File encoding

    Returns:
        List of domains
    """
    return read_urls_from_file(filepath, encoding=encoding)


def read_file_pairs(filepath: Path, separator: str = ",", encoding: str = "utf-8") -> List[tuple[str, str]]:
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
