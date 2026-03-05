"""
Progress tracking and display utilities.

Consolidated from:
- ExtractUrls/extract_urls.py (progress indicators)
- URLToolkit/url_toolkit.py (progress display)
- Multiple CLI tools with custom progress tracking
"""

import sys
from datetime import datetime, timedelta
from typing import Callable


class ProgressBar:
    """
    Simple progress bar for tracking operations.

    Example:
        >>> with ProgressBar(total=100, desc="Processing") as progress:
        ...     for i in range(100):
        ...         do_work()
        ...         progress.update(1)
    """

    def __init__(
        self,
        total: int,
        desc: str = "",
        width: int = 50,
        show_eta: bool = True,
        file=None,
    ):
        """
        Initialize progress bar.

        Args:
            total: Total number of items
            desc: Description to show
            width: Width of progress bar in characters
            show_eta: Show estimated time remaining
            file: Output file (default: sys.stdout)
        """
        self.total = total
        self.desc = desc
        self.width = width
        self.show_eta = show_eta
        self.file = file or sys.stdout

        self.current = 0
        self.start_time = datetime.now()
        self.last_update = self.start_time

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, *args):
        """Context manager exit - print final newline."""
        self.file.write("\n")
        self.file.flush()

    def update(self, n: int = 1):
        """
        Update progress by n items.

        Args:
            n: Number of items completed
        """
        self.current += n
        self._display()

    def _display(self):
        """Display current progress."""
        if self.total == 0:
            return

        percent = min(100, int(100 * self.current / self.total))
        filled = int(self.width * self.current / self.total)
        bar = "#" * filled + "-" * (self.width - filled)

        # Build progress string
        progress_str = f"\r{self.desc}{' ' if self.desc else ''}"
        progress_str += f"[{bar}] {percent}% ({self.current}/{self.total})"

        # Add ETA if enabled
        if self.show_eta and self.current > 0:
            elapsed = datetime.now() - self.start_time
            rate = self.current / elapsed.total_seconds()

            if rate > 0:
                remaining = (self.total - self.current) / rate
                eta = timedelta(seconds=int(remaining))
                progress_str += f" ETA: {eta}"

        # Write and flush
        self.file.write(progress_str)
        self.file.flush()


class SimpleProgress:
    """
    Lightweight progress counter without visual bar.

    Example:
        >>> progress = SimpleProgress(total=1000, update_interval=100)
        >>> for i in range(1000):
        ...     progress.increment()
    """

    def __init__(
        self,
        total: int,
        update_interval: int = 10,
        desc: str = "Progress",
        file=None,
    ):
        """
        Initialize simple progress counter.

        Args:
            total: Total number of items
            update_interval: Update display every N items
            desc: Description
            file: Output file
        """
        self.total = total
        self.update_interval = update_interval
        self.desc = desc
        self.file = file or sys.stdout

        self.current = 0
        self.start_time = datetime.now()

    def increment(self, n: int = 1):
        """Increment counter by n."""
        self.current += n

        if self.current % self.update_interval == 0 or self.current == self.total:
            self._display()

    def _display(self):
        """Display current count."""
        elapsed = datetime.now() - self.start_time
        rate = self.current / max(1, elapsed.total_seconds())

        msg = f"\r{self.desc}: {self.current}/{self.total}"
        msg += f" ({rate:.1f} items/sec)"

        self.file.write(msg)
        self.file.flush()

        if self.current == self.total:
            self.file.write("\n")
            self.file.flush()


def create_progress_callback(
    total: int,
    desc: str = "Processing",
    update_interval: int = 1,
) -> Callable[[int, int], None]:
    """
    Create a progress callback function for use with parallel processing.

    Args:
        total: Total number of items
        desc: Description
        update_interval: Update every N completions

    Returns:
        Callback function with signature (completed, total)

    Example:
        >>> callback = create_progress_callback(total=100, desc="Checking URLs")
        >>> results = process_parallel_with_progress(
        ...     urls, check_url, progress_callback=callback
        ... )
    """
    start_time = datetime.now()
    last_update = [0]  # Mutable to track in closure

    def callback(completed: int, total_items: int):
        """Progress callback."""
        if completed - last_update[0] >= update_interval or completed == total_items:
            percent = int(100 * completed / max(1, total_items))
            elapsed = datetime.now() - start_time
            rate = completed / max(1, elapsed.total_seconds())

            msg = f"\r{desc}: {completed}/{total_items} ({percent}%) - {rate:.1f} items/sec"

            sys.stdout.write(msg)
            sys.stdout.flush()

            last_update[0] = completed

            if completed == total_items:
                sys.stdout.write("\n")
                sys.stdout.flush()

    return callback


def print_progress_simple(current: int, total: int, prefix: str = ""):
    """
    Print simple progress without complex formatting.

    Args:
        current: Current count
        total: Total count
        prefix: Optional prefix string

    Example:
        >>> for i in range(100):
        ...     print_progress_simple(i + 1, 100, "Processing")
    """
    percent = int(100 * current / max(1, total))
    msg = f"\r{prefix}{' ' if prefix else ''}{current}/{total} ({percent}%)"

    sys.stdout.write(msg)
    sys.stdout.flush()

    if current == total:
        sys.stdout.write("\n")
        sys.stdout.flush()
