"""Shared locale loader for Wisdom Council Layer utilities.

Loads the appropriate locale JSON file and caches it per language.
Used by render_report.py and compare_reports.py.

Language selection (highest to lowest priority):
    1. Explicit ``lang`` argument passed to ``load_locale()``
    2. ``WISDOM_COUNCIL_LANG`` environment variable
    3. Default: ``"en"``
"""

import json
import os
import sys

_LOCALE_CACHE = {}


def discover_locales():
    """Return the set of available locale codes by scanning locales/*.json."""
    locales_dir = os.path.join(os.path.dirname(__file__), "..", "locales")
    if not os.path.isdir(locales_dir):
        return {"en"}
    return {
        os.path.splitext(f)[0]
        for f in os.listdir(locales_dir)
        if f.endswith(".json")
    }


def load_locale(lang=None):
    """Resolve and load a locale dictionary, cached per language.

    Args:
        lang: ISO 639-1 code (``"en"``, ``"ja"``, ``"zh"``) or ``None``
              to auto-detect from the environment.

    Returns:
        dict: The full locale data (dimensions, classifications, console,
        markdown, compare).
    """
    if lang is None:
        lang = os.environ.get("WISDOM_COUNCIL_LANG", "en")
    lang = lang.lower()

    supported = discover_locales()
    if lang not in supported:
        sys.stderr.write(
            f"Warning: unsupported language '{lang}' "
            f"(available: {sorted(supported)}), falling back to 'en'\n"
        )
        lang = "en"

    if lang not in _LOCALE_CACHE:
        locale_path = os.path.join(
            os.path.dirname(__file__), "..", "locales", f"{lang}.json"
        )
        with open(locale_path, encoding="utf-8") as f:
            _LOCALE_CACHE[lang] = json.load(f)

    return _LOCALE_CACHE[lang]
