<!-- version: 1.0.0, last_updated: 2026-08-10 -->

**Language:** [English](revision-loop.md) | [日本語](ja/revision-loop.md) | [中文](zh/revision-loop.md)

# Revision Loop — Iteration Modes for the Create → Evaluate → Re-create Loop

Two modes that control how the **evaluate → revise loop** proceeds.

## Loop basics

```
① Create (leave generation to appropriate other means)
② Evaluate (wisdom-council)
③ Check revision_direction (the next revision direction)
④ Re-create (the creation skill applies the direction)
⑤ Re-evaluate → confirm the degree of improvement with compare_reports.py
⑥ Repeat until the goal is reached or improvement plateaus
```

## Iteration modes (`iteration`)

Selected via the `iteration` field of `ARGUMENTS`.

### Mode 1: `confirm` (step-by-step confirmation · default)

**After each turn's evaluation, present the next revision direction, confirm it, and then proceed.**

```
Evaluate → present revision_direction → human/creation skill confirms the direction
  → re-create → re-evaluate → present and confirm the direction again → …
```

- The direction can be checked **at each step** (prevents over-correction and drift from the direction).
- Each turn's `revision_direction.statement` serves as the proposal asking "is this direction OK?".
- **Best suited for**: a stage where you do not yet have confidence in the work's direction. You want to polish while confirming the next move each time.

### Mode 2: `persistent` (fixed direction)

**Determine the revision direction at the first evaluation, then keep revising along that direction.**

```
First evaluation → determine (fix) revision_direction
  → re-create (along the direction) → re-evaluate (report the degree of attainment of the direction) → re-create (same direction) → …
```

- The direction does **not change**. Each iteration only varies the **concretization of execution** along the same axis.
- Each iteration's evaluation reports the **degree of attainment** (how close you came) with respect to `revision_direction.axis`, and does not reconsider the direction itself.
- **Best suited for**: a stage where the direction is already set and you want to polish deeply along it.

## revision_direction (a field of the Value Report)

```json
"revision_direction": {
  "statement": "Next revision direction (1-2 sentences)",
  "axis": ["Dimensions/elements to raise or change"],
  "preserve": ["Strengths that must not be lost"],
  "iteration": "confirm|persistent"
}
```

- `confirm` mode: this is a **proposal**; the human/creation skill confirms it before applying it.
- `persistent` mode: it is fixed at the first evaluation, and subsequent iterations maintain this direction.

## Loop guidelines

- **Keep the dimensions that were improved** (`preserve`) — do not break existing strengths through revision.
- **Raise the dimensions that were lowered** (`axis`) — the direction is brought down to the concrete ("change X to Y").
- Do not judge by the average alone; also look at **variance and disagreement**.
- **Stop when improvement plateaus** (over-correction loses the original good qualities).

## References

- `wisdom-council/SKILL.md` — implementation of the iteration modes
- `utils/render_report.py` — display of `revision_direction`
- `utils/compare_reports.py` — comparison of the degree of improvement between iterations
