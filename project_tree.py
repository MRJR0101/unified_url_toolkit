"""project_tree.py v2 -- AI-context-optimized directory tree scanner.

Prints a clean, paste-ready project tree with smart filtering,
file metadata, and summary stats. Designed to give Claude (or any AI)
instant structural understanding of a codebase.

Usage:
    python project_tree.py                          # current dir, depth 3
    python project_tree.py C:\\Dev\\PROJECTS\\Eye-Witness
    python project_tree.py . --depth 5
    python project_tree.py . --ext .py .ps1         # only these extensions
    python project_tree.py . --all                  # include hidden/noise dirs
    python project_tree.py . --sizes                # show file sizes
    python project_tree.py . --out tree.txt         # write to file
    python project_tree.py . --stats                # append summary stats
    python project_tree.py . --context              # full AI context mode
    python project_tree.py . --json                 # JSON output for tooling
    python project_tree.py . --clipboard            # copy to clipboard

AI Context Mode (--context):
    Combines --sizes --stats and prepends a header block with project
    name, total files, total size, languages detected, and key files
    found (with relative paths). Paste directly into an AI conversation.

Safety:
    - Skips symlinks/junctions (no escape from tree)
    - Skips .git, .venv, __pycache__, node_modules, etc. by default
    - No file modifications -- read-only scanner
    - Handles permission errors gracefully
    - Plain ASCII output -- no Unicode symbols
    - Output path validated (no UNC, no path traversal)

Author: MR / Claude
Version: 2.0
Requires: Python 3.10+
"""

from __future__ import annotations

__version__ = "2.0"

import argparse
import json as json_mod
import sys
from pathlib import Path

# -----------------------------------------------------------------
#  SKIP LISTS
# -----------------------------------------------------------------

SKIP_DIRS: set[str] = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".cache",
    ".tox",
    ".nox",
    ".eggs",
    "node_modules",
    "dist",
    "build",
    ".idea",
    ".vscode",
    ".cursor",
    ".dodkit",
    "htmlcov",
    ".benchmarks",
    "_lint_tmp",
    ".ipynb_checkpoints",
}

SKIP_FILES: set[str] = {
    "Thumbs.db",
    "desktop.ini",
    ".DS_Store",
}

# -----------------------------------------------------------------
#  LANGUAGE DETECTION
# -----------------------------------------------------------------

EXT_TO_LANG: dict[str, str] = {
    ".py": "Python",
    ".ps1": "PowerShell",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "JSX",
    ".tsx": "TSX",
    ".rs": "Rust",
    ".go": "Go",
    ".java": "Java",
    ".cs": "C#",
    ".c": "C",
    ".cpp": "C++",
    ".h": "C/C++ Header",
    ".rb": "Ruby",
    ".sh": "Shell",
    ".bat": "Batch",
    ".cmd": "Batch",
    ".sql": "SQL",
    ".html": "HTML",
    ".css": "CSS",
    ".md": "Markdown",
    ".toml": "TOML",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".json": "JSON",
    ".xml": "XML",
}

KEY_FILES: set[str] = {
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
    "Cargo.toml",
    "package.json",
    "go.mod",
    "Makefile",
    "justfile",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".env.example",
    ".env",
    "LICENSE",
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    ".gitignore",
    ".gitattributes",
    "uv.lock",
}


# -----------------------------------------------------------------
#  SIZE FORMATTING
# -----------------------------------------------------------------

def fmt_size(size_bytes: int) -> str:
    """Format bytes as human-readable string, ASCII only."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


# -----------------------------------------------------------------
#  STATS CONTAINER
# -----------------------------------------------------------------

def _new_stats() -> dict:
    """Create a fresh stats dictionary."""
    return {
        "files": 0,
        "dirs": 0,
        "total_bytes": 0,
        "languages": {},
        "key_files": [],
        "skipped_dirs": 0,
        "errors": 0,
    }


# -----------------------------------------------------------------
#  FILTERED CHILD COUNT
# -----------------------------------------------------------------

def _filtered_child_count(
    directory: Path,
    show_all: bool,
    ext_filter: set[str] | None,
) -> int:
    """Count visible children of a directory (respecting filters).

    This gives an accurate item count at truncation boundaries
    instead of counting noise dirs and hidden files.
    """
    count = 0
    try:
        for entry in directory.iterdir():
            if entry.is_symlink():
                continue
            if entry.is_dir():
                if not show_all and entry.name in SKIP_DIRS:
                    continue
                if not show_all and entry.name.endswith(".egg-info"):
                    continue
                count += 1
            elif entry.is_file():
                if not show_all and entry.name in SKIP_FILES:
                    continue
                if ext_filter and entry.suffix.lower() not in ext_filter:
                    continue
                count += 1
    except (PermissionError, OSError):
        pass
    return count


# -----------------------------------------------------------------
#  TREE WALKER
# -----------------------------------------------------------------

def walk_tree(
    root: Path,
    prefix: str = "",
    max_depth: int = 3,
    current_depth: int = 0,
    show_all: bool = False,
    show_sizes: bool = False,
    ext_filter: set[str] | None = None,
    lines: list[str] | None = None,
    stats: dict | None = None,
    tree_root: Path | None = None,
) -> tuple[list[str], dict]:
    """Recursively walk directory tree and collect output lines.

    Returns (lines, stats) tuple. Stats are accumulated internally
    and returned -- callers should NOT reuse a stats dict across
    multiple walk_tree calls unless accumulation is intended.
    """
    if lines is None:
        lines = []
    if stats is None:
        stats = _new_stats()
    if tree_root is None:
        tree_root = root

    if current_depth > max_depth:
        return lines, stats

    try:
        entries = sorted(
            root.iterdir(),
            key=lambda p: (p.is_file(), p.name.lower()),
        )
    except PermissionError:
        lines.append(f"{prefix}[ACCESS DENIED]")
        stats["errors"] += 1
        return lines, stats
    except OSError as exc:
        lines.append(f"{prefix}[ERROR: {exc}]")
        stats["errors"] += 1
        return lines, stats

    # Filter entries
    visible: list[Path] = []
    for entry in entries:
        # Skip symlinks/junctions
        if entry.is_symlink():
            continue

        if entry.is_dir():
            if not show_all and entry.name in SKIP_DIRS:
                stats["skipped_dirs"] += 1
                continue
            if not show_all and entry.name.endswith(".egg-info"):
                stats["skipped_dirs"] += 1
                continue
            visible.append(entry)
        elif entry.is_file():
            if not show_all and entry.name in SKIP_FILES:
                continue
            if ext_filter and entry.suffix.lower() not in ext_filter:
                continue
            visible.append(entry)

    for index, entry in enumerate(visible):
        is_last = index == len(visible) - 1
        connector = "+-- " if is_last else "|-- "
        extension_prefix = "    " if is_last else "|   "

        if entry.is_dir():
            dir_label = f"{entry.name}/"
            if current_depth >= max_depth:
                child_count = _filtered_child_count(
                    entry, show_all, ext_filter,
                )
                dir_label += f"  ({child_count} items)"

            lines.append(f"{prefix}{connector}{dir_label}")
            stats["dirs"] += 1

            if current_depth < max_depth:
                walk_tree(
                    entry,
                    prefix + extension_prefix,
                    max_depth,
                    current_depth + 1,
                    show_all,
                    show_sizes,
                    ext_filter,
                    lines,
                    stats,
                    tree_root,
                )
        else:
            try:
                size = entry.stat().st_size
            except OSError:
                size = 0

            stats["files"] += 1
            stats["total_bytes"] += size

            # Track languages
            ext = entry.suffix.lower()
            if ext in EXT_TO_LANG:
                lang = EXT_TO_LANG[ext]
                stats["languages"][lang] = stats["languages"].get(lang, 0) + 1

            # Track key files with relative paths
            if entry.name in KEY_FILES:
                try:
                    rel_path = str(entry.relative_to(tree_root))
                except ValueError:
                    rel_path = entry.name
                stats["key_files"].append(rel_path)

            # Build label
            label = entry.name
            if show_sizes:
                label += f"  ({fmt_size(size)})"

            lines.append(f"{prefix}{connector}{label}")

    return lines, stats


# -----------------------------------------------------------------
#  CONTEXT HEADER
# -----------------------------------------------------------------

def build_context_header(root: Path, stats: dict) -> list[str]:
    """Build an AI-friendly context header block."""
    header = []
    header.append("=" * 60)
    header.append(f"PROJECT: {root.name}")
    header.append(f"PATH:    {root}")
    header.append(f"FILES:   {stats['files']}  |  DIRS: {stats['dirs']}")
    header.append(f"SIZE:    {fmt_size(stats['total_bytes'])}")

    if stats["languages"]:
        sorted_langs = sorted(
            stats["languages"].items(), key=lambda x: -x[1]
        )
        lang_str = ", ".join(
            f"{name} ({count})" for name, count in sorted_langs[:8]
        )
        header.append(f"LANGS:   {lang_str}")

    if stats["key_files"]:
        unique_keys = sorted(set(stats["key_files"]))
        header.append(f"KEY:     {', '.join(unique_keys)}")

    if stats["skipped_dirs"] > 0:
        header.append(
            f"SKIPPED: {stats['skipped_dirs']} noise dirs "
            f"(.venv, __pycache__, etc.)"
        )

    if stats["errors"] > 0:
        header.append(f"ERRORS:  {stats['errors']} access/read failures")

    header.append("=" * 60)
    return header


# -----------------------------------------------------------------
#  STATS FOOTER
# -----------------------------------------------------------------

def build_stats_footer(stats: dict) -> list[str]:
    """Build a summary stats block."""
    footer = []
    footer.append("")
    footer.append("-" * 40)
    footer.append(
        f"Files: {stats['files']}  |  "
        f"Dirs: {stats['dirs']}  |  "
        f"Size: {fmt_size(stats['total_bytes'])}"
    )

    if stats["languages"]:
        sorted_langs = sorted(
            stats["languages"].items(), key=lambda x: -x[1]
        )
        lang_parts = [f"{name}: {count}" for name, count in sorted_langs]
        footer.append(f"Languages: {', '.join(lang_parts)}")

    if stats["skipped_dirs"] > 0:
        footer.append(f"Skipped: {stats['skipped_dirs']} noise directories")

    footer.append("-" * 40)
    return footer


# -----------------------------------------------------------------
#  JSON OUTPUT
# -----------------------------------------------------------------

def build_json_output(root: Path, stats: dict, tree_lines: list[str]) -> str:
    """Build JSON output with metadata and flat file list."""
    output = {
        "version": __version__,
        "root": str(root),
        "project": root.name,
        "stats": {
            "files": stats["files"],
            "dirs": stats["dirs"],
            "total_bytes": stats["total_bytes"],
            "total_size": fmt_size(stats["total_bytes"]),
            "languages": stats["languages"],
            "key_files": sorted(set(stats["key_files"])),
            "skipped_dirs": stats["skipped_dirs"],
            "errors": stats["errors"],
        },
        "tree": tree_lines,
    }
    return json_mod.dumps(output, indent=2)


# -----------------------------------------------------------------
#  OUTPUT PATH VALIDATION
# -----------------------------------------------------------------

def validate_out_path(path_str: str) -> Path | None:
    """Validate output file path. Returns Path or None on failure.

    Rejects UNC paths and path traversal sequences.
    """
    if path_str.startswith("\\\\"):
        print("ERROR: UNC paths not allowed for --out", file=sys.stderr)
        return None
    if ".." in path_str:
        print(
            "ERROR: Path traversal (..) not allowed in --out",
            file=sys.stderr,
        )
        return None

    out = Path(path_str)

    # Don't overwrite directories
    if out.is_dir():
        print(f"ERROR: --out target is a directory: {out}", file=sys.stderr)
        return None

    return out


# -----------------------------------------------------------------
#  CLIPBOARD
# -----------------------------------------------------------------

def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard. Returns True on success."""
    try:
        import subprocess
        if sys.platform == "win32":
            subprocess.run(
                ["clip.exe"],
                input=text.encode("utf-8"),
                check=True,
                timeout=5,
            )
            return True
        elif sys.platform == "darwin":
            subprocess.run(
                ["pbcopy"],
                input=text.encode("utf-8"),
                check=True,
                timeout=5,
            )
            return True
        else:
            subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=text.encode("utf-8"),
                check=True,
                timeout=5,
            )
            return True
    except Exception:
        return False


# -----------------------------------------------------------------
#  MAIN
# -----------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="AI-context-optimized project tree scanner.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Root directory to scan (default: current dir)",
    )
    parser.add_argument(
        "--depth", "-d",
        type=int,
        default=3,
        help="Max depth to recurse (default: 3)",
    )
    parser.add_argument(
        "--ext", "-e",
        nargs="+",
        default=None,
        help="Only show files with these extensions (e.g., .py .ps1)",
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        dest="show_all",
        help="Show hidden/noise directories too",
    )
    parser.add_argument(
        "--sizes", "-s",
        action="store_true",
        help="Show file sizes",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Append summary statistics",
    )
    parser.add_argument(
        "--context", "-c",
        action="store_true",
        help="Full AI context mode (header + sizes + stats)",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        dest="json_output",
        help="JSON output with metadata and tree",
    )
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="Copy output to clipboard",
    )
    parser.add_argument(
        "--out", "-o",
        type=str,
        default=None,
        help="Write output to file instead of stdout",
    )
    parser.add_argument(
        "--version", "-V",
        action="version",
        version=f"project_tree {__version__}",
    )
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: Not a directory: {root}", file=sys.stderr)
        return 1

    # Context mode enables everything
    if args.context:
        args.sizes = True
        args.stats = True

    # Normalize extension filter
    ext_filter: set[str] | None = None
    if args.ext:
        ext_filter = set()
        for e in args.ext:
            if not e.startswith("."):
                e = "." + e
            ext_filter.add(e.lower())

    # Validate output path early
    out_path: Path | None = None
    if args.out:
        out_path = validate_out_path(args.out)
        if out_path is None:
            return 1

    # Walk the tree
    tree_lines = [f"{root.name}/"]
    tree_lines, stats = walk_tree(
        root,
        prefix="",
        max_depth=args.depth,
        current_depth=0,
        show_all=args.show_all,
        show_sizes=args.sizes,
        ext_filter=ext_filter,
        lines=tree_lines,
        tree_root=root,
    )

    # Assemble output
    if args.json_output:
        output = build_json_output(root, stats, tree_lines)
    else:
        output_lines: list[str] = []

        if args.context:
            output_lines.extend(build_context_header(root, stats))
            output_lines.append("")

        output_lines.extend(tree_lines)

        if args.stats:
            output_lines.extend(build_stats_footer(stats))

        output = "\n".join(output_lines) + "\n"

    # Deliver output
    if out_path:
        out_path.write_text(output, encoding="utf-8")
        print(f"Written to: {out_path}")
    else:
        print(output, end="")

    if args.clipboard:
        if copy_to_clipboard(output):
            print("(copied to clipboard)", file=sys.stderr)
        else:
            print("(clipboard copy failed)", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
