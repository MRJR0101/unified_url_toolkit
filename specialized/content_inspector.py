"""
Content Inspection - MIME types, compression, and content analysis.

Analyzes response content including:
- Content-Type / MIME type detection
- Content-Length and size analysis
- Compression type (gzip, brotli, deflate)
- Character encoding
- Binary vs text detection
- File type fingerprinting
"""

from typing import Optional, Dict, Tuple, List
from dataclasses import dataclass, field
import mimetypes
import re


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ContentAnalysis:
    """Complete content analysis result."""

    # MIME type
    content_type: Optional[str] = None
    mime_type: Optional[str] = None  # Main type (e.g., "text/html")
    mime_category: Optional[str] = None  # "text", "image", "video", etc.
    mime_subtype: Optional[str] = None  # "html", "png", "mp4", etc.
    charset: Optional[str] = None

    # Size
    content_length: Optional[int] = None
    content_length_human: Optional[str] = None  # "1.5 MB"

    # Compression
    content_encoding: Optional[str] = None
    is_compressed: bool = False
    compression_type: Optional[str] = None  # "gzip", "brotli", "deflate"

    # Content classification
    is_binary: bool = False
    is_text: bool = False
    is_html: bool = False
    is_json: bool = False
    is_xml: bool = False
    is_image: bool = False
    is_video: bool = False
    is_audio: bool = False
    is_pdf: bool = False
    is_archive: bool = False

    # Transfer
    transfer_encoding: Optional[str] = None
    is_chunked: bool = False


# =============================================================================
# MIME TYPE ANALYSIS
# =============================================================================

MIME_CATEGORIES = {
    'text': ['text/'],
    'image': ['image/'],
    'video': ['video/'],
    'audio': ['audio/'],
    'application': ['application/'],
    'multipart': ['multipart/'],
    'message': ['message/'],
}

BINARY_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp',
    'video/mp4', 'video/mpeg', 'video/webm', 'video/quicktime',
    'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/webm',
    'application/pdf', 'application/zip', 'application/x-rar',
    'application/octet-stream', 'application/x-msdownload',
}

TEXT_MIME_TYPES = {
    'text/html', 'text/plain', 'text/css', 'text/javascript',
    'text/xml', 'text/csv', 'text/markdown',
    'application/json', 'application/xml', 'application/javascript',
    'application/xhtml+xml', 'application/rss+xml',
}


def parse_content_type(content_type: str) -> Tuple[str, Optional[str]]:
    """
    Parse Content-Type header into MIME type and charset.

    Args:
        content_type: Content-Type header value

    Returns:
        (mime_type, charset) tuple

    Example:
        >>> parse_content_type("text/html; charset=utf-8")
        ('text/html', 'utf-8')
    """
    if not content_type:
        return None, None

    parts = content_type.split(';')
    mime_type = parts[0].strip().lower()

    charset = None
    for part in parts[1:]:
        part = part.strip()
        if part.startswith('charset='):
            charset = part.split('=', 1)[1].strip().strip('"\'')

    return mime_type, charset


def get_mime_category(mime_type: str) -> Optional[str]:
    """
    Get general category for MIME type.

    Args:
        mime_type: MIME type (e.g., "text/html")

    Returns:
        Category name (e.g., "text", "image")
    """
    if not mime_type:
        return None

    mime_type = mime_type.lower()

    for category, prefixes in MIME_CATEGORIES.items():
        for prefix in prefixes:
            if mime_type.startswith(prefix):
                return category

    return "unknown"


def is_binary_mime(mime_type: str) -> bool:
    """Check if MIME type represents binary content."""
    if not mime_type:
        return False

    mime_type = mime_type.lower()

    # Check known binary types
    if mime_type in BINARY_MIME_TYPES:
        return True

    # Check by category
    category = get_mime_category(mime_type)
    if category in ('image', 'video', 'audio'):
        return True

    # Check for "octet-stream"
    if 'octet-stream' in mime_type:
        return True

    return False


def is_text_mime(mime_type: str) -> bool:
    """Check if MIME type represents text content."""
    if not mime_type:
        return False

    mime_type = mime_type.lower()

    # Check known text types
    if mime_type in TEXT_MIME_TYPES:
        return True

    # Check if starts with "text/"
    if mime_type.startswith('text/'):
        return True

    # Check for JSON/XML variants
    if 'json' in mime_type or 'xml' in mime_type:
        return True

    return False


# =============================================================================
# COMPRESSION DETECTION
# =============================================================================

COMPRESSION_TYPES = {
    'gzip': 'gzip',
    'br': 'brotli',
    'deflate': 'deflate',
    'compress': 'compress',
    'identity': 'identity',
}


def analyze_compression(content_encoding: str) -> Tuple[bool, Optional[str]]:
    """
    Analyze content encoding for compression.

    Args:
        content_encoding: Content-Encoding header value

    Returns:
        (is_compressed, compression_type) tuple
    """
    if not content_encoding:
        return False, None

    encoding = content_encoding.lower().strip()

    # Check for known compression types
    for key, compression_type in COMPRESSION_TYPES.items():
        if key in encoding:
            is_compressed = compression_type != 'identity'
            return is_compressed, compression_type if is_compressed else None

    return False, None


# =============================================================================
# SIZE FORMATTING
# =============================================================================

def format_bytes(size_bytes: int) -> str:
    """
    Format bytes into human-readable size.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.1f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"


# =============================================================================
# CONTENT ANALYSIS FUNCTION
# =============================================================================

def analyze_content(
    content_type: Optional[str] = None,
    content_length: Optional[str] = None,
    content_encoding: Optional[str] = None,
    transfer_encoding: Optional[str] = None,
) -> ContentAnalysis:
    """
    Analyze content based on response headers.

    Args:
        content_type: Content-Type header value
        content_length: Content-Length header value
        content_encoding: Content-Encoding header value
        transfer_encoding: Transfer-Encoding header value

    Returns:
        ContentAnalysis object with complete analysis

    Example:
        >>> analysis = analyze_content(
        ...     content_type="text/html; charset=utf-8",
        ...     content_length="15234",
        ...     content_encoding="gzip"
        ... )
        >>> print(f"Type: {analysis.mime_type}")
        >>> print(f"Size: {analysis.content_length_human}")
        >>> print(f"Compressed: {analysis.is_compressed}")
    """
    analysis = ContentAnalysis()

    # Parse Content-Type
    if content_type:
        analysis.content_type = content_type
        mime_type, charset = parse_content_type(content_type)

        analysis.mime_type = mime_type
        analysis.charset = charset

        if mime_type:
            # Get category and subtype
            parts = mime_type.split('/')
            if len(parts) == 2:
                analysis.mime_category = parts[0]
                analysis.mime_subtype = parts[1]
            else:
                analysis.mime_category = get_mime_category(mime_type)

            # Classify content
            analysis.is_binary = is_binary_mime(mime_type)
            analysis.is_text = is_text_mime(mime_type)
            analysis.is_html = mime_type in ('text/html', 'application/xhtml+xml')
            analysis.is_json = 'json' in mime_type
            analysis.is_xml = 'xml' in mime_type
            analysis.is_image = mime_type.startswith('image/')
            analysis.is_video = mime_type.startswith('video/')
            analysis.is_audio = mime_type.startswith('audio/')
            analysis.is_pdf = mime_type == 'application/pdf'
            analysis.is_archive = mime_type in (
                'application/zip', 'application/x-rar',
                'application/x-tar', 'application/gzip',
            )

    # Parse Content-Length
    if content_length:
        try:
            size = int(content_length)
            analysis.content_length = size
            analysis.content_length_human = format_bytes(size)
        except ValueError:
            pass

    # Parse Content-Encoding
    if content_encoding:
        analysis.content_encoding = content_encoding
        is_compressed, compression_type = analyze_compression(content_encoding)
        analysis.is_compressed = is_compressed
        analysis.compression_type = compression_type

    # Parse Transfer-Encoding
    if transfer_encoding:
        analysis.transfer_encoding = transfer_encoding
        analysis.is_chunked = 'chunked' in transfer_encoding.lower()

    return analysis


# =============================================================================
# CONTENT SNIFFING
# =============================================================================

def sniff_content_type(content: bytes, declared_type: Optional[str] = None) -> str:
    """
    Sniff actual content type from content bytes.

    Uses magic bytes and content patterns to detect actual type,
    which may differ from declared Content-Type header.

    Args:
        content: Content bytes to analyze
        declared_type: Declared Content-Type (for comparison)

    Returns:
        Detected MIME type
    """
    if not content:
        return "application/octet-stream"

    # Check magic bytes
    if content.startswith(b'\xFF\xD8\xFF'):
        return "image/jpeg"
    elif content.startswith(b'\x89PNG\r\n\x1a\n'):
        return "image/png"
    elif content.startswith(b'GIF87a') or content.startswith(b'GIF89a'):
        return "image/gif"
    elif content.startswith(b'RIFF') and b'WEBP' in content[:12]:
        return "image/webp"
    elif content.startswith(b'%PDF-'):
        return "application/pdf"
    elif content.startswith(b'PK\x03\x04'):
        return "application/zip"
    elif content.startswith(b'\x1f\x8b'):
        return "application/gzip"
    elif content.startswith(b'BZh'):
        return "application/x-bzip2"

    # Try to decode as text
    try:
        text = content[:1024].decode('utf-8', errors='strict')

        # Check for HTML
        if re.search(r'<html|<!DOCTYPE html', text, re.IGNORECASE):
            return "text/html"

        # Check for XML
        if text.strip().startswith('<?xml'):
            return "application/xml"

        # Check for JSON
        if text.strip().startswith(('{', '[')):
            try:
                import json
                json.loads(text)
                return "application/json"
            except:
                pass

        # Generic text
        return "text/plain"

    except UnicodeDecodeError:
        # Binary content
        return "application/octet-stream"


# =============================================================================
# BATCH ANALYSIS
# =============================================================================

def analyze_multiple_contents(
    responses: List[Dict[str, str]]
) -> List[ContentAnalysis]:
    """
    Analyze content for multiple responses.

    Args:
        responses: List of response header dictionaries

    Returns:
        List of ContentAnalysis objects
    """
    analyses = []

    for response in responses:
        analysis = analyze_content(
            content_type=response.get('Content-Type'),
            content_length=response.get('Content-Length'),
            content_encoding=response.get('Content-Encoding'),
            transfer_encoding=response.get('Transfer-Encoding'),
        )
        analyses.append(analysis)

    return analyses


# =============================================================================
# CONTENT TYPE UTILITIES
# =============================================================================

def guess_extension(mime_type: str) -> Optional[str]:
    """
    Guess file extension from MIME type.

    Args:
        mime_type: MIME type

    Returns:
        File extension (e.g., ".html") or None
    """
    ext = mimetypes.guess_extension(mime_type)
    return ext


def guess_mime_type(filename: str) -> Optional[str]:
    """
    Guess MIME type from filename.

    Args:
        filename: Filename or path

    Returns:
        MIME type or None
    """
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type
