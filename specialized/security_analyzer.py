"""
Security analysis for HTTP responses.

Analyzes security headers, CORS policies, robots.txt, and security best practices.
"""

from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Dict, List, Optional
from urllib.parse import urljoin, urlparse

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
class SecurityAnalysis:
    """Complete security analysis for a URL."""

    url: str

    # Security headers present
    hsts: Optional[str] = None
    csp: Optional[str] = None
    x_frame_options: Optional[str] = None
    x_content_type_options: Optional[str] = None
    x_xss_protection: Optional[str] = None
    referrer_policy: Optional[str] = None
    permissions_policy: Optional[str] = None

    # Security header analysis
    has_hsts: bool = False
    has_csp: bool = False
    has_frame_protection: bool = False
    has_mime_sniff_protection: bool = False

    # Missing headers
    missing_security_headers: List[str] = field(default_factory=list)

    # Security score
    security_score: int = 0  # 0-100

    # Issues found
    security_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert security analysis model to dictionary."""
        return asdict(self)


@dataclass
class CORSAnalysis:
    """CORS policy analysis."""

    url: str

    # CORS headers
    allow_origin: Optional[str] = None
    allow_methods: List[str] = field(default_factory=list)
    allow_headers: List[str] = field(default_factory=list)
    expose_headers: List[str] = field(default_factory=list)
    max_age: Optional[int] = None
    allow_credentials: bool = False

    # Analysis
    is_cors_enabled: bool = False
    allows_any_origin: bool = False
    allows_credentials_with_wildcard: bool = False

    # Security assessment
    cors_security_level: str = "Unknown"  # Secure, Moderate, Permissive, Insecure
    cors_issues: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert CORS analysis model to dictionary."""
        return asdict(self)


@dataclass
class RobotsAnalysis:
    """robots.txt analysis."""

    url: str
    robots_url: str

    # Content
    exists: bool = False
    content: Optional[str] = None

    # Directives
    user_agents: Dict[str, List[str]] = field(default_factory=dict)  # user-agent -> directives
    sitemaps: List[str] = field(default_factory=list)
    crawl_delays: Dict[str, int] = field(default_factory=dict)

    # Analysis for specific user agent
    is_allowed_for_agent: Optional[bool] = None
    disallowed_paths: List[str] = field(default_factory=list)
    allowed_paths: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert robots analysis model to dictionary."""
        return asdict(self)


# =============================================================================
# SECURITY HEADER ANALYSIS
# =============================================================================


def analyze_security_headers(
    url: str,
    headers: Dict[str, str],
) -> SecurityAnalysis:
    """
    Analyze security headers for a response.

    Args:
        url: URL being analyzed
        headers: Response headers

    Returns:
        SecurityAnalysis object

    Example:
        >>> analysis = analyze_security_headers(url, response.headers)
        >>> print(f"Security score: {analysis.security_score}/100")
        >>> for issue in analysis.security_issues:
        ...     print(f"Issue: {issue}")
    """
    analysis = SecurityAnalysis(url=url)
    score = 0

    # Check each security header
    analysis.hsts = headers.get("Strict-Transport-Security")
    if analysis.hsts:
        analysis.has_hsts = True
        score += 25

        # Check HSTS strength
        if "max-age" in analysis.hsts:
            max_age_str = analysis.hsts.split("max-age=")[1].split(";")[0].strip()
            try:
                max_age = int(max_age_str)
                if max_age < 31536000:  # Less than 1 year
                    analysis.security_issues.append("HSTS max-age is less than 1 year")
                    analysis.recommendations.append("Increase HSTS max-age to at least 31536000 (1 year)")
            except Exception:
                pass

        if "includeSubDomains" not in analysis.hsts:
            analysis.recommendations.append("Add includeSubDomains to HSTS for subdomain protection")
    else:
        analysis.missing_security_headers.append("Strict-Transport-Security")
        analysis.recommendations.append("Add HSTS header for HTTPS enforcement")

    # Content Security Policy
    analysis.csp = headers.get("Content-Security-Policy")
    if analysis.csp:
        analysis.has_csp = True
        score += 25

        # Check for unsafe directives
        if "'unsafe-inline'" in analysis.csp or "'unsafe-eval'" in analysis.csp:
            analysis.security_issues.append("CSP contains unsafe-inline or unsafe-eval")
            analysis.recommendations.append("Remove unsafe-inline and unsafe-eval from CSP")
    else:
        analysis.missing_security_headers.append("Content-Security-Policy")
        analysis.recommendations.append("Add CSP header to prevent XSS attacks")

    # Frame Options
    analysis.x_frame_options = headers.get("X-Frame-Options")
    if analysis.x_frame_options:
        analysis.has_frame_protection = True
        score += 15
    else:
        analysis.missing_security_headers.append("X-Frame-Options")
        analysis.recommendations.append("Add X-Frame-Options to prevent clickjacking")

    # MIME Sniffing Protection
    analysis.x_content_type_options = headers.get("X-Content-Type-Options")
    if analysis.x_content_type_options == "nosniff":
        analysis.has_mime_sniff_protection = True
        score += 15
    else:
        analysis.missing_security_headers.append("X-Content-Type-Options")
        analysis.recommendations.append("Add X-Content-Type-Options: nosniff")

    # XSS Protection
    analysis.x_xss_protection = headers.get("X-XSS-Protection")
    if analysis.x_xss_protection:
        score += 10
    else:
        analysis.missing_security_headers.append("X-XSS-Protection")

    # Referrer Policy
    analysis.referrer_policy = headers.get("Referrer-Policy")
    if analysis.referrer_policy:
        score += 5
    else:
        analysis.recommendations.append("Add Referrer-Policy header")

    # Permissions Policy
    analysis.permissions_policy = headers.get("Permissions-Policy")
    if analysis.permissions_policy:
        score += 5

    analysis.security_score = score

    return analysis


# =============================================================================
# CORS ANALYSIS
# =============================================================================


def analyze_cors(
    url: str,
    headers: Dict[str, str],
) -> CORSAnalysis:
    """
    Analyze CORS headers and policies.

    Args:
        url: URL being analyzed
        headers: Response headers

    Returns:
        CORSAnalysis object

    Example:
        >>> cors = analyze_cors(url, response.headers)
        >>> print(f"CORS enabled: {cors.is_cors_enabled}")
        >>> print(f"Security level: {cors.cors_security_level}")
    """
    analysis = CORSAnalysis(url=url)

    # Parse CORS headers
    analysis.allow_origin = headers.get("Access-Control-Allow-Origin")

    if analysis.allow_origin:
        analysis.is_cors_enabled = True

        # Check for wildcard
        if analysis.allow_origin == "*":
            analysis.allows_any_origin = True

    # Allow Methods
    allow_methods = headers.get("Access-Control-Allow-Methods")
    if allow_methods:
        analysis.allow_methods = [m.strip() for m in allow_methods.split(",")]

    # Allow Headers
    allow_headers = headers.get("Access-Control-Allow-Headers")
    if allow_headers:
        analysis.allow_headers = [h.strip() for h in allow_headers.split(",")]

    # Expose Headers
    expose_headers = headers.get("Access-Control-Expose-Headers")
    if expose_headers:
        analysis.expose_headers = [h.strip() for h in expose_headers.split(",")]

    # Max Age
    max_age = headers.get("Access-Control-Max-Age")
    if max_age:
        try:
            analysis.max_age = int(max_age)
        except ValueError:
            pass

    # Allow Credentials
    allow_creds = headers.get("Access-Control-Allow-Credentials")
    if allow_creds and allow_creds.lower() == "true":
        analysis.allow_credentials = True

        # Critical security issue: wildcard with credentials
        if analysis.allows_any_origin:
            analysis.allows_credentials_with_wildcard = True
            analysis.cors_issues.append("CRITICAL: Wildcard origin with credentials enabled")

    # Determine security level
    if analysis.allows_credentials_with_wildcard:
        analysis.cors_security_level = "Insecure"
    elif analysis.allows_any_origin:
        analysis.cors_security_level = "Permissive"
    elif analysis.is_cors_enabled:
        analysis.cors_security_level = "Moderate"
    else:
        analysis.cors_security_level = "Secure (no CORS)"

    # Additional checks
    if analysis.allow_methods and "DELETE" in analysis.allow_methods:
        analysis.cors_issues.append("DELETE method allowed via CORS")

    if analysis.allow_methods and "PUT" in analysis.allow_methods:
        analysis.cors_issues.append("PUT method allowed via CORS")

    return analysis


# =============================================================================
# ROBOTS.TXT ANALYSIS
# =============================================================================


def fetch_robots_txt(
    url: str,
    timeout: int = DEFAULT_HTTP_TIMEOUT,
    verify_ssl: bool = VERIFY_SSL,
    user_agent: str = DEFAULT_USER_AGENT,
) -> RobotsAnalysis:
    """
    Fetch and parse robots.txt for a domain.

    Args:
        url: Base URL (will fetch /robots.txt)
        timeout: Request timeout

    Returns:
        RobotsAnalysis object

    Example:
        >>> robots = fetch_robots_txt('https://example.com')
        >>> print(f"Exists: {robots.exists}")
        >>> print(f"Sitemaps: {robots.sitemaps}")
    """
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    robots_url = urljoin(base_url, "/robots.txt")

    analysis = RobotsAnalysis(
        url=url,
        robots_url=robots_url,
    )

    try:
        response = requests.get(
            robots_url,
            timeout=timeout,
            verify=verify_ssl,
            headers={"User-Agent": user_agent},
        )

        if response.status_code == 200:
            analysis.exists = True
            analysis.content = response.text

            # Parse robots.txt
            parse_robots_txt(analysis)

    except Exception:
        pass

    return analysis


def parse_robots_txt(analysis: RobotsAnalysis):
    """
    Parse robots.txt content.

    Modifies analysis object in place.
    """
    if not analysis.content:
        return

    current_agent = None

    for line in analysis.content.split("\n"):
        line = line.strip()

        # Skip comments and empty lines
        if not line or line.startswith("#"):
            continue

        # Split directive
        if ":" not in line:
            continue

        directive, value = line.split(":", 1)
        directive = directive.strip().lower()
        value = value.strip()

        # User-agent
        if directive == "user-agent":
            current_agent = value
            if current_agent not in analysis.user_agents:
                analysis.user_agents[current_agent] = []

        # Disallow
        elif directive == "disallow" and current_agent:
            analysis.user_agents[current_agent].append(f"disallow:{value}")
            analysis.disallowed_paths.append(value)

        # Allow
        elif directive == "allow" and current_agent:
            analysis.user_agents[current_agent].append(f"allow:{value}")
            analysis.allowed_paths.append(value)

        # Sitemap
        elif directive == "sitemap":
            analysis.sitemaps.append(value)

        # Crawl-delay
        elif directive == "crawl-delay" and current_agent:
            try:
                analysis.crawl_delays[current_agent] = int(value)
            except ValueError:
                pass


def check_robots_allowed(
    analysis: RobotsAnalysis,
    path: str,
    user_agent: str = "*",
) -> bool:
    """
    Check if a path is allowed for a user agent.

    Args:
        analysis: RobotsAnalysis object
        path: URL path to check
        user_agent: User agent to check for

    Returns:
        True if allowed, False if disallowed
    """
    if not analysis.exists:
        return True  # No robots.txt = allowed

    # Get directives for this user agent
    directives = analysis.user_agents.get(user_agent, [])

    # Also check wildcard
    if user_agent != "*":
        directives += analysis.user_agents.get("*", [])

    # Check directives (most specific first)
    for directive in directives:
        if directive.startswith("disallow:"):
            pattern = directive.split(":", 1)[1]
            if path.startswith(pattern):
                return False

        elif directive.startswith("allow:"):
            pattern = directive.split(":", 1)[1]
            if path.startswith(pattern):
                return True

    return True  # Default allow


# =============================================================================
# META ROBOTS TAGS
# =============================================================================


def parse_robots_meta_tag(meta_content: str) -> Dict[str, bool]:
    """
    Parse robots meta tag content.

    Args:
        meta_content: Content of meta robots tag

    Returns:
        Dictionary of directives

    Example:
        >>> parse_robots_meta_tag("noindex, nofollow")
        {'noindex': True, 'nofollow': True}
    """
    directives = {}

    for directive in meta_content.lower().split(","):
        directive = directive.strip()

        if directive in (
            "index",
            "noindex",
            "follow",
            "nofollow",
            "noarchive",
            "nosnippet",
            "noimageindex",
            "none",
            "all",
        ):
            directives[directive] = True

    return directives


def is_indexable(robots_directives: Dict[str, bool]) -> bool:
    """
    Check if page is indexable based on robots directives.

    Args:
        robots_directives: Parsed robots meta tag

    Returns:
        True if indexable, False otherwise
    """
    if robots_directives.get("noindex") or robots_directives.get("none"):
        return False

    return True


def is_followable(robots_directives: Dict[str, bool]) -> bool:
    """
    Check if links should be followed based on robots directives.

    Args:
        robots_directives: Parsed robots meta tag

    Returns:
        True if followable, False otherwise
    """
    if robots_directives.get("nofollow") or robots_directives.get("none"):
        return False

    return True
