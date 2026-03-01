#!/usr/bin/env python3
"""
Advanced usage examples showing all features of Unified URL Toolkit.

This demonstrates the complete functionality including:
- Core extraction, validation, normalization
- Parallel processing
- Progress tracking
- Error handling
- Analysis and categorization
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from unified_url_toolkit import (
    # Core
    extract_urls_from_text,
    extract_domains_from_text,
    validate_domain,
    validate_url,
    normalize_domain,
    normalize_url,

    # Processing
    process_parallel,
    process_parallel_with_progress,
    batch_items,

    # Utils
    ProgressBar,
    SimpleProgress,
    create_progress_callback,
    ErrorCollector,

    # Analysis
    categorize_urls,
    get_top_domains,
    get_top_tlds,
)


def example_parallel_processing():
    """Example: Process URLs in parallel with progress tracking."""
    print("=" * 70)
    print("EXAMPLE: Parallel Processing with Progress")
    print("=" * 70)

    # Simulate a list of URLs to validate
    urls = [
        "https://example.com",
        "http://test.org/page",
        "invalid url",
        "https://google.com",
        "http://192.168.1.1",
    ] * 20  # 100 URLs total

    def validate_and_check(url: str) -> dict:
        """Validate URL and return result."""
        is_valid, reason = validate_url(url, check_scheme=False)
        return {
            'url': url,
            'valid': is_valid,
            'reason': reason
        }

    # Process in parallel with progress
    print(f"\nValidating {len(urls)} URLs in parallel...\n")

    callback = create_progress_callback(len(urls), desc="Validating")
    results = process_parallel_with_progress(
        urls,
        validate_and_check,
        max_workers=10,
        use_threads=True,
        progress_callback=callback
    )

    # Count valid/invalid
    valid_count = sum(1 for r in results if r and r['valid'])
    print(f"\nResults: {valid_count}/{len(urls)} valid URLs")


def example_batch_processing():
    """Example: Process items in batches."""
    print("\n" + "=" * 70)
    print("EXAMPLE: Batch Processing")
    print("=" * 70)

    # Generate test domains
    domains = [f"example{i}.com" for i in range(50)]

    print(f"\nProcessing {len(domains)} domains in batches...\n")

    batch_size = 10
    total_batches = len(list(batch_items(domains, batch_size)))

    with ProgressBar(total=total_batches, desc="Processing batches") as progress:
        for batch in batch_items(domains, batch_size):
            # Process batch
            normalized = [normalize_domain(d) for d in batch]
            progress.update(1)

    print(f"Processed {len(domains)} domains in {total_batches} batches")


def example_error_handling():
    """Example: Collect errors during processing."""
    print("\n" + "=" * 70)
    print("EXAMPLE: Error Collection")
    print("=" * 70)

    test_domains = [
        "valid.com",
        "also-valid.org",
        "bad..domain",
        "localhost",
        "another.good.site",
        "192.168.1.1",
    ]

    collector = ErrorCollector()
    valid_domains = []

    print("\nValidating domains with error collection...\n")

    for domain in test_domains:
        try:
            is_valid, status = validate_domain(domain)
            if is_valid:
                valid_domains.append(domain)
                print(f"✓ {domain}")
            else:
                raise ValueError(f"Invalid: {status.value}")
        except Exception as e:
            collector.add(e, context=f"Domain: {domain}")
            print(f"✗ {domain} - {e}")

    print(f"\n{len(valid_domains)} valid, {collector.count()} errors")

    if collector.has_errors():
        print("\n" + collector.summary())


def example_url_analysis():
    """Example: Analyze and categorize URLs."""
    print("\n" + "=" * 70)
    print("EXAMPLE: URL Analysis and Categorization")
    print("=" * 70)

    test_urls = [
        "https://www.example.com/page",
        "http://test.org/article",
        "https://api.github.com/repos",
        "http://blog.example.com/posts",
        "https://example.com:8080/admin",
        "http://192.168.1.1/",
        "https://bit.ly/abc123",
        "http://test.xyz/suspicious",
    ]

    print(f"\nAnalyzing {len(test_urls)} URLs...\n")

    # Categorize
    result = categorize_urls(test_urls)

    print(f"Total unique domains: {len(result.unique_domains)}")
    print(f"URLs with ports: {len(result.with_ports)}")
    print(f"URLs with paths: {len(result.with_paths)}")
    print(f"URL shorteners: {len(result.url_shorteners)}")
    print(f"IP addresses: {len(result.ip_addresses)}")
    print(f"Suspicious URLs: {len(result.suspicious)}")

    # Top domains
    print("\nTop domains:")
    top_domains = get_top_domains(test_urls, top_n=5)
    for domain, count in top_domains:
        print(f"  {domain}: {count}")

    # Top TLDs
    print("\nTop TLDs:")
    top_tlds = get_top_tlds(test_urls, top_n=5)
    for tld, count in top_tlds:
        print(f"  .{tld}: {count}")

    # Suspicious details
    if result.suspicious:
        print("\nSuspicious URLs detected:")
        for item in result.suspicious:
            print(f"  {item['url']} - {item['reason']}")


def example_complete_pipeline():
    """Example: Complete processing pipeline."""
    print("\n" + "=" * 70)
    print("EXAMPLE: Complete Processing Pipeline")
    print("=" * 70)

    # Sample text with URLs
    text = """
    Check out these websites:
    - Main site: https://www.example.com/products
    - Blog: http://blog.example.com/articles/2024/post
    - API docs: https://api.example.com/v1/docs
    - Support: support@example.com

    Also see:
    http://test.org, https://github.com/user/repo
    Some shortlink: https://bit.ly/abc123
    """

    print("\nStep 1: Extract URLs from text")
    urls = extract_urls_from_text(text)
    print(f"Found {len(urls)} URLs")

    print("\nStep 2: Extract domains")
    domains = extract_domains_from_text(text)
    print(f"Found {len(domains)} domains")

    print("\nStep 3: Normalize domains")
    normalized = [normalize_domain(d, strip_www=True) for d in domains]
    print(f"Normalized: {', '.join(normalized)}")

    print("\nStep 4: Validate URLs (parallel)")

    def quick_validate(url):
        is_valid, _ = validate_url(url, check_scheme=False)
        return is_valid

    with ProgressBar(total=len(urls), desc="Validating") as progress:
        valid_results = []
        for url in urls:
            valid_results.append(quick_validate(url))
            progress.update(1)

    valid_count = sum(valid_results)
    print(f"\nValidation complete: {valid_count}/{len(urls)} valid")

    print("\nStep 5: Categorize URLs")
    result = categorize_urls(urls)
    print(f"Unique domains: {len(result.unique_domains)}")
    print(f"With paths: {len(result.with_paths)}")

    print("\n✅ Pipeline complete!")


def main():
    """Run all examples."""
    examples = [
        example_parallel_processing,
        example_batch_processing,
        example_error_handling,
        example_url_analysis,
        example_complete_pipeline,
    ]

    print("\n" + "=" * 70)
    print("UNIFIED URL TOOLKIT - ADVANCED USAGE EXAMPLES")
    print("=" * 70)
    print("\nDemonstrating all features of the refactored library")
    print("Consolidated from 42+ legacy projects into one clean codebase")
    print("=" * 70)

    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ Error in {example_func.__name__}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    print("ALL EXAMPLES COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    main()
