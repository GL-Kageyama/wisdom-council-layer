# Examples — ジャンル別サンプル

ジャンルごとに **生成 → 評価 → 再作成** のループを実演するサンプル集。

## フォルダ構成

| フォルダ | ジャンル | 分類の推移（v1 → v2） |
|----------|---------|----------------------|
| `creative-poem/` | 詩 | discovery_target → discovery_target（改善） |
| `creative-film/` | 映画企画 | 単体サンプル |
| `business-startup/` | 事業 | trend_object → current_success |
| `scientific-hypothesis/` | 科学仮説 | discovery_target → innovation |
| `cultural-philosophy/` | 思想エッセイ | low_signal → discovery_target |

各ジャンルのフォルダに:
- `input.md` — 評価対象のコンテンツ（v1・v2）
- `report-v1.json` — 初回評価（厳格スコア）
- `report-v2.json` — 改訂後の再評価（ループの改善を実演）

## 使い方

**評価を読む（Markdown化）:**
```bash
python ../utils/render_report.py --format md business-startup/report-v2.json
```

**ループの改善を比較:**
```bash
python ../utils/compare_reports.py business-startup/report-v1.json business-startup/report-v2.json
```

**全サンプルの検証:**
```bash
for f in */report-*.json; do python3 ../utils/validate_output.py "$f"; done
```
