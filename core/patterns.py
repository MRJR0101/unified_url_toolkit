"""
Consolidated regex patterns for URL and domain extraction.

This module contains all regex patterns extracted and optimized from 15+ implementations
across the legacy codebase. Each pattern is documented with its purpose and source.
"""

import re
from typing import Pattern


# =============================================================================
# URL PATTERNS
# =============================================================================

# Standard URL pattern (http/https/ftp)
# Consolidated from: LinkTools, ExtractUrls, URLToolkit, SimpleUrlExtractor
URL_STANDARD: Pattern = re.compile(
    r"https?://[^\s\[\]<>()\"']+",
    re.IGNORECASE
)

# Comprehensive URL pattern with more schemes
# Source: URLExtractor, DreamExtractor
URL_COMPREHENSIVE: Pattern = re.compile(
    r"(?:https?|ftp|file)://[^\s\[\]<>()\"']+",
    re.IGNORECASE
)

# URL with optional scheme (captures domain-only URLs too)
# Source: Multiple implementations
URL_WITH_OPTIONAL_SCHEME: Pattern = re.compile(
    r"(?:(?:https?|ftp)://)?"
    r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}"
    r"(?:[/?#][^\s\[\]<>()\"']*)?",
    re.IGNORECASE | re.VERBOSE
)


# =============================================================================
# DOMAIN PATTERNS
# =============================================================================

# Basic domain pattern
# Consolidated from: CleanDomains, cleanup_domains, ExtractDomains
DOMAIN_BASIC: Pattern = re.compile(
    r"(?i)\b([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
    r"(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+)\.?\b"
)

# Comprehensive domain pattern with email support
# Source: LinkTools/core/extractor.py, DreamExtractor
DOMAIN_COMPREHENSIVE: Pattern = re.compile(
    r"(?xi)"
    r"(?:(?<=@)|(?:(?:https?://|ftp://|//)?))?"
    r"((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+(?:[a-z]{2,63}|xn--[a-z0-9]{2,59}))"
)

# Domain validation pattern (stricter - for validation only)
# Source: LinkTools/core/validators.py, CleanDomainsv2
DOMAIN_VALIDATION: Pattern = re.compile(
    r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)*"
    r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
    r"(?:\.[a-z]{2,})+$",
    re.IGNORECASE | re.VERBOSE
)


# =============================================================================
# IP ADDRESS PATTERNS
# =============================================================================

# IPv4 pattern
# Consolidated from: LinkTools, URLToolkit, URL-Forensics
IPV4: Pattern = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d{1,2})\.){3}(?:25[0-5]|2[0-4]\d|1?\d{1,2})\b"
)

# IPv6 pattern (simplified)
# Source: URL-Forensics
IPV6: Pattern = re.compile(
    r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b"
)


# =============================================================================
# SCHEME PATTERNS
# =============================================================================

# URL scheme detection
# Source: LinkTools/core/validators.py
SCHEME: Pattern = re.compile(
    r"^[a-zA-Z][a-zA-Z0-9+\-.]*://",
    re.IGNORECASE
)


# =============================================================================
# EMAIL PATTERNS
# =============================================================================

# Email pattern
# Source: Multiple implementations
EMAIL: Pattern = re.compile(
    r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
)


# =============================================================================
# SUSPICIOUS PATTERNS (for analysis/forensics)
# =============================================================================

# URL shorteners
# Source: URLToolkit/url_toolkit.py::domain_categorizer
URL_SHORTENER: Pattern = re.compile(
    r"bit\.ly|tinyurl|goo\.gl|t\.co|ow\.ly|is\.gd",
    re.IGNORECASE
)

# Multiple dashes/underscores (suspicious)
# Source: URLToolkit, URL-Forensics
SUSPICIOUS_CHARS: Pattern = re.compile(
    r"-{3,}|_{3,}"
)

# Long number sequences (suspicious)
# Source: URLToolkit
LONG_NUMBERS: Pattern = re.compile(
    r"\d{5,}"
)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def has_scheme(text: str) -> bool:
    """Check if text starts with a URL scheme."""
    return bool(SCHEME.match(text))


def is_ipv4(text: str) -> bool:
    """Check if text is an IPv4 address."""
    return bool(IPV4.fullmatch(text))


def is_ipv6(text: str) -> bool:
    """Check if text is an IPv6 address."""
    return bool(IPV6.fullmatch(text))


def extract_scheme(url: str) -> str | None:
    """Extract scheme from URL."""
    match = SCHEME.match(url)
    return match.group(0).rstrip("://") if match else None


# =============================================================================
# PATTERN GROUPS (for convenience)
# =============================================================================

class PatternGroups:
    """Convenient groupings of patterns for common tasks."""

    # For URL extraction
    URL_EXTRACTION = [URL_STANDARD, URL_COMPREHENSIVE]

    # For domain extraction
    DOMAIN_EXTRACTION = [DOMAIN_COMPREHENSIVE, DOMAIN_BASIC]

    # For validation
    VALIDATION = [DOMAIN_VALIDATION]

    # For suspicious content detection
    SUSPICIOUS = [URL_SHORTENER, SUSPICIOUS_CHARS, LONG_NUMBERS]

    # For IP detection
    IP_PATTERNS = [IPV4, IPV6]
