#!/usr/bin/env python3
"""Compare two Wisdom Council Value Reports (before / after a revision) and
show the improvement per dimension. This powers the create → evaluate →
recreate loop: run the council on v1, revise per the creation
skill's directives, run the council on v2, then compare.

Usage:
    python utils/compare_reports.py before.json after.json
    python utils/compare_reports.py --before before.json --after after.json
    python utils/compare_reports.py --lang ja before.json after.json

Language selection:
    --lang en|ja|zh          Explicit language (highest priority)
    WISDOM_COUNCIL_LANG env  Fallback environment variable
    (default: en)

Exit codes:
    0  compared (improvement or not — the report says which)
    1  usage / parse error
"""

import json
import os
import sys

# Ensure utils/ is on the path so `from _locale import ...` works
# regardless of the caller's working directory.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from locale_loader import load_locale  # noqa: E402

# --- Locale-driven globals ---

_L = None
DIMENSIONS = []
CLASS_BADGE = {}
ARROWS = {"up": "▲", "down": "▼", "same": "—"}


def _set_locale(lang=None):
    global _L, DIMENSIONS, CLASS_BADGE
    _L = load_locale(lang)
    _DIMENSION_KEYS = [
        "originality", "quality", "aesthetic", "emotional_impact",
        "future_potential", "business_value", "scientific_novelty",
        "philosophical_depth", "meaning",
    ]
    DIMENSIONS[:] = [(k, _L["dimensions"][k]) for k in _DIMENSION_KEYS]
    CLASS_BADGE.clear()
    CLASS_BADGE.update(_L["classifications"])


def _cmp(key, **kwargs):
    s = _L["compare"].get(key, key)
    return s.format(**kwargs) if kwargs else s


# Populate defaults at import time
_set_locale("en")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dim_mean(report, key):
    vec = report.get("value_vector") or {}
    entry = vec.get(key)
    if isinstance(entry, dict):
        return entry.get("mean")
    return entry


def main():
    global _L, DIMENSIONS, CLASS_BADGE

    # Parse arguments (support --lang)
    raw_args = sys.argv[1:]
    lang = None
    positional = []
    i = 0
    while i < len(raw_args):
        a = raw_args[i]
        if a == "--lang" and i + 1 < len(raw_args):
            lang = raw_args[i + 1]
            i += 2
        elif a in ("--before", "--after"):
            positional.append(a)
            if i + 1 < len(raw_args):
                positional.append(raw_args[i + 1])
                i += 2
            else:
                i += 1
        elif a in ("-h", "--help"):
            print("Usage: python utils/compare_reports.py [--lang en|ja|zh] before.json after.json",
                  file=sys.stderr)
            print("       python utils/compare_reports.py [--lang en|ja|zh] --before before.json --after after.json",
                  file=sys.stderr)
            print("       WISDOM_COUNCIL_LANG env var is used when --lang is omitted (default: en)",
                  file=sys.stderr)
            return 0
        else:
            positional.append(a)
            i += 1

    _set_locale(lang)

    # Parse positional / named arguments
    if len(positional) == 2 and positional[0] not in ("--before", "--after"):
        before_path, after_path = positional[0], positional[1]
    elif (len(positional) == 4 and positional[0] == "--before"
          and positional[2] == "--after"):
        before_path, after_path = positional[1], positional[3]
    else:
        print("Usage: python utils/compare_reports.py [--lang en|ja|zh] before.json after.json",
              file=sys.stderr)
        return 1

    try:
        before, after = load(before_path), load(after_path)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Could not read reports: {e}", file=sys.stderr)
        return 1

    print("┌──────────────────────────────────────────────────────┐")
    print(f"│ 🔄 {_cmp('comparison_header')}")
    print("└──────────────────────────────────────────────────────┘")

    print(f"\n  {_cmp('classification_change')}:")
    bcls = CLASS_BADGE.get(before.get("classification"), before.get("classification", "?"))
    acls = CLASS_BADGE.get(after.get("classification"), after.get("classification", "?"))
    print(f"    {_cmp('before')}: {bcls}")
    print(f"    {_cmp('after')}:  {acls}")

    print(f"\n{_cmp('dimensional_improvement')}")
    # Use locale dimension labels for table header
    dim_label = _L["console"]["dimension"]
    score_label = _L["console"]["score"]
    print(f"  {dim_label:22s} {'before':>7s} {'after':>6s} {'Δ':>5s}")
    total = 0
    counted = 0
    changed = []
    for key, jp in DIMENSIONS:
        b = dim_mean(before, key)
        a = dim_mean(after, key)
        if b is None and a is None:
            continue
        if a is not None and b is not None:
            delta = a - b
            total += delta
            counted += 1
            if delta != 0:
                changed.append((jp, b, a, delta))
            arrow = ARROWS["up"] if delta > 0 else (ARROWS["down"] if delta < 0 else ARROWS["same"])
            b_s = f"{b:3d}" if b is not None else "  —"
            a_s = f"{a:3d}" if a is not None else "  —"
            d_s = f"{delta:+3d}" if b is not None and a is not None else "   "
            print(f"  {jp + ' (' + key + ')':28s} {b_s:>5s} {a_s:>5s} {arrow}{d_s}")
        else:
            print(f"  {jp + ' (' + key + ')':28s}   {'—' if b is None else b} -> {'—' if a is None else a}  {_cmp('one_sided_only')}")

    if counted:
        avg = total / counted
        print(f"\n  {_cmp('average_change', counted=counted)}: {total:+d} / {counted} = {avg:+.1f}")

    print(f"\n{_cmp('main_changes')}")
    if not changed:
        print(f"  {_cmp('no_significant_changes')}")
    else:
        changed_sorted = sorted(changed, key=lambda c: -abs(c[3]))
        for jp, b, a, d in changed_sorted[:6]:
            arrow = ARROWS["up"] if d > 0 else ARROWS["down"]
            print(f"  {arrow} {jp}: {b} → {a} ({d:+d})")

    print(f"\n  ※ {_cmp('raw_values_note')}")
    print(f"  ※ {_cmp('creation_skill_note')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
