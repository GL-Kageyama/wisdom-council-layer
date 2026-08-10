<!-- version: 1.0.0, last_updated: 2026-08-10 -->

**Language:** [English](value-vector-model.md) | [日本語](ja/value-vector-model.md) | [中文](zh/value-vector-model.md)

# Value Vector Model — Multi-dimensional Scoring

The flaw of simple numeric scoring is that it crushes value onto a single axis. The Wisdom Council Layer treats value as a **multi-dimensional vector**.

## Definition of the Value Vector

```
Value Vector = [originality, quality, aesthetic, emotional_impact,
                future_potential, business_value, scientific_novelty,
                philosophical_depth, meaning]
```

Each dimension is an integer score of 0-100, or `null` when that evaluator is not an expert in the dimension.

## Differences from a single score

| | Single score | Value Vector |
|--|---------|--------------|
| Information content | one number | a 9-dimensional distribution |
| Expressive power | "63 points" | "low in originality but high in future value" |
| Evaluator expertise | an average somebody | an expert in each dimension |
| Handling of contradictions | hidden | made explicit |

## Example: two ways of looking at the same work

**Work**: an avant-garde video work that failed commercially

```
Single score:  48 points (an average rating, no information)

Value Vector:
  originality:         82   ← high (evaluator: Originality)
  aesthetic:           71   ← medium-high (evaluator: Aesthetic)
  emotional_impact:    35   ← low (evaluator: Emotional)
  future_potential:    88   ← very high (evaluator: Future)
  business_value:      15   ← very low (evaluator: Business)
  philosophical_depth: 79   ← high (evaluator: Philosophical)
```

The very shape of the vector tells the story "not understood now, but with high future potential". A single score discards this information.

## Vector aggregation

The council (orchestrator) aggregates each evaluator's `value_vector_contribution`.

| Statistic | Meaning |
|--------|------|
| Mean | the central tendency of each dimension |
| Variance | how much the evaluators split (the strength of disagreement) |
| Range (min-max) | the two extremes of the assessments |
| Number of nulls | which dimensions went unevaluated (the validity of evaluator selection) |

### Interpreting the variance

| Variance | Meaning |
|------|------|
| Low variance (< 100) | Evaluators are nearly unanimous. A stable evaluation. |
| Medium variance (100-400) | A certain degree of viewpoint difference. Normal. |
| High variance (> 400) | A serious split of opinion. The content is causing some kind of division. **The most important signal.** |

## Mapping to classification

The Value Vector is reduced to two dimensions:

```
Current Value = w_q·quality + w_o·originality + w_a·aesthetic
              + w_e·emotional + w_b·business + w_s·scientific
              (non-expert dimensions omitted, weights normalized)

Hidden Potential = w_f·future_potential + w_m·meaning
                 + w_p·philosophical + w_o'·originality (future contribution)
```

This reduction is **a display for reporting purposes**; what is always stored is the complete vector.

## Why a vector

1. **Conflicts can be preserved**: the coexistence of high originality and low business value can be expressed.
2. **Withstands future re-evaluation**: when re-evaluated six months later, changes in each dimension of the vector can be tracked.
3. **Leverages evaluator expertise**: each evaluator responsibly scores only their own expert dimension.
4. **Aids human judgment**: humans gain the new role of "looking at the vector and deciding which dimensions to value".

## Future extensions

- **Time-series vectors**: overlay multiple evaluations of the same content to draw the value trajectory (Memory System).
- **Personalized weights**: humans adjust the weights of dimensions according to their own values.
- **Higher-dimensional interpretation**: allow adding dimensions beyond 9 (fit with the era, political influence, etc.).
