"""
URL and domain normalization utilities.

Consolidated from:
- CleanDomains/clean_domains.py
- CleanDomainsv2/clean_domains_v2.py
- UralCanonical
- cleanup_domains
"""

from typing import Optional
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from . import patterns

# =============================================================================
# DOMAIN NORMALIZATION
# =============================================================================


def normalize_domain(domain: str, strip_www: bool = False, strip_subdomain: bool = False) -> str:
    """
    Normalize a domain name to canonical form.

    Operations performed:
    - Lowercase
    - Strip trailing dots
    - Optionally remove www prefix
    - Optionally keep only base domain (strip all subdomains)

    Args:
        domain: Domain to normalize
        strip_www: Remove www. prefix
        strip_subdomain: Keep only base domain (e.g., sub.example.com -> example.com)

    Returns:
        Normalized domain

    Examples:
        >>> normalize_domain("WWW.Example.COM.")
        'www.example.com'
        >>> normalize_domain("WWW.Example.COM.", strip_www=True)
        'example.com'
        >>> normalize_domain("blog.api.example.com", strip_subdomain=True)
        'example.com'
    """
    # Basic normalization
    domain = domain.lower().strip().rstrip(".")

    # Remove www prefix if requested
    if strip_www and domain.startswith("www."):
        domain = domain[4:]

    # Keep only base domain if requested
    if strip_subdomain:
        parts = domain.split(".")
        if len(parts) >= 2:
            domain = ".".join(parts[-2:])

    return domain


def extract_domain_from_url(url: str, strip_www: bool = False, strip_subdomain: bool = False) -> Optional[str]:
    """
    Extract and normalize domain from a URL.

    Source: Consolidated from CleanDomains/clean_domains.py::extract_host()

    Args:
        url: URL or domain string
        strip_www: Remove www. prefix
        strip_subdomain: Keep only base domain

    Returns:
        Normalized domain or None if extraction fails

    Examples:
        >>> extract_domain_from_url("https://www.example.com/path")
        'www.example.com'
        >>> extract_domain_from_url("https://www.example.com/path", strip_www=True)
        'example.com'
        >>> extract_domain_from_url("www.example.com")
        'example.com'
    """
    text = url.strip()

    if not text or text.lower() == "www.":
        return None

    # Remove fragment
    if "#" in text:
        text = text.split("#", 1)[0].strip()
        if not text:
            return None

    # If it's a full URL with scheme, parse it
    if "://" in text:
        try:
            parsed = urlparse(text)
            hostname = parsed.hostname
            if hostname:
                text = hostname
        except Exception:
            pass

    # Extract domain using regex
    match = patterns.DOMAIN_BASIC.search(text)
    if not match:
        return None

    domain = match.group(1).lower().strip(".")

    # Validation checks
    if domain == "www" or "." not in domain:
        return None

    # Check TLD length
    tld = domain.rsplit(".", 1)[-1]
    if len(tld) < 2:
        return None

    # Apply normalization
    return normalize_domain(domain, strip_www=strip_www, strip_subdomain=strip_subdomain)


def clean_domain_list(
    domains: list[str],
    strip_www: bool = False,
    strip_subdomain: bool = False,
    remove_duplicates: bool = True,
    sort: bool = False,
) -> list[str]:
    """
    Clean and normalize a list of domains.

    Source: Consolidated from CleanDomains and CleanDomainsv2

    Args:
        domains: List of domains/URLs to clean
        strip_www: Remove www. prefix
        strip_subdomain: Keep only base domains
        remove_duplicates: Remove duplicate entries
        sort: Sort alphabetically

    Returns:
        List of cleaned domains

    Example:
        >>> domains = ["HTTPS://www.Example.COM", "www.example.com.", "test.org"]
        >>> clean_domain_list(domains, strip_www=True, remove_duplicates=True)
        ['example.com', 'test.org']
    """
    cleaned: list[str] = []
    seen: set[str] = set()

    for item in domains:
        domain = extract_domain_from_url(item, strip_www=strip_www, strip_subdomain=strip_subdomain)
        if not domain:
            continue

        if remove_duplicates:
            if domain not in seen:
                seen.add(domain)
                cleaned.append(domain)
        else:
            cleaned.append(domain)

    if sort:
        cleaned = sorted(cleaned)

    return cleaned


# =============================================================================
# URL NORMALIZATION
# =============================================================================


def normalize_url(
    url: str,
    default_scheme: str = "https",
    remove_fragment: bool = True,
    remove_query: bool = False,
    remove_trailing_slash: bool = False,
    sort_query_params: bool = False,
) -> str:
    """
    Normalize a URL to canonical form.

    Operations:
    - Add default scheme if missing
    - Lowercase scheme and domain
    - Optionally remove fragment (#section)
    - Optionally remove query string (?param=value)
    - Optionally remove trailing slash
    - Optionally sort query parameters

    Args:
        url: URL to normalize
        default_scheme: Scheme to add if missing
        remove_fragment: Remove fragment identifier
        remove_query: Remove query string
        remove_trailing_slash: Remove trailing slash from path
        sort_query_params: Sort query parameters alphabetically

    Returns:
        Normalized URL

    Examples:
        >>> normalize_url("Example.COM/path")
        'https://example.com/path'
        >>> normalize_url("https://example.com/path?b=2&a=1", sort_query_params=True)
        'https://example.com/path?a=1&b=2'
    """
    # Add scheme if missing
    if not patterns.has_scheme(url):
        url = f"{default_scheme}://{url}"

    # Parse URL
    parsed = urlparse(url)

    # Normalize components
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path
    params = parsed.params
    query = parsed.query
    fragment = parsed.fragment

    # Apply transformations
    if remove_fragment:
        fragment = ""

    if remove_query:
        query = ""
    elif sort_query_params and query:
        # Parse, sort, and rebuild query string
        query_dict = parse_qs(query, keep_blank_values=True)
        sorted_params = sorted(query_dict.items())
        query = urlencode(sorted_params, doseq=True)

    if remove_trailing_slash and path.endswith("/") and len(path) > 1:
        path = path.rstrip("/")

    # Rebuild URL
    normalized = urlunparse((scheme, netloc, path, params, query, fragment))

    return normalized


def clean_url_list(
    urls: list[str], normalize: bool = True, remove_duplicates: bool = True, sort: bool = False, **normalize_kwargs
) -> list[str]:
    """
    Clean and normalize a list of URLs.

    Args:
        urls: List of URLs to clean
        normalize: Apply URL normalization
        remove_duplicates: Remove duplicate URLs
        sort: Sort alphabetically
        **normalize_kwargs: Additional arguments for normalize_url()

    Returns:
        List of cleaned URLs
    """
    cleaned: list[str] = []
    seen: set[str] = set()

    for url in urls:
        url = url.strip()
        if not url:
            continue

        if normalize:
            try:
                url = normalize_url(url, **normalize_kwargs)
            except Exception:
                continue

        if remove_duplicates:
            if url not in seen:
                seen.add(url)
                cleaned.append(url)
        else:
            cleaned.append(url)

    if sort:
        cleaned = sorted(cleaned)

    return cleaned


# =============================================================================
# SPECIAL CLEANING OPERATIONS
# =============================================================================


def remove_url_parameters(url: str, params_to_remove: list[str] | None = None) -> str:
    """
    Remove specific query parameters from URL.

    Args:
        url: URL to clean
        params_to_remove: List of parameter names to remove (None = remove all)

    Returns:
        URL with specified parameters removed

    Example:
        >>> remove_url_parameters("https://example.com?utm_source=x&id=123", ["utm_source"])
        'https://example.com?id=123'
    """
    parsed = urlparse(url)

    if not parsed.query:
        return url

    if params_to_remove is None:
        # Remove all parameters
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, "", parsed.fragment))

    # Parse query string
    query_dict = parse_qs(parsed.query, keep_blank_values=True)

    # Remove specified parameters
    for param in params_to_remove:
        query_dict.pop(param, None)

    # Rebuild query string
    new_query = urlencode(query_dict, doseq=True)

    # Rebuild URL
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))


def remove_tracking_parameters(url: str) -> str:
    """
    Remove common tracking parameters from URL.

    Common tracking params: utm_*, fbclid, gclid, _ga, ref, source

    Args:
        url: URL to clean

    Returns:
        URL with tracking parameters removed
    """
    tracking_params = [
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_term",
        "utm_content",
        "fbclid",
        "gclid",
        "msclkid",
        "_ga",
        "_gid",
        "ref",
        "source",
        "campaign",
        "medium",
    ]

    return remove_url_parameters(url, tracking_params)
