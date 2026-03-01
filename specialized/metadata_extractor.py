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

from typing import Optional, Dict, List
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin


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


# =============================================================================
# METADATA EXTRACTION
# =============================================================================

def extract_metadata(
    url: str,
    html_content: Optional[str] = None,
    timeout: int = 10,
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
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            html_content = response.text
        except Exception as e:
            return PageMetadata(url=url)

    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')

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
    metadata.og_title = og_tags.get('og:title')
    metadata.og_description = og_tags.get('og:description')
    metadata.og_image = og_tags.get('og:image')
    metadata.og_url = og_tags.get('og:url')
    metadata.og_type = og_tags.get('og:type')
    metadata.og_site_name = og_tags.get('og:site_name')
    metadata.has_opengraph = bool(og_tags)

    # Extract Twitter Card
    twitter_tags = extract_twitter_card(soup)
    metadata.twitter_tags = twitter_tags
    metadata.twitter_card = twitter_tags.get('twitter:card')
    metadata.twitter_title = twitter_tags.get('twitter:title')
    metadata.twitter_description = twitter_tags.get('twitter:description')
    metadata.twitter_image = twitter_tags.get('twitter:image')
    metadata.twitter_site = twitter_tags.get('twitter:site')
    metadata.twitter_creator = twitter_tags.get('twitter:creator')
    metadata.has_twitter_card = bool(twitter_tags)

    # Extract canonical URL
    metadata.canonical_url = extract_canonical(soup, url)

    # Extract robots directives
    metadata.robots = metadata.meta_tags.get('robots')
    metadata.googlebot = metadata.meta_tags.get('googlebot')
    if metadata.robots:
        metadata.robots_directives = [
            d.strip() for d in metadata.robots.lower().split(',')
        ]
        metadata.is_indexable = 'noindex' not in metadata.robots_directives

    # Extract links
    metadata.favicon = extract_favicon(soup, url)
    metadata.alternate_urls = extract_alternate_urls(soup, url)
    metadata.prev_url = extract_link_rel(soup, 'prev', url)
    metadata.next_url = extract_link_rel(soup, 'next', url)
    metadata.hreflang = extract_hreflang(soup, url)

    # Extract misc
    metadata.viewport = metadata.meta_tags.get('viewport')
    metadata.charset = extract_charset(soup)
    metadata.generator = metadata.meta_tags.get('generator')

    return metadata


# =============================================================================
# BASIC HTML EXTRACTION
# =============================================================================

def extract_title(soup: BeautifulSoup) -> Optional[str]:
    """Extract page title."""
    title_tag = soup.find('title')
    return title_tag.get_text().strip() if title_tag else None


def extract_description(soup: BeautifulSoup) -> Optional[str]:
    """Extract meta description."""
    desc_tag = soup.find('meta', attrs={'name': 'description'})
    if desc_tag and desc_tag.get('content'):
        return desc_tag['content'].strip()
    return None


def extract_keywords(soup: BeautifulSoup) -> List[str]:
    """Extract meta keywords."""
    keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
    if keywords_tag and keywords_tag.get('content'):
        keywords = keywords_tag['content']
        return [k.strip() for k in keywords.split(',') if k.strip()]
    return []


def extract_author(soup: BeautifulSoup) -> Optional[str]:
    """Extract author meta tag."""
    author_tag = soup.find('meta', attrs={'name': 'author'})
    return author_tag.get('content', '').strip() if author_tag else None


def extract_language(soup: BeautifulSoup) -> Optional[str]:
    """Extract page language."""
    html_tag = soup.find('html')
    if html_tag and html_tag.get('lang'):
        return html_tag['lang']
    return None


# =============================================================================
# META TAGS EXTRACTION
# =============================================================================

def extract_meta_tags(soup: BeautifulSoup) -> Dict[str, str]:
    """Extract all meta tags with name attribute."""
    meta_tags = {}

    for meta in soup.find_all('meta'):
        name = meta.get('name') or meta.get('property')
        content = meta.get('content')

        if name and content:
            meta_tags[name] = content

    return meta_tags


# =============================================================================
# OPENGRAPH EXTRACTION
# =============================================================================

def extract_opengraph(soup: BeautifulSoup) -> Dict[str, str]:
    """Extract OpenGraph meta tags."""
    og_tags = {}

    for meta in soup.find_all('meta', property=True):
        property_name = meta.get('property', '')
        if property_name.startswith('og:'):
            content = meta.get('content', '')
            if content:
                og_tags[property_name] = content

    return og_tags


# =============================================================================
# TWITTER CARD EXTRACTION
# =============================================================================

def extract_twitter_card(soup: BeautifulSoup) -> Dict[str, str]:
    """Extract Twitter Card meta tags."""
    twitter_tags = {}

    for meta in soup.find_all('meta', attrs={'name': True}):
        name = meta.get('name', '')
        if name.startswith('twitter:'):
            content = meta.get('content', '')
            if content:
                twitter_tags[name] = content

    return twitter_tags


# =============================================================================
# CANONICAL URL EXTRACTION
# =============================================================================

def extract_canonical(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """Extract canonical URL."""
    canonical = soup.find('link', rel='canonical')
    if canonical and canonical.get('href'):
        canonical_url = canonical['href']
        # Resolve relative URLs
        return urljoin(base_url, canonical_url)
    return None


# =============================================================================
# LINK EXTRACTION
# =============================================================================

def extract_favicon(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """Extract favicon URL."""
    # Try various favicon link rels
    favicon_rels = ['icon', 'shortcut icon', 'apple-touch-icon']

    for rel in favicon_rels:
        favicon = soup.find('link', rel=rel)
        if favicon and favicon.get('href'):
            return urljoin(base_url, favicon['href'])

    # Default favicon location
    from urllib.parse import urlparse
    parsed = urlparse(base_url)
    default_favicon = f"{parsed.scheme}://{parsed.netloc}/favicon.ico"
    return default_favicon


def extract_link_rel(soup: BeautifulSoup, rel: str, base_url: str) -> Optional[str]:
    """Extract link with specific rel attribute."""
    link = soup.find('link', rel=rel)
    if link and link.get('href'):
        return urljoin(base_url, link['href'])
    return None


def extract_alternate_urls(soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
    """Extract alternate URLs (RSS, Atom, etc.)."""
    alternates = []

    for link in soup.find_all('link', rel='alternate'):
        href = link.get('href')
        if href:
            alternates.append({
                'url': urljoin(base_url, href),
                'type': link.get('type', ''),
                'title': link.get('title', ''),
            })

    return alternates


def extract_hreflang(soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
    """Extract hreflang alternate language versions."""
    hreflang_links = []

    for link in soup.find_all('link', rel='alternate', hreflang=True):
        href = link.get('href')
        if href:
            hreflang_links.append({
                'url': urljoin(base_url, href),
                'hreflang': link.get('hreflang', ''),
            })

    return hreflang_links


# =============================================================================
# CHARSET EXTRACTION
# =============================================================================

def extract_charset(soup: BeautifulSoup) -> Optional[str]:
    """Extract character encoding."""
    # Try meta charset
    charset_tag = soup.find('meta', charset=True)
    if charset_tag:
        return charset_tag.get('charset')

    # Try http-equiv
    http_equiv = soup.find('meta', attrs={'http-equiv': 'Content-Type'})
    if http_equiv:
        content = http_equiv.get('content', '')
        import re
        match = re.search(r'charset=([^;\s]+)', content)
        if match:
            return match.group(1)

    return None


# =============================================================================
# BATCH EXTRACTION
# =============================================================================

def extract_multiple_metadata(
    urls: List[str],
    timeout: int = 5,
    max_workers: int = 10,
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

    metadata_list = [None] * len(urls)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(extract_metadata, url, None, timeout): idx
            for idx, url in enumerate(urls)
        }

        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                metadata_list[idx] = future.result()
            except Exception:
                metadata_list[idx] = PageMetadata(url=urls[idx])

    return metadata_list


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

    return '\n'.join(lines)
