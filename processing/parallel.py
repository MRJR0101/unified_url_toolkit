"""
Parallel processing utilities for efficient batch operations.

Consolidated from:
- ExtractUrls/extract_urls.py (ThreadPoolExecutor with progress)
- UrlExtractorParallel/ (multiprocessing implementation)
- Parallel_extractor/ (concurrent processing patterns)
"""

from typing import Callable, List, TypeVar, Iterator, Optional, Any
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count
from functools import partial

T = TypeVar('T')
R = TypeVar('R')


def process_parallel(
    items: List[T],
    process_func: Callable[[T], R],
    max_workers: Optional[int] = None,
    use_threads: bool = False,
    chunk_size: int = 10,
    timeout: Optional[float] = None,
) -> List[R]:
    """
    Process items in parallel using threads or processes.

    Args:
        items: Items to process
        process_func: Function to apply to each item
        max_workers: Number of workers (default: CPU count - 1)
        use_threads: Use ThreadPoolExecutor instead of ProcessPoolExecutor
        chunk_size: Chunk size for processing batches
        timeout: Maximum time to wait for results (seconds)

    Returns:
        List of results in original order

    Example:
        >>> urls = ["http://example.com", "http://test.org"]
        >>> results = process_parallel(urls, check_url_status, max_workers=10, use_threads=True)
    """
    if not items:
        return []

    if max_workers is None:
        max_workers = max(1, cpu_count() - 1)

    executor_class = ThreadPoolExecutor if use_threads else ProcessPoolExecutor

    results = [None] * len(items)

    with executor_class(max_workers=max_workers) as executor:
        # Submit all tasks with their indices
        future_to_index = {
            executor.submit(process_func, item): idx
            for idx, item in enumerate(items)
        }

        # Collect results
        for future in as_completed(future_to_index, timeout=timeout):
            idx = future_to_index[future]
            try:
                results[idx] = future.result()
            except Exception as exc:
                # Store the exception instead of raising
                results[idx] = exc

    return results


def process_parallel_with_progress(
    items: List[T],
    process_func: Callable[[T], R],
    max_workers: Optional[int] = None,
    use_threads: bool = False,
    chunk_size: int = 10,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    error_callback: Optional[Callable[[T, Exception], None]] = None,
) -> List[R]:
    """
    Process items in parallel with progress tracking.

    Args:
        items: Items to process
        process_func: Function to apply to each item
        max_workers: Number of workers (default: CPU count - 1)
        use_threads: Use ThreadPoolExecutor instead of ProcessPoolExecutor
        chunk_size: Chunk size for processing batches
        progress_callback: Called with (completed, total) after each item
        error_callback: Called with (item, exception) on errors

    Returns:
        List of results (None for failed items)

    Example:
        >>> def on_progress(done, total):
        ...     print(f"Progress: {done}/{total}")
        >>> results = process_parallel_with_progress(
        ...     urls, check_url, progress_callback=on_progress
        ... )
    """
    if not items:
        return []

    if max_workers is None:
        max_workers = max(1, cpu_count() - 1)

    executor_class = ThreadPoolExecutor if use_threads else ProcessPoolExecutor

    results = [None] * len(items)
    completed = 0

    with executor_class(max_workers=max_workers) as executor:
        # Submit all tasks with their indices
        future_to_data = {
            executor.submit(process_func, item): (idx, item)
            for idx, item in enumerate(items)
        }

        # Collect results with progress tracking
        for future in as_completed(future_to_data):
            idx, item = future_to_data[future]

            try:
                results[idx] = future.result()
            except Exception as exc:
                results[idx] = None
                if error_callback:
                    error_callback(item, exc)

            completed += 1
            if progress_callback:
                progress_callback(completed, len(items))

    return results


def batch_items(items: List[T], batch_size: int) -> Iterator[List[T]]:
    """
    Split items into batches of specified size.

    Args:
        items: Items to batch
        batch_size: Size of each batch

    Yields:
        Batches of items

    Example:
        >>> urls = list(range(100))
        >>> for batch in batch_items(urls, batch_size=10):
        ...     process_batch(batch)
    """
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


def process_batches_parallel(
    items: List[T],
    batch_process_func: Callable[[List[T]], List[R]],
    batch_size: int = 100,
    max_workers: Optional[int] = None,
    use_threads: bool = False,
) -> List[R]:
    """
    Process items in parallel batches.

    Useful when the processing function works more efficiently on batches
    (e.g., database bulk inserts, API batch requests).

    Args:
        items: Items to process
        batch_process_func: Function that processes a batch and returns results
        batch_size: Size of each batch
        max_workers: Number of workers
        use_threads: Use threads instead of processes

    Returns:
        Flattened list of all results

    Example:
        >>> def process_url_batch(urls):
        ...     # Process batch of URLs efficiently
        ...     return [check_url(u) for u in urls]
        >>> results = process_batches_parallel(urls, process_url_batch, batch_size=50)
    """
    batches = list(batch_items(items, batch_size))

    if not batches:
        return []

    batch_results = process_parallel(
        batches,
        batch_process_func,
        max_workers=max_workers,
        use_threads=use_threads,
    )

    # Flatten results
    results = []
    for batch_result in batch_results:
        if isinstance(batch_result, list):
            results.extend(batch_result)
        elif batch_result is not None:
            results.append(batch_result)

    return results


def map_parallel(
    func: Callable[[T], R],
    items: List[T],
    max_workers: Optional[int] = None,
    use_threads: bool = True,
) -> List[R]:
    """
    Simplified parallel map operation.

    Args:
        func: Function to map over items
        items: Items to process
        max_workers: Number of workers
        use_threads: Use threads (default) or processes

    Returns:
        List of results in original order

    Example:
        >>> results = map_parallel(str.upper, ["hello", "world"])
        >>> # ['HELLO', 'WORLD']
    """
    return process_parallel(
        items,
        func,
        max_workers=max_workers,
        use_threads=use_threads,
    )


def filter_parallel(
    predicate: Callable[[T], bool],
    items: List[T],
    max_workers: Optional[int] = None,
    use_threads: bool = True,
) -> List[T]:
    """
    Parallel filter operation.

    Args:
        predicate: Function that returns True to keep item
        items: Items to filter
        max_workers: Number of workers
        use_threads: Use threads (default) or processes

    Returns:
        Filtered list of items

    Example:
        >>> urls = ["http://a.com", "invalid", "http://b.com"]
        >>> valid = filter_parallel(is_valid_url, urls)
    """
    results = process_parallel(
        items,
        predicate,
        max_workers=max_workers,
        use_threads=use_threads,
    )

    return [item for item, keep in zip(items, results) if keep]
