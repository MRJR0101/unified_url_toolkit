"""
Unified URL Toolkit - Comprehensive URL and domain processing library.

Surgical refactoring of 42+ legacy projects into one clean, maintainable codebase.

Author: MR (via surgical code extraction and consolidation)
Version: 0.1.0
"""

from typing import TYPE_CHECKING

__version__ = "0.1.0"
__author__ = "MR"
__description__ = "Unified toolkit for URL and domain processing"

if TYPE_CHECKING:
    from .analysis import (
        categorize_domains,
        categorize_urls,
        get_top_domains,
        get_top_tlds,
    )
    from .core import (
        FileExtractor,
        clean_domain_list,
        clean_url_list,
        extract_domains_from_text,
        extract_urls_from_text,
        is_valid_domain,
        is_valid_url,
        normalize_domain,
        normalize_url,
        validate_domain,
        validate_url,
    )
    from .processing import (
        batch_items,
        process_parallel,
        process_parallel_with_progress,
    )
    from .utils import (
        ErrorCollector,
        ProgressBar,
        SimpleProgress,
        create_progress_callback,
    )
else:
    try:
        # Import main functionality for easy access
        # Analysis
        from .analysis import (
            categorize_domains,
            categorize_urls,
            get_top_domains,
            get_top_tlds,
        )
        from .core import (
            FileExtractor,
            clean_domain_list,
            clean_url_list,
            extract_domains_from_text,
            # Extractors
            extract_urls_from_text,
            is_valid_domain,
            is_valid_url,
            # Normalizers
            normalize_domain,
            normalize_url,
            # Validators
            validate_domain,
            validate_url,
        )

        # Processing utilities
        from .processing import (
            batch_items,
            process_parallel,
            process_parallel_with_progress,
        )

        # Utilities
        from .utils import (
            ErrorCollector,
            ProgressBar,
            SimpleProgress,
            create_progress_callback,
        )
    except ImportError:
        from analysis import (
            categorize_domains,
            categorize_urls,
            get_top_domains,
            get_top_tlds,
        )
        from core import (
            FileExtractor,
            clean_domain_list,
            clean_url_list,
            extract_domains_from_text,
            extract_urls_from_text,
            is_valid_domain,
            is_valid_url,
            normalize_domain,
            normalize_url,
            validate_domain,
            validate_url,
        )
        from processing import (
            batch_items,
            process_parallel,
            process_parallel_with_progress,
        )
        from utils import (
            ErrorCollector,
            ProgressBar,
            SimpleProgress,
            create_progress_callback,
        )

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__description__",
    # Core - Validators
    "validate_domain",
    "validate_url",
    "is_valid_domain",
    "is_valid_url",
    # Core - Extractors
    "extract_urls_from_text",
    "extract_domains_from_text",
    "FileExtractor",
    # Core - Normalizers
    "normalize_domain",
    "normalize_url",
    "clean_domain_list",
    "clean_url_list",
    # Processing
    "process_parallel",
    "process_parallel_with_progress",
    "batch_items",
    # Utilities
    "ProgressBar",
    "SimpleProgress",
    "create_progress_callback",
    "ErrorCollector",
    # Analysis
    "categorize_urls",
    "categorize_domains",
    "get_top_domains",
    "get_top_tlds",
]
