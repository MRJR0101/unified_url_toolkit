"""
Utility modules for progress tracking and error handling.
"""

from .progress import (
    ProgressBar,
    SimpleProgress,
    create_progress_callback,
    print_progress_simple,
)

from .errors import (
    URLToolkitError,
    ValidationError,
    ExtractionError,
    NormalizationError,
    FileReadError,
    FileWriteError,
    NetworkError,
    ErrorCollector,
    format_error,
    log_error,
    safe_execute,
)

__all__ = [
    # Progress
    'ProgressBar',
    'SimpleProgress',
    'create_progress_callback',
    'print_progress_simple',

    # Errors
    'URLToolkitError',
    'ValidationError',
    'ExtractionError',
    'NormalizationError',
    'FileReadError',
    'FileWriteError',
    'NetworkError',
    'ErrorCollector',
    'format_error',
    'log_error',
    'safe_execute',
]
