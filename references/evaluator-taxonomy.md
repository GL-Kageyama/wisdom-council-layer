<!-- version: 1.0.0, last_updated: 2026-08-10 -->

**Language:** [English](evaluator-taxonomy.md) | [日本語](ja/evaluator-taxonomy.md) | [中文](zh/evaluator-taxonomy.md)

# Evaluator Taxonomy

The evaluator group of the Wisdom Council Layer is composed not of a single value system but of **multiple independent viewpoints**. This document defines each evaluator's position, responsible domains, and relationships with the other evaluators.

## Evaluator categories

The evaluators are divided into three layers.

### Layer 1: Current Value Analysis

Evaluates how much value the content has **at the present moment**.

| Evaluator | Viewpoint | Responsible domains |
|--------|------|--------------|
| Quality Evaluator | Completeness, technical quality | All domains |
| Originality Evaluator | Originality, meaningful deviation | All domains |
| Aesthetic Critic | Aesthetic completion, expressive power | creative |
| Emotional Impact Evaluator | Emotional impact | creative, social |
| Business Value Evaluator | Marketability, feasibility | business, digital |
| Scientific Novelty Reviewer | Scientific novelty | scientific |

### Layer 2: Hidden Potential Discovery

Discovers **future possibilities** that are not currently evaluated.

| Evaluator | Viewpoint | Responsible domains |
|--------|------|--------------|
| Future Potential Analyzer | Long-term potential, fit with the times | All domains |
| Meaning Evaluator | Meaning, intellectual depth | cultural, social |

### Layer 3: Meta Layer

Shakes the very premises of evaluation.

| Evaluator | Viewpoint |
|--------|------|
| Philosophical Evaluator | Impact on worldview and understanding of humanity |
| Anti-Generic Filter | Removal of mediocrity (works cross-sectionally across all evaluators) |

## Core question of each evaluator

| Evaluator | Core question |
|--------|----------|
| Quality Evaluator | Is this technically complete? |
| Originality Evaluator | Does this deviate from the existing in a meaningful way? |
| Aesthetic Critic | Does this create an experience of beauty? |
| Emotional Impact Evaluator | Does this move the human heart? |
| Business Value Evaluator | Does this create value in the market? |
| Scientific Novelty Reviewer | Does this push forward the frontier of knowledge? |
| Future Potential Analyzer | Will its value rise as the environment changes in the future? |
| Meaning Evaluator | Does this deepen our understanding of human existence? |
| Philosophical Evaluator | Does this have the potential to change our worldview? |
| Anti-Generic Filter | Isn't this the average solution an AI would readily produce? |

## Relationships between evaluators

### Complementary relationships

- **Originality ↔ Quality**: Highly original works are often less complete. This tension is important.
- **Future Potential ↔ Business Value**: What is valued low by the current market sometimes has higher future value (Discovery Target).
- **Emotional Impact ↔ Anti-Generic**: Emotional manipulation (sentimentality) is a form of mediocrity.

### Conflict structures

These conflicts should **not be averaged**. Rather, conflict is an important sign of value.

```
High originality + low completion = the possibility of a future masterpiece
High business value + low philosophical depth = the possibility of a Trend Object
High meaningfulness + low marketability = the possibility of a Discovery Target
```

## Correspondence with the Value Vector

Each evaluator contributes to a specific dimension of the Value Vector (the other dimensions are null).

```
Value Vector:
[originality, quality, aesthetic, emotional_impact,
 future_potential, business_value, scientific_novelty,
 philosophical_depth, meaning]
```

## Evaluator selection in the council

The council orchestrator selects evaluators according to the domain.

| Domain | Required evaluators | Optional evaluators |
|----------|-----------|-----------|
| creative | originality, anti-generic-filter, aesthetic-critic, emotional-impact | meaning-evaluator, future-potential, philosophical-evaluator |
| scientific | originality, scientific-novelty, anti-generic-filter | future-potential, quality-evaluator |
| business | business-value, originality, quality-evaluator | future-potential, anti-generic-filter |
| social | emotional-impact, meaning-evaluator, quality-evaluator | future-potential, philosophical-evaluator |
| digital | quality-evaluator, originality, anti-generic-filter | business-value, future-potential |
| cultural | meaning-evaluator, philosophical-evaluator, originality | aesthetic-critic, emotional-impact, future-potential |
