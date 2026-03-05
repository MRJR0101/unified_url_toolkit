"""
Input/Output utilities for reading and writing URL/domain data.
"""

from .readers import (
    find_and_read_files,
    read_domains_from_file,
    read_lines_from_file,
    read_urls_from_csv,
    read_urls_from_file,
    read_urls_from_multiple_files,
)
from .writers import (
    append_to_file,
    generate_report_file,
    write_check_results_to_csv,
    write_domains_to_file,
    write_lines_to_file,
    write_results_to_json,
    write_to_csv,
    write_to_json,
    write_urls_to_csv,
    write_urls_to_file,
)

__all__ = [
    # Readers
    "read_lines_from_file",
    "read_urls_from_file",
    "read_urls_from_multiple_files",
    "read_urls_from_csv",
    "read_domains_from_file",
    "find_and_read_files",
    # Writers
    "write_lines_to_file",
    "write_urls_to_file",
    "write_domains_to_file",
    "write_to_csv",
    "write_to_json",
    "write_urls_to_csv",
    "write_check_results_to_csv",
    "write_results_to_json",
    "append_to_file",
    "generate_report_file",
]
