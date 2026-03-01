#!/usr/bin/env python3
"""
Check URL status with async parallel requests.

BEFORE: 8+ separate implementations (CheckLinks, ValidateLinks, MyUrlChecker, etc.)
AFTER: One clean implementation using unified checker

Replaces:
- CheckLinks/
- ValidateLinks/
- MyUrlChecker/
- Linkchecker/
- LinkCheckerv2/
- URLToolkit url_validator and link_checker functions
"""

import argparse
import sys
from pathlib import Path

# Import from unified toolkit
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.checkers import URLChecker
from io.readers import read_urls_from_file
from io.writers import write_check_results_to_csv, write_results_to_json


def main():
    parser = argparse.ArgumentParser(
        description='Check URL accessibility with async parallel requests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s urls.txt
  %(prog)s urls.txt -o results.csv
  %(prog)s urls.txt --json results.json
  %(prog)s urls.txt -c 100 -t 20
        '''
    )

    parser.add_argument(
        'input',
        type=str,
        help='Input file with URLs (one per line)'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output CSV file for results'
    )

    parser.add_argument(
        '--json',
        type=str,
        help='Output JSON file for results'
    )

    parser.add_argument(
        '-c', '--concurrency',
        type=int,
        default=50,
        help='Max concurrent requests (default: 50)'
    )

    parser.add_argument(
        '-t', '--timeout',
        type=float,
        default=15.0,
        help='Timeout per request in seconds (default: 15)'
    )

    parser.add_argument(
        '-r', '--retries',
        type=int,
        default=2,
        help='Number of retries on errors (default: 2)'
    )

    parser.add_argument(
        '--no-redirects',
        action='store_true',
        help='Don\'t follow redirects'
    )

    parser.add_argument(
        '--show-ok',
        action='store_true',
        help='Show successful URLs in output'
    )

    parser.add_argument(
        '--show-all',
        action='store_true',
        help='Show all URLs in output (default: errors only)'
    )

    args = parser.parse_args()

    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_path}")
        sys.exit(2)

    # Read URLs
    print(f"📋 Reading URLs from {input_path}...")
    urls = read_urls_from_file(input_path)

    if not urls:
        print("[ERROR] No URLs found in input file")
        sys.exit(1)

    print(f"🔍 Checking {len(urls)} URLs...")
    print(f"⚙️  Concurrency: {args.concurrency} | Timeout: {args.timeout}s | Retries: {args.retries}")
    print()

    # Create checker and run
    checker = URLChecker(
        timeout=args.timeout,
        retries=args.retries,
        concurrency=args.concurrency,
        follow_redirects=not args.no_redirects
    )

    results = checker.check_sync(urls)

    # Display results
    print("=" * 80)

    for i, result in enumerate(results, 1):
        # Determine if we should show this result
        show = args.show_all or (args.show_ok and result.is_ok()) or result.is_error()

        if show:
            status_symbol = "✓" if result.is_ok() else "✗"
            url_display = result.url[:65] + "..." if len(result.url) > 65 else result.url

            print(f"[{i}/{len(results)}] {status_symbol} {url_display}")
            print(f"        Status: {result.http_status or 'ERROR'} | "
                  f"Time: {result.elapsed_ms}ms | "
                  f"Type: {result.status}")

            if result.error:
                print(f"        Error: {result.error}")

            if result.final_url != result.url:
                print(f"        Redirected to: {result.final_url}")

    # Summary
    summary = checker.get_summary()
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total checked: {summary['total']}")
    print(f"✓ OK: {summary['ok']} ({summary['success_rate']:.1f}%)")
    print(f"✗ Failed: {summary['failed']}")
    print()
    print("By status:")
    for status, count in summary['by_status'].items():
        print(f"  {status}: {count}")
    print()
    print(f"Average response time: {summary['avg_time_ms']}ms")
    print(f"Total time: {summary['total_time_ms'] / 1000:.2f}s")

    # Write output files
    if args.output:
        csv_path = Path(args.output)
        count = write_check_results_to_csv(results, csv_path)
        print(f"\n✅ Wrote {count} results to: {csv_path}")

    if args.json:
        json_path = Path(args.json)
        write_results_to_json(results, json_path)
        print(f"✅ Wrote results to: {json_path}")

    # Exit with error code if any URLs failed
    sys.exit(0 if summary['failed'] == 0 else 1)


if __name__ == '__main__':
    main()
