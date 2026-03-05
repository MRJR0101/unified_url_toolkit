"""
Metadata Extraction - HTML meta tags, OpenGraph, canonical URLs.

Extracts page metadata including:
- HTML title and description
- Meta tags (keywords, author, etc.)
- OpenGraph tags (og:title, og:image, etc.)
- Twitter Card tags
- Canonical URL
- Robots meta tags
- Sitemap directives
- Favicon
"""

from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Dict, List, Optional
from urllib.parse import urljoin

import requests  # type: ignore[import-untyped]
from bs4 import BeautifulSoup

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
class PageMetadata:
    """Complete page metadata."""

    # URL
    url: str
    canonical_url: Optional[str] = None

    # Basic HTML
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    author: Optional[str] = None

    # Meta tags
    meta_tags: Dict[str, str] = field(default_factory=dict)

    # OpenGraph
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    og_url: Optional[str] = None
    og_type: Optional[str] = None
    og_site_name: Optional[str] = None
    og_tags: Dict[str, str] = field(default_factory=dict)

    # Twitter Card
    twitter_card: Optional[str] = None
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    twitter_image: Optional[str] = None
    twitter_site: Optional[str] = None
    twitter_creator: Optional[str] = None
    twitter_tags: Dict[str, str] = field(default_factory=dict)

    # SEO
    robots: Optional[str] = None
    robots_directives: List[str] = field(default_factory=list)
    googlebot: Optional[str] = None

    # Links
    favicon: Optional[str] = None
    alternate_urls: List[Dict[str, str]] = field(default_factory=list)
    prev_url: Optional[str] = None
    next_url: Optional[str] = None

    # Language
    lang: Optional[str] = None
    hreflang: List[Dict[str, str]] = field(default_factory=list)

    # Misc
    viewport: Optional[str] = None
    charset: Optional[str] = None
    generator: Optional[str] = None

    # Analysis
    has_opengraph: bool = False
    has_twitter_card: bool = False
    is_indexable: bool = True

    def to_dict(self) -> dict:
        """Convert metadata model to dictionary."""
        return asdict(self)


def _attr_to_str(value: object) -> Optional[str]:
    """Normalize BeautifulSoup attribute values into plain strings."""
    if value is None:
        return None
    if isinstance(value, list):
        parts = [str(v).strip() for v in value if str(v).strip()]
        return " ".join(parts) if parts else None
    text = str(value).strip()
    return text or None


# =============================================================================
# METADATA EXTRACTION
# =============================================================================


def extract_metadata(
    url: str,
    html_content: Optional[str] = None,
    timeout: int = DEFAULT_HTTP_TIMEOUT,
    verify_ssl: bool = VERIFY_SSL,
    user_agent: str = DEFAULT_USER_AGENT,
) -> PageMetadata:
    """
    Extract all metadata from a URL or HTML content.

    Args:
        url: URL to extract from
        html_content: Optional HTML content (if None, fetches from URL)
        timeout: Request timeout if fetching

    Returns:
        PageMetadata object with all extracted data

    Example:
        >>> metadata = extract_metadata("https://example.com")
        >>> print(f"Title: {metadata.title}")
        >>> print(f"Description: {metadata.description}")
        >>> print(f"OG Image: {metadata.og_image}")
    """
    # Fetch HTML if not provided
    if html_content is None:
        try:
            response = requests.get(
                url,
                timeout=timeout,
                verify=verify_ssl,
                headers={"User-Agent": user_agent},
            )
            response.raise_for_status()
            html_content = response.text
        except Exception:
            return PageMetadata(url=url)

    # Parse HTML
    soup = BeautifulSoup(html_content, "html.parser")

    metadata = PageMetadata(url=url)

    # Extract basic HTML
    metadata.title = extract_title(soup)
    metadata.description = extract_description(soup)
    metadata.keywords = extract_keywords(soup)
    metadata.author = extract_author(soup)
    metadata.lang = extract_language(soup)

    # Extract meta tags
    metadata.meta_tags = extract_meta_tags(soup)

    # Extract OpenGraph
    og_tags = extract_opengraph(soup)
    metadata.og_tags = og_tags
    metadata.og_title = og_tags.get("og:title")
    metadata.og_description = og_tags.get("og:description")
    metadata.og_image = og_tags.get("og:image")
    metadata.og_url = og_tags.get("og:url")
    metadata.og_type = og_tags.get("og:type")
    metadata.og_site_name = og_tags.get("og:site_name")
    metadata.has_opengraph = bool(og_tags)

    # Extract Twitter Card
    twitter_tags = extract_twitter_card(soup)
    metadata.twitter_tags = twitter_tags
    metadata.twitter_card = twitter_tags.get("twitter:card")
    metadata.twitter_title = twitter_tags.get("twitter:title")
    metadata.twitter_description = twitter_tags.get("twitter:description")
    metadata.twitter_image = twitter_tags.get("twitter:image")
    metadata.twitter_site = twitter_tags.get("twitter:site")
    metadata.twitter_creator = twitter_tags.get("twitter:creator")
    metadata.has_twitter_card = bool(twitter_tags)

    # Extract canonical URL
    metadata.canonical_url = extract_canonical(soup, url)

    # Extract robots directives
    metadata.robots = metadata.meta_tags.get("robots")
    metadata.googlebot = metadata.meta_tags.get("googlebot")
    if metadata.robots:
        metadata.robots_directives = [d.strip() for d in metadata.robots.lower().split(",")]
        metadata.is_indexable = "noindex" not in metadata.robots_directives

    # Extract links
    metadata.favicon = extract_favicon(soup, url)
    metadata.alternate_urls = extract_alternate_urls(soup, url)
    metadata.prev_url = extract_link_rel(soup, "prev", url)
    metadata.next_url = extract_link_rel(soup, "next", url)
    metadata.hreflang = extract_hreflang(soup, url)

    # Extract misc
    metadata.viewport = metadata.meta_tags.get("viewport")
    metadata.charset = extract_charset(soup)
    metadata.generator = metadata.meta_tags.get("generator")

    return metadata


# =============================================================================
# BASIC HTML EXTRACTION
# =============================================================================


def extract_title(soup: BeautifulSoup) -> Optional[str]:
    """Extract page title."""
    title_tag = soup.find("title")
    return title_tag.get_text().strip() if title_tag else None


def extract_description(soup: BeautifulSoup) -> Optional[str]:
    """Extract meta description."""
    desc_tag = soup.find("meta", attrs={"name": "description"})
    return _attr_to_str(desc_tag.get("content")) if desc_tag else None


def extract_keywords(soup: BeautifulSoup) -> List[str]:
    """Extract meta keywords."""
    keywords_tag = soup.find("meta", attrs={"name": "keywords"})
    keywords = _attr_to_str(keywords_tag.get("content")) if keywords_tag else None
    if keywords:
        return [k.strip() for k in keywords.split(",") if k.strip()]
    return []


def extract_author(soup: BeautifulSoup) -> Optional[str]:
    """Extract author meta tag."""
    author_tag = soup.find("meta", attrs={"name": "author"})
    return _attr_to_str(author_tag.get("content")) if author_tag else None


def extract_language(soup: BeautifulSoup) -> Optional[str]:
    """Extract page language."""
    html_tag = soup.find("html")
    if html_tag and html_tag.get("lang"):
        return _attr_to_str(html_tag.get("lang"))
    return None


# =============================================================================
# META TAGS EXTRACTION
# =============================================================================


def extract_meta_tags(soup: BeautifulSoup) -> Dict[str, str]:
    """Extract all meta tags with name attribute."""
    meta_tags: Dict[str, str] = {}

    for meta in soup.find_all("meta"):
        name = _attr_to_str(meta.get("name")) or _attr_to_str(meta.get("property"))
        content = _attr_to_str(meta.get("content"))

        if name and content:
            meta_tags[name] = content

    return meta_tags


# =============================================================================
# OPENGRAPH EXTRACTION
# =============================================================================


def extract_opengraph(soup: BeautifulSoup) -> Dict[str, str]:
    """Extract OpenGraph meta tags."""
    og_tags: Dict[str, str] = {}

    for meta in soup.find_all("meta", property=True):
        property_name = _attr_to_str(meta.get("property")) or ""
        if property_name.startswith("og:"):
            content = _attr_to_str(meta.get("content")) or ""
            if content:
                og_tags[property_name] = content

    return og_tags


# =============================================================================
# TWITTER CARD EXTRACTION
# =============================================================================


def extract_twitter_card(soup: BeautifulSoup) -> Dict[str, str]:
    """Extract Twitter Card meta tags."""
    twitter_tags: Dict[str, str] = {}

    for meta in soup.find_all("meta", attrs={"name": True}):
        name = _attr_to_str(meta.get("name")) or ""
        if name.startswith("twitter:"):
            content = _attr_to_str(meta.get("content")) or ""
            if content:
                twitter_tags[name] = content

    return twitter_tags


# =============================================================================
# CANONICAL URL EXTRACTION
# =============================================================================


def extract_canonical(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """Extract canonical URL."""
    canonical = soup.find("link", rel="canonical")
    canonical_url = _attr_to_str(canonical.get("href")) if canonical else None
    if canonical_url:
        # Resolve relative URLs
        return urljoin(base_url, canonical_url)
    return None


# =============================================================================
# LINK EXTRACTION
# =============================================================================


def extract_favicon(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """Extract favicon URL."""
    # Try various favicon link rels
    favicon_rels = ["icon", "shortcut icon", "apple-touch-icon"]

    for rel in favicon_rels:
        favicon = soup.find("link", rel=rel)
        favicon_href = _attr_to_str(favicon.get("href")) if favicon else None
        if favicon_href:
            return urljoin(base_url, favicon_href)

    # Default favicon location
    from urllib.parse import urlparse

    parsed = urlparse(base_url)
    default_favicon = f"{parsed.scheme}://{parsed.netloc}/favicon.ico"
    return default_favicon


def extract_link_rel(soup: BeautifulSoup, rel: str, base_url: str) -> Optional[str]:
    """Extract link with specific rel attribute."""
    link = soup.find("link", rel=rel)
    href = _attr_to_str(link.get("href")) if link else None
    if href:
        return urljoin(base_url, href)
    return None


def extract_alternate_urls(soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
    """Extract alternate URLs (RSS, Atom, etc.)."""
    alternates: List[Dict[str, str]] = []

    for link in soup.find_all("link", rel="alternate"):
        href = _attr_to_str(link.get("href"))
        if href:
            alternates.append(
                {
                    "url": urljoin(base_url, href),
                    "type": _attr_to_str(link.get("type")) or "",
                    "title": _attr_to_str(link.get("title")) or "",
                }
            )

    return alternates


def extract_hreflang(soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
    """Extract hreflang alternate language versions."""
    hreflang_links: List[Dict[str, str]] = []

    for link in soup.find_all("link", rel="alternate", hreflang=True):
        href = _attr_to_str(link.get("href"))
        if href:
            hreflang_links.append(
                {
                    "url": urljoin(base_url, href),
                    "hreflang": _attr_to_str(link.get("hreflang")) or "",
                }
            )

    return hreflang_links


# =============================================================================
# CHARSET EXTRACTION
# =============================================================================


def extract_charset(soup: BeautifulSoup) -> Optional[str]:
    """Extract character encoding."""
    # Try meta charset
    charset_tag = soup.find("meta", charset=True)
    if charset_tag:
        return _attr_to_str(charset_tag.get("charset"))

    # Try http-equiv
    http_equiv = soup.find("meta", attrs={"http-equiv": "Content-Type"})
    if http_equiv:
        content = _attr_to_str(http_equiv.get("content")) or ""
        import re

        match = re.search(r"charset=([^;\s]+)", content)
        if match:
            return match.group(1)

    return None


# =============================================================================
# BATCH EXTRACTION
# =============================================================================


def extract_multiple_metadata(
    urls: List[str],
    timeout: int = DEFAULT_HTTP_TIMEOUT,
    max_workers: int = 10,
    verify_ssl: bool = VERIFY_SSL,
    user_agent: str = DEFAULT_USER_AGENT,
) -> List[PageMetadata]:
    """
    Extract metadata from multiple URLs in parallel.

    Args:
        urls: List of URLs
        timeout: Request timeout per URL
        max_workers: Number of parallel workers

    Returns:
        List of PageMetadata objects
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    metadata_by_index: dict[int, PageMetadata] = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(
                extract_metadata,
                url,
                None,
                timeout,
                verify_ssl,
                user_agent,
            ): idx
            for idx, url in enumerate(urls)
        }

        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                metadata_by_index[idx] = future.result()
            except Exception:
                metadata_by_index[idx] = PageMetadata(url=urls[idx])

    return [metadata_by_index.get(idx, PageMetadata(url=url)) for idx, url in enumerate(urls)]


# =============================================================================
# METADATA FORMATTING
# =============================================================================


def format_metadata(metadata: PageMetadata) -> str:
    """Format metadata as human-readable string."""
    lines = []
    lines.append(f"Metadata for: {metadata.url}")
    lines.append("=" * 60)

    if metadata.title:
        lines.append(f"Title: {metadata.title}")

    if metadata.description:
        lines.append(f"Description: {metadata.description[:100]}...")

    if metadata.canonical_url:
        lines.append(f"Canonical: {metadata.canonical_url}")

    if metadata.has_opengraph:
        lines.append("\nOpenGraph:")
        if metadata.og_title:
            lines.append(f"  Title: {metadata.og_title}")
        if metadata.og_image:
            lines.append(f"  Image: {metadata.og_image}")

    if metadata.has_twitter_card:
        lines.append("\nTwitter Card:")
        if metadata.twitter_card:
            lines.append(f"  Type: {metadata.twitter_card}")
        if metadata.twitter_image:
            lines.append(f"  Image: {metadata.twitter_image}")

    if metadata.robots_directives:
        lines.append(f"\nRobots: {', '.join(metadata.robots_directives)}")
        lines.append(f"Indexable: {metadata.is_indexable}")

    return "\n".join(lines)
