"""
Core URL/domain processing functionality.

This module provides the foundational capabilities for:
- Pattern matching (regex patterns)
- Validation (URL/domain validation)
- Extraction (URL/domain extraction from text and files)
- Normalization (cleaning and standardizing URLs/domains)
- Checking (HTTP status checking with async support)
"""

# Re-export main functionality for easy imports
from .patterns import (
    URL_STANDARD,
    URL_COMPREHENSIVE,
    DOMAIN_BASIC,
    DOMAIN_COMPREHENSIVE,
    IPV4,
    EMAIL,
    has_scheme,
    is_ipv4,
    is_ipv6,
)

from .validators import (
    ValidationStatus,
    validate_domain,
    validate_url,
    is_valid_domain,
    is_valid_url,
    is_url_shortener,
    is_suspicious_domain,
    filter_valid_domains,
    filter_valid_urls,
)

from .extractors import (
    extract_urls_from_text,
    extract_domains_from_text,
    extract_emails_from_text,
    FileExtractor,
    extract_from_files,
    extract_from_directory,
)

from .normalizers import (
    normalize_domain,
    normalize_url,
    extract_domain_from_url,
    clean_domain_list,
    clean_url_list,
    remove_url_parameters,
    remove_tracking_parameters,
)


__all__ = [
    # Patterns
    'URL_STANDARD',
    'URL_COMPREHENSIVE',
    'DOMAIN_BASIC',
    'DOMAIN_COMPREHENSIVE',
    'IPV4',
    'EMAIL',
    'has_scheme',
    'is_ipv4',
    'is_ipv6',

    # Validators
    'ValidationStatus',
    'validate_domain',
    'validate_url',
    'is_valid_domain',
    'is_valid_url',
    'is_url_shortener',
    'is_suspicious_domain',
    'filter_valid_domains',
    'filter_valid_urls',

    # Extractors
    'extract_urls_from_text',
    'extract_domains_from_text',
    'extract_emails_from_text',
    'FileExtractor',
    'extract_from_files',
    'extract_from_directory',

    # Normalizers
    'normalize_domain',
    'normalize_url',
    'extract_domain_from_url',
    'clean_domain_list',
    'clean_url_list',
    'remove_url_parameters',
    'remove_tracking_parameters',
]
