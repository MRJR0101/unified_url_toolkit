"""Smoke tests for unified_url_toolkit import surfaces."""

import importlib


def test_import_package() -> None:
    """Package import should succeed."""
    mod = importlib.import_module("unified_url_toolkit")
    assert mod is not None


def test_import_core_submodule() -> None:
    """Core submodule import should succeed under installed package layout."""
    mod = importlib.import_module("unified_url_toolkit.core.extractors")
    assert mod is not None
