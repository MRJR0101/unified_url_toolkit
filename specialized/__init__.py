"""
Specialized analysis modules for HTTP responses, content, and metadata.

Complete suite for analyzing what URLs return (not just their structure):
- HTTP response inspection (status, headers, timing)
- Security analysis (CORS, CSP, HSTS, robots.txt)
- Redirect chain mapping (301, 302, meta-refresh, JS)
- Content inspection (MIME types, compression, encoding)
- Metadata extraction (HTML, OpenGraph, Twitter Card)
- Cache behavior analysis (directives, fingerprinting, optimization)
- Link checking (validation, retries, batch processing)
- DOM parsing (element extraction, text, images)
"""

# HTTP Response Inspection
# Cache Analysis
from .cache_analyzer import (
    CacheAnalysis,
    analyze_cache,
    detect_fingerprint,
    format_cache_analysis,
    parse_cache_control,
    remove_fingerprint,
)

# Content Inspection
from .content_inspector import (
    ContentAnalysis,
    analyze_compression,
    analyze_content,
    format_bytes,
    get_mime_category,
    guess_extension,
    guess_mime_type,
    is_binary_mime,
    is_text_mime,
    parse_content_type,
    sniff_content_type,
)

# DOM Parsing
from .dom_parser import (
    DOMElement,
    ImageInfo,
    LinkInfo,
    count_elements_by_tag,
    extract_attribute,
    extract_dom_element,
    extract_images,
    extract_links,
    extract_text,
    find_element,
    find_elements,
    get_max_depth,
    parse_html,
)

# HTTP Response Analysis (complementary to low-level HTTP inspector)
from .http_analyzer import (
    HTTPResponse as HTTPAnalysisResponse,
    HeaderAnalysis,
    analyze_multiple_urls,
    categorize_headers,
    fetch_http_response,
    get_missing_security_headers,
)
from .http_inspector import (
    HTTPResponse,
    StatusCodeInfo,
    extract_header,
    get_cache_headers,
    get_cors_headers,
    get_request,
    get_security_headers,
    get_status_info,
    head_request,
    inspect_url,
    is_error,
    is_redirect,
    is_success,
)

# Link Checking
from .link_checker import (
    LinkCheckReport,
    LinkCheckResult,
    LinkStatus,
    check_link,
    check_link_with_fallback,
    check_multiple_links,
    format_link_check_report,
)

# Metadata Extraction
from .metadata_extractor import (
    PageMetadata,
    extract_canonical,
    extract_description,
    extract_favicon,
    extract_keywords,
    extract_metadata,
    extract_multiple_metadata,
    extract_opengraph,
    extract_title,
    extract_twitter_card,
    format_metadata,
)

# Redirect Mapping
from .redirect_mapper import (
    RedirectChain,
    RedirectHop,
    analyze_redirect_chains,
    check_js_redirect,
    check_meta_refresh_redirect,
    follow_redirect_chain,
    format_redirect_chain,
    get_redirect_summary,
)

# Security Analysis
from .security_analyzer import (
    CORSAnalysis,
    RobotsAnalysis,
    SecurityAnalysis,
    analyze_cors,
    analyze_security_headers,
    check_robots_allowed,
    fetch_robots_txt,
    is_followable,
    is_indexable,
    parse_robots_meta_tag,
)

__all__ = [
    # HTTP Inspection
    "HTTPResponse",
    "HTTPAnalysisResponse",
    "HeaderAnalysis",
    "fetch_http_response",
    "categorize_headers",
    "get_missing_security_headers",
    "analyze_multiple_urls",
    "StatusCodeInfo",
    "inspect_url",
    "head_request",
    "get_request",
    "extract_header",
    "get_security_headers",
    "get_cache_headers",
    "get_cors_headers",
    "get_status_info",
    "is_success",
    "is_redirect",
    "is_error",
    # Security Analysis
    "SecurityAnalysis",
    "CORSAnalysis",
    "RobotsAnalysis",
    "analyze_security_headers",
    "analyze_cors",
    "fetch_robots_txt",
    "check_robots_allowed",
    "parse_robots_meta_tag",
    "is_indexable",
    "is_followable",
    # Redirect Mapping
    "RedirectHop",
    "RedirectChain",
    "follow_redirect_chain",
    "check_meta_refresh_redirect",
    "check_js_redirect",
    "get_redirect_summary",
    "format_redirect_chain",
    "analyze_redirect_chains",
    # Content Inspection
    "ContentAnalysis",
    "parse_content_type",
    "get_mime_category",
    "is_binary_mime",
    "is_text_mime",
    "analyze_compression",
    "format_bytes",
    "analyze_content",
    "sniff_content_type",
    "guess_extension",
    "guess_mime_type",
    # Metadata Extraction
    "PageMetadata",
    "extract_metadata",
    "extract_title",
    "extract_description",
    "extract_keywords",
    "extract_opengraph",
    "extract_twitter_card",
    "extract_canonical",
    "extract_favicon",
    "extract_multiple_metadata",
    "format_metadata",
    # Cache Analysis
    "CacheAnalysis",
    "detect_fingerprint",
    "remove_fingerprint",
    "parse_cache_control",
    "analyze_cache",
    "format_cache_analysis",
    # Link Checking
    "LinkStatus",
    "LinkCheckResult",
    "LinkCheckReport",
    "check_link",
    "check_link_with_fallback",
    "check_multiple_links",
    "format_link_check_report",
    # DOM Parsing
    "DOMElement",
    "LinkInfo",
    "ImageInfo",
    "parse_html",
    "find_elements",
    "find_element",
    "extract_dom_element",
    "extract_links",
    "extract_images",
    "extract_text",
    "extract_attribute",
    "count_elements_by_tag",
    "get_max_depth",
]
