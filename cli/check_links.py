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
import importlib
import sys
from pathlib import Path


def _load_toolkit():
    """Import toolkit modules with package-first, path-fallback behavior."""
    try:
        checkers = importlib.import_module("unified_url_toolkit.core.checkers")
        readers = importlib.import_module("unified_url_toolkit.io.readers")
        writers = importlib.import_module("unified_url_toolkit.io.writers")
    except ModuleNotFoundError:
        project_root = Path(__file__).resolve().parents[1]
        workspace_root = project_root.parent
        if str(workspace_root) not in sys.path:
            sys.path.insert(0, str(workspace_root))
        checkers = importlib.import_module("unified_url_toolkit.core.checkers")
        readers = importlib.import_module("unified_url_toolkit.io.readers")
        writers = importlib.import_module("unified_url_toolkit.io.writers")

    return (
        checkers.URLChecker,
        readers.read_urls_from_file,
        writers.write_check_results_to_csv,
        writers.write_results_to_json,
    )


def main():
    URLChecker, read_urls_from_file, write_check_results_to_csv, write_results_to_json = _load_toolkit()

    parser = argparse.ArgumentParser(
        description="Check URL accessibility with async parallel requests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s urls.txt
  %(prog)s urls.txt -o results.csv
  %(prog)s urls.txt --json results.json
  %(prog)s urls.txt -c 100 -t 20
        """,
    )

    parser.add_argument("input", type=str, help="Input file with URLs (one per line)")

    parser.add_argument("-o", "--output", type=str, help="Output CSV file for results")

    parser.add_argument("--json", type=str, help="Output JSON file for results")

    parser.add_argument("-c", "--concurrency", type=int, default=50, help="Max concurrent requests (default: 50)")

    parser.add_argument(
        "-t", "--timeout", type=float, default=15.0, help="Timeout per request in seconds (default: 15)"
    )

    parser.add_argument("-r", "--retries", type=int, default=2, help="Number of retries on errors (default: 2)")

    parser.add_argument("--no-redirects", action="store_true", help="Don't follow redirects")

    parser.add_argument("--show-ok", action="store_true", help="Show successful URLs in output")

    parser.add_argument("--show-all", action="store_true", help="Show all URLs in output (default: errors only)")

    args = parser.parse_args()

    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_path}")
        sys.exit(2)

    # Read URLs
    print(f"[INFO] Reading URLs from {input_path}...")
    urls = read_urls_from_file(input_path)

    if not urls:
        print("[ERROR] No URLs found in input file")
        sys.exit(1)

    print(f"[INFO] Checking {len(urls)} URLs...")
    print(f"[INFO] Concurrency: {args.concurrency} | Timeout: {args.timeout}s | Retries: {args.retries}")
    print()

    # Create checker and run
    checker = URLChecker(
        timeout=args.timeout, retries=args.retries, concurrency=args.concurrency, follow_redirects=not args.no_redirects
    )

    results = checker.check_sync(urls)

    # Display results
    print("=" * 80)

    for i, result in enumerate(results, 1):
        # Determine if we should show this result
        show = args.show_all or (args.show_ok and result.is_ok()) or result.is_error()

        if show:
            status_symbol = "OK" if result.is_ok() else "ERR"
            url_display = result.url[:65] + "..." if len(result.url) > 65 else result.url

            print(f"[{i}/{len(results)}] {status_symbol} {url_display}")
            print(
                f"        Status: {result.http_status or 'ERROR'} | Time: {result.elapsed_ms}ms | Type: {result.status}"
            )

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
    print(f"OK: {summary['ok']} ({summary['success_rate']:.1f}%)")
    print(f"Failed: {summary['failed']}")
    print()
    print("By status:")
    for status in sorted(summary["by_status"]):
        count = summary["by_status"][status]
        print(f"  {status}: {count}")
    print()
    print(f"Average response time: {summary['avg_time_ms']}ms")
    print(f"Total time: {summary['total_time_ms'] / 1000:.2f}s")

    # Write output files
    if args.output:
        csv_path = Path(args.output)
        count = write_check_results_to_csv(results, csv_path)
        print(f"\n[OK] Wrote {count} results to: {csv_path}")

    if args.json:
        json_path = Path(args.json)
        write_results_to_json(results, json_path)
        print(f"[OK] Wrote results to: {json_path}")

    # Exit with error code if any URLs failed
    sys.exit(0 if summary["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
