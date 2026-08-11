**Language:** [English](CLAUDE.md) | [日本語](CLAUDE-ja.md) | [中文](CLAUDE-zh.md)

# Wisdom Council Layer

## Project Identity

This is the **Wisdom Council Layer**. A set of Claude Code agents in which multiple AI evaluator agents assess content from different intellectual perspectives and, through a council skill, produce a structured Value Report.

> **Division of labor**: This layer is **evaluation only**. The **creation** of works is deferred to other appropriate means (generative AI, dedicated creation skills, other tools) when available. This repository's job is not "making" but "seeing through to value", preparing its evaluation results as raw material for the next round of creation.

## Core Philosophy

- **Anti-Generic**: Exclude average, AI-typical output; discover meaningful deviation.
- **Polyphonic Evaluation**: Not a single judge, but multiple evaluators holding different perspectives.
- **Disagreement is a signal**: Conflict between evaluators is not averaged away — it is preserved as-is. Collision often reveals signs of value better than consensus.
- **Evaluate rather than generate**: The competitive arena of the AI era is not "how much you can make" but "how well you can see through to what is valuable".

## Directory Conventions

- `agents/{name}.md` — canonical definitions of the evaluator agents (10). Launched as independent subagents, persona-based experts
- `skills/wisdom-council/SKILL.md` — canonical definition of the council orchestrator (the only skill)
- `.claude/agents/` — symlinks for in-project detection (evaluator agents)
- `.claude/skills/` — symlinks for in-project detection (council orchestrator)
- `~/.claude/agents/`, `~/.claude/skills/` — global install locations (configured via `./install.sh`, callable from anywhere)
- `.claude-plugin/` — plugin distribution definition (for `/plugin marketplace add`)
- `schemas/` — JSON schemas for structured output
- `references/` — design documents and theoretical foundations (evaluator taxonomy, classification model, disagreement principle, vector model, strict scoring, calibration suite)
- `examples/` — sample inputs and outputs
- `utils/` — utilities such as validation, report rendering, and calibration drift checking

## How to Invoke Evaluators

**The council is invoked as a skill; evaluators are invoked as subagents.** This division of roles is the keystone of the architecture — evaluators must evaluate independently without knowing each other's results. A skill shares the same context, making it unsuited to independent evaluation. Launching evaluators as subagents isolates their contexts.

### Full council (recommended)

```
Skill: wisdom-council
Args: {"content": "...", "content_type": "text", "domain": "creative"}
```

The council does the following:
1. Determines the domain of the input
2. Selects the relevant evaluator agents (originality and anti-generic-filter are always included)
3. Launches each evaluator as a subagent (via the Agent tool, evaluating independently without knowing each other's results)
4. Synthesizes into a Value Report
5. Preserves all disagreement

### Single evaluator

For when you want to evaluate only a specific perspective. The evaluator is launched as a subagent.

```
Agent tool, subagent_type: originality
Prompt: {"content": "...", "content_type": "text", "domain": "creative"}
```

When running as an installed plugin, use the plugin-scoped name (`wisdom-council:originality`).

**mode option** — adding `"mode": "full"` to `Args` convenes all **10** evaluators at once without domain selection, yielding a complete Value Report with all 9 dimensions filled:

```
Skill: wisdom-council
Args: {"content": "...", "content_type": "text", "domain": "creative", "mode": "full"}
```

## Output Conventions

All evaluator output must be valid JSON conforming to `schemas/value-output.schema.json`.

```bash
python utils/validate_output.py < output.json
python utils/validate_output.py --json output.json   # machine-readable validation result
```

**Automatic retry**: The council skill **deterministically validates** each evaluator's output with `validate_output.py --json` and, on failure, **restarts the same evaluator up to 3 times** (including the error details in the feedback). If it still fails after 3 retries, the evaluator is explicitly recorded in `excluded_evaluators` with `reason: "JSON validation failed after 3 retries"`. **No silent drops.**

**If broken, regenerate (no manual patching)**: If an evaluator's output JSON is broken (`validate_output.py` returns `"valid": false`), **do not fix it by hand-editing the JSON directly**. Always **restart that evaluator to regenerate** and re-run validation on the freshly generated output. Because hand-patching JSON risks destroying the evaluator's independent voice (scores, judgment, style, narrative), the sole remedy for broken output is regeneration.

## Tools

| Tool | Role |
|--------|------|
| `utils/validate_output.py` | Schema validation of evaluator output. The `--json` flag emits a machine-readable result (used by the council skill's automatic retry) |
| `utils/render_report.py` | Visual rendering of the Value Report (bar charts, category badges, cross-dimension disagreements). `-o report.md` saves it as a Markdown document via automatic extension detection; `--individuals` shows all individual reports |
| `utils/compare_reports.py` | Difference comparison before and after revision (for the evaluate → recreate loop) |
| `utils/check_calibration_drift.py` | Static calibration drift check across the en / ja / zh agent variants (weights, score bands, calibration tables). `--json` emits a machine-readable result. Details: `references/calibration-suite.md` |

## Evaluation Output Is Designed as Input

**This layer's evaluation results are not an end product in themselves.** They are **input** to creation skills (dedicated skills that synthesize re-creation and improvement instructions).

- The council does **not generate the re-creation instructions themselves**. That is the responsibility of dedicated skills.
- Instead, it fully preserves each evaluator's **raw material** in `individual_reports` (`weaknesses`・`improvement_suggestions`・`expected_disagreement_points`・`narrative`).
- Field names are fixed and consistent (conforming to `schemas/value-output.schema.json`) so creation skills can read the paths directly.
- Synthesized narratives (executive_summary, etc.) are auxiliary; raw data is not discarded.

**Evaluate → recreate loop:**
```
evaluate → revision_direction (direction for the next revision) → creation skill synthesizes instructions → recreate → re-evaluate
  → check improvement with compare_reports.py → repeat
```

**Iteration modes (`iteration`):**
- `iteration: "confirm"` (default) — after each turn's evaluation, `revision_direction` is presented and you **confirm before** proceeding to the next revision.
- `iteration: "persistent"` — `revision_direction` is fixed up front, and revisions **continue along that direction** (each iteration reports progress toward it).

Guidelines:
- Judge by more than the average — also look at variance and disagreement.
- Stop the loop when improvement plateaus (over-revision destroys the original strengths).
- Details: `references/revision-loop.md`

## Key Principles

- Evaluators score only the dimensions of their own domain. Out-of-domain dimensions return `null`.
- Predicting disagreement is an evaluator's duty (imagine where one's own perspective will conflict with others').
- Evaluation must not be diplomatic. Candor is the value.
- Scoring is **deliberately strict** (`references/scoring-strictness.md`). High scores are rare. A low absolute score does not mean "poorly evaluated" — it means "generic and safe".
- The orchestrator does not dictate judgments to evaluators. It only convenes and synthesizes.
- **i18n baseline**: multilingual support (en/ja/zh) is the default baseline for any fix or change. New or modified agent prompts, schemas, and report templates must resolve through the language mechanism (evaluator agents' `-ja`/`-zh` variants, locale JSON, mirror tree), and user-facing text must be produced in the run's language.

## Installation

```bash
./install.sh            # global: ~/.claude/agents/ + ~/.claude/skills/ (callable from anywhere)
./install.sh --local    # project: .claude/agents/ + .claude/skills/
./install.sh --uninstall
```
