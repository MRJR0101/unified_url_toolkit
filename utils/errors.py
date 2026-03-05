"""
Centralized error handling and custom exceptions.

Provides consistent error reporting across all modules.
"""

from pathlib import Path
from typing import Any, Optional

# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================


class URLToolkitError(Exception):
    """Base exception for all URL toolkit errors."""

    pass


class ValidationError(URLToolkitError):
    """Error during URL or domain validation."""

    pass


class ExtractionError(URLToolkitError):
    """Error during URL or domain extraction."""

    pass


class NormalizationError(URLToolkitError):
    """Error during URL or domain normalization."""

    pass


class FileReadError(URLToolkitError):
    """Error reading input file."""

    pass


class FileWriteError(URLToolkitError):
    """Error writing output file."""

    pass


class NetworkError(URLToolkitError):
    """Error during network operations."""

    pass


# =============================================================================
# ERROR REPORTING
# =============================================================================


def format_error(
    error: Exception,
    context: Optional[str] = None,
    include_traceback: bool = False,
) -> str:
    """
    Format an error message for display.

    Args:
        error: Exception that occurred
        context: Optional context string
        include_traceback: Include full traceback

    Returns:
        Formatted error message

    Example:
        >>> try:
        ...     validate_url("invalid")
        ... except Exception as e:
        ...     print(format_error(e, context="URL validation"))
    """
    error_type = type(error).__name__
    error_msg = str(error)

    if context:
        msg = f"[{error_type}] {context}: {error_msg}"
    else:
        msg = f"[{error_type}] {error_msg}"

    if include_traceback:
        import traceback

        msg += f"\n{traceback.format_exc()}"

    return msg


def log_error(
    error: Exception,
    context: Optional[str] = None,
    filepath: Optional[Path] = None,
):
    """
    Log an error to stderr and optionally to a file.

    Args:
        error: Exception to log
        context: Optional context
        filepath: Optional file to append error to

    Example:
        >>> log_error(ValueError("Bad input"), context="Processing file.txt")
    """
    import sys
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_msg = format_error(error, context)
    log_msg = f"[{timestamp}] {error_msg}\n"

    # Print to stderr
    sys.stderr.write(log_msg)
    sys.stderr.flush()

    # Optionally write to file
    if filepath:
        try:
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(log_msg)
        except Exception as e:
            sys.stderr.write(f"Failed to write error log: {e}\n")


class ErrorCollector:
    """
    Collect errors during batch operations.

    Example:
        >>> collector = ErrorCollector()
        >>> for item in items:
        ...     try:
        ...         process(item)
        ...     except Exception as e:
        ...         collector.add(e, context=f"Item: {item}")
        >>> if collector.has_errors():
        ...     print(collector.summary())
    """

    def __init__(self):
        """Initialize error collector."""
        self.errors = []

    def add(self, error: Exception, context: Optional[str] = None, item: Any = None):
        """
        Add an error to the collection.

        Args:
            error: Exception that occurred
            context: Optional context string
            item: Optional item that caused the error
        """
        self.errors.append(
            {
                "error": error,
                "context": context,
                "item": item,
                "type": type(error).__name__,
                "message": str(error),
            }
        )

    def has_errors(self) -> bool:
        """Check if any errors were collected."""
        return len(self.errors) > 0

    def count(self) -> int:
        """Get number of errors collected."""
        return len(self.errors)

    def summary(self) -> str:
        """
        Get a summary of all errors.

        Returns:
            Multi-line summary string
        """
        if not self.errors:
            return "No errors"

        lines = [f"Collected {len(self.errors)} error(s):"]

        for i, error_info in enumerate(self.errors, 1):
            context = error_info["context"] or "Unknown context"
            error_type = error_info["type"]
            message = error_info["message"]

            lines.append(f"{i}. [{error_type}] {context}: {message}")

        return "\n".join(lines)

    def clear(self):
        """Clear all collected errors."""
        self.errors.clear()

    def get_errors(self) -> list:
        """Get raw list of error dictionaries."""
        return self.errors.copy()


def safe_execute(func, *args, default=None, suppress_errors: bool = False, **kwargs):
    """
    Safely execute a function with error handling.

    Args:
        func: Function to execute
        *args: Positional arguments
        default: Default value to return on error
        suppress_errors: If False, re-raise errors; if True, return default
        **kwargs: Keyword arguments

    Returns:
        Function result or default value on error

    Example:
        >>> result = safe_execute(int, "not a number", default=0, suppress_errors=True)
        >>> # result = 0
    """
    try:
        return func(*args, **kwargs)
    except Exception:
        if not suppress_errors:
            raise
        return default
