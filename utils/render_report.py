#!/usr/bin/env python3
"""Render a Wisdom Council Value Report (or a single evaluator output) as a
human-friendly visual report: classification badge, value-vector bar chart,
disagreement highlights, executive summary, and recommendations.

Usage:
    python utils/render_report.py < report.json
    python utils/render_report.py report.json
    python utils/render_report.py --lang ja report.json

Language selection:
    --lang en|ja|zh          Explicit language (highest priority)
    WISDOM_COUNCIL_LANG env  Fallback environment variable
    (default: en)

This is the presentation layer only. The machine contract is the JSON itself
(evaluators: schemas/value-output.schema.json; council: the Value Report
structure in skills/wisdom-council/SKILL.md). JSON stays the interchange
format; this script makes it readable by humans.
"""

import json
import os
import sys

# Ensure utils/ is on the path so `from _locale import ...` works
# regardless of the caller's working directory.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from locale_loader import load_locale  # noqa: E402

# --- Locale-driven globals (populated at module load with English default,
# then possibly overridden via --lang in main) ---

_L = None               # current locale dict
DIMENSIONS = []          # [(key, display_name), ...]
CLASS_BADGE = {}         # {classification_key: badge_string, ...}


def _set_locale(lang=None):
    """(Re)populate DIMENSIONS, CLASS_BADGE and the _L cache from a locale."""
    global _L, DIMENSIONS, CLASS_BADGE
    _L = load_locale(lang)
    _DIMENSION_KEYS = [
        "originality", "quality", "aesthetic", "emotional_impact",
        "future_potential", "business_value", "scientific_novelty",
        "philosophical_depth", "meaning",
    ]
    DIMENSIONS = [(k, _L["dimensions"][k]) for k in _DIMENSION_KEYS]
    CLASS_BADGE = dict(_L["classifications"])


# Populate defaults at import time
_set_locale("en")


def _c(key, **kwargs):
    """Shortcut for console-section locale strings."""
    s = _L["console"].get(key, key)
    return s.format(**kwargs) if kwargs else s


def _m(key, **kwargs):
    """Shortcut for markdown-section locale strings."""
    s = _L["markdown"].get(key, key)
    return s.format(**kwargs) if kwargs else s


def _cmp(key, **kwargs):
    """Shortcut for compare-section locale strings."""
    s = _L["compare"].get(key, key)
    return s.format(**kwargs) if kwargs else s


# --- Rendering helpers (pure functions, no side effects) ---

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
    print(f"\n{_c('value_vector_header')}")
    print(f"  {_c('dimension'):16s} {_c('bar'):<{BAR_WIDTH}} {_c('score')}")
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
        print(f"  {_c('no_scores')}")


def render_disagreement(value_vector):
    print(f"\n{_c('disagreement_header')}")
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
        if variance > 400:
            level = _c("disagreement_severe")
        elif variance >= 100:
            level = _c("disagreement_moderate")
        else:
            level = _c("disagreement_mild")
        print(f"  [{level}] {jp}({key}): スコア={scores}")
    if not found:
        print(f"  {_c('no_disagreement')}")


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
        print(f"\n{_c('contrast_header')}")
        for hk, hv, lk, lv in pairs:
            print(f"  ⚡ {jp[hk]}({hk}) {hv}  vs  {jp[lk]}({lk}) {lv}")
        print(f"  {_c('contrast_footer')}")


def render_council(obj, show_ind=False):
    header("🧠 Wisdom Council Value Report")
    badge = CLASS_BADGE.get(obj.get("classification"), obj.get("classification", "?"))
    print(f"\n  {_c('classification_label')}: {badge}")

    current = obj.get("current_value_score")
    hidden = obj.get("hidden_potential_score")
    if current is not None or hidden is not None:
        cbar = bar(current)
        hbar = bar(hidden)
        print(f"\n  {_c('current_value')}: {f(current)}  {cbar}")
        print(f"  {_c('hidden_potential')}: {f(hidden)}  {hbar}")

    print(f"\n  {_c('target')} {obj.get('content_summary', '—')}")
    print(f"  {_c('domain')}: {obj.get('domain', '—')}  |  {_c('evaluators_consulted')}: {len(obj.get('evaluators_consulted', []) or [])}体")

    excl = obj.get("excluded_evaluators") or []
    if excl:
        print(f"  {_c('excluded_header')}")
        for e in excl:
            eid = e.get("evaluator_id") if isinstance(e, dict) else e
            reason = e.get("reason", "") if isinstance(e, dict) else ""
            print(f"    · {eid}: {reason or _c('dimension_incompatible')}")

    render_value_vector(obj.get("value_vector"))
    render_disagreement(obj.get("value_vector"))
    render_contrasts(obj.get("value_vector"), excluded_ids(obj))

    if obj.get("executive_summary"):
        print(f"\n{_c('executive_summary')}\n  {obj['executive_summary']}")

    if obj.get("consensus_summary"):
        print(f"\n{_c('consensus_summary')}\n  {obj['consensus_summary']}")

    recs = obj.get("recommendations") or []
    if recs:
        print(f"\n{_c('recommended_actions')}")
        for i, r in enumerate(recs, 1):
            print(f"  {i}. {r}")

    rd = obj.get("revision_direction")
    if rd:
        mode = rd.get("iteration") or "confirm"
        mode_label = _c("mode_confirm") if mode == "confirm" else _c("mode_persistent")
        print(f"\n{_c('revision_direction_header', mode=mode_label)}")
        if rd.get("statement"):
            print(f"  {_c('direction')}: {rd['statement']}")
        axis = rd.get("axis") or []
        if axis:
            print(f"  {_c('raise_or_change')}: {', '.join(axis)}")
        keep = rd.get("preserve") or []
        if keep:
            print(f"  {_c('preserve')}: {', '.join(keep)}")

    caves = obj.get("caveats") or []
    if caves:
        print(f"\n{_c('caveats')}")
        for c in caves:
            print(f"  · {c}")

    ind = obj.get("individual_reports") or []
    if ind:
        if show_ind:
            print(f"\n{_c('individual_reports')}{len(ind)}体")
            for r in ind:
                render_evaluator(r)
        else:
            print(f"\n{_c('individual_reports')}{_c('individual_detail_hint', n=len(ind))}")


def render_evaluator(obj):
    header(f"🔎 {obj.get('evaluator_name', obj.get('evaluator_id', 'Evaluator'))}")
    badge = CLASS_BADGE.get(obj.get("classification"), obj.get("classification", "?"))
    print(f"\n  {_c('classification_label')}: {badge}  |  {_c('confidence')}: {f(obj.get('confidence'))}")
    print(f"\n  {_c('primary_score')}: {f(obj.get('primary_score'))}  {bar(obj.get('primary_score'))}")
    if obj.get("primary_score_rationale"):
        print(f"  {_c('rationale')}: {obj['primary_score_rationale']}")

    ds = obj.get("dimension_scores") or {}
    if ds:
        print(f"\n{_c('dimension_scores')}")
        for name, d in ds.items():
            score, w, evidence = _ds_norm(d)
            print(f"  {name:24s} {bar(score)} {f(score)}  (w={w})")
            if evidence:
                print(f"    ↳ {evidence}")

    if obj.get("unique_perspective"):
        print(f"\n{_c('unique_perspective')}\n  {obj['unique_perspective']}")

    if obj.get("expected_disagreement_points"):
        print(f"\n{_c('expected_disagreement')}")
        for p in obj["expected_disagreement_points"]:
            etype, stance = _edp_norm(p)
            print(f"  · {etype}: {stance}")

    if obj.get("narrative"):
        print(f"\n{_c('narrative')}\n  {obj['narrative']}")


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
    L.append(_m("report_title"))
    L.append("")
    L.append(f"> **{_c('classification_label')}**: {CLASS_BADGE.get(obj.get('classification'), obj.get('classification', '?'))}")
    L.append("")

    # Summary table
    L.append(_m("summary_table_title"))
    L.append("")
    L.append(f"| {_m('item')} | {_m('value')} |")
    L.append("|------|-----|")
    L.append(f"| {_m('target_row')} | {obj.get('content_summary', '—')} |")
    L.append(f"| {_m('domain_row')} | {obj.get('domain', '—')} |")
    L.append(f"| {_m('evaluators_row')} | {len(obj.get('evaluators_consulted', []) or [])}体 |")
    L.append(f"| {_m('current_value_row')} | {md_val(obj.get('current_value_score'))} |")
    L.append(f"| {_m('hidden_potential_row')} | {md_val(obj.get('hidden_potential_score'))} |")
    L.append("")

    # Excluded evaluators
    excl = obj.get("excluded_evaluators") or []
    if excl:
        L.append(_m("excluded_table_title"))
        L.append("")
        L.append(f"| {_m('evaluator_col')} | {_m('reason_col')} |")
        L.append("|--------|------|")
        for e in excl:
            eid = e.get("evaluator_id") if isinstance(e, dict) else e
            reason = e.get("reason", "") if isinstance(e, dict) else ""
            L.append(f"| `{eid}` | {reason or _c('dimension_incompatible')} |")
        L.append("")

    # Value vector
    L.append(_m("value_vector_title"))
    L.append("")
    L.append(f"| {_m('dimension_col')} | {_m('score_col')} | {_m('variance_col')} | {_m('bar_col')} |")
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
        L.append(f"| — | — | — | {_m('no_dimensions_scored')} |")
    L.append("")

    # Disagreement
    L.append(_m("disagreement_title"))
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
        if variance > 400:
            level = _c("disagreement_severe")
        elif variance >= 100:
            level = _c("disagreement_moderate")
        else:
            level = _c("disagreement_mild")
        L.append(f"- **[{level}]** {jp}（`{key}`）: スコア = {scores}")
    if not found:
        L.append(f"- {_c('no_disagreement').rstrip('いる')}")  # match shorter form used in md
    L.append("")

    # Contrasts (skip excluded evaluators, show most striking)
    pairs = contrast_pairs(vec, excluded_ids(obj))
    if pairs:
        L.append(_m("contrast_title"))
        L.append("")
        L.append(f"| {_m('high_axis_col')} | {_m('low_axis_col')} |")
        L.append("|-----------|-----------|")
        idx = {d[0]: d[1] for d in DIMENSIONS}
        for hk, hv, lk, lv in pairs:
            L.append(f"| {idx[hk]}（`{hk}`）{hv} | {idx[lk]}（`{lk}`）{lv} |")
        L.append("")
        L.append(f"> {_c('contrast_footer').lstrip('→ ')}")
        L.append("")

    if obj.get("executive_summary"):
        L.append(_m("executive_summary_title"))
        L.append("")
        L.append(f"> {obj['executive_summary']}")
        L.append("")

    if obj.get("consensus_summary"):
        L.append(_m("consensus_title"))
        L.append("")
        L.append(obj["consensus_summary"])
        L.append("")

    recs = obj.get("recommendations") or []
    if recs:
        L.append(_m("recommendations_title"))
        L.append("")
        for i, r in enumerate(recs, 1):
            L.append(f"{i}. {r}")
        L.append("")

    rd = obj.get("revision_direction")
    if rd:
        mode = rd.get("iteration") or "confirm"
        mode_label = _c("mode_confirm") if mode == "confirm" else _c("mode_persistent")
        L.append(_m("revision_direction_title", mode=mode_label))
        L.append("")
        if rd.get("statement"):
            L.append(f"> {rd['statement']}")
            L.append("")
        if rd.get("axis"):
            L.append(_m("raise_change_label"))
            for a in rd["axis"]:
                L.append(f"- {a}")
            L.append("")
        if rd.get("preserve"):
            L.append(_m("preserve_label"))
            for p in rd["preserve"]:
                L.append(f"- {p}")
            L.append("")

    caves = obj.get("caveats") or []
    if caves:
        L.append(_m("caveats_title"))
        L.append("")
        for c in caves:
            L.append(f"- {c}")
        L.append("")

    ind = obj.get("individual_reports") or []
    if ind:
        if show_ind:
            L.append(_m("individual_full_title"))
            L.append("")
            for r in ind:
                L.append("")
                L.append(render_evaluator_md(r))
        else:
            L.append(_m("individual_material_title"))
            L.append("")
            L.append(_m("individual_material_note"))
            L.append("")

    return "\n".join(L)


def render_evaluator_md(obj):
    L = []
    L.append(f"# 🔎 {obj.get('evaluator_name', obj.get('evaluator_id', 'Evaluator'))}")
    L.append("")
    L.append(f"> **{_c('classification_label')}**: {CLASS_BADGE.get(obj.get('classification'), obj.get('classification', '?'))}  |  {_c('confidence')}: {md_val(obj.get('confidence'))}")
    L.append("")
    L.append(f"**{_c('primary_score')}**: {md_val(obj.get('primary_score'))}  `{md_bar(obj.get('primary_score'))}`")
    if obj.get("primary_score_rationale"):
        L.append("")
        L.append(f"*{obj['primary_score_rationale']}*")
    L.append("")
    ds = obj.get("dimension_scores") or {}
    if ds:
        L.append(_m("evaluator_dimension_title"))
        L.append("")
        L.append(f"| {_m('dimension_col')} | {_m('score_col')} | {_m('evaluator_weight_col')} |")
        L.append("|------|:------:|:----:|")
        for name, d in ds.items():
            score, w, evidence = _ds_norm(d)
            L.append(f"| {name} | {md_val(score)} | {w if w else '—'} |")
            if evidence:
                L.append(f"| ↳ {evidence} | | |")
        L.append("")
    if obj.get("unique_perspective"):
        L.append(_m("evaluator_unique_title"))
        L.append("")
        L.append(obj["unique_perspective"])
        L.append("")
    if obj.get("expected_disagreement_points"):
        L.append(_m("evaluator_disagreement_title"))
        L.append("")
        for p in obj["expected_disagreement_points"]:
            etype, stance = _edp_norm(p)
            L.append(f"- **{etype}**: {stance}")
        L.append("")
    if obj.get("narrative"):
        L.append(_m("evaluator_narrative_title"))
        L.append("")
        L.append(obj["narrative"])
        L.append("")
    return "\n".join(L)


def main():
    global _L, DIMENSIONS, CLASS_BADGE

    args = [a for a in sys.argv[1:]]
    out_format = "console"
    out_file = None
    show_ind = False
    format_set = False
    lang = None
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
        elif a == "--lang" and i + 1 < len(args):
            lang = args[i + 1]
            i += 2
        elif a in ("--help", "-h"):
            print("Usage: python utils/render_report.py [--format console|md] [--output FILE] [--lang en|ja|zh] [--individuals] [report.json]",
                  file=sys.stderr)
            print("       WISDOM_COUNCIL_LANG env var is used when --lang is omitted (default: en)",
                  file=sys.stderr)
            return 0
        else:
            positional.append(a)
            i += 1

    # Apply language selection
    _set_locale(lang)

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
            with open(positional[0], encoding="utf-8") as fh:
                obj = json.load(fh)
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
        with open(out_file, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
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
