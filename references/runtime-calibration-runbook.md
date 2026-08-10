<!-- version: 1.0.0, last_updated: 2026-08-10 -->

**Language:** [English](runtime-calibration-runbook.md) | [日本語](ja/runtime-calibration-runbook.md) | [中文](zh/runtime-calibration-runbook.md)

# Runtime Calibration — Runbook

> 2026-08-10. This runbook turns the procedure in §2 of [`references/calibration-suite.md`](calibration-suite.md) into steps you can execute as-is **after a session restart**.
>
> **Prerequisite for running this runbook**: the session must have been restarted and the `-ja` / `-zh` agents must be registered in the registry. **Do not run it within the same session** — every agent silently falls back to English and you get a meaningless "all three languages agree" result.

---

## 0. Preconditions (do this first, after restart)

Do not proceed until all of the following hold.

- [ ] The `-ja` / `-zh` agent symlinks exist (in both locations)
  ```bash
  ls -l ~/.claude/agents/originality-ja.md ~/.claude/agents/originality-zh.md
  ls -l .claude/agents/originality-ja.md
  ```
- [ ] Registry resolution is **actually confirmed**. Open `/agents` in the CLI and see `originality-ja` / `originality-zh` listed, or try `subagent_type: originality-ja` via the Agent tool and see it is not "not found". **Actual measurement is required** — the files existing does not mean the registry reflects them (the registry loads at session start).
- [ ] The static drift check PASSes (the translated numeric contract agrees across the 3 languages)
  ```bash
  cd <wisdom-council-layer>
  python3 utils/check_calibration_drift.py
  # → RESULT: PASS — no numeric drift across en / ja / zh（exit 0）
  ```

## 1. Prepare the test content

Cross-language comparison uses one set of "**the same text translated into 3 languages**". Because the text's own language affects evaluation, three different works would not be a comparison.

**Selection conditions:**
- Prefer a work that tests the evaluators' discrimination — "good but not a masterpiece" (to measure the median ≈ 30 strictness. A perfect masterpiece or an obvious dud scores similarly in every language, hiding strictness differences).
- The source language may be English or Japanese, but **save all 3 versions in one file** so later diffs are easy.

**Recommended format** (`/tmp/calib-samples.md`, etc.):

```markdown
# Calibration Sample (3-language version)

## en
<original text here>

## ja
<Japanese translation here>

## zh
<Chinese translation here>
```

> To reuse an existing `examples/` work, translate that work's input into 3 languages. E.g. `examples/creative-poem-sea/`.

## 2. Run the evaluation in 3 languages

Run the Wisdom Council skill **once per language — 3 times total**. Pass **only that language's text** as `content` (passing all versions makes the evaluators read everything and get confused).

```
Skill: wisdom-council
Args: {"content": "<en text>", "content_type": "text", "domain": "creative", "lang": "en"}
```

```
Skill: wisdom-council
Args: {"content": "<ja text>", "content_type": "text", "domain": "creative", "lang": "ja"}
```

```
Skill: wisdom-council
Args: {"content": "<zh text>", "content_type": "text", "domain": "creative", "lang": "zh"}
```

**domain**: `creative` is the representative case. Since this is a comparison, use the **same `domain`** for all 3 runs. If time permits, repeat with `business` or `cultural` to surface cross-domain bias.

**While running:**
- Save each evaluation's output JSON (`primary_score`, `dimension_scores`) to `/tmp/calib-en.json`, `/tmp/calib-ja.json`, `/tmp/calib-zh.json`.
- Visually confirm the synthesized parts of the output report (executive_summary, etc.) are in the requested language, and that `caveats` carries no English-fallback warning.

## 3. Collect and compare distributions

Collect `primary_score` and `dimension_scores` from the 3 JSONs and compare the cross-language distributions.

```bash
cd <wisdom-council-layer>
python3 - <<'EOF'
import json, statistics

langs = ["en", "ja", "zh"]
reports = {l: json.load(open(f"/tmp/calib-{l}.json")) for l in langs}

print(f"{'lang':4s} {'primary':>8s} {'dims':>6s}")
for l, r in reports.items():
    pri = r.get("primary_score")
    dims = [d["score"] for d in (r.get("dimension_scores") or {}).values() if d.get("score") is not None]
    print(f"{l:4s} {pri:8d} {statistics.mean(dims) if dims else 0:6.1f}")

# Per-evaluator (dimension) cross-language comparison
all_dim_keys = set().union(*(r.get("dimension_scores") or {}).keys() for r in reports.values())
for k in sorted(all_dim_keys):
    vals = [reports[l]["dimension_scores"].get(k, {}).get("score") for l in langs]
    print(f"{k:28s} en={vals[0]}  ja={vals[1]}  zh={vals[2]}")
EOF
```

## 4. Judgment criteria

Check that the `references/scoring-strictness.md` design (**median ≈ 30**) is reproduced across the 3 languages.

| Check | Pass criterion |
|-------|----------------|
| Overall strictness | In all 3 languages, `primary_score` / `dimension_scores` averages sit in the "around 30" band (mediocre-to-good). A flood of 50+ means strictness collapsed |
| Cross-language agreement | The 3 languages' medians and means differ little (within ±5 or so is desirable) |
| Relative ordering agreement | The dimensions one evaluator scores high/low show the same tendency across all 3 languages |

## 5. Judgment and disposition

### 5a. PASS (no bias)
If the distributions agree across the 3 languages, conclude there is no behavioral drift. Record the result.

```bash
# Record (example)
python3 utils/check_calibration_drift.py --json  # static: re-confirm PASS
```

Record at: append an "executed" note to §2 of the calibration findings document, or create a new runtime-calibration-results note.

### 5b. FAIL (systematic bias detected)
E.g. "English is systematically 5 higher" or "Japanese never issues 0–10".

1. **Fix the English prompt as the canonical source** (adjust wording if the bias shows in English — note that English being the baseline does not mean English is correct).
2. **Re-translate** ja / zh after the English fix (preserve number-bearing translations. Update `agents/*-ja.md` / `*-zh.md`).
3. After the fix, confirm the **static drift check still passes** — the numeric contract agrees across all 3 languages (a mismatch means a translation accident).
4. **Re-run runtime calibration** in a fresh session after a restart to confirm improvement.

## 6. Completion conditions

- [ ] Static drift check PASS (§0)
- [ ] Evaluations complete in all 3 languages, no fallback warnings (§2)
- [ ] Distribution comparison run and PASS / FAIL decided (§3–4)
- [ ] Result recorded (§5)
- [ ] If FAIL: prompt fix → re-translate → re-calibrate loop completed (§5b)

---

## References

- `references/calibration-suite.md` — calibration suite overview (static check + runtime calibration)
- `references/scoring-strictness.md` — strict-scoring doctrine the runtime check measures against (median ≈ 30)
- `utils/check_calibration_drift.py` — static drift checker
