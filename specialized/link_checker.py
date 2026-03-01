"""
Comprehensive link checking with retries, timeouts, and detailed reporting.

Validates URLs by making HTTP requests and analyzing responses.
"""

from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import requests
import time

from ..config.settings import (
    DEFAULT_HTTP_TIMEOUT,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY,
    DEFAULT_USER_AGENT,
)


# =============================================================================
# ENUMS
# =============================================================================

class LinkStatus(Enum):
    """Link status categories."""
    ALIVE = 'alive'
    DEAD = 'dead'
    REDIRECT = 'redirect'
    TIMEOUT = 'timeout'
    ERROR = 'error'
    UNKNOWN = 'unknown'


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class LinkCheckResult:
    """Result of checking a single link."""

    url: str
    status: LinkStatus
    status_code: Optional[int] = None
    final_url: Optional[str] = None
    response_time_ms: float = 0.0

    # Redirect info
    redirect_count: int = 0
    redirect_chain: List[str] = field(default_factory=list)

    # Error info
    error_message: Optional[str] = None
    error_type: Optional[str] = None

    # Retry info
    attempts: int = 1
    succeeded_on_retry: bool = False

    # Timestamp
    checked_at: datetime = field(default_factory=datetime.now)

    # Analysis
    is_alive: bool = False
    is_broken: bool = False
    needs_attention: bool = False


@dataclass
class LinkCheckReport:
    """Summary report for batch link checking."""

    total_links: int = 0
    alive_links: int = 0
    dead_links: int = 0
    redirect_links: int = 0
    timeout_links: int = 0
    error_links: int = 0

    # Results
    results: List[LinkCheckResult] = field(default_factory=list)

    # Timing
    total_time_seconds: float = 0.0
    average_response_time_ms: float = 0.0

    # Analysis
    success_rate: float = 0.0
    broken_links: List[str] = field(default_factory=list)
    slow_links: List[str] = field(default_factory=list)  # > 3 seconds


# =============================================================================
# LINK CHECKING
# =============================================================================

def check_link(
    url: str,
    method: str = 'HEAD',
    timeout: int = DEFAULT_HTTP_TIMEOUT,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_delay: float = DEFAULT_RETRY_DELAY,
    follow_redirects: bool = True,
    verify_ssl: bool = True,
    user_agent: str = DEFAULT_USER_AGENT,
) -> LinkCheckResult:
    """
    Check if a link is alive with retry logic.

    Args:
        url: URL to check
        method: HTTP method (HEAD is faster, GET for fallback)
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts
        retry_delay: Delay between retries in seconds
        follow_redirects: Whether to follow redirects
        verify_ssl: Whether to verify SSL certificates
        user_agent: User agent string

    Returns:
        LinkCheckResult object

    Example:
        >>> result = check_link('https://example.com')
        >>> print(f"Status: {result.status.value}")
        >>> print(f"Alive: {result.is_alive}")
        >>> print(f"Status Code: {result.status_code}")
    """
    # Ensure URL has scheme
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    result = LinkCheckResult(
        url=url,
        status=LinkStatus.UNKNOWN,
    )

    headers = {'User-Agent': user_agent}

    # Retry loop
    for attempt in range(1, max_retries + 1):
        result.attempts = attempt
        start_time = time.time()

        try:
            # Try HEAD first (faster)
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=timeout,
                allow_redirects=follow_redirects,
                verify=verify_ssl,
            )

            # Calculate response time
            result.response_time_ms = (time.time() - start_time) * 1000

            # Extract info
            result.status_code = response.status_code
            result.final_url = response.url

            # Check redirects
            if hasattr(response, 'history') and response.history:
                result.redirect_count = len(response.history)
                result.redirect_chain = [r.url for r in response.history]
                result.status = LinkStatus.REDIRECT

            # Categorize status
            if 200 <= response.status_code < 300:
                result.status = LinkStatus.ALIVE
                result.is_alive = True
            elif 300 <= response.status_code < 400:
                result.status = LinkStatus.REDIRECT
                result.is_alive = True  # Redirects are considered alive
            elif 400 <= response.status_code < 600:
                result.status = LinkStatus.DEAD
                result.is_broken = True
            else:
                result.status = LinkStatus.UNKNOWN
                result.needs_attention = True

            # Success - no retry needed
            if attempt > 1:
                result.succeeded_on_retry = True
            break

        except requests.exceptions.Timeout:
            result.status = LinkStatus.TIMEOUT
            result.error_message = 'Request timed out'
            result.error_type = 'Timeout'
            result.needs_attention = True

            # Retry on timeout
            if attempt < max_retries:
                time.sleep(retry_delay)
                continue

        except requests.exceptions.SSLError as e:
            result.status = LinkStatus.ERROR
            result.error_message = f'SSL Error: {str(e)}'
            result.error_type = 'SSLError'
            result.needs_attention = True
            break

        except requests.exceptions.ConnectionError as e:
            result.status = LinkStatus.ERROR
            result.error_message = f'Connection Error: {str(e)}'
            result.error_type = 'ConnectionError'
            result.is_broken = True

            # Retry on connection error
            if attempt < max_retries:
                time.sleep(retry_delay)
                continue

        except requests.exceptions.RequestException as e:
            result.status = LinkStatus.ERROR
            result.error_message = str(e)
            result.error_type = type(e).__name__
            result.is_broken = True

            # Retry on general error
            if attempt < max_retries:
                time.sleep(retry_delay)
                continue

    return result


def check_link_with_fallback(
    url: str,
    **kwargs
) -> LinkCheckResult:
    """
    Check link with HEAD, fallback to GET if needed.

    Some servers don't support HEAD requests, so try GET if HEAD fails.

    Args:
        url: URL to check
        **kwargs: Additional arguments for check_link

    Returns:
        LinkCheckResult object
    """
    # Try HEAD first
    result = check_link(url, method='HEAD', **kwargs)

    # If HEAD failed with 405 Method Not Allowed, try GET
    if result.status_code == 405 or result.status == LinkStatus.ERROR:
        result = check_link(url, method='GET', **kwargs)

    return result


# =============================================================================
# BATCH LINK CHECKING
# =============================================================================

def check_multiple_links(
    urls: List[str],
    max_workers: int = 10,
    method: str = 'HEAD',
    timeout: int = 10,
    max_retries: int = 2,
    show_progress: bool = True,
) -> LinkCheckReport:
    """
    Check multiple links in parallel.

    Args:
        urls: List of URLs to check
        max_workers: Number of parallel workers
        method: HTTP method
        timeout: Request timeout
        max_retries: Retry attempts
        show_progress: Show progress output

    Returns:
        LinkCheckReport with all results

    Example:
        >>> urls = ['https://example.com', 'https://test.org']
        >>> report = check_multiple_links(urls)
        >>> print(f"Success rate: {report.success_rate:.1f}%")
        >>> print(f"Broken: {len(report.broken_links)}")
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    report = LinkCheckReport(total_links=len(urls))
    start_time = time.time()

    results = [None] * len(urls)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(
                check_link_with_fallback,
                url,
                method=method,
                timeout=timeout,
                max_retries=max_retries
            ): idx
            for idx, url in enumerate(urls)
        }

        # Collect results
        completed = 0
        for future in as_completed(future_to_index):
            idx = future_to_index[future]

            try:
                results[idx] = future.result()
            except Exception as e:
                # Create error result
                results[idx] = LinkCheckResult(
                    url=urls[idx],
                    status=LinkStatus.ERROR,
                    error_message=str(e),
                    error_type=type(e).__name__,
                    is_broken=True,
                )

            completed += 1

            if show_progress and completed % 10 == 0:
                print(f"Progress: {completed}/{len(urls)}", end='\r')

    if show_progress:
        print()  # New line after progress

    # Build report
    report.results = results
    report.total_time_seconds = time.time() - start_time

    # Calculate statistics
    response_times = []

    for result in results:
        if result.status == LinkStatus.ALIVE:
            report.alive_links += 1
        elif result.status == LinkStatus.DEAD:
            report.dead_links += 1
            report.broken_links.append(result.url)
        elif result.status == LinkStatus.REDIRECT:
            report.redirect_links += 1
        elif result.status == LinkStatus.TIMEOUT:
            report.timeout_links += 1
        elif result.status == LinkStatus.ERROR:
            report.error_links += 1
            report.broken_links.append(result.url)

        # Collect response times
        if result.response_time_ms > 0:
            response_times.append(result.response_time_ms)

        # Track slow links (> 3 seconds)
        if result.response_time_ms > 3000:
            report.slow_links.append(result.url)

    # Calculate averages
    if response_times:
        report.average_response_time_ms = sum(response_times) / len(response_times)

    # Calculate success rate
    successful = report.alive_links + report.redirect_links
    report.success_rate = (successful / report.total_links * 100) if report.total_links > 0 else 0

    return report


# =============================================================================
# REPORT FORMATTING
# =============================================================================

def format_link_check_report(report: LinkCheckReport) -> str:
    """
    Format link check report as human-readable string.

    Args:
        report: LinkCheckReport object

    Returns:
        Formatted report string
    """
    lines = []
    lines.append("Link Check Report")
    lines.append("=" * 60)
    lines.append(f"Total Links: {report.total_links}")
    lines.append(f"Total Time: {report.total_time_seconds:.1f}s")
    lines.append("")

    lines.append("Status Breakdown:")
    lines.append(f"  ✓ Alive:    {report.alive_links} ({report.alive_links/report.total_links*100:.1f}%)")
    lines.append(f"  ↻ Redirect: {report.redirect_links} ({report.redirect_links/report.total_links*100:.1f}%)")
    lines.append(f"  ✗ Dead:     {report.dead_links} ({report.dead_links/report.total_links*100:.1f}%)")
    lines.append(f"  ⏱ Timeout:  {report.timeout_links} ({report.timeout_links/report.total_links*100:.1f}%)")
    lines.append(f"  ⚠ Error:    {report.error_links} ({report.error_links/report.total_links*100:.1f}%)")
    lines.append("")

    lines.append(f"Success Rate: {report.success_rate:.1f}%")
    lines.append(f"Average Response Time: {report.average_response_time_ms:.0f}ms")

    if report.broken_links:
        lines.append("")
        lines.append(f"Broken Links ({len(report.broken_links)}):")
        for url in report.broken_links[:10]:  # Show first 10
            lines.append(f"  • {url}")
        if len(report.broken_links) > 10:
            lines.append(f"  ... and {len(report.broken_links) - 10} more")

    if report.slow_links:
        lines.append("")
        lines.append(f"Slow Links ({len(report.slow_links)} > 3s):")
        for url in report.slow_links[:5]:  # Show first 5
            lines.append(f"  • {url}")
        if len(report.slow_links) > 5:
            lines.append(f"  ... and {len(report.slow_links) - 5} more")

    return '\n'.join(lines)
