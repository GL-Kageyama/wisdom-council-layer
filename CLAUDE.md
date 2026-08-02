# Wisdom Council Layer

## プロジェクトのアイデンティティ

これは**知恵の評議会（Wisdom Council Layer）**である。複数のAI評価者が異なる知的視点からコンテンツを評価し、合議によって構造化された価値レポートを生成するClaude Codeスキル群。

> **役割分担**: このレイヤーは**評価専用**である。作品の**作成**は、適切な他の手段（生成AI・専用の作成スキル・他のツール）が利用可能ならそちらに譲る。このリポジトリは「作る」ことではなく「価値を見抜く」ことを担い、その評価結果を次回の作成へ渡す材料として整える。

## 核となる哲学

- **Anti-Generic（反凡庸）**: 平均的でAIらしい出力を排除し、意味ある逸脱を発見する。
- **多声的評価（Polyphonic Evaluation）**: 単一の審判者ではなく、異なる視点を持つ複数の評価者。
- **不一致こそシグナル**: 評価者間の対立は平均化せず、そのまま保存する。合意よりも衝突の方が価値の兆候を明かすことが多い。
- **生成より評価**: AI時代の競争領域は「どれだけ作れるか」ではなく「どれだけ価値あるものを見抜けるか」。

## ディレクトリ規約

- `skills/{name}/SKILL.md` — スキルの正本（評価者10体 + 合議オーケストレーター1体）
- `.claude/skills/` — プロジェクト内検出用symlink
- `~/.claude/skills/` — グローバルインストール先（`./install.sh` で設定、どこからでも呼べる）
- `.claude-plugin/` — プラグイン配布定義（`/plugin marketplace add` 用）
- `schemas/` — 構造化出力のJSONスキーマ
- `references/` — 設計文書と理論的基盤（評価者分類・分類モデル・不一致原則・ベクトルモデル・厳格スコアリング）
- `examples/` — サンプル入力と出力
- `utils/` — バリデーションなどのユーティリティ

## 評価者の呼び出し方

スキルは **名前** で呼び出す（`.claude/skills/` から検出される）。スキル名は評価者のディレクトリ名と一致する。

### 単一評価者

```
Skill: originality
Args: {"content": "...", "content_type": "text", "domain": "creative"}
```

### 合議全体

```
Skill: wisdom-council
Args: {"content": "...", "content_type": "text", "domain": "creative"}
```

合議は以下を実行する:
1. 入力のドメインを判定
2. 関連する評価者を選択（originality と anti-generic-filter は常に含める）
3. 各評価者を名前で起動（Skill tool経由）
4. Value Reportに統合
5. すべての不一致を保存

**modeオプション** — `Args` に `"mode": "full"` を追加すると、ドメイン選択をせず**全10体**を一気に招集し、全9次元が埋まった完全なValue Reportを得る:

```
Skill: wisdom-council
Args: {"content": "...", "content_type": "text", "domain": "creative", "mode": "full"}
```

## 出力規約

すべての評価者出力は `schemas/value-output.schema.json` に準拠した有効なJSONでなければならない。

```bash
python utils/validate_output.py < output.json
```

## ツール群

| ツール | 役割 |
|--------|------|
| `utils/validate_output.py` | 評価者出力のスキーマ検証 |
| `utils/render_report.py` | Value Report の視覚表示（バーチャート・分類バッジ・次元間の対立）。`-o report.md` で拡張子自動判定によりMarkdown文書として保存、`--individuals` で全個別レポート表示 |
| `utils/compare_reports.py` | 改訂前後の差分比較（評価→再作成ループ用） |

## 評価出力は「入力」として設計されている

**このレイヤーの評価結果は、それ自体が最終成果ではない。** 作成スキル（再作成・改善指示を合成する専用スキル）への**入力**である。

- 合議は**再作成指示そのものを生成しない**。それは専用スキルの責務。
- 代わりに、`individual_reports` に各評価者の**生の素材**（`weaknesses`・`improvement_suggestions`・`expected_disagreement_points`・`narrative`）を完全に保存する。
- フィールド名は固定・一貫（`schemas/value-output.schema.json` 準拠）で、作成スキルがパスを決め打ちで読める。
- 合成ナラティブ（executive_summary等）は補助であり、生データを捨てない。

**評価 → 再作成ループ:**
```
評価 → revision_direction（次回の修正方向）→ 作成スキルが指示を合成 → 再作成 → 再評価
  → compare_reports.py で改善度確認 → 繰り返し
```

**反復モード（`iteration`）:**
- `iteration: "confirm"`（デフォルト）— 各ターンの評価後に `revision_direction` を提示し、**確認してから**次の修正へ。
- `iteration: "persistent"` — 最初に `revision_direction` を確定し、その方向に沿って**修正し続ける**（各反復では到達度を報告）。

指針:
- 平均だけで判断せず、分散と不一致も見る。
- 改善が頭打ちになったらループを止める（過修正は元の良さを失わせる）。
- 詳細: `references/revision-loop.md`

## 重要原則

- 評価者は自分の専門領域の次元だけをスコアする。専門外は `null` を返す。
- 不一致を予測するのは評価者の義務である（自分の視点が他者とどこで対立するか想像する）。
- 評価は外交的であってはならない。率直さが価値。
- スコアリングは**意図的に厳格**である（`references/scoring-strictness.md`）。高得点は稀。絶対スコアの低さは「評価が低い」ではなく「凡庸・無難」を意味する。
- オーケストレーターは評価者に判断を指示しない。招集して統合するだけ。

## インストール

```bash
./install.sh            # グローバル: ~/.claude/skills/（どこからでも呼べる）
./install.sh --local    # プロジェクト: .claude/skills/
./install.sh --uninstall
```
