<!-- version: 1.0.0, last_updated: 2026-08-10 -->

**语言:** [English](../value-classification.md) | [日本語](../ja/value-classification.md) | [中文](value-classification.md)

# Value Classification Model

知慧评议会不是用简单的分数，而是用**当前价值 × 潜在价值**的二维矩阵对内容进行分类。

## 2x2 矩阵

```
             Hidden Potential（潜在价值）
                  ↑
                  │
   Discovery Target   Innovation
────────────────┼──────────────────→  Current Value（当前价值）
   Low Signal        Current Success
                  │
                  ↓
```

## 4种分类

### Current Success（当前价值高）
- **定义**：当前评价高，并且实际在产生价值。
- **风险**：持续性不明。可能只是赶上了潮流。
- **合议的职责**：公正地评价当前的成功，同时保持对可持续性的怀疑。
- **例**：畅销商品、热门作品

### Discovery Target（当前评价低但具有未来可能性）
- **定义**：当前评价有限，但随着未来环境变化，价值上升的可能性很高。
- **这是合议的主要使命。** 在大规模生成的时代，最值得发现的是这里。
- **合议的职责**：即使当前不被理解，也要记录其征兆，并标记为"长期观察对象"。
- **例**：初期被否定的艺术运动、最初被嘲笑的技术革新

### Trend Object（当前评价高但长期价值不明）
- **定义**：搭乘流行而当前评价较高，但是否具有深层的持续价值尚不明确。
- **合议的职责**：不否定当前价值，同时从长期视角提出怀疑。
- **例**：走红但缺乏实体的产品、一时的潮流作品

### Low Signal（当下没有价值征兆）
- **定义**：当前价值与潜在价值均未检测到。
- **合议的职责**：保留判断的同时，解释为何没有征兆。同时保留评估者可能只是遗漏了某个因素的可能性。
- **例**：平庸的AI生成内容

## 分类的导出

分类由 Value Vector 的各维度分数导出。

| 轴 | 构成要素 |
|----|---------|
| Current Value | quality、originality（当前）、aesthetic、emotional、business、scientific（当前）的加权平均 |
| Hidden Potential | future_potential、meaning、philosophical、originality（未来）的加权平均 |

### 阈值的参考标准

由于严格评分（`scoring-strictness.md`）将中位数设为约30，分类阈值也随之重新调整。

| 分类 | Current Value | Hidden Potential |
|------|---------------|------------------|
| Current Success | 高 (≥ 45) | 低 (< 35) |
| Discovery Target | 低 (< 35) | 高 (≥ 45) |
| Trend Object | 高 (≥ 45) | 中 (35-44) |
| Innovation | 高 (≥ 45) | 高 (≥ 45) |
| Low Signal | 低 (< 35) | 低 (< 35) |

※ 阈值是开始时的参考标准，将在 Meta Value Layer 实现时以实际数据调整。

## 重要注意事项

- 分类是**观察的开始，而非判断的终点**。
- 被判定为 Discovery Target 的内容，需要随时间的推移进行再评价（由未来的 Memory System 追踪）。
- 每位评估者独立分类，合议综合这些分类。分类在评估者之间产生分歧这一事实本身就是重要的信号。
