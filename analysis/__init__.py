"""
Analysis modules for URL and domain categorization and statistics.
"""

from .categorizers import (
    CategorizationResult,
    categorize_urls,
    categorize_domains,
    get_top_domains,
    get_top_tlds,
    is_suspicious_domain,
    detect_suspicious_pattern,
    group_by_base_domain,
)

__all__ = [
    'CategorizationResult',
    'categorize_urls',
    'categorize_domains',
    'get_top_domains',
    'get_top_tlds',
    'is_suspicious_domain',
    'detect_suspicious_pattern',
    'group_by_base_domain',
]
