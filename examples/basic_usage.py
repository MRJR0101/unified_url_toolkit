#!/usr/bin/env python3
"""
Basic usage examples for Unified URL Toolkit.

This demonstrates how simple it is to use the refactored library
compared to the 42+ original implementations.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from unified_url_toolkit import (
    extract_urls_from_text,
    extract_domains_from_text,
    validate_domain,
    validate_url,
    normalize_domain,
    clean_domain_list,
)


def example_extraction():
    """Example: Extract URLs and domains from text."""
    print("=" * 70)
    print("EXAMPLE 1: URL and Domain Extraction")
    print("=" * 70)

    text = """
    Visit our website at https://www.example.com/products
    Contact us at support@test.org
    Check out http://blog.company.io/posts/2024/article
    IP address: 192.168.1.1
    """

    # Extract URLs
    urls = extract_urls_from_text(text)
    print(f"\nExtracted {len(urls)} URLs:")
    for url in urls:
        print(f"  • {url}")

    # Extract domains
    domains = extract_domains_from_text(text)
    print(f"\nExtracted {len(domains)} domains:")
    for domain in domains:
        print(f"  • {domain}")


def example_validation():
    """Example: Validate URLs and domains."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: URL and Domain Validation")
    print("=" * 70)

    test_domains = [
        "example.com",
        "www.test.org",
        "invalid..domain",
        "localhost",
        "192.168.1.1"
    ]

    print("\nValidating domains:")
    for domain in test_domains:
        is_valid, status = validate_domain(domain)
        symbol = "✓" if is_valid else "✗"
        print(f"  {symbol} {domain:<20} - {status.value}")

    test_urls = [
        "https://example.com/path",
        "http://test.org",
        "invalid url with spaces",
        "example.com/path"
    ]

    print("\nValidating URLs:")
    for url in test_urls:
        is_valid, reason = validate_url(url, check_scheme=False)
        symbol = "✓" if is_valid else "✗"
        print(f"  {symbol} {url:<30} - {reason}")


def example_normalization():
    """Example: Normalize and clean domains."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Domain Normalization")
    print("=" * 70)

    messy_domains = [
        "HTTPS://WWW.Example.COM/path",
        "www.example.com.",
        "WWW.TEST.ORG",
        "blog.example.com",
        "test.org",
        "test.org",  # Duplicate
    ]

    print("\nOriginal domains:")
    for domain in messy_domains:
        print(f"  • {domain}")

    # Clean with various options
    cleaned = clean_domain_list(
        messy_domains,
        strip_www=True,
        remove_duplicates=True,
        sort=True
    )

    print(f"\nCleaned to {len(cleaned)} unique domains:")
    for domain in cleaned:
        print(f"  • {domain}")

    # Individual normalization
    print("\nNormalization examples:")
    examples = [
        ("WWW.Example.COM.", False, False),
        ("WWW.Example.COM.", True, False),
        ("blog.api.example.com", False, True),
    ]

    for domain, strip_www, strip_subdomain in examples:
        normalized = normalize_domain(
            domain,
            strip_www=strip_www,
            strip_subdomain=strip_subdomain
        )
        flags = []
        if strip_www:
            flags.append("strip_www")
        if strip_subdomain:
            flags.append("strip_subdomain")
        flags_str = f" [{', '.join(flags)}]" if flags else ""
        print(f"  {domain:<30} -> {normalized:<20}{flags_str}")


def example_file_operations():
    """Example: File I/O operations."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: File Operations")
    print("=" * 70)

    from unified_url_toolkit.io import write_urls_to_file, read_urls_from_file

    # Sample URLs
    urls = [
        "https://example.com",
        "https://test.org",
        "https://company.io"
    ]

    # Write to file
    output_file = Path("sample_urls.txt")
    count = write_urls_to_file(urls, output_file, deduplicate=True, sort=True)
    print(f"\n✓ Wrote {count} URLs to {output_file}")

    # Read back
    read_urls = read_urls_from_file(output_file)
    print(f"✓ Read {len(read_urls)} URLs from {output_file}")

    for url in read_urls:
        print(f"  • {url}")

    # Clean up
    output_file.unlink()
    print(f"\n✓ Cleaned up {output_file}")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("UNIFIED URL TOOLKIT - BASIC USAGE EXAMPLES")
    print("=" * 70)
    print("\nDemonstrating functionality consolidated from 42+ legacy projects")
    print("into one clean, maintainable library.\n")

    example_extraction()
    example_validation()
    example_normalization()
    example_file_operations()

    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)
    print("\nFor more examples, see:")
    print("  • cli/clean_domains.py - Domain cleaning tool")
    print("  • cli/extract_urls.py - URL extraction tool")
    print("  • cli/check_links.py - URL checking tool")
    print("\n")


if __name__ == '__main__':
    main()
