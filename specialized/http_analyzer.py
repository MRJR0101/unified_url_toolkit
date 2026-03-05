"""
HTTP Response Analysis - Status codes, headers, and response properties.

Analyzes HTTP responses including:
- Status codes and categories
- Server headers
- CORS headers
- Security headers
- Custom header analysis
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from urllib.parse import urlparse

import requests  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from ..config.settings import DEFAULT_HTTP_TIMEOUT, DEFAULT_USER_AGENT, VERIFY_SSL
else:
    try:
        from ..config.settings import DEFAULT_HTTP_TIMEOUT, DEFAULT_USER_AGENT, VERIFY_SSL
    except ImportError:
        from config.settings import DEFAULT_HTTP_TIMEOUT, DEFAULT_USER_AGENT, VERIFY_SSL

# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class HTTPResponse:
    """Complete HTTP response analysis."""

    # Basic info
    url: str
    final_url: str
    status_code: int
    status_category: str  # 1xx, 2xx, 3xx, 4xx, 5xx
    status_name: str  # OK, Not Found, etc.

    # Timing
    response_time_ms: float
    timestamp: datetime = field(default_factory=datetime.now)

    # Headers
    headers: Dict[str, str] = field(default_factory=dict)

    # Server info
    server: Optional[str] = None
    powered_by: Optional[str] = None

    # Content info
    content_type: Optional[str] = None
    content_length: Optional[int] = None
    content_encoding: Optional[str] = None

    # CORS
    cors_allowed: bool = False
    cors_origin: Optional[str] = None
    cors_methods: List[str] = field(default_factory=list)
    cors_headers: List[str] = field(default_factory=list)

    # Security
    security_headers: Dict[str, str] = field(default_factory=dict)
    is_https: bool = False
    hsts_enabled: bool = False

    # Cache
    cache_control: Optional[str] = None
    expires: Optional[str] = None
    etag: Optional[str] = None
    last_modified: Optional[str] = None

    # Redirect info
    is_redirect: bool = False
    redirect_location: Optional[str] = None

    # Error info
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert response model to a JSON-serializable dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class HeaderAnalysis:
    """Detailed header analysis."""

    standard_headers: Dict[str, str] = field(default_factory=dict)
    custom_headers: Dict[str, str] = field(default_factory=dict)
    security_headers: Dict[str, str] = field(default_factory=dict)
    cors_headers: Dict[str, str] = field(default_factory=dict)
    cache_headers: Dict[str, str] = field(default_factory=dict)

    missing_security_headers: List[str] = field(default_factory=list)
    unusual_headers: List[str] = field(default_factory=list)


# =============================================================================
# STATUS CODE ANALYSIS
# =============================================================================

STATUS_CODE_NAMES = {
    # 1xx Informational
    100: "Continue",
    101: "Switching Protocols",
    102: "Processing",
    103: "Early Hints",
    # 2xx Success
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    # 3xx Redirection
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    307: "Temporary Redirect",
    308: "Permanent Redirect",
    # 4xx Client Error
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    429: "Too Many Requests",
    # 5xx Server Error
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
}


def get_status_category(status_code: int) -> str:
    """Get status code category (1xx, 2xx, etc.)."""
    if 100 <= status_code < 200:
        return "1xx Informational"
    elif 200 <= status_code < 300:
        return "2xx Success"
    elif 300 <= status_code < 400:
        return "3xx Redirect"
    elif 400 <= status_code < 500:
        return "4xx Client Error"
    elif 500 <= status_code < 600:
        return "5xx Server Error"
    else:
        return "Unknown"


def get_status_name(status_code: int) -> str:
    """Get human-readable status name."""
    return STATUS_CODE_NAMES.get(status_code, "Unknown Status")


# =============================================================================
# HTTP RESPONSE FETCHER
# =============================================================================


def fetch_http_response(
    url: str,
    method: str = "GET",
    timeout: int = DEFAULT_HTTP_TIMEOUT,
    allow_redirects: bool = True,
    verify_ssl: bool = VERIFY_SSL,
    user_agent: Optional[str] = None,
) -> HTTPResponse:
    """
    Fetch and analyze HTTP response for a URL.

    Args:
        url: URL to fetch
        method: HTTP method (GET, HEAD, etc.)
        timeout: Request timeout in seconds
        allow_redirects: Whether to follow redirects
        verify_ssl: Whether to verify SSL certificates
        user_agent: Custom user agent string

    Returns:
        HTTPResponse object with complete analysis

    Example:
        >>> response = fetch_http_response("https://example.com")
        >>> print(f"Status: {response.status_code} - {response.status_name}")
        >>> print(f"Server: {response.server}")
        >>> print(f"CORS: {response.cors_allowed}")
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    headers = {"User-Agent": user_agent or DEFAULT_USER_AGENT}

    start_time = datetime.now()

    try:
        response = requests.request(
            method,
            url,
            timeout=timeout,
            allow_redirects=allow_redirects,
            verify=verify_ssl,
            headers=headers,
        )

        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000

        # Build response object
        http_response = HTTPResponse(
            url=url,
            final_url=response.url,
            status_code=response.status_code,
            status_category=get_status_category(response.status_code),
            status_name=get_status_name(response.status_code),
            response_time_ms=elapsed_ms,
            headers=dict(response.headers),
        )

        # Parse URL scheme
        http_response.is_https = urlparse(url).scheme == "https"

        # Extract server info
        http_response.server = response.headers.get("Server")
        http_response.powered_by = response.headers.get("X-Powered-By")

        # Extract content info
        http_response.content_type = response.headers.get("Content-Type")
        content_length = response.headers.get("Content-Length")
        if content_length:
            try:
                http_response.content_length = int(content_length)
            except ValueError:
                http_response.content_length = None
        http_response.content_encoding = response.headers.get("Content-Encoding")

        # Analyze CORS
        cors_analysis = analyze_cors(response.headers)
        http_response.cors_allowed = cors_analysis["allowed"]
        http_response.cors_origin = cors_analysis["origin"]
        http_response.cors_methods = cors_analysis["methods"]
        http_response.cors_headers = cors_analysis["headers"]

        # Analyze security headers
        security = analyze_security_headers(response.headers)
        http_response.security_headers = security
        http_response.hsts_enabled = "Strict-Transport-Security" in response.headers

        # Cache headers
        http_response.cache_control = response.headers.get("Cache-Control")
        http_response.expires = response.headers.get("Expires")
        http_response.etag = response.headers.get("ETag")
        http_response.last_modified = response.headers.get("Last-Modified")

        # Redirect detection
        http_response.is_redirect = 300 <= response.status_code < 400
        if http_response.is_redirect:
            http_response.redirect_location = response.headers.get("Location")

        return http_response

    except Exception as e:
        # Return error response
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000

        return HTTPResponse(
            url=url,
            final_url=url,
            status_code=0,
            status_category="Error",
            status_name="Request Failed",
            response_time_ms=elapsed_ms,
            error=str(e),
        )


# =============================================================================
# CORS ANALYSIS
# =============================================================================


def analyze_cors(headers: Dict[str, str]) -> Dict[str, Any]:
    """
    Analyze CORS headers.

    Args:
        headers: Response headers

    Returns:
        Dictionary with CORS analysis
    """
    cors_origin = headers.get("Access-Control-Allow-Origin")
    cors_methods = headers.get("Access-Control-Allow-Methods", "")
    cors_headers = headers.get("Access-Control-Allow-Headers", "")

    return {
        "allowed": bool(cors_origin),
        "origin": cors_origin,
        "methods": [m.strip() for m in cors_methods.split(",") if m.strip()],
        "headers": [h.strip() for h in cors_headers.split(",") if h.strip()],
        "credentials": headers.get("Access-Control-Allow-Credentials") == "true",
        "max_age": headers.get("Access-Control-Max-Age"),
    }


# =============================================================================
# SECURITY HEADER ANALYSIS
# =============================================================================

SECURITY_HEADERS = {
    "Strict-Transport-Security": "HSTS",
    "Content-Security-Policy": "CSP",
    "X-Frame-Options": "Frame Protection",
    "X-Content-Type-Options": "MIME Sniffing Protection",
    "X-XSS-Protection": "XSS Protection",
    "Referrer-Policy": "Referrer Policy",
    "Permissions-Policy": "Permissions Policy",
}


def analyze_security_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """
    Extract and analyze security headers.

    Args:
        headers: Response headers

    Returns:
        Dictionary of security headers and their values
    """
    security = {}

    for header, name in SECURITY_HEADERS.items():
        if header in headers:
            security[name] = headers[header]

    return security


def get_missing_security_headers(headers: Dict[str, str]) -> List[str]:
    """
    Get list of recommended security headers that are missing.

    Args:
        headers: Response headers

    Returns:
        List of missing security header names
    """
    missing = []

    for header, name in SECURITY_HEADERS.items():
        if header not in headers:
            missing.append(name)

    return missing


# =============================================================================
# HEADER CATEGORIZATION
# =============================================================================


def categorize_headers(headers: Dict[str, str]) -> HeaderAnalysis:
    """
    Categorize response headers into groups.

    Args:
        headers: Response headers

    Returns:
        HeaderAnalysis with categorized headers
    """
    standard = {}
    custom = {}
    security = {}
    cors = {}
    cache = {}

    # Standard headers
    standard_header_names = {
        "Date",
        "Server",
        "Content-Type",
        "Content-Length",
        "Connection",
        "Keep-Alive",
        "Transfer-Encoding",
        "Content-Encoding",
        "Vary",
        "Location",
    }

    # CORS headers
    cors_header_names = {
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Methods",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Credentials",
        "Access-Control-Max-Age",
        "Access-Control-Expose-Headers",
    }

    # Cache headers
    cache_header_names = {
        "Cache-Control",
        "Expires",
        "ETag",
        "Last-Modified",
        "Age",
        "Pragma",
    }

    for header, value in headers.items():
        if header in SECURITY_HEADERS:
            security[header] = value
        elif header in cors_header_names:
            cors[header] = value
        elif header in cache_header_names:
            cache[header] = value
        elif header in standard_header_names:
            standard[header] = value
        else:
            custom[header] = value

    return HeaderAnalysis(
        standard_headers=standard,
        custom_headers=custom,
        security_headers=security,
        cors_headers=cors,
        cache_headers=cache,
        missing_security_headers=get_missing_security_headers(headers),
        unusual_headers=[h for h in custom if h.startswith("X-")],
    )


# =============================================================================
# BATCH ANALYSIS
# =============================================================================


def analyze_multiple_urls(
    urls: List[str],
    method: str = "HEAD",
    timeout: int = DEFAULT_HTTP_TIMEOUT,
    max_workers: int = 10,
) -> List[HTTPResponse]:
    """
    Analyze multiple URLs in parallel.

    Args:
        urls: List of URLs to analyze
        method: HTTP method to use
        timeout: Request timeout
        max_workers: Number of parallel workers

    Returns:
        List of HTTPResponse objects
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    responses_by_index: dict[int, HTTPResponse] = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(fetch_http_response, url, method, timeout): idx for idx, url in enumerate(urls)
        }

        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                responses_by_index[idx] = future.result()
            except Exception as e:
                responses_by_index[idx] = HTTPResponse(
                    url=urls[idx],
                    final_url=urls[idx],
                    status_code=0,
                    status_category="Error",
                    status_name="Analysis Failed",
                    response_time_ms=0,
                    error=str(e),
                )

    return [
        responses_by_index.get(
            idx,
            HTTPResponse(
                url=url,
                final_url=url,
                status_code=0,
                status_category="Error",
                status_name="Analysis Failed",
                response_time_ms=0,
                error="analysis did not return a result",
            ),
        )
        for idx, url in enumerate(urls)
    ]
