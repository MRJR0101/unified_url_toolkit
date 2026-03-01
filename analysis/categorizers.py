"""
Domain and URL categorization utilities.

Consolidated from:
- URLToolkit/url_toolkit.py (domain_categorizer function)
- URL-Forensics/ (domain analysis)
"""

from typing import List, Dict, Set, Tuple
from collections import defaultdict, Counter
from urllib.parse import urlparse
import re

from ..core.patterns import DOMAIN_COMPREHENSIVE, IPV4_PATTERN
from ..config.settings import URL_SHORTENER_DOMAINS, SUSPICIOUS_TLDS


# =============================================================================
# CATEGORIZATION RESULTS
# =============================================================================

class CategorizationResult:
    """Results from domain/URL categorization."""

    def __init__(self):
        self.by_tld: Dict[str, List[str]] = defaultdict(list)
        self.by_subdomain_count: Dict[int, List[str]] = defaultdict(list)
        self.by_base_domain: Dict[str, List[str]] = defaultdict(list)
        self.unique_domains: Set[str] = set()
        self.with_ports: List[str] = []
        self.with_paths: List[str] = []
        self.with_query_params: List[str] = []
        self.url_shorteners: List[str] = []
        self.suspicious: List[Dict[str, str]] = []
        self.ip_addresses: List[str] = []

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'total_unique_domains': len(self.unique_domains),
            'by_tld': dict(self.by_tld),
            'by_subdomain_count': {k: len(v) for k, v in self.by_subdomain_count.items()},
            'by_base_domain': {k: len(v) for k, v in self.by_base_domain.items()},
            'with_ports': len(self.with_ports),
            'with_paths': len(self.with_paths),
            'with_query_params': len(self.with_query_params),
            'url_shorteners': len(self.url_shorteners),
            'suspicious': len(self.suspicious),
            'ip_addresses': len(self.ip_addresses),
        }


# =============================================================================
# CATEGORIZATION FUNCTIONS
# =============================================================================

def categorize_urls(urls: List[str]) -> CategorizationResult:
    """
    Categorize a list of URLs by various attributes.

    Args:
        urls: List of URLs to categorize

    Returns:
        CategorizationResult with categorized data

    Example:
        >>> urls = ["https://www.example.com/page", "http://test.org"]
        >>> result = categorize_urls(urls)
        >>> print(f"Found {len(result.unique_domains)} unique domains")
        >>> print(f"Top TLD: {result.by_tld.most_common(1)}")
    """
    result = CategorizationResult()

    for url in urls:
        # Ensure URL has scheme
        if not url.startswith(('http://', 'https://', 'ftp://')):
            url = 'https://' + url

        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path.split('/')[0]

            # Remove port if present
            domain_no_port = domain.split(':')[0]
            result.unique_domains.add(domain_no_port)

            # Check for IP address
            if re.match(IPV4_PATTERN, domain_no_port):
                result.ip_addresses.append(url)

            # TLD analysis
            parts = domain_no_port.split('.')
            if len(parts) >= 2:
                tld = parts[-1].lower()
                result.by_tld[tld].append(domain_no_port)

                # Base domain (last 2 parts)
                base_domain = '.'.join(parts[-2:]).lower()
                result.by_base_domain[base_domain].append(url)

                # Check for suspicious TLD
                if tld in SUSPICIOUS_TLDS:
                    result.suspicious.append({
                        'url': url,
                        'reason': f'Suspicious TLD: .{tld}'
                    })

            # Subdomain count (depth)
            subdomain_count = max(0, len(parts) - 2)
            result.by_subdomain_count[subdomain_count].append(domain_no_port)

            # Port detection
            if ':' in domain and not domain.startswith('['):  # Not IPv6
                result.with_ports.append(url)

            # Path detection
            if parsed.path and parsed.path != '/':
                result.with_paths.append(url)

            # Query parameters
            if parsed.query:
                result.with_query_params.append(url)

            # URL shorteners
            if domain_no_port in URL_SHORTENER_DOMAINS:
                result.url_shorteners.append(url)

            # Suspicious patterns
            if is_suspicious_domain(domain_no_port):
                reason = detect_suspicious_pattern(domain_no_port)
                result.suspicious.append({
                    'url': url,
                    'reason': reason
                })

        except Exception:
            # Skip malformed URLs
            continue

    return result


def categorize_domains(domains: List[str]) -> Dict[str, any]:
    """
    Categorize a list of domains.

    Args:
        domains: List of domains to categorize

    Returns:
        Dictionary with categorization results
    """
    result = {
        'total': len(domains),
        'unique': len(set(domains)),
        'by_tld': Counter(),
        'by_depth': Counter(),
        'suspicious': [],
        'ip_addresses': [],
    }

    for domain in domains:
        domain = domain.strip().lower()

        # IP address check
        if re.match(IPV4_PATTERN, domain):
            result['ip_addresses'].append(domain)
            continue

        # TLD
        parts = domain.split('.')
        if len(parts) >= 2:
            tld = parts[-1]
            result['by_tld'][tld] += 1

            # Depth (subdomain levels)
            depth = len(parts) - 2
            result['by_depth'][depth] += 1

            # Suspicious TLD
            if tld in SUSPICIOUS_TLDS:
                result['suspicious'].append({
                    'domain': domain,
                    'reason': f'Suspicious TLD: .{tld}'
                })

        # Suspicious patterns
        if is_suspicious_domain(domain):
            reason = detect_suspicious_pattern(domain)
            if reason:
                result['suspicious'].append({
                    'domain': domain,
                    'reason': reason
                })

    return result


def get_top_domains(urls: List[str], top_n: int = 20) -> List[Tuple[str, int]]:
    """
    Get the most common domains from a list of URLs.

    Args:
        urls: List of URLs
        top_n: Number of top domains to return

    Returns:
        List of (domain, count) tuples, sorted by count descending

    Example:
        >>> urls = ["http://example.com/a", "http://example.com/b", "http://test.org"]
        >>> top = get_top_domains(urls, top_n=5)
        >>> # [('example.com', 2), ('test.org', 1)]
    """
    domains = []

    for url in urls:
        if not url.startswith(('http://', 'https://', 'ftp://')):
            url = 'https://' + url

        try:
            parsed = urlparse(url)
            domain = parsed.netloc.split(':')[0].lower()
            if domain:
                domains.append(domain)
        except Exception:
            continue

    return Counter(domains).most_common(top_n)


def get_top_tlds(urls: List[str], top_n: int = 20) -> List[Tuple[str, int]]:
    """
    Get the most common TLDs from a list of URLs.

    Args:
        urls: List of URLs
        top_n: Number of top TLDs to return

    Returns:
        List of (tld, count) tuples
    """
    tlds = []

    for url in urls:
        if not url.startswith(('http://', 'https://', 'ftp://')):
            url = 'https://' + url

        try:
            parsed = urlparse(url)
            domain = parsed.netloc.split(':')[0]
            parts = domain.split('.')
            if len(parts) >= 2:
                tld = parts[-1].lower()
                tlds.append(tld)
        except Exception:
            continue

    return Counter(tlds).most_common(top_n)


# =============================================================================
# SUSPICIOUS PATTERN DETECTION
# =============================================================================

def is_suspicious_domain(domain: str) -> bool:
    """
    Check if a domain matches suspicious patterns.

    Args:
        domain: Domain to check

    Returns:
        True if domain appears suspicious
    """
    patterns = [
        r'-{3,}',  # Multiple consecutive dashes
        r'_{3,}',  # Multiple consecutive underscores
        r'\d{10,}',  # Very long number sequences
        r'^[0-9]+[a-z]+[0-9]+$',  # Numbers-letters-numbers pattern
    ]

    for pattern in patterns:
        if re.search(pattern, domain):
            return True

    # Check TLD
    parts = domain.split('.')
    if len(parts) >= 2:
        tld = parts[-1].lower()
        if tld in SUSPICIOUS_TLDS:
            return True

    return False


def detect_suspicious_pattern(domain: str) -> str:
    """
    Detect which suspicious pattern a domain matches.

    Args:
        domain: Domain to analyze

    Returns:
        Description of suspicious pattern, or empty string
    """
    if re.search(r'-{3,}', domain):
        return "Multiple consecutive dashes"

    if re.search(r'_{3,}', domain):
        return "Multiple consecutive underscores"

    if re.search(r'\d{10,}', domain):
        return "Very long number sequence"

    if re.search(r'^[0-9]+[a-z]+[0-9]+$', domain):
        return "Numbers-letters-numbers pattern"

    parts = domain.split('.')
    if len(parts) >= 2:
        tld = parts[-1].lower()
        if tld in SUSPICIOUS_TLDS:
            return f"Suspicious TLD: .{tld}"

    return ""


def group_by_base_domain(urls: List[str]) -> Dict[str, List[str]]:
    """
    Group URLs by their base domain (e.g., example.com).

    Args:
        urls: List of URLs

    Returns:
        Dictionary mapping base domains to lists of URLs

    Example:
        >>> urls = ["http://www.example.com/a", "http://api.example.com/b"]
        >>> groups = group_by_base_domain(urls)
        >>> # {'example.com': ['http://www.example.com/a', 'http://api.example.com/b']}
    """
    groups = defaultdict(list)

    for url in urls:
        if not url.startswith(('http://', 'https://', 'ftp://')):
            url = 'https://' + url

        try:
            parsed = urlparse(url)
            domain = parsed.netloc.split(':')[0]
            parts = domain.split('.')

            if len(parts) >= 2:
                base_domain = '.'.join(parts[-2:]).lower()
                groups[base_domain].append(url)
        except Exception:
            continue

    return dict(groups)
