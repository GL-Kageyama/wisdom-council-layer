# Value Vector Model — 多次元スコアリング

単純な点数評価の欠点は、価値を単一の軸に押しつぶすことである。Wisdom Council Layerは価値を**多次元ベクトル**として扱う。

## Value Vector の定義

```
Value Vector = [originality, quality, aesthetic, emotional_impact,
                future_potential, business_value, scientific_novelty,
                philosophical_depth, meaning]
```

各次元は 0-100 の整数スコア、またはその評価者が専門外の場合は `null`。

## 単一点数との違い

| | 単一点数 | Value Vector |
|--|---------|--------------|
| 情報量 | 1つの数字 | 9次元の分布 |
| 表現力 | 「63点」 | 「独創性は低いが未来価値は高い」 |
| 評価者の専門性 | 平均的な誰か | 各次元の専門家 |
| 矛盾の扱い | 隠される | 明示される |

## 例：同じ作品の2つの見方

**作品**: 商業的に失敗した前衛的な映像作品

```
単一点数:  48点（平均的な評価、情報なし）

Value Vector:
  originality:         82   ← 高い（評価者: Originality）
  aesthetic:           71   ← 中高（評価者: Aesthetic）
  emotional_impact:    35   ← 低い（評価者: Emotional）
  future_potential:    88   ← 非常に高い（評価者: Future）
  business_value:      15   ← 非常に低い（評価者: Business）
  philosophical_depth: 79   ← 高い（評価者: Philosophical）
```

ベクトルの形そのものが「現在は理解されないが、未来の可能性が高い」という物語を語る。単一点数はこの情報を破棄する。

## ベクトルの合成

合議（オーケストレーター）は各評価者の `value_vector_contribution` を集約する。

| 統計量 | 意味 |
|--------|------|
| 平均 | 各次元の中心傾向 |
| 分散 | 評価者がどれだけ割れているか（不一致の強さ） |
| 範囲 (min-max) | 評価の両端 |
| nullの数 | どの次元が未評価か（評価者選択の妥当性） |

### 分散の解釈

| 分散 | 意味 |
|------|------|
| 低分散 (< 100) | 評価者間でほぼ同意見。安定した評価。 |
| 中分散 (100-400) | ある程度の視点の違い。正常。 |
| 高分散 (> 400) | 深刻な意見の割れ。コンテンツが何らかの分裂を引き起こしている。**最も重要なシグナル。** |

## 分類への写像

Value Vector は2次元に縮約される:

```
Current Value = w_q·quality + w_o·originality + w_a·aesthetic
              + w_e·emotional + w_b·business + w_s·scientific
              （専門外の次元は省略、重みは正規化）

Hidden Potential = w_f·future_potential + w_m·meaning
                 + w_p·philosophical + w_o'·originality(未来寄与)
```

この縮約は**報告のための表示**であり、保存されるのは常に完全なベクトルである。

## なぜベクトルか

1. **対立を保存できる**: 高いオリジナリティと低いビジネス価値の共存を表現できる。
2. **将来の再評価に耐える**: 6ヶ月後に再評価したとき、ベクトルの各次元の変化を追跡できる。
3. **評価者の専門性を活かす**: 各評価者は自分の専門の次元だけを責任を持ってスコアする。
4. **人間の判断を助ける**: 人間は「ベクトルを見て、どの次元を重視するか決める」という新たな役割を持つ。

## 将来の拡張

- **時系列ベクトル**: 同じコンテンツの複数回の評価を重ねて、価値の軌跡（trajectory）を描く（Memory System）。
- **重みの個人化**: 人間が自分の価値観に合わせて次元の重みを調整する。
- **高次元の解釈**: 9次元を超える次元（時代性、政治的影響など）を追加可能にする。
