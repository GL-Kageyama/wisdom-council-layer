<!-- version: 1.0.0, last_updated: 2026-08-10 -->

**语言:** [English](../runtime-calibration-runbook.md) | [日本語](../ja/runtime-calibration-runbook.md) | [中文](runtime-calibration-runbook.md)

# 运行时校准 执行手册

> 2026-08-10 创建。将 [`references/calibration-suite.md`](../calibration-suite.md) 的 §2 步骤，落实为可在**会话重启后**直接执行的流程。
>
> **执行本手册的前提**：会话已重启，且 `-ja` / `-zh` 代理已注册到注册表。**不要在同一个会话内执行**（所有代理会静默回退到英文，产生无意义的「三语一致」结果）。

---

## 0. 前提确认（重启后最先做的事）

在以下条件全部满足前不要继续。

- [ ] `-ja` / `-zh` 代理的 symlink 存在（两个位置都有）
  ```bash
  ls -l ~/.claude/agents/originality-ja.md ~/.claude/agents/originality-zh.md
  ls -l .claude/agents/originality-ja.md
  ```
- [ ] **实际确认**注册表可以解析。在 CLI 中打开 `/agents` 看到 `originality-ja` / `originality-zh` 出现在列表中，或用 Agent 工具尝试 `subagent_type: originality-ja` 并非 "not found"。**必须以实测确认为准**（文件存在不代表注册表已反映，注册表在会话启动时加载）。
- [ ] 静态漂移检查 PASS（确认翻译后的数值契约在三语间一致）
  ```bash
  cd <wisdom-council-layer>
  python3 utils/check_calibration_drift.py
  # → RESULT: PASS — no numeric drift across en / ja / zh（exit 0）
  ```

## 1. 准备测试内容

语言间比较使用「**同一含义的文章翻译成 3 种语言**」的 1 组。因为文本本身的语言会影响评估，准备 3 个不同作品不构成比较。

**选择条件：**
- 建议选择能考验评估者判别力的作品——「佳作但非杰作」的程度（用于测量中位数≈30 的严格度。完美的杰作或明显的劣作在各语言中都会得到相近的分数，难以看出严格度的差异）。
- 源语言可以是英文或日文，但**将 3 个语言版本合并保存在 1 个文件中**，便于之后做差异对比。

**推荐格式**（如 `/tmp/calib-samples.md`）：

```markdown
# Calibration Sample（三语版本）

## en
<原文写在这里>

## ja
<日文译文写在这里>

## zh
<中文译文写在这里>
```

> 复用现有 `examples/` 中的作品时，将该作品的 input 翻译成 3 种语言使用。例如 `examples/creative-poem-sea/` 等。

## 2. 在 3 种语言下执行评估

Wisdom Council 技能**每种语言执行 1 次**，共 3 次。`content` 只传**该语言版本的文本**（传入全部语言版本会让评估者读全部内容而混乱）。

```
Skill: wisdom-council
Args: {"content": "<en版文本>", "content_type": "text", "domain": "creative", "lang": "en"}
```

```
Skill: wisdom-council
Args: {"content": "<ja版文本>", "content_type": "text", "domain": "creative", "lang": "ja"}
```

```
Skill: wisdom-council
Args: {"content": "<zh版文本>", "content_type": "text", "domain": "creative", "lang": "zh"}
```

**关于 domain**：`creative` 是代表例。既然是比较，3 次都要用**相同的 `domain`**。有余力时再用 `business` 或 `cultural` 重复，可以观察到跨领域的偏差。

**执行中的注意点：**
- 将每次评估的输出 JSON（`primary_score`, `dimension_scores`）保存到 `/tmp/calib-en.json`、`/tmp/calib-ja.json`、`/tmp/calib-zh.json`。
- 目视确认输出报告的合成部分（executive_summary 等）使用了要求的语言，且 `caveats` 中没有出现英文回退警告。

## 3. 收集・分布比较

从 3 个 JSON 中收集 `primary_score` 和 `dimension_scores`，比较语言间的分布。

```bash
cd <wisdom-council-layer>
python3 - <<'EOF'
import json, statistics

langs = ["en", "ja", "zh"]
reports = {l: json.load(open(f"/tmp/calib-{l}.json")) for l in langs}

print(f"{'lang':4s} {'primary':>8s} {'dims':>6s}")
for l, r in reports.items():
    pri = r.get("primary_score")
    dims = [d["score"] for d in (r.get("dimension_scores") or {}).values() if d.get("score") is not None]
    print(f"{l:4s} {pri:8d} {statistics.mean(dims) if dims else 0:6.1f}")

# 每个评估者(dimension)的语言间比较
all_dim_keys = set().union(*(r.get("dimension_scores") or {}).keys() for r in reports.values())
for k in sorted(all_dim_keys):
    vals = [reports[l]["dimension_scores"].get(k, {}).get("score") for l in langs]
    print(f"{k:28s} en={vals[0]}  ja={vals[1]}  zh={vals[2]}")
EOF
```

## 4. 判定标准

确认 `references/scoring-strictness.md` 的设计（**中位数≈30**）是否在 3 种语言中得到重现。

| 确认项 | 合格标准 |
|--------|----------|
| 整体严格度 | 3 种语言的 primary_score / dimension_scores 平均值都分布在「30 上下」的区间（平庸～良作）。大量出现 50 以上即为严格度崩坏 |
| 语言间一致 | 3 种语言的中位数・平均值差异小（希望控制在 ±5 以内） |
| 相对排序一致 | 某位评估者给高/低分的维度，在 3 种语言中呈现相同倾向 |

## 5. 判定与处理

### 5a. 合格（无偏差）
3 种语言的分布一致，即可判定不存在行为漂移。记录结果。

```bash
# 记录（示例）
python3 utils/check_calibration_drift.py --json  # 静态：再次确认 PASS
```

记录位置候选：在校准发现文档的 §2 追加「已执行」记录，或新建运行时校准结果备忘。

### 5b. 不合格（检测到系统性偏差）
例如出现「英文整体偏高 5 分」「只有日文从不给出 0-10」等。

1. **将英文提示词作为规范来源修正**（若偏差出现在英文则调整措辞——注意以英文为基准并不代表英文就是正确的）。
2. ja / zh 在英文修正后**重新翻译**（保持保留数字的翻译。更新 `agents/*-ja.md` / `*-zh.md`）。
3. 修正后确认**静态漂移检查仍通过**——数值契约在 3 种语言间保持一致（数值不一致即为翻译事故）。
4. 在重启后的新会话中**重新执行运行时校准**以确认改善。

## 6. 完成条件

- [ ] 静态漂移检查 PASS（§0）
- [ ] 3 种语言各完成评估，且无回退警告（§2）
- [ ] 已执行分布比较，并判定合格/不合格（§3–4）
- [ ] 已记录结果（§5）
- [ ] 不合格时：提示词修正 → 重新翻译 → 重新校准的循环已完成（§5b）

---

## 参考

- `references/calibration-suite.md` — 校准套件整体（静态检查＋运行时校准）
- `references/scoring-strictness.md` — 运行时检查的判定标准——严格评分原则（中位数≈30）
- `utils/check_calibration_drift.py` — 静态漂移检查器
