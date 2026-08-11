**语言:** [English](CLAUDE.md) | [日本語](CLAUDE-ja.md) | [中文](CLAUDE-zh.md)

# Wisdom Council Layer

## 项目定位

这是**知慧评议会（Wisdom Council Layer）**。一组 Claude Code 智能体：由多个 AI 评估者智能体从不同的智识视角评估内容，并通过合议技能生成结构化的价值报告。

> **分工**: 本层**只负责评估**。作品的**创作**交给其他适当的手段（生成式 AI・专用创作技能・其他工具），只要这些手段可用。本仓库承担的并非「制造」，而是「洞察价值」，并把评估结果整理为下一轮创作的输入材料。

## 核心哲学

- **反平庸（Anti-Generic）**: 排除平均化、AI 味十足的输出，发现有意义的偏离。
- **多声部评估（Polyphonic Evaluation）**: 不是单一的裁判，而是持有不同视角的多个评估者。
- **分歧即信号**: 评估者之间的冲突不加以平均化，而是原样保存。冲突往往比共识更能揭示价值的迹象。
- **评估重于生成**: AI 时代的竞争领域不是「能做出多少」，而是「能识别出多少有价值之物」。

## 目录约定

- `agents/{name}.md` — 评估者智能体的正本（共 10 体）。以基于人格设定的专家身份，作为独立的子智能体启动
- `skills/wisdom-council/SKILL.md` — 合议编排者的正本（唯一的技能）
- `.claude/agents/` — 供项目内检测用的 symlink（评估者智能体）
- `.claude/skills/` — 供项目内检测用的 symlink（合议编排者）
- `~/.claude/agents/`, `~/.claude/skills/` — 全局安装位置（通过 `./install.sh` 配置，可从任何位置调用）
- `.claude-plugin/` — 插件分发定义（用于 `/plugin marketplace add`）
- `schemas/` — 结构化输出的 JSON schema
- `references/` — 设计文档与理论基础（评估者分类・分类模型・分歧原则・向量模型・严格评分・校准套件）
- `examples/` — 示例输入与输出
- `utils/` — 校验、报告渲染、校准漂移检查等工具

## 评估者的调用方式

**合议用技能调用，评估者用子智能体调用。**这种角色分工是架构的要害——评估者必须在不知道彼此结果的情况下独立评估。技能会共享同一上下文，因此不适合独立评估。将评估者作为子智能体启动，可以隔离各自的上下文。

### 整体合议（推荐）

```
Skill: wisdom-council
Args: {"content": "...", "content_type": "text", "domain": "creative"}
```

合议执行以下步骤:
1. 判定输入的领域
2. 选择相关的评估者智能体（originality 与 anti-generic-filter 始终包含在内）
3. 将每个评估者作为子智能体启动（经由 Agent tool，彼此不知晓结果、独立评估）
4. 整合为 Value Report
5. 保存所有分歧

### 单个评估者

用于只想评估特定视角的情况。评估者作为子智能体启动。

```
Agent tool, subagent_type: originality
Prompt: {"content": "...", "content_type": "text", "domain": "creative"}
```

如果是以已安装插件的形式运行，请使用插件作用域名称（`wisdom-council:originality`）。

**mode 选项** — 在 `Args` 中加入 `"mode": "full"`，可在不做领域选择的情况下一次召集**全部 10 体**评估者，得到 9 个维度全部填充的完整 Value Report:

```
Skill: wisdom-council
Args: {"content": "...", "content_type": "text", "domain": "creative", "mode": "full"}
```

## 输出约定

所有评估者输出必须是符合 `schemas/value-output.schema.json` 的有效 JSON。

```bash
python utils/validate_output.py < output.json
python utils/validate_output.py --json output.json   # 机器可读的校验结果
```

**自动重试**: 合议技能会用 `validate_output.py --json` 对每个评估者的输出进行**确定性校验**，不合格时**最多重启同一评估者 3 次**（在反馈中包含错误内容）。3 次重试后仍不合格，则在 `excluded_evaluators` 中明确记录为 `reason: "JSON validation failed after 3 retries"`。**禁止静默丢弃。**

**坏了就重新生成（禁止手工修正）**: 若评估者输出的 JSON 损坏（`validate_output.py` 返回 `"valid": false`），**不得手工直接编辑 JSON 来修复**。务必**重新启动该评估者重新生成**，并用重新生成的输出重新校验。人工修补 JSON 可能破坏评估者独立的声音（分数・判断・文风・叙述），因此对损坏输出的处置统一为「重新生成」。

## 工具集

| 工具 | 作用 |
|--------|------|
| `utils/validate_output.py` | 评估者输出的 schema 校验。加 `--json` 标志可输出机器可读结果（合议技能的自动重试会用到） |
| `utils/render_report.py` | Value Report 的可视化呈现（条形图・分类徽章・维度间的冲突）。`-o report.md` 会根据扩展名自动判定保存为 Markdown 文档；`--individuals` 显示所有个别报告 |
| `utils/compare_reports.py` | 修订前后的差异比较（用于评估→再创作循环） |
| `utils/check_calibration_drift.py` | 对 en / ja / zh 各智能体变体进行静态校准漂移检查（权重・分数带・校准表）。`--json` 输出机器可读结果。详见 `references/calibration-suite.md` |

## 评估输出被设计为「输入」

**本层的评估结果本身并非最终成果。**它们是**输入**——提供给创作技能（合成再创作・改进指示的专用技能）。

- 合议**不生成再创作指示本身**。那是专用技能的职责。
- 作为替代，它在 `individual_reports` 中完整保存每个评估者的**原始素材**（`weaknesses`・`improvement_suggestions`・`expected_disagreement_points`・`narrative`）。
- 字段名固定且一致（遵循 `schemas/value-output.schema.json`），创作技能可以直接按路径读取。
- 合成叙述（如 executive_summary 等）只是辅助，不会丢弃原始数据。

**评估 → 再创作循环:**
```
评估 → revision_direction（下一次的修订方向）→ 创作技能合成指示 → 再创作 → 再评估
  → 用 compare_reports.py 确认改进程度 → 循环往复
```

**迭代模式（`iteration`）:**
- `iteration: "confirm"`（默认）— 每轮评估后出示 `revision_direction`，**确认之后**再进行下一次修订。
- `iteration: "persistent"` — 先确定 `revision_direction`，然后**沿着该方向持续修订**（每轮迭代报告达成的程度）。

指引:
- 不要只看平均值，也要看方差与分歧。
- 当改进陷入瓶颈时停止循环（过度修订会失去原有的优点）。
- 详见: `references/revision-loop.md`

## 重要原则

- 评估者只对自己的专业领域的维度打分。专业之外的维度返回 `null`。
- 预测分歧是评估者的义务（想象自己的视角会在何处与他者冲突）。
- 评估不应当圆滑。率直才是价值。
- 评分**刻意严格**（`references/scoring-strictness.md`）。高分很罕见。绝对分数低并不代表「评价低」，而是代表「平庸・稳妥」。
- 编排者不会向评估者指示判断。只负责召集与整合。
- **i18n 基准**: 多语言支持（en/ja/zh）是任何修改・变更的默认基准。新增或修改的评估者 prompt / schema / 报告模板必须通过语言机制（评估者智能体的 `-ja`/`-zh` 变体 / locale JSON / 镜像树）解析，面向用户的文本用运行语言生成。

## 安装

```bash
./install.sh            # 全局: ~/.claude/agents/ + ~/.claude/skills/（可从任何位置调用）
./install.sh --local    # 项目: .claude/agents/ + .claude/skills/
./install.sh --uninstall
```
