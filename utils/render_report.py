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
    if v is None:
        return "—"
    if isinstance(v, int):
        return f"{v:3d}"
    if isinstance(v, float):
        # 厳格スコアの平均は小数になりうる。整数値なら従来の整数表記に揃える。
        return f"{int(v):3d}" if v == int(v) else f"{v:6.2f}"
    return str(v)


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


EVAL_TO_DIM = {
    "originality": "originality",
    "anti-generic-filter": "quality",
    "aesthetic-critic": "aesthetic",
    "emotional-impact": "emotional_impact",
    "future-potential": "future_potential",
    "business-value": "business_value",
    "scientific-novelty": "scientific_novelty",
    "philosophical-evaluator": "philosophical_depth",
    "quality-evaluator": "quality",
    "meaning-evaluator": "meaning",
}


def excluded_ids(obj):
    """Set of dimension keys excluded from aggregation (exceptional feature).
    Normalizes evaluator_id (kebab-case) to value-vector dimension keys."""
    out = set()
    for e in (obj.get("excluded_evaluators") or []):
        eid = e.get("evaluator_id") if isinstance(e, dict) else e
        out.add(EVAL_TO_DIM.get(eid, eid))
    return out


def contrast_pairs(value_vector, excluded=(), limit=4):
    """Cross-dimension contrasts (high axis >= 70 vs low axis <= 25), skipping
    excluded evaluators, most striking first. A high+low coexistence is the
    strongest signal in the vector (e.g. high originality + low business)."""
    scores = {}
    for key, jp in DIMENSIONS:
        if key in excluded:
            continue
        entry = (value_vector or {}).get(key)
        mean = entry.get("mean") if isinstance(entry, dict) else entry
        if mean is not None:
            scores[key] = mean
    pairs = []
    for hk, hv in scores.items():
        if hv < 70:
            continue
        for lk, lv in scores.items():
            if lk == hk or lv > 25:
                continue
            pairs.append((hk, hv, lk, lv))
    pairs.sort(key=lambda p: -(p[1] - p[3]))
    return pairs[:limit]


def render_contrasts(value_vector, excluded=()):
    pairs = contrast_pairs(value_vector, excluded)
    if pairs:
        jp = {d[0]: d[1] for d in DIMENSIONS}
        print("\n【次元間の対立（Contrast）】高スコア軸と低スコア軸の共存 = 価値の緊張関係")
        for hk, hv, lk, lv in pairs:
            print(f"  ⚡ {jp[hk]}({hk}) {hv}  vs  {jp[lk]}({lk}) {lv}")
        print("  → この対立は平均化せず、そのまま保存する（debate-principles.md）")


def render_council(obj, show_ind=False):
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

    excl = obj.get("excluded_evaluators") or []
    if excl:
        print("  ⏭️ 除外（例外的機能）: 集計から除外した評価者")
        for e in excl:
            eid = e.get("evaluator_id") if isinstance(e, dict) else e
            reason = e.get("reason", "") if isinstance(e, dict) else ""
            print(f"    · {eid}: {reason or '次元が不適合'}")

    render_value_vector(obj.get("value_vector"))
    render_disagreement(obj.get("value_vector"))
    render_contrasts(obj.get("value_vector"), excluded_ids(obj))

    if obj.get("executive_summary"):
        print(f"\n【総評】\n  {obj['executive_summary']}")

    if obj.get("consensus_summary"):
        print(f"\n【一致点】\n  {obj['consensus_summary']}")

    recs = obj.get("recommendations") or []
    if recs:
        print("\n【推奨アクション】")
        for i, r in enumerate(recs, 1):
            print(f"  {i}. {r}")

    rd = obj.get("revision_direction")
    if rd:
        mode = rd.get("iteration") or "confirm"
        label = "逐次確認（confirm）" if mode == "confirm" else "方向固定（persistent）"
        print(f"\n🔧 【次回の修正方向（revision_direction）】モード: {label}")
        if rd.get("statement"):
            print(f"  方向: {rd['statement']}")
        axis = rd.get("axis") or []
        if axis:
            print(f"  上げる/変える: {', '.join(axis)}")
        keep = rd.get("preserve") or []
        if keep:
            print(f"  維持すべき: {', '.join(keep)}")

    caves = obj.get("caveats") or []
    if caves:
        print("\n【注意点】")
        for c in caves:
            print(f"  · {c}")

    ind = obj.get("individual_reports") or []
    if ind:
        if show_ind:
            print(f"\n【個別評価】{len(ind)}体")
            for r in ind:
                render_evaluator(r)
        else:
            print(f"\n【個別評価】{len(ind)}体の詳細は JSON 側に保存（--individuals で全レポート表示）")


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
            score, w, evidence = _ds_norm(d)
            print(f"  {name:24s} {bar(score)} {f(score)}  (w={w})")
            if evidence:
                print(f"    ↳ {evidence}")

    if obj.get("unique_perspective"):
        print(f"\n【この評価者にしか見えないもの】\n  {obj['unique_perspective']}")

    if obj.get("expected_disagreement_points"):
        print("\n【予測される不一致】")
        for p in obj["expected_disagreement_points"]:
            etype, stance = _edp_norm(p)
            print(f"  · {etype}: {stance}")

    if obj.get("narrative"):
        print(f"\n【ナラティブ】\n  {obj['narrative']}")


def md_bar(score, width=20):
    """Compact bar for Markdown table cells."""
    if score is None:
        return "—"
    filled = max(0, min(100, int(score))) * width // 100
    return "█" * filled + "░" * (width - filled)


def md_val(v):
    return "—" if v is None else f"{v}"


def _ds_norm(d):
    """dimension_scores の値は評価者により int（スコア直接）と
    dict（score/weight/evidence）が混在する。両形式を正規化する。"""
    if isinstance(d, dict):
        return d.get("score"), d.get("weight", 0), d.get("evidence")
    return d, 0, None


def _edp_norm(p):
    """expected_disagreement_points の要素は評価者により dict
    （evaluator_type/predicted_stance）と文字列（"Evaluator: stance"）
    が混在する。両形式を (評価者, 主張) に正規化する。"""
    if isinstance(p, dict):
        return p.get("evaluator_type"), p.get("predicted_stance")
    if isinstance(p, str) and ":" in p:
        etype, stance = p.split(":", 1)
        return etype.strip(), stance.strip()
    return None, p


def render_council_md(obj, show_ind=False):
    """Readable Markdown report (suitable for .md files / GitHub preview)."""
    L = []
    L.append("# 🧠 Wisdom Council Value Report")
    L.append("")
    L.append(f"> **分類**: {CLASS_BADGE.get(obj.get('classification'), obj.get('classification', '?'))}")
    L.append("")

    # Summary table
    L.append("## 📋 概要")
    L.append("")
    L.append("| 項目 | 値 |")
    L.append("|------|-----|")
    L.append(f"| 対象 | {obj.get('content_summary', '—')} |")
    L.append(f"| ドメイン | {obj.get('domain', '—')} |")
    L.append(f"| 招集評価者 | {len(obj.get('evaluators_consulted', []) or [])}体 |")
    L.append(f"| 現在価値 | {md_val(obj.get('current_value_score'))} |")
    L.append(f"| 潜在価値 | {md_val(obj.get('hidden_potential_score'))} |")
    L.append("")

    # Excluded evaluators
    excl = obj.get("excluded_evaluators") or []
    if excl:
        L.append("## ⏭️ 除外した評価者（例外的機能）")
        L.append("")
        L.append("| 評価者 | 理由 |")
        L.append("|--------|------|")
        for e in excl:
            eid = e.get("evaluator_id") if isinstance(e, dict) else e
            reason = e.get("reason", "") if isinstance(e, dict) else ""
            L.append(f"| `{eid}` | {reason or '次元が不適合'} |")
        L.append("")

    # Value vector
    L.append("## 📊 Value Vector")
    L.append("")
    L.append("| 次元 | スコア | 分散 | バー |")
    L.append("|------|:------:|:----:|------|")
    vec = obj.get("value_vector") or {}
    any_scored = False
    for key, jp in DIMENSIONS:
        entry = vec.get(key)
        if isinstance(entry, dict):
            mean = entry.get("mean")
            variance = entry.get("variance")
            scores = entry.get("scores") or []
        else:
            mean = entry
            variance = None
            scores = []
        if mean is None and variance is None:
            continue
        any_scored = True
        v = f"{variance}" if variance is not None else "—"
        n = f" (n={len(scores)})" if scores else ""
        L.append(f"| {jp} (`{key}`) | {md_val(mean)} | {v}{n} | `{md_bar(mean)}` |")
    if not any_scored:
        L.append("| — | — | — | スコアされた次元なし |")
    L.append("")

    # Disagreement
    L.append("## 🔀 不一致（Disagreement）")
    L.append("")
    found = False
    for key, jp in DIMENSIONS:
        entry = vec.get(key)
        if not isinstance(entry, dict):
            continue
        scores = entry.get("scores") or []
        variance = entry.get("variance")
        if variance is None or len(set(scores)) < 2:
            continue
        found = True
        level = "⚠⚠ 深刻" if variance > 400 else ("⚠ 中程度" if variance >= 100 else "軽度")
        L.append(f"- **[{level}]** {jp}（`{key}`）: スコア = {scores}")
    if not found:
        L.append("- 有意な不一致なし（評価者は概ね一致）")
    L.append("")

    # Contrasts (skip excluded evaluators, show most striking)
    pairs = contrast_pairs(vec, excluded_ids(obj))
    if pairs:
        L.append("## ⚡ 次元間の対立（Contrast）")
        L.append("")
        L.append("| 高スコア軸 | 低スコア軸 |")
        L.append("|-----------|-----------|")
        idx = {d[0]: d[1] for d in DIMENSIONS}
        for hk, hv, lk, lv in pairs:
            L.append(f"| {idx[hk]}（`{hk}`）{hv} | {idx[lk]}（`{lk}`）{lv} |")
        L.append("")
        L.append("> この対立は平均化せず保存する（debate-principles.md）")
        L.append("")

    if obj.get("executive_summary"):
        L.append("## 📝 総評")
        L.append("")
        L.append(f"> {obj['executive_summary']}")
        L.append("")

    if obj.get("consensus_summary"):
        L.append("## 🤝 一致点")
        L.append("")
        L.append(obj["consensus_summary"])
        L.append("")

    recs = obj.get("recommendations") or []
    if recs:
        L.append("## 🎯 推奨アクション")
        L.append("")
        for i, r in enumerate(recs, 1):
            L.append(f"{i}. {r}")
        L.append("")

    rd = obj.get("revision_direction")
    if rd:
        mode = rd.get("iteration") or "confirm"
        label = "逐次確認（confirm）" if mode == "confirm" else "方向固定（persistent）"
        L.append(f"## 🔧 次回の修正方向（`{label}`）")
        L.append("")
        if rd.get("statement"):
            L.append(f"> {rd['statement']}")
            L.append("")
        if rd.get("axis"):
            L.append("**上げる／変える**:")
            for a in rd["axis"]:
                L.append(f"- {a}")
            L.append("")
        if rd.get("preserve"):
            L.append("**維持すべき**:")
            for p in rd["preserve"]:
                L.append(f"- {p}")
            L.append("")

    caves = obj.get("caveats") or []
    if caves:
        L.append("## ⚠️ 注意点")
        L.append("")
        for c in caves:
            L.append(f"- {c}")
        L.append("")

    ind = obj.get("individual_reports") or []
    if ind:
        if show_ind:
            L.append("## 📄 個別評価（全レポート）")
            L.append("")
            for r in ind:
                L.append("")
                L.append(render_evaluator_md(r))
        else:
            L.append("## 📄 個別評価の素材")
            L.append("")
            L.append("作成スキルは、各評価者の `weaknesses`・`improvement_suggestions`・`expected_disagreement_points` を入力に使う。生データは JSON（`individual_reports`）に保存。`--individuals` で全レポートを表示。")
            L.append("")

    return "\n".join(L)


def render_evaluator_md(obj):
    L = []
    L.append(f"# 🔎 {obj.get('evaluator_name', obj.get('evaluator_id', 'Evaluator'))}")
    L.append("")
    L.append(f"> **分類**: {CLASS_BADGE.get(obj.get('classification'), obj.get('classification', '?'))}  |  信頼度: {md_val(obj.get('confidence'))}")
    L.append("")
    L.append(f"**総合スコア**: {md_val(obj.get('primary_score'))}  `{md_bar(obj.get('primary_score'))}`")
    if obj.get("primary_score_rationale"):
        L.append("")
        L.append(f"*{obj['primary_score_rationale']}*")
    L.append("")
    ds = obj.get("dimension_scores") or {}
    if ds:
        L.append("## 次元別")
        L.append("")
        L.append("| 次元 | スコア | 重み |")
        L.append("|------|:------:|:----:|")
        for name, d in ds.items():
            score, w, evidence = _ds_norm(d)
            L.append(f"| {name} | {md_val(score)} | {w if w else '—'} |")
            if evidence:
                L.append(f"| ↳ {evidence} | | |")
        L.append("")
    if obj.get("unique_perspective"):
        L.append(f"## 👁️ この評価者にしか見えないもの")
        L.append("")
        L.append(obj["unique_perspective"])
        L.append("")
    if obj.get("expected_disagreement_points"):
        L.append("## 🔮 予測される不一致")
        L.append("")
        for p in obj["expected_disagreement_points"]:
            etype, stance = _edp_norm(p)
            L.append(f"- **{etype}**: {stance}")
        L.append("")
    if obj.get("narrative"):
        L.append("## 📖 ナラティブ")
        L.append("")
        L.append(obj["narrative"])
        L.append("")
    return "\n".join(L)


def main():
    args = [a for a in sys.argv[1:]]
    out_format = "console"
    out_file = None
    show_ind = False
    format_set = False
    positional = []
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("--format", "-f") and i + 1 < len(args):
            out_format = args[i + 1]
            format_set = True
            i += 2
        elif a in ("--output", "-o") and i + 1 < len(args):
            out_file = args[i + 1]
            i += 2
        elif a in ("--individuals", "--ind"):
            show_ind = True
            i += 1
        elif a in ("--help", "-h"):
            print("Usage: python utils/render_report.py [--format console|md] [--output FILE] [--individuals] [report.json]",
                  file=sys.stderr)
            return 0
        else:
            positional.append(a)
            i += 1

    # Auto-detect Markdown output: -o report.md produces MD without --format.
    if not format_set and out_file and out_file.endswith(".md"):
        out_format = "md"

    if out_format not in ("console", "md"):
        print("--format must be 'console' or 'md'", file=sys.stderr)
        return 1
    if len(positional) > 1:
        print("Usage: python utils/render_report.py [--format console|md] [--output FILE] [report.json]",
              file=sys.stderr)
        return 2

    try:
        if positional:
            with open(positional[0], encoding="utf-8") as f:
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
        text = render_council_md(obj, show_ind) if out_format == "md" else _console_council(obj, show_ind)
    elif isinstance(obj, dict) and "evaluator_id" in obj:
        text = render_evaluator_md(obj) if out_format == "md" else _console_evaluator(obj)
    else:
        print("Input is neither a council report (report_id) nor an evaluator output (evaluator_id).",
              file=sys.stderr)
        return 1

    if out_file:
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"✓ wrote {out_file}")
    else:
        print(text)
    return 0


def _console_council(obj, show_ind=False):
    import io
    buf = io.StringIO()
    import contextlib
    with contextlib.redirect_stdout(buf):
        render_council(obj, show_ind)
    return buf.getvalue()


def _console_evaluator(obj):
    import io
    buf = io.StringIO()
    import contextlib
    with contextlib.redirect_stdout(buf):
        render_evaluator(obj)
    return buf.getvalue()


if __name__ == "__main__":
    sys.exit(main())
