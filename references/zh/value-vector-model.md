<!-- version: 1.0.0, last_updated: 2026-08-10 -->

**语言:** [English](../value-vector-model.md) | [日本語](../ja/value-vector-model.md) | [中文](value-vector-model.md)

# Value Vector Model — 多维评分

单纯点数评分的缺点，在于把价值压扁到单一轴线上。知慧评议会将价值视为**多维向量**。

## Value Vector 的定义

```
Value Vector = [originality, quality, aesthetic, emotional_impact,
                future_potential, business_value, scientific_novelty,
                philosophical_depth, meaning]
```

每个维度是 0-100 的整数分数；若该评估者并非该维度专家，则为 `null`。

## 与单一点数的差异

| | 单一点数 | Value Vector |
|--|---------|--------------|
| 信息量 | 1个数字 | 9维的分布 |
| 表现力 | "63分" | "独创性低但未来价值高" |
| 评估者的专业性 | 平均化的某个人 | 各维度的专家 |
| 对矛盾的处理 | 被隐藏 | 被明确展示 |

## 例：同一作品的两种看法

**作品**：商业上失败的前卫影像作品

```
单一点数:  48分（平均的评价，没有信息）

Value Vector:
  originality:         82   ← 高（评估者: Originality）
  aesthetic:           71   ← 中高（评估者: Aesthetic）
  emotional_impact:    35   ← 低（评估者: Emotional）
  future_potential:    88   ← 非常高（评估者: Future）
  business_value:      15   ← 非常低（评估者: Business）
  philosophical_depth: 79   ← 高（评估者: Philosophical）
```

向量本身的形态就讲述着"当下不被理解，但未来的可能性很高"这一故事。单一点数会丢弃这些信息。

## 向量的合成

合议（编排器 orchestrator）汇总各评估者的 `value_vector_contribution`。

| 统计量 | 含义 |
|--------|------|
| 平均 | 各维度的中心倾向 |
| 分散度（variance） | 评估者分歧的程度（分歧的强度） |
| 范围 (min-max) | 评价的两端 |
| null的数量 | 哪些维度未被评价（评估者选择的合理性） |

### 分散度的解读

| 分散度 | 含义 |
|------|------|
| 低分散 (< 100) | 评估者之间几乎意见一致。稳定的评价。 |
| 中分散 (100-400) | 有一定程度的视角差异。正常。 |
| 高分散 (> 400) | 意见严重割裂。内容正在引发某种分裂。**最重要的信号。** |

## 向分类的映射

Value Vector 被压缩为2维：

```
Current Value = w_q·quality + w_o·originality + w_a·aesthetic
              + w_e·emotional + w_b·business + w_s·scientific
              （省略非专业维度，权重归一化）

Hidden Potential = w_f·future_potential + w_m·meaning
                 + w_p·philosophical + w_o'·originality（未来贡献）
```

这种压缩**是为了报告而作的显示**，保存的始终是完整的向量。

## 为什么要用向量

1. **能够保存对立**：可以表达高独创性与低商业价值的共存。
2. **经得起将来的再评价**：6个月后重新评价时，可以追踪向量各维度的变化。
3. **发挥评估者的专业性**：每位评估者只对自己擅长的维度负责评分。
4. **有助于人的判断**：人获得了"观看向量，决定重视哪个维度"这一新的角色。

## 将来的扩展

- **时序向量**：叠加对同一内容的多次评价，描绘价值的轨迹（trajectory）（Memory System）。
- **权重的个性化**：人根据自己的价值观调整维度的权重。
- **高维解释**：允许添加超过9维的维度（时代性、政治影响等）。
