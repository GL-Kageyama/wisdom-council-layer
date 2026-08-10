<!-- version: 1.0.0, last_updated: 2026-08-10 -->

**Language:** [English](value-classification.md) | [日本語](ja/value-classification.md) | [中文](zh/value-classification.md)

# Value Classification Model

The Wisdom Council Layer classifies content not with a simple score, but with a two-dimensional matrix of **current value × hidden potential**.

## The 2x2 matrix

```
             Hidden Potential
                  ↑
                  │
   Discovery Target   Innovation
────────────────┼──────────────────→  Current Value
   Low Signal        Current Success
                  │
                  ↓
```

## The four classifications

### Current Success (high current value)
- **Definition**: Rated highly at present, and actually producing value.
- **Risk**: Sustainability is unclear. It may simply have ridden a trend.
- **Role of the council**: Fairly assess the current success while maintaining doubt about its sustainability.
- **Examples**: hit products, talked-about works

### Discovery Target (currently low-rated but with future potential)
- **Definition**: Limited in current assessment, but likely to rise in value with future environmental changes.
- **This is the council's primary mission.** In the era of mass generation, what is most worth finding is here.
- **Role of the council**: Even if not understood now, record its signs and mark it as a "long-term observation target".
- **Examples**: art movements denied in their early days, technological innovations first ridiculed

### Trend Object (currently high-rated but long-term value unclear)
- **Definition**: Rated highly now by riding a trend, but whether it has deep lasting value is unclear.
- **Role of the council**: Without denying its current value, present skepticism from a long-term perspective.
- **Examples**: products that went viral but lack substance, one-off trend works

### Low Signal (no sign of value at present)
- **Definition**: Neither current value nor hidden potential is detected.
- **Role of the council**: Withhold judgment while explaining why no signs exist. Also keep open the possibility that the evaluators have simply overlooked something.
- **Examples**: average AI-generated content

## Deriving the classification

The classification is derived from the dimension scores of the Value Vector.

| Axis | Components |
|----|---------|
| Current Value | weighted average of quality, originality (current), aesthetic, emotional, business, scientific (current) |
| Hidden Potential | weighted average of future_potential, meaning, philosophical, originality (future) |

### Threshold guidelines

Because strict scoring (`scoring-strictness.md`) sets the median around 30, the classification thresholds are also re-adjusted to match.

| Classification | Current Value | Hidden Potential |
|------|---------------|------------------|
| Current Success | high (≥ 45) | low (< 35) |
| Discovery Target | low (< 35) | high (≥ 45) |
| Trend Object | high (≥ 45) | medium (35-44) |
| Innovation | high (≥ 45) | high (≥ 45) |
| Low Signal | low (< 35) | low (< 35) |

※ The thresholds are starting guidelines and will be adjusted with real data when the Meta Value Layer is implemented.

## Important notes

- Classification is **the beginning of observation, not the end of judgment**.
- Content classified as a Discovery Target requires re-evaluation over time (to be tracked by the future Memory System).
- Each evaluator classifies independently, and the council synthesizes these. The fact that classifications split among evaluators is itself an important signal.
