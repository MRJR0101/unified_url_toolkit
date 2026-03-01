"""
Redirect Chain Mapping - Track and analyze redirect sequences.

Analyzes redirect behavior including:
- Redirect chains (301 → 302 → 200)
- Redirect types (permanent, temporary, meta-refresh)
- JavaScript-based redirects
- Redirect loops
- Final destination tracking
"""

from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import requests
from urllib.parse import urlparse
import re


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class RedirectHop:
    """Single redirect in a chain."""

    url: str
    status_code: int
    redirect_type: str  # "301 Permanent", "302 Temporary", "Meta Refresh", "JS Redirect"
    location: Optional[str] = None
    response_time_ms: float = 0
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class RedirectChain:
    """Complete redirect chain analysis."""

    start_url: str
    final_url: str
    hops: List[RedirectHop] = field(default_factory=list)
    total_redirects: int = 0
    total_time_ms: float = 0
    has_loop: bool = False
    loop_urls: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    # Redirect type summary
    permanent_redirects: int = 0  # 301, 308
    temporary_redirects: int = 0  # 302, 303, 307
    meta_refresh_redirects: int = 0
    js_redirects: int = 0

    # Analysis
    redirect_distance: int = 0  # Number of hops
    crosses_domains: bool = False
    crosses_protocols: bool = False  # HTTP → HTTPS

    error: Optional[str] = None


# =============================================================================
# REDIRECT TYPE MAPPING
# =============================================================================

REDIRECT_TYPES = {
    300: "300 Multiple Choices",
    301: "301 Moved Permanently",
    302: "302 Found (Temporary)",
    303: "303 See Other",
    304: "304 Not Modified",
    307: "307 Temporary Redirect",
    308: "308 Permanent Redirect",
}

PERMANENT_REDIRECT_CODES = {301, 308}
TEMPORARY_REDIRECT_CODES = {302, 303, 307}


def get_redirect_type(status_code: int) -> str:
    """Get redirect type description."""
    return REDIRECT_TYPES.get(status_code, f"{status_code} Redirect")


# =============================================================================
# REDIRECT CHAIN TRACKING
# =============================================================================

def follow_redirect_chain(
    url: str,
    max_redirects: int = 10,
    timeout: int = 10,
    check_meta_refresh: bool = True,
    check_js_redirect: bool = True,
    verify_ssl: bool = True,
) -> RedirectChain:
    """
    Follow redirect chain and analyze each hop.

    Args:
        url: Starting URL
        max_redirects: Maximum redirects to follow
        timeout: Request timeout per hop
        check_meta_refresh: Check for meta refresh redirects
        check_js_redirect: Check for JavaScript redirects
        verify_ssl: Verify SSL certificates

    Returns:
        RedirectChain with complete analysis

    Example:
        >>> chain = follow_redirect_chain("http://example.com")
        >>> print(f"Redirects: {chain.total_redirects}")
        >>> print(f"Final URL: {chain.final_url}")
        >>> for hop in chain.hops:
        ...     print(f"  {hop.url} -> {hop.redirect_type}")
    """
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    chain = RedirectChain(
        start_url=url,
        final_url=url,
    )

    current_url = url
    visited_urls = set()
    start_time = datetime.now()

    try:
        for hop_num in range(max_redirects + 1):
            # Check for redirect loop
            if current_url in visited_urls:
                chain.has_loop = True
                chain.loop_urls = list(visited_urls)
                break

            visited_urls.add(current_url)
            hop_start = datetime.now()

            # Make request (don't follow redirects automatically)
            response = requests.get(
                current_url,
                timeout=timeout,
                allow_redirects=False,
                verify=verify_ssl,
            )

            hop_time = (datetime.now() - hop_start).total_seconds() * 1000

            # Create hop record
            hop = RedirectHop(
                url=current_url,
                status_code=response.status_code,
                redirect_type="",
                response_time_ms=hop_time,
                headers=dict(response.headers),
            )

            # Analyze redirect type
            if 300 <= response.status_code < 400:
                # HTTP redirect
                location = response.headers.get('Location')
                hop.location = location
                hop.redirect_type = get_redirect_type(response.status_code)

                # Count redirect types
                if response.status_code in PERMANENT_REDIRECT_CODES:
                    chain.permanent_redirects += 1
                elif response.status_code in TEMPORARY_REDIRECT_CODES:
                    chain.temporary_redirects += 1

                chain.hops.append(hop)

                if location:
                    # Resolve relative URLs
                    from urllib.parse import urljoin
                    current_url = urljoin(current_url, location)
                    chain.total_redirects += 1
                else:
                    # Redirect without location header
                    break

            elif response.status_code == 200:
                # Successful response - check for meta refresh and JS redirects
                hop.redirect_type = "200 OK (Final)"
                chain.hops.append(hop)

                # Check meta refresh
                if check_meta_refresh:
                    meta_url = check_meta_refresh_redirect(response.text)
                    if meta_url:
                        meta_hop = RedirectHop(
                            url=current_url,
                            status_code=200,
                            redirect_type="Meta Refresh",
                            location=meta_url,
                            response_time_ms=0,
                        )
                        chain.hops.append(meta_hop)
                        chain.meta_refresh_redirects += 1
                        chain.total_redirects += 1

                        from urllib.parse import urljoin
                        current_url = urljoin(current_url, meta_url)
                        continue

                # Check JavaScript redirect
                if check_js_redirect:
                    js_url = check_js_redirect(response.text)
                    if js_url:
                        js_hop = RedirectHop(
                            url=current_url,
                            status_code=200,
                            redirect_type="JavaScript Redirect",
                            location=js_url,
                            response_time_ms=0,
                        )
                        chain.hops.append(js_hop)
                        chain.js_redirects += 1
                        chain.total_redirects += 1

                        from urllib.parse import urljoin
                        current_url = urljoin(current_url, js_url)
                        continue

                # No more redirects
                break
            else:
                # Non-redirect, non-success status
                hop.redirect_type = f"{response.status_code} (Stopped)"
                chain.hops.append(hop)
                break

        # Set final URL
        chain.final_url = current_url
        chain.total_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        chain.redirect_distance = len(chain.hops) - 1

        # Analyze cross-domain and cross-protocol
        chain.crosses_domains = crosses_domains(chain.start_url, chain.final_url)
        chain.crosses_protocols = crosses_protocols(chain.start_url, chain.final_url)

    except Exception as e:
        chain.error = str(e)

    return chain


# =============================================================================
# META REFRESH DETECTION
# =============================================================================

def check_meta_refresh_redirect(html_content: str) -> Optional[str]:
    """
    Check for meta refresh redirect in HTML.

    Args:
        html_content: HTML content to check

    Returns:
        Redirect URL if found, None otherwise

    Example:
        >>> html = '<meta http-equiv="refresh" content="0;url=https://example.com">'
        >>> check_meta_refresh_redirect(html)
        'https://example.com'
    """
    # Pattern: <meta http-equiv="refresh" content="0;url=...">
    pattern = r'<meta\s+http-equiv=["\']?refresh["\']?\s+content=["\']?\d+;\s*url=([^"\'>\s]+)["\']?'

    match = re.search(pattern, html_content, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Alternative pattern: content first
    pattern2 = r'<meta\s+content=["\']?\d+;\s*url=([^"\'>\s]+)["\']?\s+http-equiv=["\']?refresh["\']?'

    match = re.search(pattern2, html_content, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    return None


# =============================================================================
# JAVASCRIPT REDIRECT DETECTION
# =============================================================================

def check_js_redirect(html_content: str) -> Optional[str]:
    """
    Check for common JavaScript redirect patterns.

    Args:
        html_content: HTML content to check

    Returns:
        Redirect URL if found, None otherwise

    Example:
        >>> html = '<script>window.location="https://example.com";</script>'
        >>> check_js_redirect(html)
        'https://example.com'
    """
    # Common patterns
    patterns = [
        r'window\.location\s*=\s*["\']([^"\']+)["\']',
        r'window\.location\.href\s*=\s*["\']([^"\']+)["\']',
        r'window\.location\.replace\(["\']([^"\']+)["\']\)',
        r'document\.location\s*=\s*["\']([^"\']+)["\']',
        r'document\.location\.href\s*=\s*["\']([^"\']+)["\']',
    ]

    for pattern in patterns:
        match = re.search(pattern, html_content, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


# =============================================================================
# REDIRECT ANALYSIS HELPERS
# =============================================================================

def crosses_domains(url1: str, url2: str) -> bool:
    """Check if redirect crosses domain boundaries."""
    domain1 = urlparse(url1).netloc.lower()
    domain2 = urlparse(url2).netloc.lower()

    # Strip www. for comparison
    domain1 = domain1.replace('www.', '')
    domain2 = domain2.replace('www.', '')

    return domain1 != domain2


def crosses_protocols(url1: str, url2: str) -> bool:
    """Check if redirect changes protocol (http → https)."""
    scheme1 = urlparse(url1).scheme.lower()
    scheme2 = urlparse(url2).scheme.lower()

    return scheme1 != scheme2


def get_redirect_summary(chain: RedirectChain) -> Dict[str, any]:
    """
    Get summary statistics for redirect chain.

    Args:
        chain: RedirectChain to summarize

    Returns:
        Dictionary with summary statistics
    """
    return {
        'total_redirects': chain.total_redirects,
        'total_time_ms': chain.total_time_ms,
        'redirect_distance': chain.redirect_distance,
        'permanent_redirects': chain.permanent_redirects,
        'temporary_redirects': chain.temporary_redirects,
        'meta_refresh_redirects': chain.meta_refresh_redirects,
        'js_redirects': chain.js_redirects,
        'crosses_domains': chain.crosses_domains,
        'crosses_protocols': chain.crosses_protocols,
        'has_loop': chain.has_loop,
        'start_url': chain.start_url,
        'final_url': chain.final_url,
    }


def format_redirect_chain(chain: RedirectChain) -> str:
    """
    Format redirect chain as human-readable string.

    Args:
        chain: RedirectChain to format

    Returns:
        Formatted string representation
    """
    lines = []
    lines.append(f"Redirect Chain Analysis")
    lines.append(f"=" * 60)
    lines.append(f"Start URL: {chain.start_url}")
    lines.append(f"Final URL: {chain.final_url}")
    lines.append(f"Total Redirects: {chain.total_redirects}")
    lines.append(f"Total Time: {chain.total_time_ms:.0f}ms")
    lines.append("")

    if chain.error:
        lines.append(f"Error: {chain.error}")
    elif chain.has_loop:
        lines.append(f"⚠️  Redirect Loop Detected!")
        lines.append(f"Loop URLs: {', '.join(chain.loop_urls)}")
    else:
        lines.append("Redirect Hops:")
        for i, hop in enumerate(chain.hops, 1):
            arrow = " → " if i < len(chain.hops) else ""
            lines.append(f"  {i}. {hop.url}")
            lines.append(f"     {hop.redirect_type} ({hop.response_time_ms:.0f}ms)")
            if hop.location:
                lines.append(f"     Location: {hop.location}")
            if arrow:
                lines.append("")

    if chain.crosses_domains:
        lines.append("")
        lines.append("⚠️  Crosses domain boundaries")

    if chain.crosses_protocols:
        lines.append("🔒 Protocol upgrade (HTTP → HTTPS)")

    return '\n'.join(lines)


# =============================================================================
# BATCH REDIRECT ANALYSIS
# =============================================================================

def analyze_redirect_chains(
    urls: List[str],
    max_workers: int = 10,
    timeout: int = 5,
) -> List[RedirectChain]:
    """
    Analyze redirect chains for multiple URLs in parallel.

    Args:
        urls: List of URLs to analyze
        max_workers: Number of parallel workers
        timeout: Request timeout per hop

    Returns:
        List of RedirectChain objects
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    chains = [None] * len(urls)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(follow_redirect_chain, url, timeout=timeout): idx
            for idx, url in enumerate(urls)
        }

        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                chains[idx] = future.result()
            except Exception as e:
                chains[idx] = RedirectChain(
                    start_url=urls[idx],
                    final_url=urls[idx],
                    error=str(e),
                )

    return chains
