<!-- version: 1.1.0, last_updated: 2026-08-10 -->

**Language:** [English](calibration-suite.md) | [日本語](ja/calibration-suite.md) | [中文](zh/calibration-suite.md)

# Calibration Suite

The Wisdom Council Layer ships each of its 10 evaluator agents in **3 language variants** (en / ja / zh). Calibration answers two distinct questions about those variants:

1. **Static drift** — did the *numbers* (weights, score bands, calibration values) drift during translation?
2. **Behavioral drift** — does the LLM, given the *same* numbers, score with different strictness in different languages?

The static check is **implemented and PASSing**. The runtime check is **pending a session restart** (see [§2](#2-runtime-calibration-pending)).

## 1. Static calibration drift check (implemented · PASS)

Checks that the numeric calibration contract of all 30 agent files (10 evaluators × 3 languages) is identical across languages. This excludes "a number changed during translation" drift — e.g. a weight silently becoming `0.30` instead of `0.35`.

### What is verified

For each of the 10 evaluators, across en / ja / zh:

| Check | Source | Format |
|-------|--------|--------|
| **Dimension weights** | `#### N. … — weight 0.35` heading lines | 4 decimals, order preserved |
| **Score bands** | `- 0-10:` … `- 91-100:` bullets in the Scoring Guidelines section | 6 ranges |
| **Calibration table** | 2nd column of the Calibration Reference table | `N-N` ranges (annotations ignored) |

### How to run

```bash
python utils/check_calibration_drift.py        # human-readable PASS/FAIL per evaluator
python utils/check_calibration_drift.py --json # machine-readable, for CI
```

Exit code `0` = PASS, `1` = FAIL. The script guards against the pitfalls below — an empty extraction is reported as FAIL, never as a silent PASS.

### Current status

**PASS — 2026-08-10.** All 10 evaluators × 3 checks agree across en / ja / zh. (Score bands are identical for all 10 evaluators; weights and calibration values are per-evaluator but consistent across languages — e.g. `business-value` → `15-30 / 40-60 / 60-80 / 80-95`, `anti-generic-filter` → `10-25 / 30-50 / 60-80 / 70-90`.)

**What PASS does NOT prove:** the same numbers do not guarantee the LLM applies them equally strictly per language. That is behavioral drift, measured only by the runtime check.

## 2. Runtime calibration (pending)

> **Executable runbook:** a step-by-step, copy-paste procedure for after the restart lives in [`references/runtime-calibration-runbook.md`](runtime-calibration-runbook.md). The overview below is its condensed version.

### Why it is blocked

Agent names are registered in the registry at **session start**. A newly created `-ja` / `-zh` symlink is resolvable only after a restart — within the current session the Agent tool reports `Agent type 'originality-ja' not found`.

Running the skill in this state would silently fall back to the unsuffixed (English) agents per the SKILL.md R3 mitigation, producing an apparent "all three languages agree" result that is actually "all three ran in English". Running after a restart avoids a meaningless result.

### Procedure (after restart)

1. Confirm the suffixed agents are registered, e.g. `ls ~/.claude/agents/originality-ja.md`.
2. Prepare **one content sample translated into all 3 languages** — the language of the text itself affects scoring, so cross-language comparison requires the *same meaning* in 3 languages.
3. Run the skill once per language:
   ```
   Skill: wisdom-council
   Args: {"content": "<3-language text>", "content_type": "text", "domain": "creative", "lang": "en|ja|zh"}
   ```
4. Collect `primary_score` and `dimension_scores.*.score` from the output JSON; compare the cross-language distributions (median / mean / variance) with `utils/compare_reports.py` or a small aggregator.
5. **Judgment** (per `references/scoring-strictness.md`): is the strictness doctrine reproduced — median ≈ 30, mediocrity below 50? If a systematic language bias appears (e.g. English systematically higher/lower), adjust the English prompt as the canonical source and re-translate ja / zh.

## 3. Pitfalls (learned building the static check)

These caused "10/10 FAIL" reports that were entirely script bugs — the content had zero drift. Worth carrying into any future checker.

1. **Empty-list equality is a false PASS.** `[] == [] == []` is `True`. A checker that extracts nothing agrees trivially. **Guard**: require non-empty AND equal, and print one extraction example so a total extraction failure is visible.
2. **`##+` regex swallows `####` headings.** Matching sections with `r"##+ .*"` lets a `#### 1. …` dimension heading match a following "High score" line and split the section mid-body. **Guard**: split sections on `^#{2,3}` only; keep `####` lines inside the parent section body.
3. **Calibration values carry trailing annotations.** `| … | 75-95 (quality/marketability expected to be low) |` — anchoring `N-N` to the `|` boundary misses the value. **Guard**: extract `N-N` at any position of the cell.
4. **CJK characters are `\w`.** `\b2-3\b` does not match in `- 2-3段落` (the digit is followed by a CJK `\w`), while the English `- 2-3 paragraph` splits on a space. **Guard**: match at line / cell boundaries rather than with `\b`.

## References

- `references/runtime-calibration-runbook.md` — the executable runbook for the runtime check (run after a session restart)
- `references/scoring-strictness.md` — the strict-scoring doctrine (median ≈ 30) the runtime check measures against
- `references/evaluator-taxonomy.md` — the 10 evaluators and their domains
- `utils/check_calibration_drift.py` — the implemented static checker
