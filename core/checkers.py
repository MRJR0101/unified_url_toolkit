"""
Async URL checking with retry logic and intelligent fallback strategies.

Source: Extracted from LinkTools/core/checker.py
Enhanced with additional functionality from ValidateLinks and MyUrlChecker
"""

import asyncio
import time
import sys
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple

try:
    import aiohttp
    from aiohttp import ClientTimeout
except ImportError:
    aiohttp = None
    ClientTimeout = None


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class CheckResult:
    """Result of a single URL check."""

    url: str
    final_url: str
    status: str  # ok | redirected | client_error | server_error | timeout | network_error
    http_status: Optional[int]
    reason: str
    content_type: Optional[str]
    content_length: Optional[int]
    elapsed_ms: int
    error: Optional[str]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    def is_ok(self) -> bool:
        """Check if URL is accessible (2xx status)."""
        return self.status == 'ok'

    def is_error(self) -> bool:
        """Check if URL has an error."""
        return self.status in ('client_error', 'server_error', 'timeout', 'network_error')


# =============================================================================
# URL CHECKER
# =============================================================================

class URLChecker:
    """
    Async URL checker with intelligent retry and fallback strategies.

    Features:
    - HEAD request with GET fallback
    - Configurable retry logic with exponential backoff
    - Concurrent request limiting
    - Detailed status reporting
    - Summary statistics

    Source: LinkTools/core/checker.py
    """

    def __init__(
        self,
        timeout: float = 15.0,
        retries: int = 2,
        concurrency: int = 50,
        user_agent: str = "UnifiedURLToolkit/1.0",
        follow_redirects: bool = True,
    ):
        """
        Initialize URL checker.

        Args:
            timeout: Per-request timeout in seconds
            retries: Number of retries on transient errors
            concurrency: Max concurrent requests
            user_agent: User-Agent string
            follow_redirects: Whether to follow redirects
        """
        if aiohttp is None:
            import warnings
            warnings.warn(
                "aiohttp not installed: pip install aiohttp for async checking. "
                "URL checking will not be available."
            )

        self.timeout = timeout
        self.retries = retries
        self.concurrency = concurrency
        self.user_agent = user_agent
        self.follow_redirects = follow_redirects
        self.results: List[CheckResult] = []

    async def _fetch_head_then_get(
        self,
        session: aiohttp.ClientSession,
        url: str
    ) -> Tuple[str, Optional[int], str, Optional[str], Optional[int]]:
        """
        Try HEAD first, fall back to GET if needed.

        Returns:
            (final_url, status, reason, content_type, content_length)
        """
        try:
            # Try HEAD first (faster, less bandwidth)
            async with session.head(url, allow_redirects=self.follow_redirects) as resp:
                await resp.read()
                ct = resp.headers.get('Content-Type')
                cl = resp.headers.get('Content-Length')
                cl_int = int(cl) if cl and cl.isdigit() else None
                return str(resp.url), resp.status, resp.reason or '', ct, cl_int
        except (aiohttp.ClientError, asyncio.TimeoutError):
            pass

        # Fallback to GET
        try:
            async with session.get(url, allow_redirects=self.follow_redirects) as resp:
                body = await resp.read()
                ct = resp.headers.get('Content-Type')
                cl = resp.headers.get('Content-Length')
                cl_int = int(cl) if cl and cl.isdigit() else len(body)
                return str(resp.url), resp.status, resp.reason or '', ct, cl_int
        except (aiohttp.ClientError, asyncio.TimeoutError):
            raise

    async def _check_one(
        self,
        session: aiohttp.ClientSession,
        url: str
    ) -> CheckResult:
        """Check a single URL with retry logic."""
        t0 = time.perf_counter()
        last_err: Optional[str] = None
        attempt = 0

        while True:
            try:
                final_url, st, reason, ctype, clen = await self._fetch_head_then_get(session, url)
                elapsed_ms = int((time.perf_counter() - t0) * 1000)

                # Determine status category
                if st is None:
                    status = 'network_error'
                elif 200 <= st <= 299:
                    status = 'ok'
                elif 300 <= st <= 399:
                    status = 'redirected'
                elif 400 <= st <= 499:
                    status = 'client_error'
                else:
                    status = 'server_error'

                return CheckResult(
                    url=url,
                    final_url=final_url,
                    status=status,
                    http_status=st,
                    reason=reason,
                    content_type=ctype,
                    content_length=clen,
                    elapsed_ms=elapsed_ms,
                    error=None,
                )

            except asyncio.TimeoutError:
                last_err = 'Timeout'
                attempt += 1
            except aiohttp.ClientError as e:
                last_err = f"{type(e).__name__}: {e}"
                attempt += 1
            except Exception as e:
                last_err = f"{type(e).__name__}: {e}"
                attempt += 1

            # Check if we've exhausted retries
            if attempt > self.retries:
                elapsed_ms = int((time.perf_counter() - t0) * 1000)
                status = 'timeout' if last_err == 'Timeout' else 'network_error'
                return CheckResult(
                    url=url,
                    final_url=url,
                    status=status,
                    http_status=None,
                    reason='Error',
                    content_type=None,
                    content_length=None,
                    elapsed_ms=elapsed_ms,
                    error=last_err,
                )

            # Exponential backoff before retry
            await asyncio.sleep(0.5 * (2 ** (attempt - 1)))

    async def check_all(self, urls: List[str]) -> List[CheckResult]:
        """
        Check multiple URLs concurrently.

        Args:
            urls: List of URLs to check

        Returns:
            List of CheckResult objects
        """
        if aiohttp is None:
            raise ImportError("aiohttp required: pip install aiohttp")

        # Windows event loop policy fix
        if sys.platform.startswith('win'):
            try:
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            except Exception:
                pass

        timeout = ClientTimeout(total=self.timeout)
        connector = aiohttp.TCPConnector(limit_per_host=0, ttl_dns_cache=300)
        headers = {'User-Agent': self.user_agent}

        sem = asyncio.Semaphore(self.concurrency)
        results: List[CheckResult] = []

        async with aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers=headers
        ) as session:

            async def worker(url: str):
                async with sem:
                    result = await self._check_one(session, url)
                    results.append(result)

            tasks = [asyncio.create_task(worker(url)) for url in urls]
            await asyncio.gather(*tasks, return_exceptions=True)

        self.results = results
        return results

    def check_sync(self, urls: List[str]) -> List[CheckResult]:
        """Synchronous wrapper around check_all."""
        return asyncio.run(self.check_all(urls))

    def get_summary(self) -> dict:
        """
        Get summary statistics of checked URLs.

        Returns:
            Dictionary with summary stats
        """
        if not self.results:
            return {}

        status_counts = {}
        total_time = 0
        ok_count = 0

        for r in self.results:
            status_counts[r.status] = status_counts.get(r.status, 0) + 1
            total_time += r.elapsed_ms
            if r.status == 'ok':
                ok_count += 1

        return {
            'total': len(self.results),
            'ok': ok_count,
            'failed': len(self.results) - ok_count,
            'by_status': status_counts,
            'avg_time_ms': total_time // len(self.results) if self.results else 0,
            'total_time_ms': total_time,
            'success_rate': (ok_count / len(self.results) * 100) if self.results else 0,
        }

    def get_failed_urls(self) -> List[CheckResult]:
        """Get all URLs that failed checks."""
        return [r for r in self.results if r.is_error()]

    def get_ok_urls(self) -> List[CheckResult]:
        """Get all URLs that passed checks."""
        return [r for r in self.results if r.is_ok()]


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def check_urls(urls: List[str],
               timeout: float = 15.0,
               concurrency: int = 50) -> List[CheckResult]:
    """
    Convenience function to check URLs synchronously.

    Args:
        urls: List of URLs to check
        timeout: Timeout per request
        concurrency: Max concurrent requests

    Returns:
        List of CheckResult objects
    """
    checker = URLChecker(timeout=timeout, concurrency=concurrency)
    return checker.check_sync(urls)


def check_url(url: str, timeout: float = 15.0) -> CheckResult:
    """
    Convenience function to check a single URL.

    Args:
        url: URL to check
        timeout: Timeout for request

    Returns:
        CheckResult object
    """
    results = check_urls([url], timeout=timeout, concurrency=1)
    return results[0] if results else None
