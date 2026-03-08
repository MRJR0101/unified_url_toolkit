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

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Only check the first N URLs (after --offset). Useful for sampling large files.",
    )

    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        metavar="N",
        help="Skip the first N URLs. Use with --limit to resume a previous run (default: 0).",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        metavar="N",
        help=(
            "Process URLs in batches of N. Writes CSV output after each batch so progress "
            "is never lost. Recommended for files with 10k+ URLs (e.g. --batch-size 1000)."
        ),
    )

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

    # Apply offset and limit
    if args.offset:
        if args.offset >= len(urls):
            print(f"[ERROR] --offset {args.offset} exceeds total URL count ({len(urls)})")
            sys.exit(2)
        urls = urls[args.offset:]
        print(f"[INFO] Skipping first {args.offset} URLs (--offset)")

    if args.limit is not None:
        urls = urls[:args.limit]
        print(f"[INFO] Limiting to {args.limit} URLs (--limit)")

    total_urls = len(urls)
    print(f"[INFO] Checking {total_urls} URLs...")
    print(f"[INFO] Concurrency: {args.concurrency} | Timeout: {args.timeout}s | Retries: {args.retries}")
    if args.batch_size:
        import math
        total_batches = math.ceil(total_urls / args.batch_size)
        print(f"[INFO] Batch mode: {args.batch_size} URLs/batch | {total_batches} batches total")
    print()

    # Create checker
    checker = URLChecker(
        timeout=args.timeout, retries=args.retries, concurrency=args.concurrency, follow_redirects=not args.no_redirects
    )

    # --- Batch mode ---
    if args.batch_size:
        import math
        import time as _time

        all_results = []
        total_batches = math.ceil(total_urls / args.batch_size)
        run_start = _time.monotonic()

        for batch_num in range(total_batches):
            batch_start_idx = batch_num * args.batch_size
            batch_urls = urls[batch_start_idx: batch_start_idx + args.batch_size]
            batch_abs_offset = args.offset + batch_start_idx

            print(f"[Batch {batch_num + 1}/{total_batches}] URLs {batch_abs_offset + 1}"
                  f"-{batch_abs_offset + len(batch_urls)} of {args.offset + total_urls}")

            batch_results = checker.check_sync(batch_urls)
            all_results.extend(batch_results)

            # Write CSV progress after every batch
            if args.output:
                csv_path = Path(args.output)
                written = write_check_results_to_csv(all_results, csv_path)
                elapsed = _time.monotonic() - run_start
                pct = len(all_results) / total_urls * 100
                print(f"  -> {written} results saved | {pct:.1f}% done | {elapsed:.0f}s elapsed")

        results = all_results

    # --- Single-pass mode ---
    else:
        results = checker.check_sync(urls)

    # Display results
    print()
    print("=" * 80)

    for i, result in enumerate(results, 1):
        show = args.show_all or (args.show_ok and result.is_ok()) or result.is_error()

        if show:
            status_symbol = "OK" if result.is_ok() else "ERR"
            abs_index = args.offset + i
            url_display = result.url[:65] + "..." if len(result.url) > 65 else result.url

            print(f"[{abs_index}] {status_symbol} {url_display}")
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
    if args.offset:
        print(f"URL range: {args.offset + 1} - {args.offset + total_urls}")
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

    # Write output files (single-pass or final batch write)
    if args.output and not args.batch_size:
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
