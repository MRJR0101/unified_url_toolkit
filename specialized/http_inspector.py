"""
HTTP response inspection and header analysis.

Analyzes HTTP status codes, headers, server info, and response characteristics.
"""

from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Dict, List, Optional

import requests  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from ..config.settings import (
        DEFAULT_HTTP_TIMEOUT,
        DEFAULT_USER_AGENT,
        VERIFY_SSL,
    )
else:
    try:
        from ..config.settings import (
            DEFAULT_HTTP_TIMEOUT,
            DEFAULT_USER_AGENT,
            VERIFY_SSL,
        )
    except ImportError:
        from config.settings import (
            DEFAULT_HTTP_TIMEOUT,
            DEFAULT_USER_AGENT,
            VERIFY_SSL,
        )

# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class HTTPResponse:
    """Complete HTTP response information."""

    url: str
    final_url: str
    status_code: int
    reason: str

    # Headers
    headers: Dict[str, str] = field(default_factory=dict)

    # Server info
    server: Optional[str] = None
    powered_by: Optional[str] = None

    # Timing
    response_time_ms: float = 0.0
    dns_time_ms: Optional[float] = None
    connect_time_ms: Optional[float] = None

    # Redirect info
    was_redirected: bool = False
    redirect_count: int = 0
    redirect_chain: List[str] = field(default_factory=list)

    # Content info
    content_type: Optional[str] = None
    content_length: Optional[int] = None
    charset: Optional[str] = None

    # Response characteristics
    is_compressed: bool = False
    compression_type: Optional[str] = None

    # Error info
    error: Optional[str] = None
    error_type: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert response model to dictionary."""
        return asdict(self)


@dataclass
class StatusCodeInfo:
    """Information about an HTTP status code."""

    code: int
    category: str  # informational, success, redirect, client_error, server_error
    reason: str
    description: str
    is_success: bool
    is_error: bool
    is_redirect: bool

    def to_dict(self) -> dict:
        """Convert status code model to dictionary."""
        return asdict(self)


# =============================================================================
# HTTP INSPECTION
# =============================================================================


def inspect_url(
    url: str,
    method: str = "GET",
    timeout: int = DEFAULT_HTTP_TIMEOUT,
    follow_redirects: bool = True,
    verify_ssl: bool = VERIFY_SSL,
    custom_headers: Optional[Dict[str, str]] = None,
) -> HTTPResponse:
    """
    Perform comprehensive HTTP inspection of a URL.

    Args:
        url: URL to inspect
        method: HTTP method (GET, HEAD, POST, etc.)
        timeout: Request timeout in seconds
        follow_redirects: Whether to follow redirects
        verify_ssl: Whether to verify SSL certificates
        custom_headers: Additional headers to send

    Returns:
        HTTPResponse object with all collected information

    Example:
        >>> response = inspect_url('https://example.com')
        >>> print(f"Status: {response.status_code}")
        >>> print(f"Server: {response.server}")
        >>> print(f"Response time: {response.response_time_ms}ms")
    """
    # Ensure URL has scheme
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Prepare headers
    headers = {"User-Agent": DEFAULT_USER_AGENT}
    if custom_headers:
        headers.update(custom_headers)

    result = HTTPResponse(
        url=url,
        final_url=url,
        status_code=0,
        reason="",
    )

    try:
        # Make request
        response = requests.request(
            method=method,
            url=url,
            timeout=timeout,
            allow_redirects=follow_redirects,
            verify=verify_ssl,
            headers=headers,
        )

        # Basic info
        result.status_code = response.status_code
        result.reason = response.reason
        result.final_url = response.url
        result.headers = dict(response.headers)

        # Server info
        result.server = response.headers.get("Server")
        result.powered_by = response.headers.get("X-Powered-By")

        # Timing
        if hasattr(response, "elapsed"):
            result.response_time_ms = response.elapsed.total_seconds() * 1000

        # Redirect info
        result.was_redirected = response.url != url
        if hasattr(response, "history"):
            result.redirect_count = len(response.history)
            result.redirect_chain = [r.url for r in response.history]

        # Content info
        content_type = response.headers.get("Content-Type", "")
        if content_type:
            parts = content_type.split(";")
            result.content_type = parts[0].strip()

            # Extract charset
            for part in parts[1:]:
                if "charset=" in part:
                    result.charset = part.split("=", 1)[1].strip()

        content_length = response.headers.get("Content-Length")
        if content_length:
            try:
                result.content_length = int(content_length)
            except ValueError:
                pass

        # Compression
        encoding = response.headers.get("Content-Encoding")
        if encoding:
            result.is_compressed = True
            result.compression_type = encoding

    except requests.RequestException as e:
        result.error = str(e)
        result.error_type = type(e).__name__

    return result


def head_request(url: str, **kwargs) -> HTTPResponse:
    """
    Perform HEAD request (faster, no body download).

    Args:
        url: URL to check
        **kwargs: Additional arguments for inspect_url

    Returns:
        HTTPResponse object
    """
    return inspect_url(url, method="HEAD", **kwargs)


def get_request(url: str, **kwargs) -> HTTPResponse:
    """
    Perform GET request (full response).

    Args:
        url: URL to fetch
        **kwargs: Additional arguments for inspect_url

    Returns:
        HTTPResponse object
    """
    return inspect_url(url, method="GET", **kwargs)


# =============================================================================
# HEADER ANALYSIS
# =============================================================================


def extract_header(
    response: HTTPResponse,
    header_name: str,
    case_sensitive: bool = False,
) -> Optional[str]:
    """
    Extract a specific header from response.

    Args:
        response: HTTPResponse object
        header_name: Name of header to extract
        case_sensitive: Whether to match case exactly

    Returns:
        Header value or None
    """
    if case_sensitive:
        return response.headers.get(header_name)

    # Case-insensitive search
    header_lower = header_name.lower()
    for key, value in response.headers.items():
        if key.lower() == header_lower:
            return value

    return None


def get_security_headers(response: HTTPResponse) -> Dict[str, Optional[str]]:
    """
    Extract security-related headers.

    Args:
        response: HTTPResponse object

    Returns:
        Dictionary of security headers
    """
    security_headers = [
        "Strict-Transport-Security",
        "Content-Security-Policy",
        "X-Content-Type-Options",
        "X-Frame-Options",
        "X-XSS-Protection",
        "Referrer-Policy",
        "Permissions-Policy",
    ]

    return {header: extract_header(response, header) for header in security_headers}


def get_cache_headers(response: HTTPResponse) -> Dict[str, Optional[str]]:
    """
    Extract cache-related headers.

    Args:
        response: HTTPResponse object

    Returns:
        Dictionary of cache headers
    """
    cache_headers = [
        "Cache-Control",
        "Pragma",
        "Expires",
        "ETag",
        "Last-Modified",
        "Age",
    ]

    return {header: extract_header(response, header) for header in cache_headers}


def get_cors_headers(response: HTTPResponse) -> Dict[str, Optional[str]]:
    """
    Extract CORS-related headers.

    Args:
        response: HTTPResponse object

    Returns:
        Dictionary of CORS headers
    """
    cors_headers = [
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Methods",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Credentials",
        "Access-Control-Max-Age",
        "Access-Control-Expose-Headers",
    ]

    return {header: extract_header(response, header) for header in cors_headers}


# =============================================================================
# STATUS CODE ANALYSIS
# =============================================================================

STATUS_CODE_INFO = {
    # 1xx Informational
    100: ("Informational", "Continue", "Client should continue request"),
    101: ("Informational", "Switching Protocols", "Server switching protocols"),
    # 2xx Success
    200: ("Success", "OK", "Request succeeded"),
    201: ("Success", "Created", "Resource created"),
    202: ("Success", "Accepted", "Request accepted for processing"),
    204: ("Success", "No Content", "Request succeeded, no content to return"),
    206: ("Success", "Partial Content", "Partial resource delivered"),
    # 3xx Redirection
    300: ("Redirect", "Multiple Choices", "Multiple options available"),
    301: ("Redirect", "Moved Permanently", "Resource permanently moved"),
    302: ("Redirect", "Found", "Resource temporarily moved"),
    303: ("Redirect", "See Other", "See other URL"),
    304: ("Redirect", "Not Modified", "Resource not modified"),
    307: ("Redirect", "Temporary Redirect", "Temporary redirect, preserve method"),
    308: ("Redirect", "Permanent Redirect", "Permanent redirect, preserve method"),
    # 4xx Client Errors
    400: ("Client Error", "Bad Request", "Invalid request syntax"),
    401: ("Client Error", "Unauthorized", "Authentication required"),
    403: ("Client Error", "Forbidden", "Access denied"),
    404: ("Client Error", "Not Found", "Resource not found"),
    405: ("Client Error", "Method Not Allowed", "HTTP method not allowed"),
    408: ("Client Error", "Request Timeout", "Request took too long"),
    410: ("Client Error", "Gone", "Resource permanently removed"),
    429: ("Client Error", "Too Many Requests", "Rate limit exceeded"),
    # 5xx Server Errors
    500: ("Server Error", "Internal Server Error", "Server error occurred"),
    502: ("Server Error", "Bad Gateway", "Invalid response from upstream"),
    503: ("Server Error", "Service Unavailable", "Service temporarily unavailable"),
    504: ("Server Error", "Gateway Timeout", "Upstream timeout"),
}


def get_status_info(status_code: int) -> StatusCodeInfo:
    """
    Get information about an HTTP status code.

    Args:
        status_code: HTTP status code

    Returns:
        StatusCodeInfo object
    """
    if status_code in STATUS_CODE_INFO:
        category, reason, description = STATUS_CODE_INFO[status_code]
    else:
        # Generic category
        if 100 <= status_code < 200:
            category = "Informational"
        elif 200 <= status_code < 300:
            category = "Success"
        elif 300 <= status_code < 400:
            category = "Redirect"
        elif 400 <= status_code < 500:
            category = "Client Error"
        elif 500 <= status_code < 600:
            category = "Server Error"
        else:
            category = "Unknown"

        reason = f"Status {status_code}"
        description = f"HTTP status code {status_code}"

    return StatusCodeInfo(
        code=status_code,
        category=category,
        reason=reason,
        description=description,
        is_success=(200 <= status_code < 300),
        is_error=(400 <= status_code < 600),
        is_redirect=(300 <= status_code < 400),
    )


def is_success(status_code: int) -> bool:
    """Check if status code indicates success (2xx)."""
    return 200 <= status_code < 300


def is_redirect(status_code: int) -> bool:
    """Check if status code indicates redirect (3xx)."""
    return 300 <= status_code < 400


def is_client_error(status_code: int) -> bool:
    """Check if status code indicates client error (4xx)."""
    return 400 <= status_code < 500


def is_server_error(status_code: int) -> bool:
    """Check if status code indicates server error (5xx)."""
    return 500 <= status_code < 600


def is_error(status_code: int) -> bool:
    """Check if status code indicates any error (4xx or 5xx)."""
    return 400 <= status_code < 600
