#!/usr/bin/env python3
"""
Extract URLs from files with parallel processing.

BEFORE: 247 lines with embedded multiprocessing, CSV writing, progress tracking
AFTER: ~80 lines focusing on CLI interface only

Replaces:
- ExtractUrls/extract_urls.py
- URLExtractor/
- SimpleUrlExtractor/
- DreamExtractor/
"""

import argparse
import importlib
import sys
from datetime import datetime
from pathlib import Path


def _load_toolkit():
    """Import toolkit modules with package-first, path-fallback behavior."""
    try:
        extractors = importlib.import_module("unified_url_toolkit.core.extractors")
        writers = importlib.import_module("unified_url_toolkit.io.writers")
    except ModuleNotFoundError:
        project_root = Path(__file__).resolve().parents[1]
        workspace_root = project_root.parent
        if str(workspace_root) not in sys.path:
            sys.path.insert(0, str(workspace_root))
        extractors = importlib.import_module("unified_url_toolkit.core.extractors")
        writers = importlib.import_module("unified_url_toolkit.io.writers")

    return extractors.extract_from_files, writers.write_to_csv, writers.write_urls_to_file


def _collect_files_from_directory(directory: Path, recursive: bool, extensions: list[str] | None) -> list[Path]:
    """Collect matching files from a directory in deterministic order."""
    pattern = "**/*" if recursive else "*"
    collected: list[Path] = []

    try:
        for path in directory.glob(pattern):
            try:
                if path.is_file() and (not extensions or path.suffix.lower() in extensions):
                    collected.append(path)
            except OSError:
                continue
    except OSError:
        return []

    return sorted(collected)


def main():
    extract_from_files, write_to_csv, write_urls_to_file = _load_toolkit()

    parser = argparse.ArgumentParser(
        description="Extract URLs from files with parallel processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s file.txt -o urls.txt
  %(prog)s folder/ -r -e txt,md,html
  %(prog)s folder/ -r --csv results.csv
  %(prog)s . -r -e txt --domains
        """,
    )

    parser.add_argument("paths", nargs="+", help="File(s) or folder(s) to process")

    parser.add_argument("-r", "--recursive", action="store_true", help="Search folders recursively")

    parser.add_argument("-e", "--extensions", type=str, help="Comma-separated file extensions (e.g., txt,md,html)")

    parser.add_argument("-o", "--output", type=str, help="Output text file for URLs (one per line)")

    parser.add_argument("--csv", type=str, help="Output CSV file with filename, URL columns")

    parser.add_argument("--domains", action="store_true", help="Extract domains instead of URLs")

    unique_group = parser.add_mutually_exclusive_group()
    unique_group.add_argument(
        "--unique",
        dest="unique",
        action="store_true",
        default=True,
        help="Only unique URLs/domains (default behavior)",
    )
    unique_group.add_argument(
        "--keep-duplicates",
        dest="unique",
        action="store_false",
        help="Keep duplicate URLs/domains in combined output",
    )

    args = parser.parse_args()

    # Parse extensions
    extensions = None
    if args.extensions:
        extensions = []
        for ext in args.extensions.split(","):
            normalized_ext = ext.strip().lower()
            if not normalized_ext:
                continue
            if not normalized_ext.startswith("."):
                normalized_ext = f".{normalized_ext}"
            extensions.append(normalized_ext)

    # Determine content type
    content_type = "domains" if args.domains else "urls"

    # Process paths
    all_files: list[Path] = []
    seen_files: set[Path] = set()
    for path_str in args.paths:
        path = Path(path_str).resolve()

        if not path.exists():
            print(f"[WARN] Path not found: {path_str}")
            continue

        if path.is_file():
            if path not in seen_files:
                all_files.append(path)
                seen_files.add(path)
        elif path.is_dir():
            print(f"[INFO] Scanning directory: {path}")
            directory_files = _collect_files_from_directory(path, recursive=args.recursive, extensions=extensions)
            print(f"[INFO]   Found {len(directory_files)} matching files")
            for filepath in directory_files:
                if filepath not in seen_files:
                    all_files.append(filepath)
                    seen_files.add(filepath)

    if not all_files:
        print("[ERROR] No files found to process")
        sys.exit(1)

    print(f"[INFO] Found {len(all_files)} file(s) to process")
    print(f"[INFO] Extracting {content_type}...\n")

    # Extract from all files
    start_time = datetime.now()
    results = extract_from_files(all_files, content_type=content_type, unique_per_file=True, unique_total=args.unique)
    elapsed = (datetime.now() - start_time).total_seconds()

    # Summary
    total_items = len(results["all"])
    files_with_items = len([f for f, items in results["by_file"].items() if items])

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total files processed: {len(all_files)}")
    print(f"Files with {content_type}: {files_with_items}")
    print(f"Total {content_type} found: {total_items}")
    print(f"Time elapsed: {elapsed:.2f}s")

    # Per-file breakdown
    if files_with_items <= 20:  # Only show if reasonable number
        print("\nPer-file breakdown:")
        for filepath, items in results["by_file"].items():
            if items:
                print(f"  {Path(filepath).name}: {len(items)} {content_type}")

    # Write output
    if args.output:
        output_path = Path(args.output)
        write_urls_to_file(results["all"], output_path)
        print(f"\n[OK] Wrote {content_type} to: {output_path}")

    if args.csv:
        csv_path = Path(args.csv)
        csv_data = []
        for filepath, items in results["by_file"].items():
            for item in items:
                csv_data.append(
                    {
                        "filename": Path(filepath).name,
                        content_type.rstrip("s"): item,  # 'url' or 'domain'
                        "filepath": str(filepath),
                    }
                )

        write_to_csv(csv_data, csv_path)
        print(f"[OK] Wrote CSV to: {csv_path}")

    if not args.output and not args.csv:
        # No output specified, use default
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_output = f"{content_type}_extract_{timestamp}.txt"
        write_urls_to_file(results["all"], Path(default_output))
        print(f"\n[OK] Wrote {content_type} to: {default_output}")


if __name__ == "__main__":
    main()
