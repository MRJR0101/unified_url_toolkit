"""
URL and domain extraction utilities supporting multiple text sources.

Consolidated from:
- LinkTools/core/extractor.py
- ExtractUrls/extract_urls.py
- URLExtractor, DreamExtractor, SimpleUrlExtractor
- 12+ extraction implementations
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, List, Optional, cast

from . import patterns

# Optional imports for specialized extraction
try:
    import docx
except ImportError:
    docx = cast(Any, None)

try:
    import PyPDF2
except ImportError:
    PyPDF2 = cast(Any, None)

try:
    import bs4
except ImportError:
    bs4 = cast(Any, None)


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class ExtractionResult:
    """Result of an extraction operation."""

    items: List[str]
    source: str
    count: int
    unique_count: int


# =============================================================================
# TEXT-BASED EXTRACTION
# =============================================================================


def extract_urls_from_text(text: str, unique: bool = True, pattern: re.Pattern | None = None) -> List[str]:
    """
    Extract URLs from text using regex pattern.

    Args:
        text: Input text to extract URLs from
        unique: Return only unique URLs
        pattern: Custom regex pattern (default: patterns.URL_STANDARD)

    Returns:
        List of extracted URLs

    Examples:
        >>> text = "Visit https://example.com and http://test.org"
        >>> extract_urls_from_text(text)
        ['https://example.com', 'http://test.org']
    """
    if pattern is None:
        pattern = patterns.URL_STANDARD

    urls = pattern.findall(text)

    if unique:
        # Preserve order while removing duplicates
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        return unique_urls

    return urls


def extract_domains_from_text(text: str, unique: bool = True, include_ipv4: bool = True) -> List[str]:
    """
    Extract domain names from text (from URLs, emails, bare domains).

    Source: Consolidated from LinkTools/core/extractor.py and multiple implementations

    Args:
        text: Input text to extract domains from
        unique: Return only unique domains
        include_ipv4: Include IPv4 addresses in results

    Returns:
        List of extracted domains

    Examples:
        >>> text = "Email: user@example.com Visit: https://test.org"
        >>> extract_domains_from_text(text)
        ['example.com', 'test.org']
    """
    domains = []

    # Extract from URLs and emails
    for match in patterns.DOMAIN_COMPREHENSIVE.finditer(text):
        domain = match.group(1) if match.lastindex else match.group(0)
        if domain:
            domains.append(domain.lower().strip())

    # Extract IPv4 addresses
    if include_ipv4:
        ipv4_addresses = patterns.IPV4.findall(text)
        domains.extend(ipv4_addresses)

    if unique:
        # Preserve order while removing duplicates
        seen = set()
        unique_domains = []
        for domain in domains:
            if domain not in seen:
                seen.add(domain)
                unique_domains.append(domain)
        return unique_domains

    return domains


def extract_emails_from_text(text: str, unique: bool = True) -> List[str]:
    """
    Extract email addresses from text.

    Args:
        text: Input text
        unique: Return only unique emails

    Returns:
        List of email addresses
    """
    emails = patterns.EMAIL.findall(text)

    if unique:
        seen = set()
        unique_emails = []
        for email in emails:
            email_lower = email.lower()
            if email_lower not in seen:
                seen.add(email_lower)
                unique_emails.append(email)
        return unique_emails

    return emails


# =============================================================================
# FILE-BASED EXTRACTION
# =============================================================================


class FileExtractor:
    """
    Extract text, URLs, and domains from various file formats.

    Source: Extracted from LinkTools/core/extractor.py
    """

    @staticmethod
    def extract_text(filepath: Path) -> Optional[str]:
        """
        Extract text from file based on extension.

        Supported formats: .txt, .md, .html, .htm, .docx, .pdf
        """
        ext = filepath.suffix.lower()

        if ext in (".txt", ".md", ".log", ".csv"):
            return FileExtractor._extract_text_plain(filepath)
        elif ext == ".docx":
            return FileExtractor._extract_text_docx(filepath)
        elif ext == ".pdf":
            return FileExtractor._extract_text_pdf(filepath)
        elif ext in (".html", ".htm"):
            return FileExtractor._extract_text_html(filepath)
        else:
            # Try as plain text fallback
            return FileExtractor._extract_text_plain(filepath)

    @staticmethod
    def _extract_text_plain(filepath: Path) -> str:
        """Extract text from plain text file."""
        try:
            return filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""

    @staticmethod
    def _extract_text_docx(filepath: Path) -> Optional[str]:
        """Extract text from DOCX file."""
        if docx is None:
            return None

        try:
            doc = docx.Document(str(filepath))
            paragraphs = [p.text for p in doc.paragraphs if p.text]
            return "\n".join(paragraphs)
        except Exception:
            return None

    @staticmethod
    def _extract_text_pdf(filepath: Path) -> Optional[str]:
        """Extract text from PDF file."""
        if PyPDF2 is None:
            return None

        try:
            reader = PyPDF2.PdfReader(str(filepath))
            pages = []
            for page in reader.pages:
                text = page.extract_text() or ""
                if text:
                    pages.append(text)
            return "\n".join(pages)
        except Exception:
            return None

    @staticmethod
    def _extract_text_html(filepath: Path) -> Optional[str]:
        """Extract text from HTML file."""
        if bs4 is None:
            return None

        try:
            html = filepath.read_text(encoding="utf-8", errors="ignore")
            soup = bs4.BeautifulSoup(html, "html.parser")
            return soup.get_text(separator=" ", strip=True)
        except Exception:
            return None

    @staticmethod
    def extract_urls(filepath: Path, unique: bool = True) -> List[str]:
        """
        Extract URLs from file.

        Args:
            filepath: Path to file
            unique: Return only unique URLs

        Returns:
            List of URLs extracted from file
        """
        text = FileExtractor.extract_text(filepath)
        if not text:
            return []

        return extract_urls_from_text(text, unique=unique)

    @staticmethod
    def extract_domains(filepath: Path, unique: bool = True) -> List[str]:
        """
        Extract domains from file.

        Args:
            filepath: Path to file
            unique: Return only unique domains

        Returns:
            List of domains extracted from file
        """
        text = FileExtractor.extract_text(filepath)
        if not text:
            return []

        return extract_domains_from_text(text, unique=unique)


# =============================================================================
# BULK EXTRACTION FROM MULTIPLE FILES
# =============================================================================


def extract_from_files(
    filepaths: List[Path], content_type: str = "urls", unique_per_file: bool = True, unique_total: bool = True
) -> dict:
    """
    Extract URLs or domains from multiple files.

    Consolidated from ExtractUrls/extract_urls.py

    Args:
        filepaths: List of file paths to process
        content_type: 'urls' or 'domains'
        unique_per_file: Deduplicate within each file
        unique_total: Deduplicate across all files

    Returns:
        Dictionary with 'by_file' mapping and 'all' list

    Example:
        >>> files = [Path('file1.txt'), Path('file2.txt')]
        >>> result = extract_from_files(files, content_type='urls')
        >>> result['all']  # All URLs from all files
        >>> result['by_file'][Path('file1.txt')]  # URLs from file1
    """
    results: dict[str, Any] = {"by_file": {}, "all": []}

    all_items_set: set[str] = set()

    for filepath in filepaths:
        try:
            if content_type == "urls":
                items = FileExtractor.extract_urls(filepath, unique=unique_per_file)
            elif content_type == "domains":
                items = FileExtractor.extract_domains(filepath, unique=unique_per_file)
            else:
                raise ValueError(f"Unknown content_type: {content_type}")

            results["by_file"][filepath] = items

            if unique_total:
                for item in items:
                    if item not in all_items_set:
                        all_items_set.add(item)
                        results["all"].append(item)
            else:
                results["all"].extend(items)

        except Exception:
            # Log error but continue processing
            results["by_file"][filepath] = []
            continue

    return results


def extract_from_directory(
    directory: Path, content_type: str = "urls", recursive: bool = False, extensions: Optional[List[str]] = None
) -> dict:
    """
    Extract URLs or domains from all files in a directory.

    Args:
        directory: Directory to scan
        content_type: 'urls' or 'domains'
        recursive: Search subdirectories
        extensions: List of file extensions to include (e.g., ['.txt', '.md'])

    Returns:
        Dictionary with extraction results
    """
    # Collect files
    if recursive:
        pattern = "**/*"
    else:
        pattern = "*"

    files = []
    try:
        for filepath in sorted(directory.glob(pattern)):
            try:
                if not filepath.is_file():
                    continue
            except OSError:
                continue

            if extensions and filepath.suffix.lower() not in extensions:
                continue

            files.append(filepath)
    except OSError:
        return {"by_file": {}, "all": []}

    return extract_from_files(files, content_type=content_type)


# =============================================================================
# STREAMING EXTRACTION (for large files)
# =============================================================================


def extract_urls_streaming(filepath: Path, chunk_size: int = 1024 * 1024) -> Iterator[str]:
    """
    Stream URLs from large file without loading entire file into memory.

    Args:
        filepath: Path to file
        chunk_size: Size of chunks to read (bytes)

    Yields:
        URLs as they are found
    """
    seen = set()

    with filepath.open("r", encoding="utf-8", errors="ignore") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break

            urls = extract_urls_from_text(chunk, unique=False)
            for url in urls:
                if url not in seen:
                    seen.add(url)
                    yield url
