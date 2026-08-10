<!-- version: 1.0.0, last_updated: 2026-08-10 -->

**语言:** [English](../evaluator-taxonomy.md) | [日本語](../ja/evaluator-taxonomy.md) | [中文](evaluator-taxonomy.md)

# Evaluator Taxonomy

知慧评议会的评估者群并非由单一的价值观构成，而是由**多个独立的视角**构成。本文件定义了每位评估者的定位、负责领域，以及与其他评估者的关系。

## 评估者的类别

评估者分为3个层。

### 第1层：当前价值分析（Current Value Analysis）

评估内容**在当下**具有多大的价值。

| 评估者 | 视角 | 负责领域 |
|--------|------|--------------|
| Quality Evaluator | 完成度、技术质量 | 全部领域 |
| Originality Evaluator | 独创性、有意义的偏离 | 全部领域 |
| Aesthetic Critic | 美的完成度、表现力 | creative |
| Emotional Impact Evaluator | 对情感的影响 | creative, social |
| Business Value Evaluator | 市场性、可实现性 | business, digital |
| Scientific Novelty Reviewer | 科学新颖性 | scientific |

### 第2层：潜在价值发现（Hidden Potential Discovery）

发现当前尚未被评估的**未来的可能性**。

| 评估者 | 视角 | 负责领域 |
|--------|------|--------------|
| Future Potential Analyzer | 长期可能性、时代契合度 | 全部领域 |
| Meaning Evaluator | 意义、思想性 | cultural, social |

### 第3层：基准层（Meta Layer）

动摇评价本身的前提。

| 评估者 | 视角 |
|--------|------|
| Philosophical Evaluator | 对世界观、对人的理解的影响 |
| Anti-Generic Filter | 平庸性的排除（横向作用于所有评估者） |

## 各评估者的核心问题

| 评估者 | 核心问题 |
|--------|----------|
| Quality Evaluator | 这在技术上是否完成？ |
| Originality Evaluator | 这是否以有意义的方式偏离了既有之物？ |
| Aesthetic Critic | 这是否创造了美的体验？ |
| Emotional Impact Evaluator | 这是否打动了人心？ |
| Business Value Evaluator | 这是否能在市场上创造价值？ |
| Scientific Novelty Reviewer | 这是否推进了知识的前沿？ |
| Future Potential Analyzer | 它是否会因未来的环境变化而价值上升？ |
| Meaning Evaluator | 这是否深化了对人之存在的理解？ |
| Philosophical Evaluator | 这是否有可能改变世界观？ |
| Anti-Generic Filter | 这是否是AI容易给出的平均解？ |

## 评估者之间的关系

### 互补关系

- **Originality ↔ Quality**：独创性越高的作品，完成度往往越低。这种紧张关系很重要。
- **Future Potential ↔ Business Value**：当前市场评价越低的事物，未来价值有时反而越高（Discovery Target）。
- **Emotional Impact ↔ Anti-Generic**：情感操控（sentimentality）是平庸性的一种。

### 对立结构

这种对立**不应被平均化**。相反，冲突正是价值的重要征兆。

```
高独创性 + 低完成度 = 未来杰作的可能性
高商业价值 + 低哲学深度 = Trend Object 的可能性
高意义性 + 低市场性 = Discovery Target 的可能性
```

## 与 Value Vector 的对应

每位评估者只对 Value Vector 的特定维度作出贡献（其他维度为 null）。

```
Value Vector:
[originality, quality, aesthetic, emotional_impact,
 future_potential, business_value, scientific_novelty,
 philosophical_depth, meaning]
```

## 合议中的评估者选择

合议编排器（orchestrator）根据领域选择评估者。

| 领域 | 必选评估者 | 可选评估者 |
|----------|-----------|-----------|
| creative | originality, anti-generic-filter, aesthetic-critic, emotional-impact | meaning-evaluator, future-potential, philosophical-evaluator |
| scientific | originality, scientific-novelty, anti-generic-filter | future-potential, quality-evaluator |
| business | business-value, originality, quality-evaluator | future-potential, anti-generic-filter |
| social | emotional-impact, meaning-evaluator, quality-evaluator | future-potential, philosophical-evaluator |
| digital | quality-evaluator, originality, anti-generic-filter | business-value, future-potential |
| cultural | meaning-evaluator, philosophical-evaluator, originality | aesthetic-critic, emotional-impact, future-potential |
