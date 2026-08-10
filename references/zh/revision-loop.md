<!-- version: 1.0.0, last_updated: 2026-08-10 -->

**语言:** [English](../revision-loop.md) | [日本語](../ja/revision-loop.md) | [中文](revision-loop.md)

# Revision Loop — 创作→评价→再创作循环的迭代模式

控制**评价→修正循环**如何推进的2种模式。

## 循环的基本流程

```
① 创作（生成交由合适的其他手段）
② 评价（wisdom-council）
③ 确认 revision_direction（下次修正方向）
④ 再创作（创作技能应用 direction）
⑤ 再评价 → 用 compare_reports.py 确认改善度
⑥ 重复直至达成目标或到达天花板
```

## 迭代模式（`iteration`）

通过 `ARGUMENTS` 的 `iteration` 字段选择。

### 模式1: `confirm`（逐次确认・默认）

**在每轮评价之后，提示下次的修正方向，确认后再继续。**

```
评价 → 提示 revision_direction → 人类/创作技能确认方向
  → 再创作 → 再评价 → 再次提示并确认方向 → …
```

- 可以在每一步**检查方向**（防止过度修正与偏离方向）。
- 每轮的 `revision_direction.statement` 成为"这个方向可以吗？"的提案。
- **适用场景**：对作品的方向性还没有自信的阶段。希望在每次确认下一步的同时进行打磨。

### 模式2: `persistent`（方向固定）

**在首次评价时确定修正方向，并沿该方向持续修正。**

```
首次评价 → 确定（固定）revision_direction
  → 再创作（沿方向） → 再评价（报告对方向的到达度） → 再创作（同一方向） → …
```

- **不改变方向**。每次迭代只改变对同一轴**执行的具体化**。
- 每次迭代的评价报告对 `revision_direction.axis` 的**到达度**（接近了多少），不重新考虑方向本身。
- **适用场景**：方向已定，希望在该方向上深入打磨的阶段。

## revision_direction（Value Report 的字段）

```json
"revision_direction": {
  "statement": "下次修改方向（1-2句）",
  "axis": ["应提升/改变的维度或要素"],
  "preserve": ["不可丢失的优势"],
  "iteration": "confirm|persistent"
}
```

- `confirm` 模式：这是**提案**，由人类/创作技能确认后再应用。
- `persistent` 模式：在首次评价时确定，后续迭代保持这一方向。

## 循环的指导方针

- **保持提升过的维度**（`preserve`）—— 修正时不破坏既有优势。
- **提升下降的维度**（`axis`）—— 方向要落到具体（"将X改为Y"）。
- 不要只看平均，也要看**分散度与分歧**。
- 当改善**到达天花板时停止**（过度修正会失去原有的优点）。

## 参考

- `wisdom-council/SKILL.md` — 迭代模式的实现
- `utils/render_report.py` — `revision_direction` 的显示
- `utils/compare_reports.py` — 迭代间的改善度比较
