<!-- version: 1.1.0, last_updated: 2026-08-10 -->

**语言:** [English](../calibration-suite.md) | [日本語](../ja/calibration-suite.md) | [中文](calibration-suite.md)

# Calibration Suite — 校准套件

Wisdom Council Layer 的 10 位评估者代理各有 **3 种语言版本**（en / ja / zh）。校准要回答关于这些语言版本的**两个不同的问题**：

1. **静态漂移** — 翻译过程中*数字*（权重、分数带、校准值）是否发生了偏移？
2. **行为漂移** — 面对*相同的数字*，LLM 在不同语言下打分时是否会使用不同的严格程度？

静态检查**已实现 · PASS**。运行时检查**待会话重启**（见 [§2](#2-运行时校准未执行)）。

## 1. 静态校准漂移检查（已实现 · PASS）

验证全部 30 个代理文件（10 位评估者 × 3 种语言）的数值校准契约在语言间完全一致。由此排除「翻译过程中数字改变」类漂移（例如权重从 `0.35` 悄悄变成 `0.30`）。

### 检查对象

对 10 位评估者各自的 en / ja / zh：

| 检查项 | 提取来源 | 格式 |
|-------|---------|------|
| **维度权重** | `#### N. … — weight 0.35` 标题行 | 4 个小数，保持顺序 |
| **分数带** | Scoring Guidelines 小节中的 `- 0-10:` … `- 91-100:` 列表项 | 6 个范围 |
| **校准表** | Calibration Reference 表的第 2 列 | `N-N` 范围（忽略注释） |

### 运行方法

```bash
python utils/check_calibration_drift.py        # 每个评估者的 PASS/FAIL，人类可读
python utils/check_calibration_drift.py --json # 机器可读（供 CI 使用）
```

退出码 `0` = PASS、`1` = FAIL。脚本对下述陷阱做了防御——即使提取结果为空也会报告 FAIL，绝不会静默 PASS。

### 当前状态

**PASS — 2026-08-10。** 全部 10 位评估者 × 3 项检查在 en / ja / zh 间完全一致。（分数带对 10 位评估者全部相同；权重与校准值按评估者各异，但在语言间一致——例如 `business-value` → `15-30 / 40-60 / 60-80 / 80-95`、`anti-generic-filter` → `10-25 / 30-50 / 60-80 / 70-90`。）

**PASS 不证明什么：** 相同的数字并不保证 LLM 会在各语言中按同样的严格程度应用。那是行为漂移，只能通过运行时检查来测量。

## 2. 运行时校准（未执行）

> **可执行手册**：重启后可直接复制运行的详细版步骤见 [`references/runtime-calibration-runbook.md`](../runtime-calibration-runbook.md)。以下为要点摘要。

### 为何受阻

代理名称在**会话启动时**载入注册表。新创建的 `-ja` / `-zh` 符号链接要到重启后才可解析——当前会话内 Agent tool 会报告 `Agent type 'originality-ja' not found`。

在这种状态下运行技能，会按 SKILL.md 的 R3 对策**静默回退到无后缀（英语）代理**，得到看似「三种语言一致」、实则「三次都以英语评估」的无意义结果。重启后运行可避免这一情况。

### 步骤（重启后）

1. 确认带后缀的代理已注册，例如 `ls ~/.claude/agents/originality-ja.md`。
2. 准备**同一内容翻译成 3 种语言**的样本——文本本身的语言会影响评分，因此跨语言比较必须使用「含义相同的句子」。
3. 每种语言运行一次技能：
   ```
   Skill: wisdom-council
   Args: {"content": "<3语言版文本>", "content_type": "text", "domain": "creative", "lang": "en|ja|zh"}
   ```
4. 收集输出 JSON 中的 `primary_score` / `dimension_scores.*.score`，用 `utils/compare_reports.py` 或小型聚合脚本比较跨语言分布（中位数 / 均值 / 方差）。
5. **判定**（依据 `references/scoring-strictness.md`）：严格评分的信条是否得到复现——中位数≈30、平庸作品低于 50？若出现系统性语言偏差（例如英语整体偏高/偏低），则以英语提示词为规范源进行修正，再重新翻译 ja / zh。

## 3. 陷阱（构建静态检查时学到的教训）

这些来自「10/10 不一致」的结果其实全部是**检查脚本自身的 bug**——内容漂移为零。值得写进任何未来的检查器。

1. **空列表相等是「假 PASS」。** `[] == [] == []` 为 `True`。即使完全提取不到任何内容，一致性判断也会通过。**对策**：同时要求非空且相等，并打印一个提取示例，让提取全失败变得可见。
2. **`##+` 正则吞掉 `####` 标题。** 用 `r"##+ .*"` 匹配小节，会让 `#### 1. …` 维度标题匹配到随后的 "High score" 行，从而在小节中部错误切分。**对策**：仅按 `^#{2,3}` 切分小节，将 `####` 行保留在父小节正文内。
3. **校准值带有尾部注释。** `| … | 75-95 (quality/marketability expected to be low) |` — 若把 `N-N` 锚定在 `|` 边界会漏掉该值。**对策**：在单元格内任意位置提取 `N-N`。
4. **CJK 字符属于 `\w`。** `\b2-3\b` 无法匹配 `- 2-3段落`（数字后紧跟 CJK `\w`），而英文 `- 2-3 paragraph` 以空格分隔。**对策**：以行首 / 单元格边界判定，而非 `\b`。

## 参考

- `references/runtime-calibration-runbook.md` — 运行时检查的执行手册（会话重启后运行）
- `references/scoring-strictness.md` — 运行时检查的判定基准：严格评分信条（中位数≈30）
- `references/evaluator-taxonomy.md` — 10 位评估者及其负责的领域
- `utils/check_calibration_drift.py` — 已实现的静态检查器
