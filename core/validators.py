"""
URL and domain validation utilities.

Consolidated from:
- LinkTools/core/validators.py
- CleanDomainsv2/clean_domains_v2.py
- Multiple validation implementations across 8+ projects
"""

import re
from typing import Tuple
from urllib.parse import urlparse
from enum import Enum

from . import patterns


# =============================================================================
# ENUMS & CONSTANTS
# =============================================================================

class ValidationStatus(Enum):
    """Validation result statuses."""
    VALID = "valid"
    VALID_IPV4 = "valid_ipv4"
    INVALID_FORMAT = "invalid_format"
    INVALID_TLD = "invalid_tld"
    INVALID_EXTENSION = "invalid_extension"
    LOOPBACK = "loopback"
    EMPTY = "empty"
    IPV4_NOT_ALLOWED = "ipv4_not_allowed"


# Common valid TLDs (extensible)
# Source: LinkTools/core/validators.py + additions from CleanDomainsv2
COMMON_TLDS = {
    "com", "org", "net", "io", "gov", "edu", "co", "us", "dev", "ai", "ca", "uk",
    "app", "info", "biz", "xyz", "site", "online", "store", "tv", "me", "tech",
    "blog", "news", "de", "fr", "jp", "cn", "ru", "in", "br", "au", "nz", "it",
    "es", "nl", "se", "no", "dk", "fi", "pl", "cz", "at", "ch", "be", "pt", "gr"
}

# Invalid file extensions that shouldn't be treated as domains
INVALID_EXTENSIONS = {".html", ".htm", ".inf", ".zip", ".pdf", ".exe", ".dll"}

# Loopback/localhost patterns
LOOPBACK_PATTERNS = ["127.", "0.", "localhost", "::1"]


# =============================================================================
# CORE VALIDATION FUNCTIONS
# =============================================================================

def validate_domain(domain: str, allow_ipv4: bool = True) -> Tuple[bool, ValidationStatus]:
    """
    Validate a domain name with comprehensive checks.

    Consolidated from LinkTools and CleanDomainsv2 implementations.

    Args:
        domain: Domain to validate
        allow_ipv4: Whether to accept IPv4 addresses as valid domains

    Returns:
        (is_valid, status) tuple

    Examples:
        >>> validate_domain("example.com")
        (True, ValidationStatus.VALID)
        >>> validate_domain("192.168.1.1")
        (True, ValidationStatus.VALID_IPV4)
        >>> validate_domain("invalid..domain")
        (False, ValidationStatus.INVALID_FORMAT)
    """
    domain = domain.strip().lower()

    # Empty check
    if not domain:
        return False, ValidationStatus.EMPTY

    # File extension check
    if any(domain.endswith(ext) for ext in INVALID_EXTENSIONS):
        return False, ValidationStatus.INVALID_EXTENSION

    # Loopback/localhost check
    if any(domain.startswith(pattern) for pattern in LOOPBACK_PATTERNS):
        return False, ValidationStatus.LOOPBACK

    # IPv4 check
    if patterns.is_ipv4(domain):
        if allow_ipv4:
            return True, ValidationStatus.VALID_IPV4
        else:
            return False, ValidationStatus.IPV4_NOT_ALLOWED

    # Domain format validation
    if not patterns.DOMAIN_VALIDATION.match(domain):
        return False, ValidationStatus.INVALID_FORMAT

    # TLD check
    parts = domain.split(".")
    if len(parts) < 2:
        return False, ValidationStatus.INVALID_TLD

    tld = parts[-1]
    if not (tld.isalpha() and len(tld) >= 2):
        return False, ValidationStatus.INVALID_TLD

    # Optional: Check against known TLDs (can be disabled for performance)
    # Uncomment to enforce TLD whitelist:
    # if tld not in COMMON_TLDS:
    #     return False, ValidationStatus.INVALID_TLD

    return True, ValidationStatus.VALID


def validate_url(url: str, check_scheme: bool = True,
                 allowed_schemes: list[str] | None = None) -> Tuple[bool, str]:
    """
    Validate a URL with optional scheme checking.

    Args:
        url: URL to validate
        check_scheme: Whether to require a valid scheme
        allowed_schemes: List of allowed schemes (default: http, https, ftp)

    Returns:
        (is_valid, reason) tuple

    Examples:
        >>> validate_url("https://example.com")
        (True, "Valid URL")
        >>> validate_url("example.com", check_scheme=False)
        (True, "Valid URL")
        >>> validate_url("invalid url with spaces")
        (False, "Invalid URL format")
    """
    url = url.strip()

    if not url:
        return False, "Empty URL"

    # Default allowed schemes
    if allowed_schemes is None:
        allowed_schemes = ["http", "https", "ftp"]

    # Add scheme if missing (for parsing)
    original_url = url
    if not patterns.has_scheme(url):
        if check_scheme:
            return False, "Missing URL scheme"
        url = "https://" + url

    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"URL parsing failed: {e}"

    # Scheme validation
    if check_scheme and parsed.scheme not in allowed_schemes:
        return False, f"Invalid scheme: {parsed.scheme}"

    # Extract and validate domain/hostname
    hostname = parsed.hostname or parsed.netloc
    if not hostname:
        return False, "No hostname found"

    # Validate the hostname as a domain
    is_valid, status = validate_domain(hostname, allow_ipv4=True)
    if not is_valid:
        return False, f"Invalid hostname: {status.value}"

    return True, "Valid URL"


def is_valid_domain(domain: str, allow_ipv4: bool = True) -> bool:
    """
    Simple boolean check if domain is valid.

    Args:
        domain: Domain to check
        allow_ipv4: Whether to accept IPv4 addresses

    Returns:
        True if valid, False otherwise
    """
    is_valid, _ = validate_domain(domain, allow_ipv4)
    return is_valid


def is_valid_url(url: str, check_scheme: bool = True) -> bool:
    """
    Simple boolean check if URL is valid.

    Args:
        url: URL to check
        check_scheme: Whether to require a scheme

    Returns:
        True if valid, False otherwise
    """
    is_valid, _ = validate_url(url, check_scheme)
    return is_valid


# =============================================================================
# SPECIALIZED VALIDATORS
# =============================================================================

def is_url_shortener(url: str) -> bool:
    """
    Check if URL is from a known URL shortener service.

    Source: URLToolkit/url_toolkit.py

    Args:
        url: URL to check

    Returns:
        True if URL shortener, False otherwise
    """
    return bool(patterns.URL_SHORTENER.search(url))


def is_suspicious_domain(domain: str) -> Tuple[bool, list[str]]:
    """
    Check if domain has suspicious characteristics.

    Source: URLToolkit/url_toolkit.py::domain_categorizer

    Args:
        domain: Domain to check

    Returns:
        (is_suspicious, reasons) tuple
    """
    reasons = []

    # IP address
    if patterns.is_ipv4(domain):
        reasons.append("IP address instead of domain")

    # Multiple dashes/underscores
    if patterns.SUSPICIOUS_CHARS.search(domain):
        reasons.append("Multiple consecutive dashes/underscores")

    # Long number sequences
    if patterns.LONG_NUMBERS.search(domain):
        reasons.append("Long number sequence")

    # URL shortener
    if is_url_shortener(domain):
        reasons.append("URL shortener service")

    return len(reasons) > 0, reasons


# =============================================================================
# BATCH VALIDATION
# =============================================================================

def validate_domains_batch(domains: list[str],
                          allow_ipv4: bool = True) -> dict[str, Tuple[bool, ValidationStatus]]:
    """
    Validate multiple domains at once.

    Args:
        domains: List of domains to validate
        allow_ipv4: Whether to accept IPv4 addresses

    Returns:
        Dictionary mapping domain -> (is_valid, status)
    """
    return {
        domain: validate_domain(domain, allow_ipv4)
        for domain in domains
    }


def filter_valid_domains(domains: list[str],
                        allow_ipv4: bool = True) -> list[str]:
    """
    Filter list to only valid domains.

    Args:
        domains: List of domains to filter
        allow_ipv4: Whether to accept IPv4 addresses

    Returns:
        List of valid domains only
    """
    return [
        domain for domain in domains
        if is_valid_domain(domain, allow_ipv4)
    ]


def filter_valid_urls(urls: list[str],
                     check_scheme: bool = True) -> list[str]:
    """
    Filter list to only valid URLs.

    Args:
        urls: List of URLs to filter
        check_scheme: Whether to require schemes

    Returns:
        List of valid URLs only
    """
    return [
        url for url in urls
        if is_valid_url(url, check_scheme)
    ]
