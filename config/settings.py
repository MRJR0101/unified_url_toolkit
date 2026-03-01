"""
Configuration settings and constants for URL toolkit.

Centralized configuration to avoid magic numbers and scattered settings.
"""

from pathlib import Path
from typing import Set

# =============================================================================
# GENERAL SETTINGS
# =============================================================================

# Default encoding for file operations
DEFAULT_ENCODING = 'utf-8'

# Default timeout for HTTP requests (seconds)
DEFAULT_HTTP_TIMEOUT = 10

# Maximum number of retries for failed requests
DEFAULT_MAX_RETRIES = 3

# Retry delay (seconds)
DEFAULT_RETRY_DELAY = 1.0

# Default number of parallel workers
# None = auto-detect (CPU count - 1)
DEFAULT_WORKERS = None


# =============================================================================
# URL/DOMAIN VALIDATION SETTINGS
# =============================================================================

# Whether to allow IPv4 addresses as valid domains
ALLOW_IPV4_DOMAINS = True

# Whether to allow URLs without schemes (e.g., "example.com")
ALLOW_SCHEMELESS_URLS = True

# Default allowed URL schemes
DEFAULT_ALLOWED_SCHEMES = {'http', 'https', 'ftp', 'ftps'}

# Whether to strip www. prefix by default when normalizing domains
DEFAULT_STRIP_WWW = False


# =============================================================================
# EXTRACTION SETTINGS
# =============================================================================

# Whether to return only unique URLs/domains by default
DEFAULT_UNIQUE_ONLY = True

# Maximum file size to process (bytes)
# None = no limit
MAX_FILE_SIZE = None

# Whether to skip binary files during extraction
SKIP_BINARY_FILES = True

# Binary file extensions to skip
BINARY_EXTENSIONS = {
    '.exe', '.dll', '.so', '.dylib',
    '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico',
    '.mp3', '.mp4', '.avi', '.mov', '.wav',
    '.bin', '.dat', '.db', '.sqlite',
}


# =============================================================================
# OUTPUT SETTINGS
# =============================================================================

# Default CSV delimiter
CSV_DELIMITER = ','

# Whether to include header row in CSV output
CSV_INCLUDE_HEADER = True

# JSON output indentation (None for compact)
JSON_INDENT = 2

# Default output directory for results
DEFAULT_OUTPUT_DIR = Path('url_toolkit_output')


# =============================================================================
# PROGRESS/LOGGING SETTINGS
# =============================================================================

# Whether to show progress bars by default
SHOW_PROGRESS = True

# Progress update interval (update every N items)
PROGRESS_UPDATE_INTERVAL = 10

# Whether to show verbose output
VERBOSE = False


# =============================================================================
# HTTP CHECKING SETTINGS
# =============================================================================

# User agent for HTTP requests
DEFAULT_USER_AGENT = 'Mozilla/5.0 (compatible; URLToolkit/1.0)'

# Whether to follow redirects
FOLLOW_REDIRECTS = True

# Maximum number of redirects to follow
MAX_REDIRECTS = 5

# Whether to verify SSL certificates
VERIFY_SSL = True

# HTTP methods to try (in order)
# HEAD is faster but some servers don't support it
HTTP_METHODS = ['HEAD', 'GET']

# Status codes considered "alive"
ALIVE_STATUS_CODES = {200, 201, 202, 203, 204, 205, 206}

# Status codes considered redirects
REDIRECT_STATUS_CODES = {300, 301, 302, 303, 307, 308}

# Status codes to retry
RETRY_STATUS_CODES = {408, 429, 500, 502, 503, 504}


# =============================================================================
# TLD (TOP-LEVEL DOMAIN) SETTINGS
# =============================================================================

# Common valid TLDs for validation
# This is a subset - not comprehensive
COMMON_TLDS: Set[str] = {
    # Generic TLDs
    'com', 'org', 'net', 'edu', 'gov', 'mil', 'int',
    'info', 'biz', 'name', 'museum', 'coop', 'aero',
    'jobs', 'mobi', 'travel', 'tel', 'asia', 'cat', 'pro',

    # New generic TLDs
    'io', 'dev', 'ai', 'app', 'tech', 'blog', 'online',
    'site', 'website', 'space', 'store', 'cloud', 'digital',
    'email', 'news', 'media', 'video', 'music', 'photo',

    # Country code TLDs (common ones)
    'us', 'uk', 'ca', 'au', 'de', 'fr', 'jp', 'cn', 'in',
    'br', 'ru', 'nl', 'es', 'it', 'pl', 'se', 'no', 'dk',
    'fi', 'be', 'ch', 'at', 'nz', 'sg', 'hk', 'tw', 'kr',
    'mx', 'ar', 'cl', 'co', 'za', 'ie', 'il', 'ae', 'sa',

    # Common two-letter TLDs
    'me', 'tv', 'cc', 'ws', 'to', 'tk', 'fm', 'am',
}

# Suspicious TLD patterns (often used for malicious purposes)
SUSPICIOUS_TLDS = {
    'tk', 'ml', 'ga', 'cf', 'gq',  # Free domains
    'xyz', 'top', 'work', 'click', 'link',  # Spam-heavy
}


# =============================================================================
# URL SHORTENER DOMAINS
# =============================================================================

# Known URL shortener domains
URL_SHORTENER_DOMAINS = {
    'bit.ly', 'goo.gl', 'tinyurl.com', 't.co', 'ow.ly',
    'is.gd', 'buff.ly', 'adf.ly', 'bit.do', 'short.to',
    'tiny.cc', 'cli.gs', 'pic.gd', 'DwarfURL.com',
    'yfrog.com', 'migre.me', 'ff.im', 'tiny.pl', 'url4.eu',
    'tr.im', 'twit.ac', 'su.pr', 'twurl.nl', 'snipurl.com',
    'short.ie', 'BudURL.com', 'ping.fm', 'Digg.com',
    'post.ly', 'Just.as', 'bkite.com', 'snipr.com',
    'fic.kr', 'loopt.us', 'doiop.com', 'twitthis.com',
    'htxt.it', 'AltURL.com', 'RedirX.com', 'DigBig.com',
    'short.to', 'ping.fm', 'Fly2.ws', 'Xrl.us', 'budurl.com',
}


# =============================================================================
# TRACKING PARAMETER PATTERNS
# =============================================================================

# Common tracking parameters to remove when normalizing URLs
TRACKING_PARAMS = {
    # Google Analytics
    'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
    'utm_name', 'utm_cid', 'utm_reader', 'utm_viz_id', 'utm_pubreferrer',

    # Facebook
    'fbclid', 'fb_action_ids', 'fb_action_types', 'fb_ref', 'fb_source',

    # Other common trackers
    'gclid', 'gclsrc', 'dclid', 'zanpid', 'msclkid', 'otracker',
    'mc_cid', 'mc_eid',

    # Email tracking
    '_hsenc', '_hsmi', 'mkt_tok',

    # General tracking
    'ref', 'referrer', 'campaign', 'source', 'medium',
}


# =============================================================================
# SUSPICIOUS PATTERNS
# =============================================================================

# Regex patterns for suspicious domains/URLs
# These are patterns, not full regexes
SUSPICIOUS_PATTERNS = [
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # IP addresses
    r'-{3,}',  # Multiple consecutive dashes
    r'_{3,}',  # Multiple consecutive underscores
    r'\d{10,}',  # Very long number sequences
    r'[a-z0-9]{20,}',  # Very long random-looking strings
]


# =============================================================================
# FILE FORMAT SETTINGS
# =============================================================================

# Text file extensions to process
TEXT_EXTENSIONS = {
    '.txt', '.md', '.markdown', '.rst', '.log', '.csv', '.tsv',
    '.json', '.xml', '.html', '.htm', '.css', '.js', '.py',
    '.java', '.cpp', '.c', '.h', '.sh', '.bat', '.ps1',
}

# Document file extensions that require special handling
DOCUMENT_EXTENSIONS = {
    '.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt',
}


# =============================================================================
# BATCH PROCESSING SETTINGS
# =============================================================================

# Default batch size for batch processing
DEFAULT_BATCH_SIZE = 100

# Chunk size for multiprocessing
DEFAULT_CHUNK_SIZE = 10


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_setting(name: str, default=None):
    """
    Get a setting value by name.

    Args:
        name: Setting name (e.g., 'DEFAULT_HTTP_TIMEOUT')
        default: Default value if setting not found

    Returns:
        Setting value or default
    """
    return globals().get(name, default)


def update_setting(name: str, value):
    """
    Update a setting value.

    Args:
        name: Setting name
        value: New value

    Raises:
        KeyError: If setting doesn't exist
    """
    if name not in globals():
        raise KeyError(f"Unknown setting: {name}")
    globals()[name] = value
