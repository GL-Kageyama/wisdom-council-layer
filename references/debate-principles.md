<!-- version: 1.0.0, last_updated: 2026-08-10 -->

**Language:** [English](debate-principles.md) | [日本語](ja/debate-principles.md) | [中文](zh/debate-principles.md)

# Debate Principles — Preserving Disagreement

The core belief of the Wisdom Council Layer:

> **Truth emerges from the collision of different viewpoints, not from their averaging.**

This document defines how the council handles disagreement among evaluators.

## Principle 1: Disagreement is not a defect, but part of the output

In a single-evaluator system, differences of opinion are removed as "noise". In the Wisdom Council Layer, disagreement is a **first-class output**.

- When evaluators assign widely different scores on the same dimension, those scores should not be averaged.
- The **reason** for the disagreement is precisely the information essential to understanding the content.

## Principle 2: Unanimity is itself suspicious

If 10 evaluators all assign the same score, the following possibilities arise:

1. The evaluators are not thinking independently (conformity)
2. The content is extremely mediocre, and every viewpoint arrives at the same assessment (a true red flag)
3. The evaluation criteria are biased

Suspecting "unanimity" is a duty incumbent on every evaluator.

## Principle 3: Rebuttal is the evaluator's duty

Each evaluator must predict how their own assessment would be attacked from the perspectives of the other evaluators, and report this explicitly.

```
Example:
- Originality Evaluator: highly original (85 points)
- Business Value Evaluator: low marketability (25 points)
- This conflict itself is the key information: "this work is niche but groundbreaking"
```

## Principle 4: Distinguish the types of conflict

Not all disagreements carry the same weight.

| Type of conflict | Meaning | How the council treats it |
|-----------|------|-----------|
| **Difference of viewpoint** (evaluating the same facts with different value systems) | Healthy. A reflection of pluralistic values | Preserve it and record both sides |
| **Difference of factual recognition** (interpreting the same thing differently) | One side may be misrecognizing the facts | Re-examine the evidence and correct the misrecognition |
| **Score scatter** (nearly the same opinion, but the numbers drift) | Normal variation | Record as a range |

## Principle 5: Visualize disagreement numerically

The Value Report includes a **Disagreement Map**. It shows, as a heatmap, the variance of evaluator scores on each dimension.

- A dimension with high variance = a dimension on which evaluators split = the dimension with the most information
- Preserve both sides of this dimension together with each side's rationale

## Principle 6: Disagreement itself is a sign of value

Historically, innovative works have been "polarizing".

```
A painting once ridiculed → ridiculed at first → now regarded as a masterpiece
An avant-garde work initially rejected → rejected → now a turning point
```

Therefore, **content on which evaluators sharply split is itself worthy of attention**. Go beyond a simple "good/bad" and evaluate the quality and depth of the debate.

## Principle 7: The council does not render a verdict

The role of the council (orchestrator) is not to "determine the correct answer".

- Explore possibilities from different value systems
- Provide an intellectual support foundation for human judgment
- **The final value judgment is the responsibility of humans** (the UVIN philosophy)

## Phase 3 (future) expansion

Currently, each evaluator reports "predictions from others' viewpoints" in a single turn. In the future Debate Engine:

- Evaluators read one another's assessments and **counter-rebut**
- Record how viewpoints change through multi-turn debate
- Allow the debate itself to generate new insights
