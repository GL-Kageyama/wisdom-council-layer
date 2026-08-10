#!/usr/bin/env python3
"""Static calibration drift check for the Wisdom Council Layer.

Verifies that the numeric calibration contracts of the 10 evaluator agent
definitions are identical across the 3 language variants (en / ja / zh):

    1. dimension weights   (`#### N. — weight 0.35` heading lines)
    2. score-band anchors  (`- 0-10:` bullets in the scoring-guidelines section)
    3. calibration table   (the `N-N` range in the 2nd column of the
                            Calibration Reference table)

The static check proves that the *numbers* did not drift during translation.
It cannot prove that the LLM applies the same strictness per language — that is
the job of the runtime calibration suite (see references/calibration-suite.md),
which is run after a session restart once the `-ja` / `-zh` agents are in the
agent registry.

Pitfalls handled here (learned while developing this check, see
references/calibration-suite.md §Pitfalls):

  P1  Empty-list equality is a false PASS (`[] == [] == []` is True). Every
      extraction must be non-empty AND equal; an example is printed so a total
      extraction failure is visible, not silently green.
  P2  A `##+` regex swallows `####` dimension headings. Sections are split on
      `^#{2,3}` only; `####` lines stay inside the parent section's body.
  P3  Calibration values can carry trailing annotations
      (`| ... | 75-95 (quality/marketability expected to be low) |`). The
      `N-N` range is extracted at any position of the cell, not anchored to
      the `|` boundary.
  P4  CJK characters are `\\w`, so `\\b` does not terminate after a digit when
      a Japanese/Chinese string follows (`- 2-3段落`). Bullets are matched at
      the line start rather than with `\\b`.

Usage:
    python utils/check_calibration_drift.py               # human-readable report
    python utils/check_calibration_drift.py --json        # machine-readable result

Exit codes:
    0  all checks PASS
    1  drift found, or usage error
"""

import json
import os
import re
import sys

AGENTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "agents")

LANGS = ("en", "ja", "zh")
SUFFIX = {"en": "", "ja": "-ja", "zh": "-zh"}

# --- Section splitting (P2) ---
# Split on `##` / `###` only. `####` (dimension headings) stays in the body.
SECTION_RE = re.compile(r"^#{2,3}\s+.+$")


def split_sections(text):
    """Return [(heading, body_lines)] for `##`/`###` sections. `####` is kept
    in the body of its parent section (P2)."""
    sections = []
    cur_heading = None
    cur_body = []
    for line in text.splitlines():
        if SECTION_RE.match(line):
            if cur_heading is not None:
                sections.append((cur_heading, cur_body))
            cur_heading = line
            cur_body = []
        elif cur_heading is not None:
            cur_body.append(line)
    if cur_heading is not None:
        sections.append((cur_heading, cur_body))
    return sections


def find_section(sections, keyword_re):
    """Return the body lines of the first section whose heading matches."""
    for heading, body in sections:
        if keyword_re.search(heading):
            return body
    return None


# --- Extraction ---

# P4: `- 0-10:` / `- 0-10：` bullets anchored at line start, no `\b`.
# Full-width colon `：` appears in the zh scoring sections.
BAND_RE = re.compile(r"^[-•*]\s*(\d{1,3}-\d{1,3})\s*[:：]")
# P3: a range anywhere inside a table cell (2nd column of the calibration row).
CELL_RANGE_RE = re.compile(r"(\d{1,3}-\d{1,3})")
# `#### N. Title — weight 0.35` — capture the weight decimal (MULTILINE so
# `^` matches at line starts; do NOT pass flags to finditer as pos).
WEIGHT_RE = re.compile(r"^####\s+.*—\s*(?:weight|重み|权重)\s+(\d+\.\d+)", re.MULTILINE)

# Scoring-guidelines heading: English canonical, plus zh/ja localized variants.
SCORING_RE = re.compile(r"Scoring|评分|スコア")
CALIB_RE = re.compile(r"Calibration|校准|較正")


def extract_weights(text):
    return [m.group(1) for m in WEIGHT_RE.finditer(text)]


def extract_bands(sections):
    body = find_section(sections, SCORING_RE)
    if body is None:
        return None
    bands = []
    for line in body:
        m = BAND_RE.match(line.strip())
        if m:
            bands.append(m.group(1))
    return bands


def extract_calibration(sections):
    body = find_section(sections, CALIB_RE)
    if body is None:
        return None
    values = []
    for line in body:
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        m = CELL_RANGE_RE.search(cells[1])
        if m:
            values.append(m.group(1))
    return values


def extract(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    sections = split_sections(text)
    return {
        "weights": extract_weights(text),
        "bands": extract_bands(sections),
        "calibration": extract_calibration(sections),
    }


# --- Comparison ---

CHECKS = ("weights", "bands", "calibration")
LABELS = {"weights": "dimension weights", "bands": "score bands",
          "calibration": "calibration table"}


def is_pass(vals):
    """P1: equal AND non-None AND non-empty. `[] == [] == []` is NOT a pass."""
    if any(v is None for v in vals):
        return False
    if not vals[0]:
        return False
    return all(v == vals[0] for v in vals)


def main():
    json_out = "--json" in sys.argv[1:]
    if not os.path.isdir(AGENTS_DIR):
        print(f"agents/ directory not found: {AGENTS_DIR}", file=sys.stderr)
        return 1

    # Base evaluator names = en files (no suffix)
    base_names = sorted(
        n[:-len(".md")] for n in os.listdir(AGENTS_DIR)
        if n.endswith(".md") and not re.search(r"-(ja|zh)\.md$", n)
    )

    results = {}
    all_pass = True

    for name in base_names:
        files = {lang: os.path.join(AGENTS_DIR, name + SUFFIX[lang] + ".md")
                 for lang in LANGS}
        extracted = {}
        missing = [lang for lang, p in files.items() if not os.path.isfile(p)]
        if missing:
            results[name] = {"missing": missing}
            all_pass = False
            continue
        for lang in LANGS:
            extracted[lang] = extract(files[lang])

        per_check = {}
        for check in CHECKS:
            vals = [extracted[lang][check] for lang in LANGS]
            ok = is_pass(vals)
            per_check[check] = (ok, vals)
            if not ok:
                all_pass = False
        results[name] = per_check

    if json_out:
        payload = {"valid": all_pass, "evaluators": {}}
        for name, r in results.items():
            if "missing" in r:
                payload["evaluators"][name] = {"valid": False, "missing": r["missing"]}
                continue
            payload["evaluators"][name] = {
                check: {"valid": ok, "values": vals}
                for check, (ok, vals) in r.items()
            }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if all_pass else 1

    print("Calibration drift check (agents/, 10 evaluators × 3 checks)")
    print("Checks: dimension weights · score bands · calibration table\n")
    for name in sorted(results):
        r = results[name]
        if "missing" in r:
            print(f"  ✗ {name:24s} MISSING FILES: {', '.join(r['missing'])}")
            continue
        print(f"  {name}:")
        for check in CHECKS:
            ok, vals = r[check]
            mark = "✓" if ok else "✗"
            if not ok and vals[0] is None:
                detail = "section not found"
            elif not ok and not vals[0]:
                detail = "extraction empty (false-PASS guard)"
            elif not ok:
                detail = " → ".join(repr(v) for v in vals)
            else:
                detail = " = ".join(repr(v) for v in vals)
            print(f"    {mark} {LABELS[check]:20s} {detail}")

    print()
    if all_pass:
        print("RESULT: PASS — no numeric drift across en / ja / zh")
        return 0
    print("RESULT: FAIL — numeric drift detected (or missing files)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
