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
import sys
from pathlib import Path
from datetime import datetime

# Import from unified toolkit
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.extractors import extract_from_files, extract_from_directory
from io.writers import write_to_csv, write_urls_to_file


def main():
    parser = argparse.ArgumentParser(
        description='Extract URLs from files with parallel processing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s file.txt -o urls.txt
  %(prog)s folder/ -r -e txt,md,html
  %(prog)s folder/ -r --csv results.csv
  %(prog)s . -r -e txt --domains
        '''
    )

    parser.add_argument(
        'paths',
        nargs='+',
        help='File(s) or folder(s) to process'
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Search folders recursively'
    )

    parser.add_argument(
        '-e', '--extensions',
        type=str,
        help='Comma-separated file extensions (e.g., txt,md,html)'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output text file for URLs (one per line)'
    )

    parser.add_argument(
        '--csv',
        type=str,
        help='Output CSV file with filename, URL columns'
    )

    parser.add_argument(
        '--domains',
        action='store_true',
        help='Extract domains instead of URLs'
    )

    parser.add_argument(
        '--unique',
        action='store_true',
        default=True,
        help='Only unique URLs/domains (default: True)'
    )

    args = parser.parse_args()

    # Parse extensions
    extensions = None
    if args.extensions:
        extensions = [
            ext if ext.startswith('.') else f'.{ext}'
            for ext in args.extensions.split(',')
        ]

    # Determine content type
    content_type = 'domains' if args.domains else 'urls'

    # Process paths
    all_files = []
    for path_str in args.paths:
        path = Path(path_str)

        if not path.exists():
            print(f"⚠️  Path not found: {path_str}")
            continue

        if path.is_file():
            all_files.append(path)
        elif path.is_dir():
            # Use extract_from_directory for folders
            print(f"📁 Scanning directory: {path}")
            result = extract_from_directory(
                path,
                content_type=content_type,
                recursive=args.recursive,
                extensions=extensions
            )

            # Convert to file list format
            for filepath, items in result['by_file'].items():
                all_files.append(Path(filepath))

    if not all_files:
        print("❌ No files found to process")
        sys.exit(1)

    print(f"📋 Found {len(all_files)} file(s) to process")
    print(f"🔍 Extracting {content_type}...\n")

    # Extract from all files
    start_time = datetime.now()
    results = extract_from_files(
        all_files,
        content_type=content_type,
        unique_per_file=True,
        unique_total=args.unique
    )
    elapsed = (datetime.now() - start_time).total_seconds()

    # Summary
    total_items = len(results['all'])
    files_with_items = len([f for f, items in results['by_file'].items() if items])

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total files processed: {len(all_files)}")
    print(f"Files with {content_type}: {files_with_items}")
    print(f"Total {content_type} found: {total_items}")
    print(f"Time elapsed: {elapsed:.2f}s")

    # Per-file breakdown
    if files_with_items <= 20:  # Only show if reasonable number
        print(f"\nPer-file breakdown:")
        for filepath, items in results['by_file'].items():
            if items:
                print(f"  {Path(filepath).name}: {len(items)} {content_type}")

    # Write output
    if args.output:
        output_path = Path(args.output)
        write_urls_to_file(results['all'], output_path)
        print(f"\n✅ Wrote {content_type} to: {output_path}")

    if args.csv:
        csv_path = Path(args.csv)
        csv_data = []
        for filepath, items in results['by_file'].items():
            for item in items:
                csv_data.append({
                    'filename': Path(filepath).name,
                    content_type.rstrip('s'): item,  # 'url' or 'domain'
                    'filepath': str(filepath)
                })

        write_to_csv(csv_data, csv_path)
        print(f"✅ Wrote CSV to: {csv_path}")

    if not args.output and not args.csv:
        # No output specified, use default
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_output = f"{content_type}_extract_{timestamp}.txt"
        write_urls_to_file(results['all'], Path(default_output))
        print(f"\n✅ Wrote {content_type} to: {default_output}")


if __name__ == '__main__':
    main()
