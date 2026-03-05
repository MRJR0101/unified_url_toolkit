"""
Utility modules for progress tracking and error handling.
"""

from .errors import (
    ErrorCollector,
    ExtractionError,
    FileReadError,
    FileWriteError,
    NetworkError,
    NormalizationError,
    URLToolkitError,
    ValidationError,
    format_error,
    log_error,
    safe_execute,
)
from .progress import (
    ProgressBar,
    SimpleProgress,
    create_progress_callback,
    print_progress_simple,
)

__all__ = [
    # Progress
    "ProgressBar",
    "SimpleProgress",
    "create_progress_callback",
    "print_progress_simple",
    # Errors
    "URLToolkitError",
    "ValidationError",
    "ExtractionError",
    "NormalizationError",
    "FileReadError",
    "FileWriteError",
    "NetworkError",
    "ErrorCollector",
    "format_error",
    "log_error",
    "safe_execute",
]
