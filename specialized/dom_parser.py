"""
DOM parsing and HTML extraction utilities.

Advanced HTML parsing for extracting specific elements, attributes, and text.
"""

from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from bs4 import BeautifulSoup, Tag, NavigableString
import re


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class DOMElement:
    """Represents a DOM element with its properties."""

    tag_name: str
    text: str = ""
    attributes: Dict[str, str] = field(default_factory=dict)
    classes: List[str] = field(default_factory=list)
    id: Optional[str] = None

    # Location
    parent_tag: Optional[str] = None
    depth: int = 0

    # Content
    inner_html: str = ""
    outer_html: str = ""


@dataclass
class LinkInfo:
    """Information about a link found in HTML."""

    url: str
    text: str = ""
    title: Optional[str] = None
    rel: Optional[str] = None
    target: Optional[str] = None

    # Context
    parent_tag: Optional[str] = None
    is_external: bool = False
    is_anchor: bool = False


@dataclass
class ImageInfo:
    """Information about an image found in HTML."""

    src: str
    alt: Optional[str] = None
    title: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None

    # Lazy loading
    loading: Optional[str] = None
    srcset: Optional[str] = None


# =============================================================================
# DOM PARSING
# =============================================================================

def parse_html(
    html: str,
    parser: str = 'html.parser',
) -> BeautifulSoup:
    """
    Parse HTML into BeautifulSoup object.

    Args:
        html: HTML content
        parser: Parser to use ('html.parser', 'lxml', 'html5lib')

    Returns:
        BeautifulSoup object
    """
    return BeautifulSoup(html, parser)


def find_elements(
    soup: BeautifulSoup,
    tag: str,
    class_: Optional[str] = None,
    id_: Optional[str] = None,
    attrs: Optional[Dict[str, str]] = None,
    text: Optional[str] = None,
) -> List[Tag]:
    """
    Find elements matching criteria.

    Args:
        soup: BeautifulSoup object
        tag: Tag name to search for
        class_: Class name to match
        id_: ID to match
        attrs: Additional attributes to match
        text: Text content to match

    Returns:
        List of matching Tag objects

    Example:
        >>> soup = parse_html(html)
        >>> links = find_elements(soup, 'a', class_='external')
        >>> for link in links:
        ...     print(link.get('href'))
    """
    kwargs = {}

    if class_:
        kwargs['class_'] = class_

    if id_:
        kwargs['id'] = id_

    if attrs:
        kwargs['attrs'] = attrs

    if text:
        kwargs['string'] = re.compile(text)

    return soup.find_all(tag, **kwargs)


def find_element(
    soup: BeautifulSoup,
    tag: str,
    **kwargs
) -> Optional[Tag]:
    """
    Find first element matching criteria.

    Args:
        soup: BeautifulSoup object
        tag: Tag name
        **kwargs: Additional search criteria

    Returns:
        First matching Tag or None
    """
    return soup.find(tag, **kwargs)


# =============================================================================
# ELEMENT EXTRACTION
# =============================================================================

def extract_dom_element(tag: Tag, depth: int = 0) -> DOMElement:
    """
    Extract DOM element information from a Tag.

    Args:
        tag: BeautifulSoup Tag object
        depth: Current depth in DOM tree

    Returns:
        DOMElement object
    """
    element = DOMElement(
        tag_name=tag.name,
        text=tag.get_text(strip=True),
        attributes=dict(tag.attrs),
        depth=depth,
    )

    # Extract classes
    if 'class' in tag.attrs:
        element.classes = tag.attrs['class']

    # Extract ID
    element.id = tag.get('id')

    # Parent
    if tag.parent and hasattr(tag.parent, 'name'):
        element.parent_tag = tag.parent.name

    # HTML content
    element.inner_html = ''.join(str(child) for child in tag.children)
    element.outer_html = str(tag)

    return element


# =============================================================================
# LINK EXTRACTION
# =============================================================================

def extract_links(
    soup: BeautifulSoup,
    base_url: Optional[str] = None,
) -> List[LinkInfo]:
    """
    Extract all links from HTML.

    Args:
        soup: BeautifulSoup object
        base_url: Base URL for resolving relative links

    Returns:
        List of LinkInfo objects

    Example:
        >>> soup = parse_html(html)
        >>> links = extract_links(soup, 'https://example.com')
        >>> for link in links:
        ...     print(f"{link.text}: {link.url}")
    """
    from urllib.parse import urljoin, urlparse

    links = []

    for a_tag in soup.find_all('a', href=True):
        url = a_tag['href']

        # Resolve relative URLs
        if base_url:
            url = urljoin(base_url, url)

        link = LinkInfo(
            url=url,
            text=a_tag.get_text(strip=True),
            title=a_tag.get('title'),
            rel=a_tag.get('rel'),
            target=a_tag.get('target'),
        )

        # Parent context
        if a_tag.parent:
            link.parent_tag = a_tag.parent.name

        # Check if external
        if base_url:
            base_domain = urlparse(base_url).netloc
            link_domain = urlparse(url).netloc
            link.is_external = (base_domain != link_domain)

        # Check if anchor link
        link.is_anchor = url.startswith('#')

        links.append(link)

    return links


def extract_links_by_selector(
    soup: BeautifulSoup,
    selector: str,
) -> List[str]:
    """
    Extract links matching a CSS selector.

    Args:
        soup: BeautifulSoup object
        selector: CSS selector

    Returns:
        List of URLs
    """
    links = []

    for element in soup.select(selector):
        href = element.get('href')
        if href:
            links.append(href)

    return links


# =============================================================================
# IMAGE EXTRACTION
# =============================================================================

def extract_images(soup: BeautifulSoup) -> List[ImageInfo]:
    """
    Extract all images from HTML.

    Args:
        soup: BeautifulSoup object

    Returns:
        List of ImageInfo objects

    Example:
        >>> soup = parse_html(html)
        >>> images = extract_images(soup)
        >>> for img in images:
        ...     print(f"{img.alt}: {img.src}")
    """
    images = []

    for img_tag in soup.find_all('img'):
        src = img_tag.get('src')

        if src:
            image = ImageInfo(
                src=src,
                alt=img_tag.get('alt'),
                title=img_tag.get('title'),
                width=img_tag.get('width'),
                height=img_tag.get('height'),
                loading=img_tag.get('loading'),
                srcset=img_tag.get('srcset'),
            )
            images.append(image)

    return images


# =============================================================================
# TEXT EXTRACTION
# =============================================================================

def extract_text(
    soup: BeautifulSoup,
    strip: bool = True,
    separator: str = '\n',
) -> str:
    """
    Extract all text from HTML.

    Args:
        soup: BeautifulSoup object
        strip: Whether to strip whitespace
        separator: Separator between text blocks

    Returns:
        Extracted text
    """
    return soup.get_text(strip=strip, separator=separator)


def extract_text_from_selector(
    soup: BeautifulSoup,
    selector: str,
) -> List[str]:
    """
    Extract text from elements matching selector.

    Args:
        soup: BeautifulSoup object
        selector: CSS selector

    Returns:
        List of text strings
    """
    texts = []

    for element in soup.select(selector):
        text = element.get_text(strip=True)
        if text:
            texts.append(text)

    return texts


# =============================================================================
# ATTRIBUTE EXTRACTION
# =============================================================================

def extract_attribute(
    soup: BeautifulSoup,
    tag: str,
    attribute: str,
) -> List[str]:
    """
    Extract specific attribute from all matching tags.

    Args:
        soup: BeautifulSoup object
        tag: Tag name to search
        attribute: Attribute name to extract

    Returns:
        List of attribute values

    Example:
        >>> # Extract all src attributes from img tags
        >>> srcs = extract_attribute(soup, 'img', 'src')
    """
    values = []

    for element in soup.find_all(tag):
        value = element.get(attribute)
        if value:
            values.append(value)

    return values


def extract_data_attributes(tag: Tag) -> Dict[str, str]:
    """
    Extract all data-* attributes from a tag.

    Args:
        tag: BeautifulSoup Tag object

    Returns:
        Dictionary of data attributes (without 'data-' prefix)

    Example:
        >>> data = extract_data_attributes(tag)
        >>> # {'id': '123', 'name': 'test'} from data-id and data-name
    """
    data_attrs = {}

    for attr, value in tag.attrs.items():
        if attr.startswith('data-'):
            key = attr[5:]  # Remove 'data-' prefix
            data_attrs[key] = value

    return data_attrs


# =============================================================================
# STRUCTURAL ANALYSIS
# =============================================================================

def count_elements_by_tag(soup: BeautifulSoup) -> Dict[str, int]:
    """
    Count elements by tag name.

    Args:
        soup: BeautifulSoup object

    Returns:
        Dictionary mapping tag names to counts
    """
    counts = {}

    for element in soup.find_all():
        tag_name = element.name
        counts[tag_name] = counts.get(tag_name, 0) + 1

    return counts


def get_max_depth(soup: BeautifulSoup) -> int:
    """
    Calculate maximum depth of DOM tree.

    Args:
        soup: BeautifulSoup object

    Returns:
        Maximum nesting depth
    """
    def calculate_depth(element, current_depth=0):
        max_child_depth = current_depth

        for child in element.children:
            if isinstance(child, Tag):
                child_depth = calculate_depth(child, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)

        return max_child_depth

    return calculate_depth(soup)


# =============================================================================
# FILTERING
# =============================================================================

def filter_elements(
    elements: List[Tag],
    predicate: Callable[[Tag], bool],
) -> List[Tag]:
    """
    Filter elements using a custom predicate function.

    Args:
        elements: List of Tag objects
        predicate: Function that returns True to keep element

    Returns:
        Filtered list of elements

    Example:
        >>> # Get only links with non-empty text
        >>> links = find_elements(soup, 'a')
        >>> non_empty = filter_elements(links, lambda a: a.get_text(strip=True))
    """
    return [el for el in elements if predicate(el)]


def find_elements_with_text(
    soup: BeautifulSoup,
    text_pattern: str,
    tag: Optional[str] = None,
) -> List[Tag]:
    """
    Find elements containing specific text.

    Args:
        soup: BeautifulSoup object
        text_pattern: Text or regex pattern to search for
        tag: Optional tag name to limit search

    Returns:
        List of matching elements
    """
    search_kwargs = {'string': re.compile(text_pattern)}

    if tag:
        return soup.find_all(tag, **search_kwargs)

    return soup.find_all(**search_kwargs)
