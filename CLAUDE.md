# Wisdom Council Layer

## プロジェクトのアイデンティティ

これは**知恵の評議会（Wisdom Council Layer）**である。複数のAI評価者が異なる知的視点からコンテンツを評価し、合議によって構造化された価値レポートを生成するClaude Codeスキル群。

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
| `utils/render_report.py` | Value Report の視覚表示（バーチャート・分類バッジ・再作成指令） |
| `utils/compare_reports.py` | 改訂前後の差分比較（作成→評価→再作成ループ用） |

## 作成 → 評価 → 再作成 ループ

合議は `rebuild_feedback`（再作成指令）を出力する。これを使って作品を改善し、ループさせる。

```
評価 → rebuild_feedback（最優先・具体的変更・保持すべき強み）
  → 再作成（directive適用） → 再評価 → compare_reports.py で改善度確認 → 繰り返し
```

指針:
- **preserve**（失ってはいけない強み）を守り、修正で既存の高次元を壊さない。
- `concrete_changes` の directive は「改善する」ではなく「XをYに変える」の具体形にする。
- 改善が頭打ちになったらループを止める（過修正は元の良さを失わせる）。

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
