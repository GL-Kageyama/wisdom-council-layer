**Language:** [English](README.md) | [日本語](README-ja.md) | [中文](README-zh.md)

# Wisdom Council Layer

**知恵の評議会（Council of Wisdom）** — a multi-agent value evaluation layer for discovering what is truly valuable amid the flood of generative-AI output.

## Why This Is Needed

With the rise of generative AI, we now live in an era where writing, images, music, code, plans — virtually every kind of creation — can be mass-produced.

But a new problem has emerged.

> **The scarce ability is no longer the ability to create, but the ability to recognize what is truly valuable.**

AI can produce output that is average and technically polished. Yet what truly matters does not always live inside the average.

- Things that seem strange at first glance but are genuinely innovative
- Things not yet understood at the present moment
- Minority views that will shape the culture of the future
- Things that change how humans perceive the world

**Wisdom Council Layer** is the infrastructure built to discover these.

## Core Philosophy

- **Anti-Generic**: reject the average answer and discover meaningful deviation.
- **Polyphonic Evaluation**: not a single judge, but a council of multiple evaluators holding different perspectives.
- **Disagreement Is a Signal**: conflict between evaluators is not averaged away — it is preserved as-is.
- **Evaluation over Generation**: in the AI era, the competitive frontier shifts from "how much can you create" to "how well can you recognize what is valuable."

## Division of Roles (Where This Repository Stands)

> **This repository exists for evaluation. Creation (Generation) is left to other, more suitable means whenever they are available.**

| Role | Responsibility |
|------|----------------|
| **Creation (Generation)** | Generative AI, dedicated creation skills, and other tools (this repository does **not** create) |
| **Evaluation** | This repository. Evaluates what has been created from multiple perspectives and prepares the material for the next round of creation (`weaknesses` and `improvement_suggestions`) |

**Principle**: keep "the one who creates" and "the one who evaluates" separate, and leave each to its own specialty. This layer is the evaluation specialist and **leaves creation to other means**. If no creation tool is available, a human receives the evaluation results and produces the next work.

## Architecture

```
Content to be evaluated
        ↓
┌────────────── 知恵の評議会 (Wisdom Council) ──────────────┐
│  Originality  Aesthetic  Emotional        │
│  Anti-Generic Business   Scientific       │
│  Future       Philosophical  Meaning      │
│  Quality                                    │
└────────────────────────────────────────────┘
        ↓
  Value Vector (multi-dimensional scores)
        ↓
  Disagreement Map (disagreement preserved)
        ↓
  Value Report (for the human decision-maker)
```

### Three-Layer Structure

```
Layer 1: Generation Layer (the AI that generates) ※ outside this project; delegated to other suitable means
Layer 2: Evaluation Layer (the AI that evaluates) ← this project
Layer 3: Meta Value Layer (the AI that reflects on value criteria themselves) ← future phase
```

**This project covers only Layer 2 (Evaluation).** Layer 1 (Generation) is left to suitable means such as generative AI and creation skills.

## Directory Structure

```
wisdom-council-layer/
├── CLAUDE.md                          # Project conventions
├── install.sh                         # Global / project installer
├── agents/                            # Source of truth for the evaluator agents (10)
│   ├── originality.md
│   ├── anti-generic-filter.md
│   ├── aesthetic-critic.md
│   ├── emotional-impact.md
│   ├── future-potential.md
│   ├── business-value.md
│   ├── scientific-novelty.md
│   ├── philosophical-evaluator.md
│   ├── quality-evaluator.md
│   └── meaning-evaluator.md
├── skills/                            # Source of truth for the skill (council orchestrator)
│   └── wisdom-council/SKILL.md        # Council orchestrator
├── .claude/agents/                    # symlinks for in-project detection (evaluators)
├── .claude/skills/                    # symlinks for in-project detection (council)
├── .claude-plugin/                    # Plugin distribution definitions
│   ├── marketplace.json
│   └── plugin.json
├── schemas/
│   └── value-output.schema.json       # Output contract for all evaluators
├── references/                        # Theoretical foundations
│   ├── evaluator-taxonomy.md
│   ├── value-classification.md
│   ├── debate-principles.md
│   ├── value-vector-model.md
│   ├── scoring-strictness.md          # Strict scoring criteria
│   ├── calibration-suite.md           # Static drift check + runtime calibration procedure
│   └── runtime-calibration-runbook.md # Executable runtime-calibration runbook (after restart)
├── examples/                          # Genre-based samples (create → evaluate → recreate)
│   ├── README.md
│   ├── creative-poem/                 # Poetry
│   ├── creative-film/                 # Film pitch
│   ├── business-startup/              # Business
│   ├── scientific-hypothesis/         # Scientific hypothesis
│   ├── cultural-philosophy/           # Thought essay
│   ├── digital-oss/                   # OSS software
│   ├── architecture-house/            # Private residence design (architecture)
│   ├── creative-watercolor/           # Image-generation prompt (watercolor)
│   └── creative-photography/          # Image-generation prompt (photography)
└── utils/
    ├── validate_output.py             # Output validation (machine-readable via --json; used by the council's automatic retry)
    ├── render_report.py               # Visualization (console / Markdown)
    ├── compare_reports.py             # Compare before / after a revision
    └── check_calibration_drift.py     # Static drift check across en/ja/zh agents (weights, bands, calibration)
```

## Usage

### Installation

**Global (callable from anywhere):**

```bash
./install.sh
```

symlinks are created in `~/.claude/agents/` (evaluator agents) and `~/.claude/skills/` (council skill), making them available in any project.

**Project-scoped:**

```bash
./install.sh --local
```

**Distribute and install as a plugin** (after publishing to GitHub):

```
/plugin marketplace add https://github.com/<your-account>/wisdom-council-layer
/plugin install wisdom-council-layer@wisdom-council-layer
```

### Invocation Flow (3 Levels)

Choose from three levels depending on your use case.

| Level | What to call | What you get | Use case |
|-------|--------------|--------------|----------|
| **1** | A **single** evaluator | Single-dimension evaluation JSON | Only want to check one specific perspective |
| **2** | **Council (auto)** | Integrated Value Report (3–5 dimensions) | Efficient overall evaluation tuned to the domain |
| **3** | **Council (full)** | Complete Value Report with all 9 dimensions filled | Want to evaluate from every perspective at once from the start |

---

#### Level 1: Invoke a Single Evaluator

When you want to evaluate only one specific perspective. The evaluator is launched as a **subagent**.

```
Agent tool, subagent_type: originality
Prompt: {"content": "...", "content_type": "text", "domain": "creative"}
```

Examples:
- Only check the originality of a plan → evaluator agent `originality`
- Check for AI-ness (genericness) → evaluator agent `anti-generic-filter`
- Only check marketability → evaluator agent `business-value`

→ Returns: the JSON of that single evaluator (conforms to `schemas/value-output.schema.json`; 1 dimension + narrative)

> **When running as a plugin**: evaluators are launched with a scoped name (e.g. `wisdom-council:originality`). When running inside the project, the bare name (`originality`) is fine.

---

#### Level 2: Invoke the Council (Recommended)

When you want a comprehensive evaluation across multiple perspectives. The council detects the domain, **selects 3–5 evaluators for independent evaluation**, and returns an integrated Value Report.

```
Skill: wisdom-council
Args: {"content": "...", "content_type": "text", "domain": "creative"}
```

What the council does:

```
Content to be evaluated
   ↓
Domain detection → select 3–5 evaluators (originality and anti-generic-filter are always included)
   ↓
Call each evaluator independently (each evaluates without knowing the others' results)
   ↓
Synthesize the Value Vector (mean, variance, range)
   ↓
Generate the disagreement map (record the split dimensions and both positions)
   ↓
Output the Value Report (classification, recommendations, full text of each evaluator)
```

→ Returns: an integrated Value Report (multi-dimensional score distribution + disagreement + 4-quadrant classification + recommendations)

---

#### Level 3: Invoke All Evaluators at Once

When you want to evaluate from every perspective from the start. Call the council with `mode: "full"` to run **all 10 evaluators in a single independent evaluation**, returning a complete Value Report with all 9 dimensions filled.

```
Skill: wisdom-council
Args: {"content": "...", "content_type": "text", "domain": "creative", "mode": "full"}
```

What the council does (full mode):

```
Content to be evaluated
   ↓
Convene all 10 evaluators (mode: full)
   ↓
Call each evaluator independently (each evaluates without knowing the others' results)
   ↓
Synthesize the Value Vector (all 9 dimensions filled)
   ↓
Generate the disagreement map (record the split dimensions and both positions)
   ↓
Output the complete Value Report (classification, recommendations, full text of each evaluator)
```

→ Returns: an integrated Value Report (a Value Vector with **all 9 dimensions filled** + disagreement + 4-quadrant classification + recommendations)

> **Tip**: you can also call each evaluator individually (repeating Level 1), but `mode: "full"` achieves the same result in a single call. `mode: "auto"` (Level 2) selects 3–5 evaluators based on the domain, so unconvened dimensions are `null`.

---

### Validating Output

```bash
python utils/validate_output.py < evaluator_output.json
python utils/validate_output.py --json output.json   # machine-readable result (used by the council's automatic retry)
```

The council skill deterministically validates each evaluator's output with this validator and retries **up to 3 times** on failure. Evaluators that still fail after retries are explicitly recorded in `excluded_evaluators` (no silent drops).

### Visualizing Results

If raw JSON is hard to read, use the renderer to convert it into a visual display.

**Console display:**
```bash
python utils/render_report.py < report.json     # from stdin
python utils/render_report.py report.json        # from a file
```

**Markdown output (for a readable document):**

```bash
python utils/render_report.py report.json                          # console display (bar chart)
python utils/render_report.py report.json -o report.md             # save to an MD file (auto-detected by extension)
python utils/render_report.py --format md report.json              # Markdown to stdout
python utils/render_report.py --individuals report.json            # also show each evaluator's individual report
```

**How Markdown output works**: if the **output extension is `.md`** (e.g. `-o report.md`), the report is automatically formatted as Markdown. You can also specify it explicitly with `--format md`. The generated MD is composed of headings, tables, and quotes, and is readable as-is in GitHub / VSCode preview.

MD output is a format **readable as-is in GitHub / VSCode preview** (headings, tables, quotes). Live example: [examples/creative-poem/report.md](wisdom-council-layer/examples/creative-poem/report.md)

**Output example** (rendered from [examples/creative-poem/report-v2.json](wisdom-council-layer/examples/creative-poem/report-v2.json)):

```
┌──────────────────────────────────────────────────────┐
│ 🧠 Wisdom Council Value Report
└──────────────────────────────────────────────────────┘

  Classification: 🔍 Discovery Target
  Current Value:  49  █████████████████░░░░░░░░░░░░░░░░░░░
  Hidden Potential:  59  █████████████████████░░░░░░░░░░░░░░░

【Value Vector】Multi-Dimensional Scores (0–100, strict scale)
  Originality (originality)          ████████████████████████████░░  78
  Quality (quality)                  ███████████████████████░░░░░░  65
  Aesthetics (aesthetic)             ██████████████████████░░░░░░░  62
  Emotional Impact (emotional_impact) ████████████████████████░░░░░  68
  Future Potential (future_potential) ██████████████████░░░░░░░░░░  50
  Business Value (business_value)    ██████░░░░░░░░░░░░░░░░░░░░░░░  18
  Scientific Novelty (scientific_novelty) █░░░░░░░░░░░░░░░░░░░░░░░░░   5
  Philosophical Depth (philosophical_depth) █████████████████████░░░░░░  60
  Meaning (meaning)                  ███████████████████████░░░░░░  66

【Cross-Dimensional Contrast】High vs Low Score Coexistence = Value Tension
  ⚡ Originality (originality) 78  vs  Business Value (business_value) 18
  ⚡ Originality (originality) 78  vs  Scientific Novelty (scientific_novelty) 5
```

The renderer displays:
- **Classification badge** (🔍 Discovery Target / 🟢 Current Success / 🔶 Trend Object / ⚪ Low Signal / ⭐ Innovation)
- **Current Value / Hidden Potential** bars
- **9-dimensional Value Vector** bar chart (strict scale; the higher the score, the rarer a long bar)
- **Disagreement** (dimensions where evaluators split, with variance severity)
- **Cross-dimensional contrast** (the tension between high and low scores — preserved without averaging)
- **Executive summary, consensus points, recommended actions, caveats**

## Evaluation Results Are Designed to Be Input

The evaluation results of this layer are not the final product; they are **input to a creation skill (a dedicated skill that synthesizes re-creation and improvement instructions)**.

The council does not generate the re-creation instructions itself. Instead, it leaves behind the **raw material** — in complete form — for the creation skill to synthesize instructions from:

| Material | How the creation skill uses it |
|----------|-------------------------------|
| `individual_reports[].weaknesses` | Weaknesses (with rationale) — identifying what to fix |
| `individual_reports[].improvement_suggestions` | Each evaluator's improvement suggestions — candidates for instructions |
| `individual_reports[].expected_disagreement_points` | Predicted objections from other perspectives — for balance |
| `disagreement_map` | Dimensions where evaluators split — clues for improvement |
| `value_vector` | Score distribution across all dimensions — deciding priorities |

(Implementing the dedicated skill that synthesizes re-creation instructions is a future phase.)

### The Evaluate → Recreate Loop

```
① Create
    ↓
② Evaluate (wisdom-council / mode:full)
    ↓
③ Check revision_direction (the direction for the next revision)
    ↓
④ The creation skill synthesizes instructions from the evaluation as input → recreate
    ↓
⑤ Re-evaluate
    ↓
⑥ Compare (check the improvement with compare_reports.py)
    ↓
⑦ Repeat until the goal is reached or improvement plateaus
```

**Iteration modes (`iteration`) — managing the revision direction:**

```bash
Skill: wisdom-council
Args: {"content": "...", "domain": "creative", "iteration": "confirm"}
```

| iteration | Behavior | When to use |
|-----------|----------|-------------|
| `confirm` (default) | Presents `revision_direction` after each round of evaluation, and proceeds to the next revision **only after confirmation** | Want to check the direction change at each step |
| `persistent` | Fixes `revision_direction` up front and **keeps revising along that direction** | Want to fix a direction and keep polishing |

- `confirm` = step-by-step confirmation mode (you can confirm "which direction to revise" at every turn)
- `persistent` = fixed-direction mode (shows the direction once and stays on it)
- Details: [references/revision-loop.md](wisdom-council-layer/references/revision-loop.md)

**Comparing improvement:**

```bash
python utils/compare_reports.py before.json after.json
```

Example output:

```
🔍 Classification: Discovery Target (no change)

  【Dimensional Improvement】
  Aesthetics (aesthetic)     62 → 75  ▲ +13
  Quality (quality)          65 → 72  ▲ +7
  Meaning (meaning)          66 → 70  ▲ +4
  Average change (9 dimensions): +3.8
```

**Loop guidelines:**
- **Evaluation never discards raw data** (the synthesized narrative is auxiliary; the material stays in the JSON)
- Don't judge by the average alone — also look at **variance and disagreement** (a single dimension may stand out while the whole stays unchanged)
- **Stop the loop when improvement plateaus** (over-revision risks losing what was originally good)

## Evaluator Roster

The 10 evaluators are **subagents** (`agents/{name}.md`). The council launches them in independent contexts to guarantee the independence of each evaluation. To call one individually, launch it with the Agent tool (see Level 1).

| Evaluator (agent name) | Core question | Score dimension |
|------------------------|---------------|-----------------|
| Originality Evaluator (`originality`) | Is it a meaningful deviation, or a recombination? | originality |
| Anti-Generic Filter (`anti-generic-filter`) | Is it not an AI-typical average solution? | quality |
| Aesthetic Critic (`aesthetic-critic`) | Does it create a deep aesthetic experience? | aesthetic |
| Emotional Impact Evaluator (`emotional-impact`) | Does it move the human heart? | emotional_impact |
| Future Potential Analyzer (`future-potential`) | Will its value rise in future environments? | future_potential |
| Business Value Evaluator (`business-value`) | Does it create value in the market? | business_value |
| Scientific Novelty Reviewer (`scientific-novelty`) | Does it push back the frontier of knowledge? | scientific_novelty |
| Philosophical Evaluator (`philosophical-evaluator`) | Can it change our worldview? | philosophical_depth |
| Quality Evaluator (`quality-evaluator`) | Is it technically complete? | quality |
| Meaning Evaluator (`meaning-evaluator`) | Does it give meaning to life? | meaning |

## Value Classification

Classifies along a two-dimensional matrix of Current Value × Hidden Potential.

```
             Hidden Potential
                  ↑
   Discovery Target   Innovation
────────────────┼──────────────────→  Current Value
   Low Signal        Current Success
```

The council's primary mission is to discover **Discovery Target** (currently rated low but with future potential).

## Roadmap

- **Phase 1 (complete)**: Universal Evaluation Core — 10 evaluator agents + council orchestrator skill + Value Vector + Value Report
- **Phase 2 (future)**: Hidden Potential Layer — Historical Analyzer, Mutation Detector, Timing Analyzer
- **Phase 3 (future)**: Debate Engine — multi-turn debate between evaluators
- **Phase 4 (future)**: Meta Value Layer — Bias Detection, Evaluation Critic, Value Evolution

## License

MIT License — Copyright (c) 2026 GL-Kageyama

## Core Statement

> In the AI era, the competitive frontier shifts
> from "how much you can create"
> to "how well you can recognize what is valuable."

Wisdom Council Layer is the value-discovery infrastructure for that purpose.
