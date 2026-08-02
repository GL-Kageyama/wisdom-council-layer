# Evaluator Taxonomy

Wisdom Council Layerの評価者群は、単一の価値観ではなく**複数の独立した視点**から構成される。この文書は各評価者の位置づけ、担当ドメイン、他の評価者との関係を定義する。

## 評価者のカテゴリ

評価者は3つの層に分かれる。

### 第1層：現在価値分析（Current Value Analysis）

コンテンツが**現時点で**どれだけ価値を持つかを評価する。

| 評価者 | 視点 | 担当ドメイン |
|--------|------|--------------|
| Quality Evaluator | 完成度・技術品質 | 全ドメイン |
| Originality Evaluator | 独自性・意味ある逸脱 | 全ドメイン |
| Aesthetic Critic | 美的完成度・表現力 | creative |
| Emotional Impact Evaluator | 感情への影響 | creative, social |
| Business Value Evaluator | 市場性・実現可能性 | business, digital |
| Scientific Novelty Reviewer | 科学的新規性 | scientific |

### 第2層：潜在価値発見（Hidden Potential Discovery）

現在評価されていない**未来の可能性**を発見する。

| 評価者 | 視点 | 担当ドメイン |
|--------|------|--------------|
| Future Potential Analyzer | 長期的可能性・時代適合性 | 全ドメイン |
| Meaning Evaluator | 意味・思想性 | cultural, social |

### 第3層：基準層（Meta Layer）

評価の前提そのものを揺さぶる。

| 評価者 | 視点 |
|--------|------|
| Philosophical Evaluator | 世界観・人間理解への影響 |
| Anti-Generic Filter | 凡庸性の除去（全評価者に横断的に働く） |

## 各評価者の核となる問い

| 評価者 | コア質問 |
|--------|----------|
| Quality Evaluator | これは技術的に完成しているか？ |
| Originality Evaluator | これは意味ある形で既存から逸脱しているか？ |
| Aesthetic Critic | これは美の体験を創出しているか？ |
| Emotional Impact Evaluator | これは人間の心を動かすか？ |
| Business Value Evaluator | これは市場で価値を生むか？ |
| Scientific Novelty Reviewer | これは知識の前線を押し広げるか？ |
| Future Potential Analyzer | これは未来の環境変化で価値が上昇するか？ |
| Meaning Evaluator | これは人間の存在についての理解を深めるか？ |
| Philosophical Evaluator | これは世界観を変える可能性があるか？ |
| Anti-Generic Filter | これはAIが出しやすい平均解ではないか？ |

## 評価者間の関係

### 補完関係

- **Originality ↔ Quality**: 独創性の高い作品ほど完成度が低いことが多い。この緊張関係が重要。
- **Future Potential ↔ Business Value**: 現在の市場評価が低いものほど未来価値が高いことがある（Discovery Target）。
- **Emotional Impact ↔ Anti-Generic**: 感情的な操作（sentimentality）は凡庸性の一種である。

### 対立構造

この対立は**平均化されるべきではない**。むしろ、衝突が価値の重要な兆候である。

```
高い独創性 + 低い完成度 = 未来の傑作の可能性
高いビジネス価値 + 低い哲学的深さ = トレンドオブジェクトの可能性
高い意味性 + 低い市場性 = Discovery Targetの可能性
```

## Value Vector との対応

各評価者は Value Vector の特定の次元に貢献する（他の次元は null）。

```
Value Vector:
[originality, quality, aesthetic, emotional_impact,
 future_potential, business_value, scientific_novelty,
 philosophical_depth, meaning]
```

## 合議での評価者選択

合議オーケストレーターはドメインに応じて評価者を選択する。

| ドメイン | 必須評価者 | 任意評価者 |
|----------|-----------|-----------|
| creative | originality, anti-generic-filter, aesthetic-critic, emotional-impact | meaning-evaluator, future-potential, philosophical-evaluator |
| scientific | originality, scientific-novelty, anti-generic-filter | future-potential, quality-evaluator |
| business | business-value, originality, quality-evaluator | future-potential, anti-generic-filter |
| social | emotional-impact, meaning-evaluator, quality-evaluator | future-potential, philosophical-evaluator |
| digital | quality-evaluator, originality, anti-generic-filter | business-value, future-potential |
| cultural | meaning-evaluator, philosophical-evaluator, originality | aesthetic-critic, emotional-impact, future-potential |
