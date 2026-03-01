#!/usr/bin/env python3
"""
Content & Response Analysis Examples

Demonstrates all specialized modules for analyzing what URLs return:
- HTTP response analysis (status, headers, CORS, security)
- Redirect chain mapping
- Content inspection (MIME, compression)
- Metadata extraction (HTML, OpenGraph, Twitter Card)
- Cache behavior analysis
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from unified_url_toolkit.specialized import (
    # HTTP Analysis
    fetch_http_response,
    categorize_headers,
    get_missing_security_headers,

    # Redirect Mapping
    follow_redirect_chain,
    format_redirect_chain,

    # Content Inspection
    analyze_content,
    sniff_content_type,

    # Metadata Extraction
    extract_metadata,
    format_metadata,

    # Cache Analysis
    analyze_cache,
    format_cache_analysis,
    detect_fingerprint,
)


def example_http_response_analysis():
    """Example: Analyze HTTP response, headers, and security."""
    print("=" * 70)
    print("EXAMPLE 1: HTTP Response Analysis")
    print("=" * 70)

    url = "https://github.com"

    print(f"\nAnalyzing: {url}\n")

    # Fetch and analyze response
    response = fetch_http_response(url, method="GET", timeout=10)

    print(f"Status: {response.status_code} - {response.status_name}")
    print(f"Category: {response.status_category}")
    print(f"Response Time: {response.response_time_ms:.0f}ms")
    print(f"Server: {response.server}")
    print(f"Content-Type: {response.content_type}")
    print(f"Content-Length: {response.content_length}")
    print(f"Compression: {response.content_encoding}")

    # CORS analysis
    print(f"\nCORS:")
    print(f"  Allowed: {response.cors_allowed}")
    if response.cors_origin:
        print(f"  Origin: {response.cors_origin}")
    if response.cors_methods:
        print(f"  Methods: {', '.join(response.cors_methods)}")

    # Security headers
    print(f"\nSecurity Headers:")
    if response.security_headers:
        for name, value in response.security_headers.items():
            print(f"  {name}: {value[:50]}...")
    else:
        print("  None found")

    # Missing security headers
    missing = get_missing_security_headers(response.headers)
    if missing:
        print(f"\n⚠️  Missing recommended headers: {', '.join(missing)}")

    # Categorize headers
    print(f"\nHeader Analysis:")
    categorized = categorize_headers(response.headers)
    print(f"  Standard headers: {len(categorized.standard_headers)}")
    print(f"  Security headers: {len(categorized.security_headers)}")
    print(f"  Cache headers: {len(categorized.cache_headers)}")
    print(f"  Custom headers: {len(categorized.custom_headers)}")


def example_redirect_chain():
    """Example: Follow redirect chains."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Redirect Chain Mapping")
    print("=" * 70)

    # URLs that redirect
    test_urls = [
        "http://github.com",  # HTTP → HTTPS redirect
        "https://bit.ly/3xMJK3M",  # URL shortener (example)
    ]

    for url in test_urls:
        print(f"\nFollowing redirects for: {url}\n")

        chain = follow_redirect_chain(url, max_redirects=5, timeout=5)

        if chain.error:
            print(f"Error: {chain.error}")
            continue

        print(f"Total Redirects: {chain.total_redirects}")
        print(f"Total Time: {chain.total_time_ms:.0f}ms")
        print(f"Final URL: {chain.final_url}")

        if chain.permanent_redirects:
            print(f"Permanent (301/308): {chain.permanent_redirects}")
        if chain.temporary_redirects:
            print(f"Temporary (302/303/307): {chain.temporary_redirects}")

        print(f"\nRedirect Hops:")
        for i, hop in enumerate(chain.hops, 1):
            print(f"  {i}. {hop.redirect_type}")
            print(f"     {hop.url}")
            if hop.location:
                print(f"     → {hop.location}")

        if chain.crosses_domains:
            print(f"\n⚠️  Crosses domain boundaries")
        if chain.crosses_protocols:
            print(f"🔒 Protocol upgrade (HTTP → HTTPS)")


def example_content_inspection():
    """Example: Analyze content type, compression, and MIME."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Content Inspection")
    print("=" * 70)

    url = "https://github.com"

    print(f"\nFetching: {url}\n")

    response = fetch_http_response(url)

    # Analyze content
    content_analysis = analyze_content(
        content_type=response.content_type,
        content_length=str(response.content_length) if response.content_length else None,
        content_encoding=response.content_encoding,
    )

    print(f"MIME Type: {content_analysis.mime_type}")
    print(f"Category: {content_analysis.mime_category}")
    print(f"Charset: {content_analysis.charset}")
    print(f"Size: {content_analysis.content_length_human}")

    print(f"\nContent Classification:")
    print(f"  Is Text: {content_analysis.is_text}")
    print(f"  Is HTML: {content_analysis.is_html}")
    print(f"  Is JSON: {content_analysis.is_json}")
    print(f"  Is Binary: {content_analysis.is_binary}")
    print(f"  Is Image: {content_analysis.is_image}")

    if content_analysis.is_compressed:
        print(f"\n✓ Compressed: {content_analysis.compression_type}")
    else:
        print(f"\n✗ Not compressed")


def example_metadata_extraction():
    """Example: Extract page metadata, OpenGraph, Twitter Card."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Metadata Extraction")
    print("=" * 70)

    url = "https://github.com"

    print(f"\nExtracting metadata from: {url}\n")

    try:
        metadata = extract_metadata(url, timeout=10)

        print(f"Title: {metadata.title}")
        print(f"Description: {metadata.description[:100]}..." if metadata.description else "Description: None")

        if metadata.canonical_url:
            print(f"Canonical: {metadata.canonical_url}")

        # OpenGraph
        if metadata.has_opengraph:
            print(f"\n✓ OpenGraph Tags Found:")
            if metadata.og_title:
                print(f"  Title: {metadata.og_title}")
            if metadata.og_description:
                print(f"  Description: {metadata.og_description[:80]}...")
            if metadata.og_image:
                print(f"  Image: {metadata.og_image}")
            if metadata.og_type:
                print(f"  Type: {metadata.og_type}")
        else:
            print(f"\n✗ No OpenGraph tags")

        # Twitter Card
        if metadata.has_twitter_card:
            print(f"\n✓ Twitter Card Found:")
            if metadata.twitter_card:
                print(f"  Type: {metadata.twitter_card}")
            if metadata.twitter_site:
                print(f"  Site: {metadata.twitter_site}")
        else:
            print(f"\n✗ No Twitter Card")

        # SEO
        print(f"\nSEO:")
        print(f"  Robots: {metadata.robots or 'Not specified'}")
        print(f"  Indexable: {metadata.is_indexable}")

        if metadata.favicon:
            print(f"  Favicon: {metadata.favicon}")

    except Exception as e:
        print(f"Error extracting metadata: {e}")


def example_cache_analysis():
    """Example: Analyze cache headers and fingerprinting."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Cache Analysis")
    print("=" * 70)

    # Examples of different caching scenarios
    test_cases = [
        {
            'name': 'Fingerprinted static asset',
            'url': 'https://example.com/app.min.js?v=1.2.3',
            'cache_control': 'public, max-age=31536000, immutable',
            'etag': '"abc123def456"',
        },
        {
            'name': 'Non-fingerprinted HTML',
            'url': 'https://example.com/index.html',
            'cache_control': 'public, max-age=3600, must-revalidate',
            'last_modified': 'Mon, 16 Jan 2026 12:00:00 GMT',
        },
        {
            'name': 'No caching (API response)',
            'url': 'https://api.example.com/data',
            'cache_control': 'no-store, no-cache, must-revalidate',
        },
    ]

    for test in test_cases:
        print(f"\n{test['name']}:")
        print(f"URL: {test['url']}")

        # Detect fingerprinting
        has_fp, fp_type, fp_value = detect_fingerprint(test['url'])
        if has_fp:
            print(f"✓ Fingerprinted: {fp_type} = {fp_value}")
        else:
            print(f"✗ Not fingerprinted")

        # Analyze cache
        cache = analyze_cache(
            url=test['url'],
            cache_control=test.get('cache_control'),
            etag=test.get('etag'),
            last_modified=test.get('last_modified'),
        )

        print(f"Cache Score: {cache.cache_score}/100")
        print(f"Cacheable: {cache.is_cacheable}")
        if cache.max_age:
            print(f"Max Age: {cache.max_age}s")
        if cache.cache_directives:
            print(f"Directives: {', '.join(cache.cache_directives)}")

        if cache.recommendations:
            print(f"Recommendations:")
            for rec in cache.recommendations:
                print(f"  • {rec}")


def example_complete_url_analysis():
    """Example: Complete analysis of a URL."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Complete URL Analysis")
    print("=" * 70)

    url = "https://github.com/features"

    print(f"\nPerforming complete analysis of: {url}\n")
    print("This combines all specialized modules:")
    print("  1. HTTP Response")
    print("  2. Redirect Chain")
    print("  3. Content Inspection")
    print("  4. Metadata Extraction")
    print("  5. Cache Analysis")
    print("")

    # 1. HTTP Response
    print("Step 1: HTTP Response Analysis...")
    response = fetch_http_response(url)
    print(f"  ✓ Status: {response.status_code} {response.status_name}")
    print(f"  ✓ Response Time: {response.response_time_ms:.0f}ms")

    # 2. Redirect Chain
    print("\nStep 2: Redirect Chain...")
    chain = follow_redirect_chain(url, max_redirects=5)
    if chain.total_redirects > 0:
        print(f"  ✓ {chain.total_redirects} redirect(s) detected")
        print(f"  ✓ Final URL: {chain.final_url}")
    else:
        print(f"  ✓ No redirects (direct response)")

    # 3. Content Inspection
    print("\nStep 3: Content Inspection...")
    content = analyze_content(
        content_type=response.content_type,
        content_length=str(response.content_length) if response.content_length else None,
        content_encoding=response.content_encoding,
    )
    print(f"  ✓ Type: {content.mime_type}")
    print(f"  ✓ Compressed: {content.is_compressed}")

    # 4. Metadata
    print("\nStep 4: Metadata Extraction...")
    try:
        metadata = extract_metadata(url, timeout=10)
        print(f"  ✓ Title: {metadata.title[:50]}..." if metadata.title else "  ✗ No title")
        print(f"  ✓ OpenGraph: {metadata.has_opengraph}")
        print(f"  ✓ Twitter Card: {metadata.has_twitter_card}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    # 5. Cache Analysis
    print("\nStep 5: Cache Analysis...")
    cache = analyze_cache(
        url=url,
        cache_control=response.cache_control,
        etag=response.etag,
        last_modified=response.last_modified,
    )
    print(f"  ✓ Cache Score: {cache.cache_score}/100")
    print(f"  ✓ Cacheable: {cache.is_cacheable}")

    print("\n✅ Complete analysis finished!")


def main():
    """Run all examples."""
    examples = [
        example_http_response_analysis,
        example_redirect_chain,
        example_content_inspection,
        example_metadata_extraction,
        example_cache_analysis,
        example_complete_url_analysis,
    ]

    print("\n" + "=" * 70)
    print("SPECIALIZED MODULES - CONTENT & RESPONSE ANALYSIS")
    print("=" * 70)
    print("\nDemonstrating analysis of what URLs return:")
    print("• HTTP responses, headers, security")
    print("• Redirect chains and types")
    print("• Content MIME types and compression")
    print("• Page metadata and SEO tags")
    print("• Cache behavior and optimization")
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
    print("\nThese modules analyze HTTP responses and page content,")
    print("complementing the core URL/domain modules.")
    print("=" * 70)


if __name__ == "__main__":
    main()
