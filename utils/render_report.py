#!/usr/bin/env python3
"""Render a Wisdom Council Value Report (or a single evaluator output) as a
human-friendly visual report: classification badge, value-vector bar chart,
disagreement highlights, executive summary, and recommendations.

Usage:
    python utils/render_report.py < report.json
    python utils/render_report.py report.json

This is the presentation layer only. The machine contract is the JSON itself
(evaluators: schemas/value-output.schema.json; council: the Value Report
structure in skills/wisdom-council/SKILL.md). JSON stays the interchange
format; this script makes it readable by humans.
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
    "current_success": "🟢 Current Success（現在成功）",
    "discovery_target": "🔍 Discovery Target（潜在価値）",
    "trend_object": "🔶 Trend Object（一過性）",
    "low_signal": "⚪ Low Signal（兆候なし）",
    "innovation": "⭐ Innovation（革新）",
}

BAR_WIDTH = 36
LINE = "─" * 54


def bar(score):
    """Fixed 0-100 scale bar. High bars are deliberately rare to earn."""
    if score is None:
        return "░" * BAR_WIDTH
    filled = max(0, min(100, int(score))) * BAR_WIDTH // 100
    return "█" * filled + "░" * (BAR_WIDTH - filled)


def f(v):
    return "—" if v is None else f"{v:3d}"


def header(title):
    print(f"\n┌{'─' * 54}┐")
    print(f"│ {title}")
    print(f"└{'─' * 54}┘")


def render_value_vector(value_vector):
    print("\n【Value Vector】多次元スコア（0-100、厳格スケール）")
    print(f"  {'次元':16s} {'バー':<{BAR_WIDTH}} {'スコア'}")
    any_scored = False
    for key, jp in DIMENSIONS:
        entry = (value_vector or {}).get(key)
        if isinstance(entry, dict):
            mean = entry.get("mean")
            variance = entry.get("variance")
            n = len(entry.get("scores") or [])
        else:
            mean = entry
            variance = None
            n = None
        if mean is None and variance is None:
            continue
        any_scored = True
        extra = ""
        if variance is not None:
            mark = "⚠⚠" if variance > 400 else ("⚠" if variance >= 100 else "")
            extra = f"  n={n} var={variance} {mark}"
        print(f"  {jp + ' (' + key + ')':24s} {bar(mean)} {f(mean)}{extra}")
    if not any_scored:
        print("  （スコアされた次元がない）")


def render_disagreement(value_vector):
    print("\n【不一致（Disagreement）】評価者が割れた次元 = 最も情報量の多い次元")
    found = False
    for key, jp in DIMENSIONS:
        entry = (value_vector or {}).get(key)
        if not isinstance(entry, dict):
            continue
        scores = entry.get("scores") or []
        variance = entry.get("variance")
        if variance is None or len(set(scores)) < 2:
            continue
        found = True
        level = "⚠⚠ 深刻" if variance > 400 else ("⚠ 中程度" if variance >= 100 else "軽度")
        print(f"  [{level}] {jp}({key}): スコア={scores}")
    if not found:
        print("  有意な不一致なし（評価者は概ね一致している）")


def render_contrasts(value_vector):
    """Cross-dimension contrasts: a notably high axis alongside a notably low
    axis is the strongest signal in the vector (e.g. high originality + low
    business = a classic Discovery Target)."""
    scores = {}
    for key, jp in DIMENSIONS:
        entry = (value_vector or {}).get(key)
        mean = entry.get("mean") if isinstance(entry, dict) else entry
        if mean is not None:
            scores[key] = mean
    high = [(k, v) for k, v in scores.items() if v >= 70]
    low = [(k, v) for k, v in scores.items() if v <= 25]
    if high and low:
        print("\n【次元間の対立（Contrast）】高スコア軸と低スコア軸の共存 = 価値の緊張関係")
        for hk, hv in high:
            for lk, lv in low:
                print(f"  ⚡ {DIMENSIONS[[d[0] for d in DIMENSIONS].index(hk)][1]}({hk}) {hv}"
                      f"  vs  {DIMENSIONS[[d[0] for d in DIMENSIONS].index(lk)][1]}({lk}) {lv}")
        print("  → この対立は平均化せず、そのまま保存する（debate-principles.md）")


def render_council(obj):
    header("🧠 Wisdom Council Value Report")
    badge = CLASS_BADGE.get(obj.get("classification"), obj.get("classification", "?"))
    print(f"\n  分類: {badge}")

    current = obj.get("current_value_score")
    hidden = obj.get("hidden_potential_score")
    if current is not None or hidden is not None:
        cbar = bar(current)
        hbar = bar(hidden)
        print(f"\n  現在価値: {f(current)}  {cbar}")
        print(f"  潜在価値: {f(hidden)}  {hbar}")

    print(f"\n  【対象】 {obj.get('content_summary', '—')}")
    print(f"  ドメイン: {obj.get('domain', '—')}  |  招集評価者: {len(obj.get('evaluators_consulted', []) or [])}体")

    render_value_vector(obj.get("value_vector"))
    render_disagreement(obj.get("value_vector"))
    render_contrasts(obj.get("value_vector"))

    if obj.get("executive_summary"):
        print(f"\n【総評】\n  {obj['executive_summary']}")

    if obj.get("consensus_summary"):
        print(f"\n【一致点】\n  {obj['consensus_summary']}")

    recs = obj.get("recommendations") or []
    if recs:
        print("\n【推奨アクション】")
        for i, r in enumerate(recs, 1):
            print(f"  {i}. {r}")

    fb = obj.get("rebuild_feedback")
    if fb:
        print("\n【再作成指令（rebuild_feedback）】作成→評価→再作成ループ用")
        top = fb.get("top_priorities") or []
        if top:
            print("  🎯 最優先:")
            for i, p in enumerate(top, 1):
                print(f"    {i}. {p}")
        changes = fb.get("concrete_changes") or []
        if changes:
            print("  🔧 具体的な変更:")
            for c in changes:
                src = c.get("source_evaluator", "?")
                imp = c.get("expected_impact", "")
                print(f"    · [{src}] {c.get('directive', '')}  ({imp})")
        keep = fb.get("preserve") or []
        if keep:
            print("  🔒 失ってはいけない強み:")
            for k in keep:
                print(f"    · {k}")

    caves = obj.get("caveats") or []
    if caves:
        print("\n【注意点】")
        for c in caves:
            print(f"  · {c}")

    ind = obj.get("individual_reports") or []
    if ind:
        print(f"\n【個別評価】{len(ind)}体の詳細は JSON 側に保存（各評価者の narrative 参照）")


def render_evaluator(obj):
    header(f"🔎 {obj.get('evaluator_name', obj.get('evaluator_id', 'Evaluator'))}")
    badge = CLASS_BADGE.get(obj.get("classification"), obj.get("classification", "?"))
    print(f"\n  分類: {badge}  |  信頼度: {f(obj.get('confidence'))}")
    print(f"\n  総合スコア: {f(obj.get('primary_score'))}  {bar(obj.get('primary_score'))}")
    if obj.get("primary_score_rationale"):
        print(f"  理由: {obj['primary_score_rationale']}")

    ds = obj.get("dimension_scores") or {}
    if ds:
        print("\n【次元別】")
        for name, d in ds.items():
            w = d.get("weight", 0)
            print(f"  {name:24s} {bar(d.get('score'))} {f(d.get('score'))}  (w={w})")
            if d.get("evidence"):
                print(f"    ↳ {d['evidence']}")

    if obj.get("unique_perspective"):
        print(f"\n【この評価者にしか見えないもの】\n  {obj['unique_perspective']}")

    if obj.get("expected_disagreement_points"):
        print("\n【予測される不一致】")
        for p in obj["expected_disagreement_points"]:
            print(f"  · {p.get('evaluator_type')}: {p.get('predicted_stance')}")

    if obj.get("narrative"):
        print(f"\n【ナラティブ】\n  {obj['narrative']}")


def main():
    if len(sys.argv) > 2:
        print("Usage: python utils/render_report.py [report.json]", file=sys.stderr)
        return 2
    try:
        if len(sys.argv) == 2:
            with open(sys.argv[1], encoding="utf-8") as f:
                obj = json.load(f)
        else:
            obj = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"Could not read input: {e}", file=sys.stderr)
        return 2

    if isinstance(obj, dict) and "report_id" in obj:
        render_council(obj)
    elif isinstance(obj, dict) and "evaluator_id" in obj:
        render_evaluator(obj)
    else:
        print("Input is neither a council report (report_id) nor an evaluator output (evaluator_id).",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
