"""
Configuration module for URL toolkit settings.
"""

from .settings import *

__all__ = [
    'DEFAULT_ENCODING',
    'DEFAULT_HTTP_TIMEOUT',
    'DEFAULT_MAX_RETRIES',
    'DEFAULT_RETRY_DELAY',
    'DEFAULT_WORKERS',
    'ALLOW_IPV4_DOMAINS',
    'DEFAULT_ALLOWED_SCHEMES',
    'DEFAULT_UNIQUE_ONLY',
    'COMMON_TLDS',
    'SUSPICIOUS_TLDS',
    'URL_SHORTENER_DOMAINS',
    'TRACKING_PARAMS',
    'get_setting',
    'update_setting',
]
