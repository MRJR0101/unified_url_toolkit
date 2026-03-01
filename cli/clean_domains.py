#!/usr/bin/env python3
"""
Clean and normalize domains from a file.

BEFORE: 42+ lines with embedded logic
AFTER: 8 lines of business logic + argparse

Replaces:
- CleanDomains/clean_domains.py
- CleanDomainsv2/clean_domains_v2.py
- cleanup_domains/
"""

import argparse
import sys
from pathlib import Path

# Import from unified toolkit
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.normalizers import clean_domain_list
from io.readers import read_urls_from_file
from io.writers import write_domains_to_file


def main():
    parser = argparse.ArgumentParser(
        description='Clean and normalize domains from a file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s raw_domains.txt -o cleaned.txt
  %(prog)s input.txt --strip-www --sort
  %(prog)s domains.txt -o output.txt --strip-subdomain
        '''
    )

    parser.add_argument(
        'input',
        type=str,
        nargs='?',
        default='raw_domains.txt',
        help='Input file with domains/URLs (default: raw_domains.txt)'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default='domains.txt',
        help='Output file for cleaned domains (default: domains.txt)'
    )

    parser.add_argument(
        '--strip-www',
        action='store_true',
        help='Remove www. prefix from domains'
    )

    parser.add_argument(
        '--strip-subdomain',
        action='store_true',
        help='Keep only base domain (remove all subdomains)'
    )

    parser.add_argument(
        '--sort',
        action='store_true',
        help='Sort domains alphabetically'
    )

    parser.add_argument(
        '--keep-duplicates',
        action='store_true',
        help='Keep duplicate domains (default: remove)'
    )

    args = parser.parse_args()

    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_path.resolve()}")

        # Helpful hints
        here = Path('.').resolve()
        candidates = list(here.glob('*.txt'))
        if candidates:
            print("[HINT] Text files in current folder:")
            for c in candidates[:10]:
                print(f"  - {c.name}")

        print(f"\nFix by either:")
        print(f"  - placing your file at {input_path.resolve()}")
        print(f"  - OR passing the correct path:")
        print(f"    python {Path(__file__).name} \"C:\\path\\to\\yourfile.txt\"")
        sys.exit(2)

    # =========================================================================
    # CORE BUSINESS LOGIC - Just 8 lines thanks to unified modules!
    # =========================================================================

    # Read domains/URLs from file
    raw_items = read_urls_from_file(input_path)

    # Clean and normalize
    cleaned = clean_domain_list(
        raw_items,
        strip_www=args.strip_www,
        strip_subdomain=args.strip_subdomain,
        remove_duplicates=not args.keep_duplicates,
        sort=args.sort
    )

    # Write output
    output_path = Path(args.output)
    count = write_domains_to_file(cleaned, output_path, deduplicate=False, sort=False)

    # Report results
    print(f"[OK] Wrote {output_path.resolve()}")
    print(f"     Kept: {count} domains | Discarded: {len(raw_items) - count}")


if __name__ == '__main__':
    main()
