"""
Data processing utilities for batch operations and parallel execution.

Consolidated from:
- ExtractUrls/extract_urls.py (ThreadPoolExecutor)
- UrlExtractorParallel/ (multiprocessing)
- Parallel_extractor/ (concurrent processing)
"""

from .parallel import (
    batch_items,
    process_parallel,
    process_parallel_with_progress,
)

__all__ = [
    "process_parallel",
    "process_parallel_with_progress",
    "batch_items",
]
