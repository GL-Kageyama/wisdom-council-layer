# Sample Input — 合議テスト用コンテンツ

このファイルは Wisdom Council の動作テスト用サンプル入力である。下記の「コンテンツ」を合議に渡すことで、各評価者の出力とValue Reportの生成を検証できる。

## コンテンツ

```json
{
  "content": "『記憶の庭師』——ある深夜の図書館で、本に閉じ込められた記憶を解放する仕事をする庭師の物語。彼は人々の忘れたい記憶を『記憶の種』として蒔き、その記憶が芽吹くことで、人々は『忘れたくないけれど苦しい記憶』を取り戻す選択を迫られる。技術的には完全な静寂演出と、色が段階的に失われていく映像表現が特徴。現在は地下のアートシーンで評価されているが、商業的には未開拓。",
  "content_type": "structured",
  "domain": "creative",
  "context": "独立系映画監督の長編デビュー作。10分の短編が国際映画祭で受賞した後に制作された。予算は極めて限定的。"
}
```

## このサンプルの意図

このコンテンツは合議の本領を発揮させるよう設計されている:

- **独創性**: 高い（記憶という普遍テーマを「庭師」という視点で再構成）
- **品質**: 中〜高（演出は評価されているが、予算の制約が残る）
- **感情**: 高い（記憶と選択という深い感情テーマ）
- **未来価値**: 高い（商業的には未開拓、しかし将来的な可能性）
- **ビジネス価値**: 低い（現在は商業的に未開拓）

つまり「現在評価は限定的だが、長期観察対象（Discovery Target）」になることを期待した設計である。

## 使い方

### 単一評価者を呼ぶ

```
Skill: originality
Args: {"content": "...", "content_type": "structured", "domain": "creative", "context": "..."}
```

### 合議全体を呼ぶ

```
Skill: wisdom-council
Args: {"content": "...", "content_type": "structured", "domain": "creative", "context": "..."}
```

合議は creative ドメインとして、originality, anti-generic-filter, aesthetic-critic, emotional-impact を必須評価者として招集する。
