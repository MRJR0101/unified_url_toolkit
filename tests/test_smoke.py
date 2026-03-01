"""Smoke tests for unified_url_toolkit.

Verifies that all modules can be imported without errors.
"""

import importlib.util
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _import_from_file(name, filepath):
    """Import a module by file path."""
    spec = importlib.util.spec_from_file_location(name, filepath)
    assert spec is not None, f"Could not load spec for {filepath}"
    assert spec.loader is not None, f"No loader for {filepath}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_import_package():
    """src/unified_url_toolkit/ package imports cleanly."""
    src_init = PROJECT_ROOT / "src" / "unified_url_toolkit" / "__init__.py"
    mod = _import_from_file("unified_url_toolkit", src_init)
    assert mod is not None
