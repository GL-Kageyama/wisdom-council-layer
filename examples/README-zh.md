**语言:** [English](README.md) | [日本語](README-ja.md) | [中文](README-zh.md)

# Examples — 按体裁分类的示例

按体裁演示 **生成 → 评估 → 再创作** 循环的示例集。

## 文件夹结构

| 文件夹 | 体裁 | 分类的变迁（v1 → v2） |
|----------|---------|----------------------|
| `creative-poem/` | 诗歌 | discovery_target → current_success |
| `creative-poem-sea/` | 诗歌（大海・《借来的话》） | discovery_target → innovation（v1〜v10） |
| `creative-poem-sea-desk/` | 诗歌（大海・《海的书桌》） | discovery_target（v1） |
| `music-lyrics/` | 歌谣曲的歌词（《雨后的电话》） | trend_object → innovation（v1〜v5） |
| `creative-film/` | 电影企划 | discovery_target → innovation |
| `creative-watercolor/` | 图像生成提示词（水彩） | discovery_target → innovation |
| `creative-photography/` | 图像生成提示词（照片） | discovery_target → innovation |
| `business-startup/` | 事业 | trend_object → current_success |
| `scientific-hypothesis/` | 科学假说 | discovery_target → innovation |
| `cultural-philosophy/` | 思想随笔 | low_signal → discovery_target |
| `digital-oss/` | OSS 软件 | trend_object → current_success |
| `architecture-house/` | 私人住宅设计（建筑） | discovery_target → innovation |
| `digital-elevate-draft-engine/` | AI 生成引擎（代码・full 合议） | discovery_target（v1） |

各体裁的文件夹中:
- `input.md` — 被评估的内容（v1・v2）
- `report-v1.json` — 初次评估（严格评分）
- `report-v2.json` — 修订后的再次评估（演示循环的改进）
- `report.md` — v2 的 Markdown 呈现（可在 GitHub / VSCode 预览中阅读）

## 使用方法

**阅读评估（转为 Markdown）:**
```bash
python ../utils/render_report.py --format md business-startup/report-v2.json
```

**显示全部评估者的个别报告:**
```bash
python ../utils/render_report.py --individuals business-startup/report-v2.json
```

**比较循环的改进:**
```bash
python ../utils/compare_reports.py business-startup/report-v1.json business-startup/report-v2.json
```

**校验全部示例:**
```bash
for f in */report-*.json; do python3 ../utils/validate_output.py "$f"; done
```

## 个别评估报告（individual_reports）

每个报告的 `individual_reports` 中存放着**所召集的全部评估者的原始数据**（`weaknesses`・`improvement_suggestions`・`narrative`）。这是**创作技能作为再创作材料去读取的输入**。

- **`business-startup/`** 是完整实现了全部 6 位评估者个别报告的**规范形态**（可用 `--individuals` 确认）。
- 其他体裁的示例出于**可读性做了摘要**。实际的合议会保存全部被召集的评估者。
