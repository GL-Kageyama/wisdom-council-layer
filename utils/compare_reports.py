#!/usr/bin/env python3
"""Compare two Wisdom Council Value Reports (before / after a revision) and
show the improvement per dimension. This powers the create → evaluate →
recreate loop: run the council on v1, revise per the downstream
recreation skill's directives, run the council on v2, then compare.

Usage:
    python utils/compare_reports.py before.json after.json
    python utils/compare_reports.py --before before.json --after after.json

Exit codes:
    0  compared (improvement or not — the report says which)
    1  usage / parse error
"""

import json
import sys

DIMENSIONS = [
    ("originality", "独創性"),
    ("quality", "品質"),
    ("aesthetic", "美"),
    ("emotional_impact", "感情"),
    ("future_potential", "未来"),
    ("business_value", "ビジネス"),
    ("scientific_novelty", "科学"),
    ("philosophical_depth", "哲学"),
    ("meaning", "意味"),
]

CLASS_BADGE = {
    "current_success": "🟢 Current Success",
    "discovery_target": "🔍 Discovery Target",
    "trend_object": "🔶 Trend Object",
    "low_signal": "⚪ Low Signal",
    "innovation": "⭐ Innovation",
}

ARROWS = {"up": "▲", "down": "▼", "same": "—"}


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
    if len(sys.argv) == 3:
        before_path, after_path = sys.argv[1], sys.argv[2]
    elif len(sys.argv) == 5 and sys.argv[1] == "--before" and sys.argv[3] == "--after":
        before_path, after_path = sys.argv[2], sys.argv[4]
    else:
        print("Usage: python utils/compare_reports.py before.json after.json", file=sys.stderr)
        return 1

    try:
        before, after = load(before_path), load(after_path)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Could not read reports: {e}", file=sys.stderr)
        return 1

    print("┌──────────────────────────────────────────────────────┐")
    print("│ 🔄 作成 → 評価 → 再作成 ループの比較")
    print("└──────────────────────────────────────────────────────┘")

    print("\n  分類の変化:")
    bcls = CLASS_BADGE.get(before.get("classification"), before.get("classification", "?"))
    acls = CLASS_BADGE.get(after.get("classification"), after.get("classification", "?"))
    print(f"    before: {bcls}")
    print(f"    after:  {acls}")

    print("\n【次元別の改善】")
    print(f"  {'次元':22s} {'before':>7s} {'after':>6s} {'Δ':>5s}")
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
            print(f"  {jp + ' (' + key + ')':28s}   {'—' if b is None else b} -> {'—' if a is None else a}  (片側のみ)")

    if counted:
        avg = total / counted
        print(f"\n  平均変化（評価された{counted}次元）: {total:+d} / {counted} = {avg:+.1f}")

    print("\n【主な変化】")
    if not changed:
        print("  有意な次元変化なし")
    else:
        changed_sorted = sorted(changed, key=lambda c: -abs(c[3]))
        for jp, b, a, d in changed_sorted[:6]:
            arrow = ARROWS["up"] if d > 0 else ARROWS["down"]
            print(f"  {arrow} {jp}: {b} → {a} ({d:+d})")

    print("\n  ※ 全次元の生値は JSON を参照。平均だけで判断せず、分散と不一致も見ること。")
    print("  ※ 下流の再作成スキルは individual_reports の weaknesses / improvement_suggestions を入力に使う。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
