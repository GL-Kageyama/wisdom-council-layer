# Sample Value Report — 合議の最終成果物の実例

以下は `examples/sample-input.md` のコンテンツ（『記憶の庭師』）に対して、creative ドメインの合議が生成する Value Report の**想定例**である。

この例は出力の形を示すためのもので、実際の合議結果は実行時の評価者出力に依存する。**必ずしもこのスコアになるとは限らない。**

---

```json
{
  "report_id": "wisdom-council-report",
  "report_timestamp": "2026-08-02T00:00:00Z",
  "content_summary": "映画『記憶の庭師』——記憶を解放する庭師の物語。地下アートシーンで評価され商業的には未開拓。",
  "content_type": "structured",
  "domain": "creative",
  "evaluators_consulted": [
    "originality",
    "anti-generic-filter",
    "aesthetic-critic",
    "emotional-impact",
    "future-potential"
  ],
  "value_vector": {
    "originality": { "mean": 82, "variance": 120, "min": 75, "max": 88, "scores": [82, 80, 85] },
    "quality": { "mean": 58, "variance": 250, "min": 45, "max": 72, "scores": [58, 45, 72] },
    "aesthetic": { "mean": 76, "variance": 90, "min": 70, "max": 82, "scores": [76, 82, 70] },
    "emotional_impact": { "mean": 84, "variance": 60, "min": 80, "max": 88, "scores": [84, 88, 80] },
    "future_potential": { "mean": 88, "variance": 40, "min": 85, "max": 92, "scores": [88, 85, 92] },
    "business_value": null,
    "scientific_novelty": null,
    "philosophical_depth": { "mean": 71, "variance": 180, "min": 60, "max": 82, "scores": [71, 60, 82] },
    "meaning": { "mean": 79, "variance": 100, "min": 72, "max": 86, "scores": [79, 86, 72] }
  },
  "current_value_score": 72,
  "hidden_potential_score": 84,
  "classification": "discovery_target",
  "disagreement_map": [
    {
      "dimension": "quality",
      "variance": 250,
      "disputing_evaluators": ["quality-evaluator", "originality"],
      "arguments": [
        "quality-evaluator: 予算の制約により演出の一部（特に大規模シーン）が粗い。58点。",
        "originality: 粗さは予算の制約であり、コンセプトの完成度は極めて高い。粗さを品質の低さと同一視すべきではない。"
      ]
    },
    {
      "dimension": "philosophical_depth",
      "variance": 180,
      "disputing_evaluators": ["philosophical-evaluator", "aesthetic-critic"],
      "arguments": [
        "philosophical-evaluator: 記憶とアイデンティティの関係という深い問いを誠実に扱っている。82点。",
        "aesthetic-critic: 映像表現は美しいが、思想的な深さを言語化するより感覚に訴える作品。60点。"
      ]
    }
  ],
  "consensus_summary": "独創性・感情・未来価値の3次元で評価者が強く合意している。この作品が『現在評価は低いが、独自の価値を持つ』ことは全評価者の一致した見解。",
  "executive_summary": "『記憶の庭師』は現在の地下アートシーンでは評価されているが、商業的には未開拓の作品である。独創性・感情的な深さ・未来価値が高く評価される一方、技術的な完成度と商業的な可能性については評価者が割れている。総合判定は Discovery Target（現在評価は限定的だが長期観察対象）。",
  "synthesis_narrative": "この作品は合議の本領を最もよく示すケースである。独創性、感情、未来価値という『価値の兆候』の次元では全評価者が高得点で一致した。一方、品質と思想的深さの次元では評価者が割れ、その不一致が『この作品の現在の評価が限定的な理由』を説明している。予算の制約による演出の粗さは、品質評価者の評価を下げたが、独創性評価者はこれを『コンセプトの完全性』と区別して評価した。この緊張関係は、作品が完成されれば（またはより多くの予算を得れば）大きく価値が跳ね上がる可能性を示唆する。商業的未開拓性はビジネス評価者の不在によって明示的なスコアは出ていないが、未来価値の高さから『環境が整えば評価が変わる』と判断できる。",
  "individual_reports": [
    {
      "evaluator_id": "originality",
      "evaluator_name": "Originality Evaluator",
      "primary_score": 85,
      "value_vector_contribution": { "originality": 85, "quality": null, "aesthetic": null, "emotional_impact": null, "future_potential": null, "business_value": null, "scientific_novelty": null, "philosophical_depth": null, "meaning": null },
      "classification": "discovery_target",
      "unique_perspective": "記憶という普遍テーマを『庭師が記憶を種として蒔く』という視点で再構成した点が、既存の記憶テーマ作品から明確に差別化されている。",
      "narrative": "この作品の独創性は『記憶』という使い古されたテーマを、比喩のレベルで刷新している点にある。..."
    },
    {
      "evaluator_id": "anti-generic-filter",
      "evaluator_name": "Anti-Generic Filter",
      "primary_score": 80,
      "value_vector_contribution": { "originality": null, "quality": 80, "aesthetic": null, "emotional_impact": null, "future_potential": null, "business_value": null, "scientific_novelty": null, "philosophical_depth": null, "meaning": null },
      "classification": "discovery_target",
      "unique_perspective": "『忘れたい記憶を種として蒔く』という独自のメタファーと、『色が段階的に失われる』という具体的な映像演出が、AIらしい凡庸な記憶物語とは明確に異なる。",
      "narrative": "..."
    }
  ],
  "recommendations": [
    "この作品を Discovery Target として記録し、6ヶ月後に再評価する",
    "技術的完成度の向上（特に予算が許せば大規模シーンの演出改善）が、評価を大きく押し上げる可能性がある",
    "現在の地下アートシーンの評価を、商業的チャネルに橋渡しすることを検討",
    "哲学的評価の低さは『思想の言語化』の不足によるもので、映像体験としての価値は別途評価されている点に注意"
  ],
  "caveats": [
    "ビジネス価値は未評価（このドメイン選択では評価者が招集されていない）",
    "サンプル入力に基づく想定例であり、実際のスコアとは異なる可能性がある",
    "未来価値は本質的に不確実であり、観察が続くべき対象である"
  ]
}
```

---

## 読み方のポイント

1. **value_vector**: 各次元の平均・分散・範囲を集約。`business_value` と `scientific_novelty` はこのドメインで招集されなかったため `null`。
2. **disagreement_map**: 品質と思想的深さの2次元で評価者が割れている。その不一致がこの作品の現在評価の限界を説明する。
3. **classification**: `discovery_target` —— 現在評価は限定的だが未来可能性が高い。
4. **consensus_summary**: 一致点を正直に記す。不一致だけを誇張しない。
5. **recommendations**: 人間の意思決定者への橋渡し。
