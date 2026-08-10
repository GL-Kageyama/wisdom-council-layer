<!-- version: 1.0.0, last_updated: 2026-08-10 -->

**言語:** [English](../runtime-calibration-runbook.md) | [日本語](runtime-calibration-runbook.md) | [中文](../zh/runtime-calibration-runbook.md)

# ランタイム較正 実行ランブック

> 2026-08-10 作成。[`references/calibration-suite.md`](../calibration-suite.md) の §2 の手順を、**セッション再起動後**にそのまま実行できるように実務化したもの。
>
> **このランブックを実行する前提**: セッションが再起動され、`-ja` / `-zh` エージェントがレジストリに登録されていること。**同一セッション内では実行しない**（全エージェントが沈黙裡に英語フォールバックし、無意味な「3言語一致」が出る）。

---

## 0. 前提確認（再起動後に最初にやる）

以下が満たされるまで進まない。

- [ ] `-ja` / `-zh` エージェントのsymlinkが存在する（両方の場所に）
  ```bash
  ls -l ~/.claude/agents/originality-ja.md ~/.claude/agents/originality-zh.md
  ls -l .claude/agents/originality-ja.md
  ```
- [ ] レジストリで解決できることを**実際に確認**する。CLI で `/agents` を開いて `originality-ja` / `originality-zh` が一覧に出るか、または Agent tool で `subagent_type: originality-ja` を試して "not found" でないことを見る。**実測での確認が必須**（ファイルが存在してもレジストリ反映はセッション起動時）。
- [ ] 静的ドリフトチェックが PASS する（翻訳後の数値契約が3言語一致していることの確認）
  ```bash
  cd <wisdom-council-layer>
  python3 utils/check_calibration_drift.py
  # → RESULT: PASS — no numeric drift across en / ja / zh（exit 0）
  ```

## 1. テストコンテンツの用意

言語間比較に使うのは「**同じ意味の文章を3言語に翻訳したもの**」1セット。テキスト自体の言語が評価に影響するため、別々の作品を3つ用意しても比較にならない。

**選定の条件:**
- 評価者の判別力が試される「良作だが傑作ではない」程度の作品が望ましい（中央値≈30 の厳格さを測るため。完璧な傑作や明らかな駄作は全言語で似た点数になり、厳格さの差が見えにくい）。
- 元言語は英語・日本語どちらでもよいが、**3言語版を1つのファイルにまとめて保存**すると後で差分が取りやすい。

**推奨フォーマット**（`/tmp/calib-samples.md` など）:

```markdown
# Calibration Sample（3言語版）

## en
<原文をここに>

## ja
<日本語訳をここに>

## zh
<中国語訳をここに>
```

> 既存の `examples/` の作品を流用する場合は、その作品の input を3言語に翻訳して使う。例: `examples/creative-poem-sea/` など。

## 2. 3言語で評価を実行

Wisdom Council スキルを **1言語につき1回**、計3回実行する。`content` には**その言語版のテキストのみ**を渡す（全言語版を渡すと評価者が全部読んで混乱する）。

```
Skill: wisdom-council
Args: {"content": "<en版テキスト>", "content_type": "text", "domain": "creative", "lang": "en"}
```

```
Skill: wisdom-council
Args: {"content": "<ja版テキスト>", "content_type": "text", "domain": "creative", "lang": "ja"}
```

```
Skill: wisdom-council
Args: {"content": "<zh版テキスト>", "content_type": "text", "domain": "creative", "lang": "zh"}
```

**domain について**: `creative` が代表例。比較が目的なので3回とも同じ `domain` を使うこと。余力があれば `business` や `cultural` でも繰り返すと、ドメイン横断のバイアスが見える。

**実行中の注意点:**
- 各評価の出力 JSON（`primary_score`, `dimension_scores`）を `/tmp/calib-en.json`, `/tmp/calib-ja.json`, `/tmp/calib-zh.json` に保存。
- 出力レポートの合成部（executive_summary 等）が要求言語になっているか、`caveats` に英語フォールバック警告が出ていないかを目視確認。

## 3. 収集・分布比較

3つのJSONから `primary_score` と `dimension_scores` を集めて、言語間の分布を比較する。

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

# 各評価者(dimension)ごとの言語間比較
all_dim_keys = set().union(*(r.get("dimension_scores") or {}).keys() for r in reports.values())
for k in sorted(all_dim_keys):
    vals = [reports[l]["dimension_scores"].get(k, {}).get("score") for l in langs]
    print(f"{k:28s} en={vals[0]}  ja={vals[1]}  zh={vals[2]}")
EOF
```

## 4. 判定基準

`references/scoring-strictness.md` の設計（**中央値≈30**）が3言語で再現されるかを確認する。

| 確認項目 | 合格の目安 |
|---------|-----------|
| 全体的な厳格さ | 3言語とも primary_score / dimension_scores の平均が「30前後」の帯に分布（凡庸〜良作）。50超が大量に出ていたら厳格さ崩壊 |
| 言語間の一致 | 3言語の中央値・平均の差が小さい（±5程度以内が望ましい） |
| 相対順位の一致 | ある評価者が高い/低いとした次元が、3言語で同じ傾向を示す |

## 5. 判定と対処

### 5a. 合格（バイアスなし）
3言語で分布が一致していれば挙動ドリフトはないと判断する。結果を記録する。

```bash
# 記録（例）
python3 utils/check_calibration_drift.py --json  # 静的: PASS を再確認
```

記録先の候補: 較正知見文書の §2 に「実施済み」を追記、または新規のランタイム較正結果メモ。

### 5b. 不合格（系統的バイアスを検出）
例えば「英語が全体的に5点高い」「日本語だけ 0-10 を一切出さない」などが見えた場合。

1. **英語プロンプトを正規ソースとして修正**する（英語でバイアスが出ている場合は文言調整。英語が基準なので英語が正しいとは限らない点に注意）。
2. ja / zh は英語修正後に**再翻訳**する（数値を保持した翻訳を維持。`agents/*-ja.md` / `*-zh.md` を更新）。
3. 修正後、**静的ドリフトチェックで数値契約が3言語一致したまま**であることを確認（数値がずれたら翻訳事故）。
4. 再起動後の新規セッションで**ランタイム較正を再実行**して改善を確認。

## 6. 完了条件

- [ ] 静的ドリフトチェック PASS（§0）
- [ ] 3言語それぞれで評価が完了し、フォールバック警告なし（§2）
- [ ] 分布比較を実行し、合格/不合格を判定（§3–4）
- [ ] 結果を記録（§5）
- [ ] 不合格だった場合: プロンプト修正 → 再翻訳 → 再較正のループを回した（§5b）

---

## 参考

- `references/calibration-suite.md` — 較正スイート全体（静的チェック＋ランタイム較正）
- `references/scoring-strictness.md` — ランタイムチェックの判定基準となる厳格スコアリングのドクトリン（中央値≈30）
- `utils/check_calibration_drift.py` — 静的ドリフトチェッカー
