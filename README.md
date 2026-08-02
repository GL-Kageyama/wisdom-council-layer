# Wisdom Council Layer

**知恵の評議会** —— 生成AIの大量アウトプットの中から、真に価値あるものを発見するための多エージェント価値評価レイヤー。

## なぜ必要か

生成AIの発展により、文章・画像・音楽・コード・企画など、あらゆる創造物を大量に生成できる時代になった。

しかし、新たな問題が発生している。

> **作る能力ではなく、価値あるものを見抜く能力が不足する。**

AIは平均的で完成度の高いアウトプットを生成できる。しかし、本当に重要なものは必ずしも平均の中には存在しない。

- 一見奇妙だが革新的なもの
- 現時点では理解されないもの
- 少数派だが未来文化を作るもの
- 人間の認識を変えるもの

これらを発見するための基盤が **Wisdom Council Layer** である。

## 核となる哲学

- **Anti-Generic（反凡庸）**: 平均的な答えを排除し、意味ある逸脱を発見する。
- **多声的評価**: 単一の審判者ではなく、異なる視点を持つ複数の評価者による合議。
- **不一致こそシグナル**: 評価者間の対立は平均化せず、そのまま保存する。
- **生成より評価**: AI時代の競争領域は「どれだけ作れるか」から「どれだけ価値あるものを見抜けるか」へ移る。

## アーキテクチャ

```
評価対象のコンテンツ
        ↓
┌─────────────── 知恵の評議会 ───────────────┐
│  Originality  Aesthetic  Emotional        │
│  Anti-Generic Business   Scientific       │
│  Future       Philosophical  Meaning      │
│  Quality                                    │
└────────────────────────────────────────────┘
        ↓
  Value Vector（多次元スコア）
        ↓
  Disagreement Map（不一致の保存）
        ↓
  Value Report（人間の意思決定者へ）
```

### 3層構造

```
Layer 1: Generation Layer（生成するAI）
Layer 2: Evaluation Layer（評価するAI）← このプロジェクト
Layer 3: Meta Value Layer（価値基準そのものを考えるAI）← 将来フェーズ
```

## ディレクトリ構造

```
wisdom-council-layer/
├── CLAUDE.md                          # プロジェクト規約
├── install.sh                         # グローバル/プロジェクトインストーラー
├── skills/                            # スキルの正本（11体）
│   ├── originality/SKILL.md
│   ├── anti-generic-filter/SKILL.md
│   ├── aesthetic-critic/SKILL.md
│   ├── emotional-impact/SKILL.md
│   ├── future-potential/SKILL.md
│   ├── business-value/SKILL.md
│   ├── scientific-novelty/SKILL.md
│   ├── philosophical-evaluator/SKILL.md
│   ├── quality-evaluator/SKILL.md
│   ├── meaning-evaluator/SKILL.md
│   └── wisdom-council/SKILL.md        # 合議オーケストレーター
├── .claude/skills/                    # プロジェクト内検出用symlink
├── .claude-plugin/                    # プラグイン配布定義
│   ├── marketplace.json
│   └── plugin.json
├── schemas/
│   └── value-output.schema.json       # 全評価者の出力契約
├── references/                        # 理論的基盤
│   ├── evaluator-taxonomy.md
│   ├── value-classification.md
│   ├── debate-principles.md
│   ├── value-vector-model.md
│   └── scoring-strictness.md          # 厳格スコアリング基準
├── examples/
│   ├── sample-input.md
│   └── sample-value-report.md
└── utils/
    └── validate_output.py             # 出力バリデーション
```

## 使い方

### インストール

**グローバル（どこからでも呼べる）:**

```bash
./install.sh
```

`~/.claude/skills/` にsymlinkが作成され、どのプロジェクトでもスキルが利用可能になる。

**プロジェクト限定:**

```bash
./install.sh --local
```

**プラグインとして配布・インストール**（GitHub公開後）:

```
/plugin marketplace add https://github.com/<あなたのアカウント>/wisdom-council-layer
/plugin install wisdom-council-layer@wisdom-council-layer
```

### 単一評価者を呼ぶ

スキルは **名前** で呼び出す:

```
Skill: originality
Args: {"content": "...", "content_type": "text", "domain": "creative"}
```

各評価者は `schemas/value-output.schema.json` に準拠したJSONを出力する。

### 合議全体を呼ぶ

```
Skill: wisdom-council
Args: {"content": "...", "content_type": "text", "domain": "creative"}
```

合議は以下を実行する:
1. ドメインを判定し、3〜5体の評価者を選択
2. 各評価者を独立に招集（originality と anti-generic-filter は常に含む）
3. Value Vector を合成
4. 不一致マップを生成
5. Value Report を出力

### 出力の検証

```bash
python utils/validate_output.py < evaluator_output.json
```

## 評価者一覧

| 評価者 | コア質問 | スコア次元 |
|--------|----------|-----------|
| Originality Evaluator | 意味ある逸脱か、再結合か？ | originality |
| Anti-Generic Filter | AIらしい平均解ではないか？ | quality |
| Aesthetic Critic | 深い美の体験を創出しているか？ | aesthetic |
| Emotional Impact Evaluator | 人間の心を動かすか？ | emotional_impact |
| Future Potential Analyzer | 未来の環境で価値が上昇するか？ | future_potential |
| Business Value Evaluator | 市場で価値を生むか？ | business_value |
| Scientific Novelty Reviewer | 知識の前線を押し広げるか？ | scientific_novelty |
| Philosophical Evaluator | 世界観を変える可能性があるか？ | philosophical_depth |
| Quality Evaluator | 技術的に完成しているか？ | quality |
| Meaning Evaluator | 生に意味を与えるか？ | meaning |

## Value Classification

現在価値 × 潜在価値の2次元マトリクスで分類する。

```
             Hidden Potential
                  ↑
   Discovery Target   Innovation
────────────────┼──────────────────→  Current Value
   Low Signal        Current Success
```

合議の主要ミッションは **Discovery Target**（現在評価は低いが未来可能性あり）を発見することである。

## ロードマップ

- **Phase 1（完了）**: Universal Evaluation Core — 10体の評価者スキル + 合議オーケストレーター + Value Vector + Value Report
- **Phase 2（将来）**: Hidden Potential Layer — Historical Analyzer, Mutation Detector, Timing Analyzer
- **Phase 3（将来）**: Debate Engine — 評価者間の多ターン議論
- **Phase 4（将来）**: Meta Value Layer — Bias Detection, Evaluation Critic, Value Evolution

## ライセンス

MIT License — Copyright (c) 2026 GL-Kageyama

## Core Statement

> AI時代の競争領域は、
> 「どれだけ作れるか」から、
> 「どれだけ価値あるものを見抜けるか」へ移る。

Wisdom Council Layerは、そのための価値発見インフラである。
