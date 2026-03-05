"""
Cache Analysis - Cache headers, fingerprinting, and cache behavior.

Analyzes caching behavior including:
- Cache-Control directives
- Expires headers
- ETag validation
- Last-Modified headers
- Resource fingerprinting (file.js?v=123)
- Cache freshness calculation
"""

import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class CacheAnalysis:
    """Complete cache behavior analysis."""

    # URL and fingerprinting
    url: str
    has_fingerprint: bool = False
    fingerprint_type: Optional[str] = None  # "query", "path", "hash"
    fingerprint_value: Optional[str] = None
    clean_url: Optional[str] = None  # URL without fingerprint

    # Cache-Control
    cache_control: Optional[str] = None
    cache_directives: List[str] = field(default_factory=list)
    max_age: Optional[int] = None  # seconds
    s_maxage: Optional[int] = None  # CDN max age
    is_public: bool = False
    is_private: bool = False
    must_revalidate: bool = False
    no_cache: bool = False
    no_store: bool = False
    immutable: bool = False

    # Validation
    etag: Optional[str] = None
    etag_is_weak: bool = False
    last_modified: Optional[str] = None
    last_modified_date: Optional[datetime] = None

    # Expiration
    expires: Optional[str] = None
    expires_date: Optional[datetime] = None
    age: Optional[int] = None  # Current age in seconds

    # Analysis
    is_cacheable: bool = False
    is_fresh: bool = False
    freshness_lifetime: Optional[int] = None  # seconds
    current_age: Optional[int] = None  # seconds
    time_to_expire: Optional[int] = None  # seconds remaining

    # Recommendations
    cache_score: Optional[int] = None  # 0-100
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert analysis model to a JSON-serializable dictionary."""
        data = asdict(self)
        data["last_modified_date"] = self.last_modified_date.isoformat() if self.last_modified_date else None
        data["expires_date"] = self.expires_date.isoformat() if self.expires_date else None
        return data


# =============================================================================
# RESOURCE FINGERPRINTING DETECTION
# =============================================================================


def detect_fingerprint(url: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Detect resource fingerprinting in URL.

    Common patterns:
    - Query parameter: file.js?v=123, file.css?version=1.2.3
    - Path: /static/v123/file.js, /assets/file.123abc.js
    - Hash: file.abc123def.js

    Args:
        url: URL to analyze

    Returns:
        (has_fingerprint, type, value) tuple

    Example:
        >>> detect_fingerprint("https://example.com/app.js?v=1.2.3")
        (True, 'query', '1.2.3')
    """
    parsed = urlparse(url)

    # Check query parameters
    query_params = parse_qs(parsed.query)
    version_params = ["v", "ver", "version", "rev", "hash", "h", "t", "time"]

    for param in version_params:
        if param in query_params:
            value = query_params[param][0]
            return True, "query", value

    # Check path for versioning
    path = parsed.path

    # Pattern: /v123/file.js or /version-1.2.3/file.js
    version_path_pattern = r"/(?:v|version)[-_]?(\d+(?:\.\d+)*)"
    match = re.search(version_path_pattern, path, re.IGNORECASE)
    if match:
        return True, "path", match.group(1)

    # Pattern: file.abc123def.js (hash in filename)
    hash_pattern = r"\.([a-f0-9]{8,})\."
    match = re.search(hash_pattern, path)
    if match:
        return True, "hash", match.group(1)

    # Pattern: file-abc123.js
    hash_pattern2 = r"-([a-f0-9]{8,})\."
    match = re.search(hash_pattern2, path)
    if match:
        return True, "hash", match.group(1)

    return False, None, None


def remove_fingerprint(url: str) -> str:
    """
    Remove fingerprinting from URL to get clean canonical URL.

    Args:
        url: URL with fingerprinting

    Returns:
        Clean URL without fingerprinting
    """
    parsed = urlparse(url)

    # Remove version query parameters
    query_params = parse_qs(parsed.query)
    version_params = ["v", "ver", "version", "rev", "hash", "h", "t", "time"]

    cleaned_params = {k: v for k, v in query_params.items() if k not in version_params}

    # Rebuild query string
    if cleaned_params:
        from urllib.parse import urlencode

        new_query = urlencode(cleaned_params, doseq=True)
    else:
        new_query = ""

    # Remove hash from path
    path = parsed.path
    path = re.sub(r"\.([a-f0-9]{8,})\.", ".", path)
    path = re.sub(r"-([a-f0-9]{8,})\.", ".", path)

    # Rebuild URL
    from urllib.parse import urlunparse

    return urlunparse((parsed.scheme, parsed.netloc, path, parsed.params, new_query, parsed.fragment))


# =============================================================================
# CACHE-CONTROL PARSING
# =============================================================================


def parse_cache_control(cache_control: str) -> Dict[str, Any]:
    """
    Parse Cache-Control header.

    Args:
        cache_control: Cache-Control header value

    Returns:
        Dictionary of directives
    """
    if not cache_control:
        return {}

    directives: Dict[str, Any] = {}

    for directive in cache_control.split(","):
        directive = directive.strip()

        if "=" in directive:
            key, value = directive.split("=", 1)
            key = key.strip()
            value = value.strip()

            # Try to convert to int if it's a number
            try:
                value = int(value)
            except ValueError:
                pass

            directives[key] = value
        else:
            directives[directive] = True

    return directives


def _directive_as_int(value: Any) -> Optional[int]:
    """Convert cache directive value to int when possible."""
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _directive_as_bool(value: Any) -> bool:
    """Convert cache directive value to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "1"}:
            return True
        if normalized in {"false", "no", "0"}:
            return False
    return bool(value)


# =============================================================================
# CACHE ANALYSIS FUNCTION
# =============================================================================


def analyze_cache(
    url: str,
    cache_control: Optional[str] = None,
    expires: Optional[str] = None,
    etag: Optional[str] = None,
    last_modified: Optional[str] = None,
    age: Optional[str] = None,
    date: Optional[str] = None,
) -> CacheAnalysis:
    """
    Analyze caching behavior based on headers.

    Args:
        url: Request URL
        cache_control: Cache-Control header
        expires: Expires header
        etag: ETag header
        last_modified: Last-Modified header
        age: Age header
        date: Date header

    Returns:
        CacheAnalysis with complete analysis

    Example:
        >>> analysis = analyze_cache(
        ...     url="https://example.com/app.js?v=1.2.3",
        ...     cache_control="public, max-age=31536000, immutable",
        ...     etag='"abc123"'
        ... )
        >>> print(f"Cacheable: {analysis.is_cacheable}")
        >>> print(f"Fingerprint: {analysis.has_fingerprint}")
    """
    analysis = CacheAnalysis(url=url)

    # Detect fingerprinting
    has_fp, fp_type, fp_value = detect_fingerprint(url)
    analysis.has_fingerprint = has_fp
    analysis.fingerprint_type = fp_type
    analysis.fingerprint_value = fp_value
    if has_fp:
        analysis.clean_url = remove_fingerprint(url)

    # Parse Cache-Control
    if cache_control:
        analysis.cache_control = cache_control
        directives = parse_cache_control(cache_control)
        analysis.cache_directives = list(directives.keys())

        # Extract specific directives
        analysis.max_age = _directive_as_int(directives.get("max-age"))
        analysis.s_maxage = _directive_as_int(directives.get("s-maxage"))
        analysis.is_public = _directive_as_bool(directives.get("public", False))
        analysis.is_private = _directive_as_bool(directives.get("private", False))
        analysis.must_revalidate = _directive_as_bool(directives.get("must-revalidate", False))
        analysis.no_cache = _directive_as_bool(directives.get("no-cache", False))
        analysis.no_store = _directive_as_bool(directives.get("no-store", False))
        analysis.immutable = _directive_as_bool(directives.get("immutable", False))

        # Determine cacheability
        if analysis.no_store:
            analysis.is_cacheable = False
        elif analysis.max_age or analysis.is_public:
            analysis.is_cacheable = True

    # Parse ETag
    if etag:
        analysis.etag = etag
        analysis.etag_is_weak = etag.startswith("W/")

    # Parse Last-Modified
    if last_modified:
        analysis.last_modified = last_modified
        try:
            analysis.last_modified_date = parse_http_date(last_modified)
        except Exception:
            pass

    # Parse Expires
    if expires:
        analysis.expires = expires
        try:
            analysis.expires_date = parse_http_date(expires)
        except Exception:
            pass

    # Parse Age
    if age:
        try:
            analysis.age = int(age)
            analysis.current_age = int(age)
        except ValueError:
            pass

    # Calculate freshness
    if analysis.max_age is not None:
        analysis.freshness_lifetime = analysis.max_age

        if analysis.current_age is not None:
            time_remaining = analysis.max_age - analysis.current_age
            analysis.time_to_expire = max(0, time_remaining)
            analysis.is_fresh = time_remaining > 0
        else:
            analysis.is_fresh = True  # Assume fresh if no age
    elif analysis.expires_date and date:
        try:
            date_dt = parse_http_date(date)
            freshness = (analysis.expires_date - date_dt).total_seconds()
            analysis.freshness_lifetime = int(freshness)

            if analysis.current_age is not None:
                time_remaining = int(freshness) - analysis.current_age
                analysis.time_to_expire = max(0, time_remaining)
                analysis.is_fresh = time_remaining > 0
        except Exception:
            pass

    # Calculate cache score and recommendations
    calculate_cache_score(analysis)

    return analysis


# =============================================================================
# CACHE SCORING
# =============================================================================


def calculate_cache_score(analysis: CacheAnalysis):
    """
    Calculate cache optimization score (0-100) and provide recommendations.

    Modifies analysis object in-place.
    """
    score = 0
    recommendations = []

    # Fingerprinting (+30 points)
    if analysis.has_fingerprint:
        score += 30
        if analysis.immutable:
            score += 10  # Bonus for immutable with fingerprinting
    else:
        recommendations.append("Add version fingerprinting to static resources for better caching")

    # Max-age set (+20 points)
    if analysis.max_age is not None:
        score += 20

        # Appropriate max-age (+10 points)
        if analysis.has_fingerprint and analysis.max_age >= 31536000:
            score += 10  # 1 year is good for fingerprinted resources
        elif not analysis.has_fingerprint and analysis.max_age >= 3600:
            score += 5  # 1 hour+ is reasonable for non-fingerprinted
    else:
        recommendations.append("Set explicit Cache-Control max-age")

    # Public (+10 points for shared caching)
    if analysis.is_public:
        score += 10
    elif not analysis.is_private:
        recommendations.append("Consider 'public' directive for CDN caching")

    # Immutable (+10 points with fingerprinting)
    if analysis.immutable and analysis.has_fingerprint:
        score += 10
    elif analysis.has_fingerprint and not analysis.immutable:
        recommendations.append("Add 'immutable' directive for fingerprinted resources")

    # ETag or Last-Modified (+10 points)
    if analysis.etag or analysis.last_modified:
        score += 10
    else:
        recommendations.append("Add ETag or Last-Modified for conditional requests")

    # Penalties
    if analysis.no_store:
        score = 0
        recommendations.clear()
        recommendations.append("no-store prevents all caching - reconsider if appropriate")
    elif analysis.no_cache:
        score = max(0, score - 20)
        recommendations.append("no-cache requires revalidation on every request")

    analysis.cache_score = score
    analysis.recommendations = recommendations


# =============================================================================
# DATE PARSING
# =============================================================================


def parse_http_date(date_str: str) -> datetime:
    """
    Parse HTTP date format to datetime.

    Supports RFC 1123 format: "Mon, 16 Jan 2026 12:00:00 GMT"
    """
    from email.utils import parsedate_to_datetime

    return parsedate_to_datetime(date_str)


# =============================================================================
# BATCH ANALYSIS
# =============================================================================


def analyze_multiple_caches(responses: List[Dict[str, str]]) -> List[CacheAnalysis]:
    """
    Analyze cache behavior for multiple responses.

    Args:
        responses: List of response dictionaries with URL and headers

    Returns:
        List of CacheAnalysis objects
    """
    analyses = []

    for response in responses:
        analysis = analyze_cache(
            url=response.get("url", ""),
            cache_control=response.get("Cache-Control"),
            expires=response.get("Expires"),
            etag=response.get("ETag"),
            last_modified=response.get("Last-Modified"),
            age=response.get("Age"),
            date=response.get("Date"),
        )
        analyses.append(analysis)

    return analyses


# =============================================================================
# CACHE FORMATTING
# =============================================================================


def format_cache_analysis(analysis: CacheAnalysis) -> str:
    """Format cache analysis as human-readable string."""
    lines = []
    lines.append(f"Cache Analysis for: {analysis.url}")
    lines.append("=" * 60)

    if analysis.has_fingerprint:
        lines.append(f"[YES] Fingerprinted ({analysis.fingerprint_type}: {analysis.fingerprint_value})")
        lines.append(f"  Clean URL: {analysis.clean_url}")
    else:
        lines.append("[NO] Not fingerprinted")

    lines.append(f"\nCache Score: {analysis.cache_score}/100")

    if analysis.is_cacheable:
        lines.append("Cacheable: Yes")
        if analysis.max_age:
            lines.append(f"Max Age: {analysis.max_age}s ({format_duration(analysis.max_age)})")
        if analysis.is_fresh:
            lines.append(f"Fresh: Yes ({analysis.time_to_expire}s remaining)")
        else:
            lines.append("Fresh: No (expired)")
    else:
        lines.append("Cacheable: No")

    if analysis.cache_directives:
        lines.append(f"\nDirectives: {', '.join(analysis.cache_directives)}")

    if analysis.recommendations:
        lines.append("\nRecommendations:")
        for rec in analysis.recommendations:
            lines.append(f"  - {rec}")

    return "\n".join(lines)


def format_duration(seconds: int) -> str:
    """Format seconds into human-readable duration."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m"
    elif seconds < 86400:
        return f"{seconds // 3600}h"
    elif seconds < 2592000:
        return f"{seconds // 86400}d"
    else:
        return f"{seconds // 2592000}mo"
