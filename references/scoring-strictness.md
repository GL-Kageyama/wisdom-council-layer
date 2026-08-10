<!-- version: 1.0.0, last_updated: 2026-08-10 -->

**Language:** [English](scoring-strictness.md) | [日本語](ja/scoring-strictness.md) | [中文](zh/scoring-strictness.md)

# Scoring Strictness Doctrine — Strict Scoring Standards

This layer deliberately performs **strict scoring**. The reason is that the purpose of the council is not to "praise good things" but to "see through what is truly valuable". Loose scoring pushes mediocre works up into high ratings and undermines the council's discriminative power.

## Fundamental principles

1. **High scores are given rarely.** Only works that prove "true excellence" score 60 or above. 75 or above is exceptional. 85 or above is almost never given.
2. **Mediocrity falls into low scores.** Works that are "safe but unremarkable" fall into the 20-40 range. High completion alone does not produce a high score.
3. **The standard is pulled toward strictness.** Most everyday output, including AI-generated content, is distributed below 50. Place the median of the distribution at **around 30**. In other words, "decently good" work falls into 30-45.
4. **Red flags are strongly penalized.** A single serious red flag (generic expression, emotional manipulation, false novelty, etc.) pulls the score down by 25-40 points even when the other dimensions are good.

## Common score bands (a yardstick common to all evaluators)

| Band | Meaning | Expected frequency |
|----|------|-------------|
| 0-10 | Serious defect, no sign of value | Give rarely |
| 11-30 | Weak. Partially inferior | Often |
| 31-50 | Safe, mediocre. Passably done | **The largest population** |
| 51-70 | Truly good. A sign of excellence | Somewhat rare |
| 71-90 | Exceptional. Outstanding value | Rare |
| 91-100 | Historical significance | Almost never given |

**The iron rule of judgment**: Before giving a score, ask yourself "does this really have value exceeding 50?" When in doubt, score low. "Decently good" does not reach 50.

## How to apply

Each evaluator follows this doctrine and strictly scores their own "primary dimension".

- Before giving a score, ask "does this really have value exceeding 60?"
- When in doubt, score on the lower side. The role of the council is **discovery**, not **approval**.
- Give classifications strictly as well. Use `current_success` and `innovation` only when the evidence is strong.

## Supplementary notes

- This strictness is meant to increase the **relative discriminative power** of scores; it does not claim absolute correctness.
- It serves as the baseline for introducing per-evaluator strictness calibration (bias detection) in the future Meta Value Layer.
