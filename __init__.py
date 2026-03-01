"""
Unified URL Toolkit - Comprehensive URL and domain processing library.

Surgical refactoring of 42+ legacy projects into one clean, maintainable codebase.

Author: MR (via surgical code extraction and consolidation)
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "MR"
__description__ = "Unified toolkit for URL and domain processing"

# Import main functionality for easy access
from .core import (
    # Validators
    validate_domain,
    validate_url,
    is_valid_domain,
    is_valid_url,

    # Extractors
    extract_urls_from_text,
    extract_domains_from_text,
    FileExtractor,

    # Normalizers
    normalize_domain,
    normalize_url,
    clean_domain_list,
    clean_url_list,
)

# Processing utilities
from .processing import (
    process_parallel,
    process_parallel_with_progress,
    batch_items,
)

# Utilities
from .utils import (
    ProgressBar,
    SimpleProgress,
    create_progress_callback,
    ErrorCollector,
)

# Analysis
from .analysis import (
    categorize_urls,
    categorize_domains,
    get_top_domains,
    get_top_tlds,
)

__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__description__',

    # Core - Validators
    'validate_domain',
    'validate_url',
    'is_valid_domain',
    'is_valid_url',

    # Core - Extractors
    'extract_urls_from_text',
    'extract_domains_from_text',
    'FileExtractor',

    # Core - Normalizers
    'normalize_domain',
    'normalize_url',
    'clean_domain_list',
    'clean_url_list',

    # Processing
    'process_parallel',
    'process_parallel_with_progress',
    'batch_items',

    # Utilities
    'ProgressBar',
    'SimpleProgress',
    'create_progress_callback',
    'ErrorCollector',

    # Analysis
    'categorize_urls',
    'categorize_domains',
    'get_top_domains',
    'get_top_tlds',
]
