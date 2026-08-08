# Examples — ジャンル別サンプル

ジャンルごとに **生成 → 評価 → 再作成** のループを実演するサンプル集。

## フォルダ構成

| フォルダ | ジャンル | 分類の推移（v1 → v2） |
|----------|---------|----------------------|
| `creative-poem/` | 詩 | discovery_target → current_success |
| `creative-poem-sea/` | 詩（海・『借りた言葉』） | discovery_target → innovation（v1〜v10） |
| `music-lyrics/` | 歌謡曲の歌詞（『雨上がりの電話』） | trend_object → innovation（v1〜v5） |
| `creative-film/` | 映画企画 | discovery_target → innovation |
| `creative-watercolor/` | 画像生成プロンプト（水彩） | discovery_target → innovation |
| `creative-photography/` | 画像生成プロンプト（写真） | discovery_target → innovation |
| `business-startup/` | 事業 | trend_object → current_success |
| `scientific-hypothesis/` | 科学仮説 | discovery_target → innovation |
| `cultural-philosophy/` | 思想エッセイ | low_signal → discovery_target |
| `digital-oss/` | OSSソフトウェア | trend_object → current_success |
| `architecture-house/` | 個人邸設計（建築） | discovery_target → innovation |
| `digital-elevate-draft-engine/` | AI生成エンジン（コード・full合議） | discovery_target（v1） |

各ジャンルのフォルダに:
- `input.md` — 評価対象のコンテンツ（v1・v2）
- `report-v1.json` — 初回評価（厳格スコア）
- `report-v2.json` — 改訂後の再評価（ループの改善を実演）
- `report.md` — v2のMarkdown表示（GitHub / VSCodeプレビューで読める）

## 使い方

**評価を読む（Markdown化）:**
```bash
python ../utils/render_report.py --format md business-startup/report-v2.json
```

**全評価者の個別レポートまで表示:**
```bash
python ../utils/render_report.py --individuals business-startup/report-v2.json
```

**ループの改善を比較:**
```bash
python ../utils/compare_reports.py business-startup/report-v1.json business-startup/report-v2.json
```

**全サンプルの検証:**
```bash
for f in */report-*.json; do python3 ../utils/validate_output.py "$f"; done
```

## 個別評価レポート（individual_reports）

各レポートの `individual_reports` には**招集した全評価者の生データ**（`weaknesses`・`improvement_suggestions`・`narrative`）が入る。これは**作成スキルが再作成の材料として読む入力**である。

- **`business-startup/`** は全6評価者の個別レポートを完全実装した**正規の形**（`--individuals` で確認できる）。
- 他のジャンルのサンプルは**可読性のため要約**してある。実際の合議は全招集評価者を保存する。
