# Insight Synapse 設計仕様書群 忠実ダイジェスト

本文書は、`資料/インサイト シナプス docs/`（設計仕様書群・37本・11カテゴリ）の忠実な要約です。独自の脚色・評価・判断を加えず、仕様書に書かれている内容だけを正確に伝えます。

## 0. 文書群の概要（README.md より）

**Insight Synapse** は、「答えを生成するAI」ではなく「**考え方を自ら改善し続けるAI**」を作るための**認知アーキテクチャフレームワーク**の設計である。回答や成果物だけでなく、AI自身の**思考状態・判断過程・評価・改善**を管理対象にし、思考を「目的に向かって状態を変化させる処理」と捉え、その**思考経路そのもの**を再利用可能な知識にしようとする。実行基盤の第一ターゲットは **Claude Code**（Markdown + Git + Skillシステム）。小さく検証しながら段階的に拡張する方針。

本資料群は、構想（なぜ）→ 設計（どういう構造）→ 仕様（実装の詳細）→ 計画（いつ・どう作る）の順に構成される。最終定義は「より速く答えるAI」ではなく「考え方を自ら改善し続けるAI」を作ること。

資料群の注記：
- 重複していた8組を正の1本へ統合済み（オーケストレーター判断 / プリミティブシステム / Skillシステム / エバリュエーションシステム / テスト戦略 / セキュリティ設計 / メモリー / 実装ロードマップ）。
- v0.1改訂で `03_コアコンポーネント/00_数値定義書.md` を新設し、評価5軸の重み・合格しきい値・正規化・Confidence/Unknown算出式・Cost式を「例」から**既定値**へ一本化。各文書の `> **正版**` 注記が数値・構造の正版（参照先）を示す。
- 改訂済みの軸：①数値定義の公式化 ②単一反証可能な仮説とPOC対照実験（`11/09`）③単一正版化（リポジトリ構成・Primitive数・思考Level・Phase表記・unknown/unknown_level）④既存フレームワークとの差異化（`01/01` §8）⑤テーゼの人間的価値への写像（`08/03` §14 受益者物語）。

## 1. 核となる思想（全カテゴリを貫く5つの考え方）

1. **思考 = 状態変化** — 思考は文章生成ではなく、状態を目的に近づける変換処理。
2. **責務分離** — 判断 / 実行 / 記憶 / 評価 / 改善 をレイヤー分離する。
3. **思考の軌跡を中心とした記憶** — 「何を知っていたか」ではなく「どう考えたか」を保存する。
4. **評価は改善のため** — 採点が目的ではなく、次に改善すべき点を発見する。
5. **人間は方向調整者** — 作業者ではなく、方向を調整する立場。

主要コンポーネントは **State / Orchestrator / Skill / Primitive / Memory / Evaluation / Learning** の7つ（+ Cognitive Cost Manager）。

## 2. 01 コンセプトと哲学

### 01_AI思考アーキテクチャフレームワーク（概要仕様書）
- 現在のAIエージェントの問題として「思考過程が再利用できない」「なぜ判断したか分からない」「判断基準が固定」「長期的改善が難しい」「人間が介入できるポイントが少ない」を挙げ、**思考そのものを管理対象にする**。
- システム目標は4能力：**理解能力**（現在状態把握・未知発見・問題定義）、**思考能力**（問い生成・仮説・選択肢比較・抽象化・再構成）、**制作能力**（成果物生成・改善・バージョン管理）、**内省能力**（判断評価・失敗理由分析・次回戦略改善）。
- 全体アーキテクチャ：Goal → Workflow Engine → Orchestrator → State管理 → Skill/Primitive Layer → 実行 → Evaluation → Learning → Memory。
- 5つの設計原則：AIは答えを作るだけではなく思考を管理する / 重要な判断には理由を残す / 結果だけではなく過程を保存する / 評価は改善につなげる / 人間は作業者ではなく方向調整者になる。
- MVP実装対象：MarkdownによるState管理・Thought Trace生成・Claude Code連携・基本Orchestrator・基本Skill・評価ループ。初期対象外：Webアプリ・複数ユーザー対応・モデル学習・大規模自律エージェント・分散システム。
- リポジトリ思想：リポジトリ自体を「AIの思考作業環境」として扱う（state/ memory/ skills/ evaluation/ workflows/ artifacts/）。
- 開発順序 Phase 1: Memory → Orchestrator → 基本Skill / Phase 2: Evaluation → 改善ループ / Phase 3: Learning → Workflow最適化 → 高度な自律化。

### 02_設計原則仕様書（15原則）
- 思考と実行を分離する（最重要）。判断はOrchestratorに集約。制作より評価を重視。Memoryは知識ではなく経験を保存。Primitiveは少数精鋭。Workflowは固定化しない（Unknown高→探索増加、Confidence高→制作移行）。汎用性を優先（制作物ごとに専用AIを作らない）。評価は多視点で行う（単一AI評価の偏り回避）。思考コストを管理。透明性を維持（Decision/Reason/Alternative/Risk）。人間は価値判断を担当（AI:探索・分析・制作・改善 / 人間:目的・美的判断・倫理・最終決定）。自己改善には制約を設ける（Memory追加→Pattern追加→Workflow変更→Core Policy変更、後半ほど人間確認が必要）。Gitを思考履歴として利用。MVPでは複雑化しない。最終目的は知能の構造化（経験→思考→判断→改善→成長の知的循環）。

### 03_開発ポリシー・設計判断基準仕様書
- Policyとは「何を優先し、何を避け、どのように判断するか」を定義する高次ルール。階層は Principle → Policy → Rule → Implementation。PolicyはAIの能力を制限するものではなく、**方向性を維持するもの**。
- Core Principles：思考過程を保存する / 判断理由を残す / 小さく進化する / 評価を必ず行う。
- 制作時優先順位：Goal適合 → User価値 → 一貫性 → 独自性 → 完成度。
- Cost Policy：Simple Task→Simple Thinking、Complex Task→Deep Thinking。すべてを最大推論で処理することを禁止。
- 失敗Policy：失敗を削除しない（Failure → Pattern → Knowledge）。
- 自己改善Policy：「自分を大きくする」より「自分を良くする」ことを優先。
- Policy保存構造：`governance/policies/`（architecture.md, thinking.md, evaluation.md, development.md）。MVP Policyは architecture / thinking / memory / change の4種。

## 3. 02 アーキテクチャ

### 01_システムアーキテクチャ仕様書
- 単一の巨大AIではなく、**状態管理・判断・実行・評価・改善を分離した認知システム**。基本ループ：Goal → State認識 → 判断 → 実行 → 評価 → 改善 → 次のState。
- コンポーネント責務：Goal Layer（目的定義）、Workflow Engine（大きな流れ管理）、Orchestrator（次Action決定、生成は行わない・判断専門）、State Engine（現在状態管理）、Skill Layer（高レベル思考能力）、Primitive Layer（最小思考操作）、Artifact Layer（成果物生成、成果物とMemoryは分離）、Evaluation Engine（Process/Decision/Artifactの3対象）、Learning Engine（Policy/Workflow/Skill選択/Patternの改善）、Memory System（経験保存、構造は working/traces/decisions/patterns/knowledge、優先順位は Thought Trace→Decision→Pattern→Knowledge）。
- 実行単位は **Cognitive Cycle**（Observe→Think→Act→Evaluate→Learn）。
- 設計上の重要判断：最初から完全自律化しない / Memoryを後付けにしない（思考履歴がLearningの入力になるため）/ 評価を独立層にする（自己生成と自己評価を分離）。
- 最終定義：単なるAI Agent Frameworkではなく「AIの思考プロセスを設計・管理・改善する**認知オペレーティングシステム**」。

### 02_マルチエージェントアーキテクチャ仕様書
- 「全部をマルチエージェント化する」ことを目的にしない。**制作は集中、評価は分散、判断は統合**が設計思想。
- 制作は基本的に単一のCreator Agentを中心（一貫性・文脈維持・世界観維持のため）。必要な場合だけResearch/Critic/Specialist Agentを追加。
- 評価はマルチエージェントが適している（価値判断は単一視点では偏る）。Evaluation Orchestrator配下に Quality/Logic/Creative/Risk の各Agent。
- Agent同士は直接議論させすぎない。Structured Report → Orchestrator → Decision の経路を推奨（自由会話は情報量増大・収束困難のため）。
- Agent出力統一形式：# Agent Report（Observation / Evaluation / Confidence / Recommendation）。
- Agent生成基準：Skillでは不足するか / 専門的視点が必要か / 継続利用価値があるか / 評価可能な役割か。Agent増加に伴う問題管理：Agent評価・利用コスト・重複・廃止判断。

### 03_全体統合アーキテクチャ仕様書
- 全体は Human Interface → Orchestrator（知的制御中枢）→ Workflow / Policy / Memory → Skill Layer → Primitive Layer → Execution → Evaluation Engine → Learning Loop の層構造。
- Orchestratorは「何をするか」ではなく「どう考えるべきか」を決定する層。
- 3つのモード：**制作モード**（一貫性重視・基本Single Agent・必要時のみ専門Agent）、**評価モード**（多視点・分散判断・バイアス低減）、**改善モード**（Evaluation Result → Reflection → Pattern Extraction → Memory Update → Workflow Improvement）。
- 成長段階モデル：Level 1 生成AI → Level 2 判断AI → Level 3 改善AI → Level 4 成長型知能。核心概念：「生成するAIから、成長するAIへ」。

## 4. 03 コアコンポーネント

### 00_数値定義書（単一正版・最重要）
評価・しきい値・算出式の**単一の正版**。旧版の「例」を根拠付きの**既定値**として固定し、各仕様書は本書を参照し数値を再定義しない。

**評価5軸と既定の重み**：
- Quality（完成度）0.25 / Logic（論理性）0.20 / Creativity（新規性）0.20 / Value（価値）0.25 / Risk（リスク）0.10。各軸は0〜1スケール。
- Riskのみ**低いほど良い**値であり、正規化時に反転する。
- **Overallスコア算出式**：`overall = quality×0.25 + logic×0.20 + creativity×0.20 + value×0.25 + (1−risk)×0.10`。

**合格しきい値**：
- overall ≥ 0.70 → 合格（Pass）→ 次フェーズへ
- 0.50〜0.69 → 要改善（Revise）→ 改善指示を生成し再制作
- < 0.50 → 不合格（Regenerate）→ 前提の見直しから再検討

**採点ルーブリック（各軸の行動的定義）**：Quality（明確・一貫・使用可能=0.8-1.0 / 一部欠落=0.5-0.7 / 不明瞭・不整合=0.0-0.4）、Logic（矛盾なし・根拠あり=0.8-1.0 / 根拠不足・飛躍=0.5-0.7 / 矛盾・根拠欠如=0.0-0.4）、Creativity（既存と明確に異なる=0.8-1.0 / 既存の組み合わせだが新規観点=0.5-0.7 / 焼き直し=0.0-0.4）、Value（必要性・影響力・継続性が明確=0.8-1.0 / 不確か=0.5-0.7 / 確認できない=0.0-0.4）、Risk（失敗時の影響大・実現可能性低=0.8-1.0 / 部分リスク=0.5-0.7 / 限定的・実現可能性高=0.0-0.4）。

**評価のキャリブレーション**：評価者自身の偏りを監査するため、同一入力を複数回評価しスコアの分散を記録。分散 < 0.05：安定 / 0.05〜0.15：要確認 / > 0.15：評価基準を再確認。

**Confidence / Unknown の算出**：
- `unknown`：**質的**。知らない項目のリスト。
- `unknown_level`：**量的**。未知の度合い（0〜1）。
- `unknown_level = Σ(重要度_i × 未解決_i) ÷ Σ(重要度_i)`（重要度で重み付け。重要度_i：各未知項目の重要度0〜1、未解決_i：未解決なら1・解決済みなら0）。
- `confidence = 1 − unknown_level`（基本形）。仮説が存在する場合は `confidence = 0.5 × (1 − unknown_level) + 0.5 × mean(hypotheses.confidence)`。

**判断しきい値**：
- 探索継続：unknown_level ≥ 0.6 → Explore / Research を優先
- 制作開始：confidence ≥ 0.75 かつ unknown_level ≤ 0.25 → Create へ
- 判断保留：それ以外 → 情報収集・代替案検討

**Cognitive Cost と思考Level**：
- `Cost = Importance × Uncertainty × Impact`。Importance：問題の重要度（0〜1）、Uncertainty：不確実性（0〜1、Stateの unknown_level と一致）、Impact：判断結果の影響範囲（0〜1）。
- Cost < 0.3 → Level 0〜1（即答・簡易分析）/ 0.3 ≦ Cost < 0.7 → Level 2（構造化思考）/ ≥ 0.7 → Level 3〜4（深い探索・戦略思考）。
- Level定義：0 Instant Response（単純回答・定型処理）/ 1 Basic Reasoning（一般的判断・軽い分析）/ 2 Structured Thinking（分解・比較・構造的判断）/ 3 Deep Reasoning（重要意思決定・研究・探索）/ 4 Strategic Thinking（長期戦略・複数シナリオ・複数Agent検証）。

**潜在価値モデル**：`Potential Value = Novelty × Growth × Adaptability × Timing`（各要素0〜1。いずれかが低いと全体が急減するため積形式のまま維持）。

**正版参照の表記揺れ解決**：リポジトリ構成=最終リポジトリ構成仕様書 / Primitive分類=6カテゴリ×20種・MVP8種 / 思考Level=本節4.3 / State Phase=observe→…→improve（小文字）/ Workflow Phase=Observe→…→Reflect（大文字）/ unknown, unknown_level=本節3.1。

**最終定義**：数値は装飾ではない。数値はこの設計の約束（考え方を自ら改善し続けるAI）を**反証可能にする手段**である。

### 01_状態モデル仕様書
- Stateは作業状況ではなく「AIが現在どのような認識状態にあり、次にどのような思考行動を取るべきかを判断するための内部状態」。
- State Object は14フィールド：id / goal / context / phase / known / unknown / unknown_level / hypotheses / constraints / confidence / active_question / available_actions / history / timestamp。unknown_levelはunknownから導出される量。
- **Phase表記の正版**：`state.phase`（状態段階）は7段階（小文字）`observe → understand → explore → design → create → evaluate → improve`。これは実行手順の `workflow phase`（Observe→Question→Explore→Structure→Create→Evaluate→Reflect、大文字）とは**別概念**。state.phaseは「今どの思考段階にいるか（状態）」、workflow phaseは「どの処理をどの順で実行するか（手順）」。
- State Transitionモデル：Current State → Action → Result → Evaluation → New State。
- State更新が発生する条件：新情報取得 / 仮説変更 / 評価結果 / 人間からの介入。
- StateとMemoryの関係：State=「今どこにいるか」、Memory=「どうやってそこに来たか」。
- 設計上の重要原則：Stateを隠さない（人間が確認可能に）/ Unknownを重要情報として扱う / State変更には理由を残す。
- MVP実装は Markdown + YAML（state/current.yaml, history/, schema.yaml）。

### 02_オーケストレーター仕様書（統合版）
- Orchestratorは「目的達成のために、必要な思考・制作・評価プロセスを選択し制御する**メタ判断エンジン**」。
- 担当しないこと：直接成果物を作る / 詳細な分析 / 長文生成。判断専門。
- 入力：state / workflow / available_skills / memory / policy / evaluation_history。出力は必ず判断理由付き（action / skill / reason / confidence）。
- 判断モデル：Goal + Current State + Unknown + Risk + Cost + Past Pattern → Next Action。
- Action分類：Observe / Question / Explore / Analyze / Create / Evaluate / Reflect / Stop。
- Action選択基準：Explore（unknown_level ≧ 0.6、Confidence低・判断材料不足）、Create（Structure十分・Goal明確・Confidence十分）、Evaluate（成果物完成・確認必要）、Reflect（失敗・改善余地・新パターン発見）。
- Agentを呼ぶ条件：単一視点では危険 / 専門知識が必要 / 評価の偏り防止が必要 / 失敗コストが高い。
- Policy Layer：判断基準は固定ではなく `core/orchestrator/policy.yaml` で管理（例：exploration.when_unknown: high、creation.minimum_confidence: 0.75、evaluation.always_after_creation: true）。
- 重要判断では複数候補を比較（Alternative Analysis）し、Decision Memory（memory/decisions/）に状況・判断・理由・結果を保存。
- 人間はOrchestratorを直接操作しない。介入場所は Goal変更 / Constraint追加 / Policy修正 / 評価基準変更。
- Orchestratorが避けること：すぐ制作する（探索不足）/ 全部Agent化する（コスト増大）/ 評価なしで終了する（改善不能）。
- MVPはルールベースで開始（policy.yaml, decision_template.md, rules.yaml, state.yaml, logs/）。
- 最終定義：AIが「何をするか」ではなく「なぜそれをするべきか」「どの程度考えるべきか」「どの能力を使うべきか」を判断するための**メタ認知制御層**。知能の中心は「思考方法を選択する能力」。

### 03_プリミティブライブラリ設計仕様書（統合版・正版）
- Primitiveとは「複雑な思考を構成する最小レベルの認知操作」。階層：Goal → Workflow → Skill → Primitive → Operation。
- 作る理由：文章・コード・システム設計の根底にある思考操作（分解・比較・抽象化・統合）は共通であり、「**汎用知能の基盤はPrimitive層に存在する**」。
- Skill（目的達成能力）とPrimitive（思考操作）は区別。Skill=「何ができるか」、Agent=「誰が判断するか」、Primitive=「どう考えるか」。
- 分類は**6カテゴリ・全20種**：
  - Analysis：Decompose（分解）, Compare（比較）, Classify（分類）
  - Generation：Generate（新規生成）, Combine（組合せ）, Expand（拡大）
  - Transformation：Abstract（抽象化）, Reframe（視点変更）, Simplify（単純化）, Synthesize（統合）
  - Reasoning：Infer（推論）, Deduce（演繹）, Induce（帰納）
  - Evaluation：Score（数値評価）, Critique（問題発見）, Verify（検証）, Evaluate（総合評価：5軸統合でoverallスコアと改善点を出力）
  - Reflection：Reflect（振り返り）, Extract Pattern（経験の法則化）, Update Belief（判断基準更新）
- **MVP Primitiveセット（8種）**：decompose / compare / abstract / reframe / generate / synthesize / evaluate / reflect。カタログ対応：Analysis→decompose, compare / Generation→generate / Transformation→abstract, reframe, synthesize / Reasoning→（なし）/ Evaluation→evaluate / Reflection→reflect。カタログに無いPrimitiveをMVPへ追加する場合は先に本書を改版してから追加。
- Primitive設計原則：小さくする / 汎用化する / 組み合わせ可能にする / 評価可能にする。Primitive追加基準：既存で表現できないか / 複数Skillで利用されるか / 独立評価できるか。
- Learning Engineとの関係：Primitive自体は頻繁に変更しない。改善対象は組み合わせ方・使用タイミング・順序。
- Primitive評価軸：Accuracy / Usefulness / Efficiency / Reusability。

### 04_思考コスト管理仕様書（正版）
- 目的：「AIが必要な場面では深く考え、不要な場面では効率的に処理するための判断制御層」。すべてを深く考えると時間・コスト増加・効率低下になるため、問いの重要度 × 不確実性 × 影響範囲で思考深度を決定。
- Cognitive Cost Managerの役割：Input → 問題分析 → 必要思考量判断 → 推論レベル決定 → Orchestratorへ通知。配置は Interface と Orchestrator の間。
- 判断パラメータ：Importance（問題の重要度）、Uncertainty（未知度・unknown_level 0.0-1.0）、Impact（影響範囲）、Time Constraint。
- 思考Level定義：Level 0 Instant Response（直接回答）/ Level 1 Basic Reasoning（分析→回答）/ Level 2 Structured Thinking（分解→比較→判断）/ Level 3 Deep Reasoning（Research→Hypothesis→Evaluation→Decision）/ Level 4 Strategic Thinking（Multiple Scenario→Risk Analysis→Simulation→Strategy）。
- Cost Score Model例：cognitive_cost: importance 0.8 / uncertainty 0.7 / impact 0.9 / time_pressure 0.2。計算：`Cost = Importance × Uncertainty × Impact`。
- 評価連携：成果物だけではなく**結果品質 + 思考効率**を評価（同品質なら短時間の方を高評価）。
- Failure Pattern：**Over Thinking**（簡単な問題に大量推論 → Cost Threshold調整）、**Under Thinking**（重要問題を浅く処理 → Impact判定強化）。
- MVP実装：Importance判定 / Unknown判定 / Thinking Level選択 / Orchestrator連携 / Log保存。後期：自己最適化・Dynamic Cost Learning・Multi Agent Resource Allocation（初期は除外）。
- 将来的にはAI自身の「注意制御機構」になる（思考量管理→注意配分→推論戦略選択→自己改善）。
- 最終定義：目的は「より長く考えるAI」ではなく「**必要な時に必要な深さで考えられるAI**」。

## 5. 04 スキルとワークフロー

### 01_スキルアーキテクチャ仕様書（統合版）
- Skillは「特定の目的達成のためにPrimitiveを組み合わせて構成された再利用可能な能力単位」。AIの「人格」ではなく能力モジュール。
- Skillは増やしすぎない（管理コスト増・組合せ爆発・判断困難）。制作は万能Skill（Create Everything）で作らない（判断不能・改善不能・再利用困難）。
- Skill階層（5階層）：Cognitive Skills（思考）/ Creation Skills（制作）/ Evaluation Skills（評価）/ Communication Skills / Tool Skills。
- Cognitive Skills：Question（良い問い生成）、Analyze（情報理解）、Structure（構造化）。Creation Skills：Generate（初期生成）、Refine（改善：Draft→Critique→Rewrite）、Transform（形式変換）。Evaluation Skills：Critique（弱点発見）、Compare（比較評価）、Score（数値化）。Meta Skills：Plan（作業計画）、Reflect（改善点抽出）、Learn（Pattern生成）。
- Skill内部構造：`skills/question/`（skill.md, input.yaml, output.yaml, examples/）。定義形式はYAML（name / purpose / requires / outputs）。
- Skill選択基準（Orchestratorが判断）：Goal + Current Phase + Required Capability + 過去成功パターン + Cost。
- MVP Skill構成（6種）：question / analyze / structure / create / evaluate / reflect。
- Claude Code実装：`.claude/skills/` に配置。設計ルール：Skillに人格を持たせない / Skillに最終判断を持たせない / Skillは再利用可能にする / Skill追加前にPrimitiveで表現できないか確認する。

### 02_ワークフローシステム仕様書
- Workflowとは「目的達成のために、どの思考プロセスをどの順番で実行するかを管理する**動的な手順構造**」。固定プロンプトではなく、状態確認→思考経路選択→実行→評価→改善。
- **Phase表記の正版**：`workflow phase`（実行手順）は7フェーズ（大文字）`Observe → Question → Explore → Structure → Create → Evaluate → Reflect`。これはStateの phase（小文字）とは別概念。
- 各Phase定義：Observe（現在状態理解・出力Context/Unknown）、Question（本質的な問い・出力Active Question/Research Direction）、Explore（未知を減らす・情報収集/比較/仮説形成）、Structure（構造設計）、Create（成果物生成）、Evaluate（品質確認・目的達成度/一貫性/改善点）、Reflect（経験化・Pattern抽出/Memory保存/Workflow改善）。
- 汎用Workflow設計：制作物ごとの専用Workflowを大量に作らない（小説専用・映画専用・企画書専用は再利用性低・管理コスト増）。共通思考フロー（問題理解→探索→構造化→生成→改善→評価）を利用。
- Workflowは固定ではない。OrchestratorがStateを見て変更（unknown high・confidence low→Explore追加、confidence high→Createへ移行）。
- 成功したWorkflowはPattern化（Workflow実行→Evaluation→成功パターン抽出→Pattern Memory→次回利用）。MVP構成：workflows/templates/（creation, research, problem-solving）+ active/。

### 03_ワークフローエンジンアーキテクチャ仕様書
- Workflow Engineの役割：Phase管理 / Process制御 / Feedback反映。Orchestrator=「何をするべきか判断」、Workflow Engine=「どう進めるか管理」、Skill=「実行」。
- State Driven Workflow：状態で流れを変える（unknown 0.8・confidence 0.3→Explore継続、unknown 0.1・confidence 0.9→Create移行）。
- 基本Workflow一覧：Creation Workflow（Goal→Research→Structure→Draft→Critique→Improve→Finalize）、Problem Solving Workflow（Problem→Decompose→Analyze→Generate Options→Evaluate→Decision）、Research Workflow（Question→Explore→Collect→Compare→Synthesize→Insight）、Learning Workflow（Result→Reflection→Extract Pattern→Memory Update）。
- Transition条件：`transition: from: explore, to: create, condition: confidence >= 0.75, unknown_level <= 0.25`（正版 §3.4 に揃える）。
- Workflow評価項目：Efficiency / Quality / Cost / Success Rate / Reusability。
- Workflow自体の改善ループ：Execution→Evaluation→Problem Detection→Workflow Modification→Verification。
- 避ける設計：巨大Workflow / 全タスク共通Workflow / SkillとWorkflowの混同。
- 将来拡張：Adaptive Workflow / Workflow Optimization / Multi-Agent Workflow。

## 6. 05 メモリー

### 01_メモリーアーキテクチャ仕様書（統合版）
- Memoryは「AIがどのように考え、なぜ判断し、その結果どう改善したかを保存する**知的経験データベース**」。知識保存ではなく思考履歴保存が中心。
- 保存価値の優先順位：**1. Thought Trace（思考軌跡）→ 2. Decision Memory（判断履歴）→ 3. Pattern Memory（成功パターン）→ 4. Knowledge Memory（知識情報）**。
- 全体構造（4層）：State Memory / Thought Trace Memory / Pattern Memory / Knowledge Memory。ディレクトリ構造：memory/working, traces, decisions, patterns, knowledge。
- **Thought Traceは最重要Memory**：「状態がどのように変化したかを記録した思考ログ」。保存するもの：何を考えたか / なぜ判断したか / 他の選択肢 / 迷った点 / 結果（次に何をするか）。形式はMarkdown。
- Markdownを採用する理由：可読性 / 編集可能性（AIと人間の共同管理）/ Git親和性 / 長期保存性。
- Knowledge Memoryは優先度低（「知識そのものより、知識をどう使ったか」が重要）。
- Memory更新タイミング：常時保存せず、重要イベント時のみ（Decision変更・失敗発生・成功発見・新Pattern発見・Workflow変更）。書き込み条件：判断が変化 / 新パターン発見 / 失敗理由判明 / 将来再利用価値。
- Memory読み込み：大量検索しない。Current State → 必要なMemory種類判断 → 関連Memory検索 → Decision補助。
- Memory肥大化対策：Consolidation（類似Memory統合）/ Abstraction（具体例からPattern化）/ Forgetting（価値低下Memory整理）。
- Memory Evolution：Log → Trace → Pattern → Principle → Intelligence。
- Claude Code統合：`Git Diff + Thought Trace = 進化履歴`。
- MVP実装：Markdownベース（memory/current.md, traces/, decisions/, patterns/）。不要：Vector DB / Knowledge Graph / 複雑な検索基盤。
- 最終定義：Memoryは情報保存庫ではなく「**AIの思考進化を記録する長期的な認知履歴**」であり「AIが成長した証跡そのもの」。

## 7. 06 評価と学習

### 01_エバリュエーションエンジン詳細仕様書（統合版）
- Evaluation Engineは「成果物・判断・プロセスを多面的に評価し、価値向上につながるフィードバックを生成するシステム」。目的は単純な採点ではない：良し悪しの判断 / 問題点発見 / 改善方向提示 / 次回判断への反映。
- 評価対象は成果物だけではない：**Artifact（成果物）/ Decision（判断）/ Process（思考過程・Workflow・Skill利用・思考経路）/ System（Agent・Skill・Primitive）**。
- 基本評価軸（MVP）：Quality / Logic / Creativity / Value / Risk。各軸の評価質問：Quality「実際に使える状態か」、Logic「説明可能な構造か」、Creativity「既存との差分は何か」、Value「将来的な価値はあるか」、Risk「失敗すると何が起きるか」。
- 潜在価値評価（Insight Synapse独自）：現在価値だけでなく「未来で伸びる可能性」を見る。`Potential Value = Novelty × Growth Potential × Adaptability × Timing`。
- Multi Evaluator Architecture：評価は分散（Logic / Creative / Value / Risk / Quality Evaluator → Integrated Score）。単一AIの自己正当化・視点固定・見落としを防ぐ。
- 評価出力は点数だけではなく改善情報（# Evaluation Report：Overall Score / Strength / Weakness / Potential / Improvement / Recommendation）。
- 評価基準自体も改善対象（Evaluation → Compare Result → Improve Criteria）。
- 初期評価基準（重み）：quality 25% / logic 20% / creativity 20% / value 25% / risk 10%（正版は数値定義書 §2）。
- 中心能力は「生成能力ではなく、価値を見抜き改善する能力」。Evaluationは「自己批評能力」を担当。

### 02_ラーニングシステム仕様書
- Learningは「過去の思考・判断・結果から、より良い問題解決方法を発見し、未来の行動選択を改善するプロセス」。一般的なモデル更新ではなく、経験→評価→パターン抽出→判断改善→能力向上。
- 「上達」の定義（回答品質が上がるだけではない）：判断能力の向上 / 問題発見能力の向上（本質的な問題の再定義）/ Workflow選択能力の向上 / 評価精度の向上。
- Learning対象（4種類）：**Policy Learning**（判断基準・評価基準・思考コスト判断）/ **Pattern Learning**（成功・失敗パターン抽出）/ **Workflow Learning**（問題解決手順改善）/ **Skill Learning**（使用タイミング・組み合わせ・順序）。
- Learning Loop：Experience → Thought Trace → Evaluation → Insight Extraction → Memory → Policy/Workflow Update → Future Decision。
- Insight ExtractionはLearningの中心処理（入力：Thought Trace・Evaluation Result・Outcome、出力：problem / cause / improvement）。
- **自己改善の制約（完全自律変更は禁止）**：Level 1 Memory追加=許可 / Level 2 Pattern追加=許可 / Level 3 Workflow変更=要確認 / Level 4 Core Policy変更=人間承認。
- Learning Metrics（成長確認指標）：Decision Accuracy → Problem Definition Quality → Iteration Reduction → Output Quality → Human Satisfaction。
- MVPは自動学習ではなく**半自動改善**（learning/insights, patterns, proposals, approved）。Claude Code運用：Memory追加→Diff確認→Human Review→採用。
- 学習とはモデル変更ではなく**思考方法改善**。失敗を重要な学習データとして扱う。

### 03_テスト・評価フレームワーク仕様書（統合版）
- 単純な出力正解判定ではなく、「思考→判断→実行→評価→学習」の循環が機能しているかを検証する。
- 評価対象4階層：Level 1 成果物 / Level 2 制作プロセス / Level 3 思考・判断（Problem Definition・Exploration Quality・Decision Quality・Risk Awareness・Alternative Consideration）/ Level 4 システム進化能力。
- テスト対象レイヤー：Primitive / Skill / Workflow / Orchestrator / Evaluation / Memory / System の各Test。
- 重要テスト：**Memory Influence Test**（過去経験あり→判断改善、なし→判断低下になるか）。**Intelligence Growth Test**（Version 1→2→3で判断精度・作業効率・評価品質・再利用性を比較）。
- 評価エンジン構造：Criteria Manager / Scoring Engine / Critic（単純採点ではなく改善点発見）/ Insight Extractor / Report Generator。重みは数値定義書 §2 に従う（overall = quality×0.25 + logic×0.20 + creativity×0.20 + value×0.25 + (1−risk)×0.10）。
- Regression Test：Workflow・Skill・Primitive・Evaluation基準変更による劣化防止（新バージョン→過去ケース再実行→品質比較）。
- Benchmark設計：評価用タスクを保存（creative_task / coding_task / planning_task / research_task）。
- 評価スコアの扱い：数値だけで判断しない（Score + Reason + Weakness + Next Improvement）。
- 成長指標：少ない修正回数で完成 / 判断理由の品質向上 / 再利用パターン増加 / Workflow改善速度 / 人間評価向上。
- Human Evaluation：理解可能性・納得度・有用性・信頼性。AI評価だけに依存しない。
- 最終目的：評価はランキングではない。評価→理解→改善→成長。最重要評価は「**昨日より良い判断ができるようになっているか**」。

## 8. 07 インターフェースとAPI

### 01_ヒューマンインターフェース仕様書
- 人間とAIの役割分離：人間は「目的・価値・方向性を調整する存在」、担当は Goal設定・制約設定・評価基準設定・最終判断・重要な方向修正。AIは情報整理・思考展開・仮説生成・制作・評価・改善提案。
- 人間介入ポイントは限定：Point 1 Goal設定（開始時）/ Point 2 Direction確認（探索後）/ Point 3 Evaluation確認（成果物後）。
- MVP操作方式：UIを作らない。Claude Code + Markdown + Git を利用。コマンド設計：`/synapse think`（思考開始・State確認・次Action判断・Thought Trace生成）、`/synapse evaluate`（評価基準読込・Evaluation実行・改善提案）、`/synapse status`（Current State・Phase・Unknown・Next Action表示）、`/synapse trace`（Thought Trace・Decision履歴表示）。
- Human Feedbackは自由文章だけにしない：構造化する（# Feedback：Decision / Change / Reason）。種類：Direction Change（方向修正）/ Constraint Addition（制約追加）/ Quality Judgment（評価）。
- AIから人間への提示：結果だけを返さない。Decision → Reason → Alternative → Risk → Recommendation。
- 自律性レベル（0〜4）：0 質問回答 / 1 提案型 / 2 半自律（AI実行・人間確認）/ 3 監督型自律 / 4 高度自律（限定領域で自己改善）。**MVP推奨レベルは Level 2**（制御可能・改善履歴が残る・暴走しにくい）。
- 将来UI拡張：Markdown → Web Dashboard → Multi User Platform。

### 02_ヒューマンインターフェースMVP仕様書
- UI設計方針：軽量にする。不要：高度な3D表示・複雑なグラフ・大規模管理画面。必要：状態確認・思考履歴確認・判断確認・承認操作。
- MVP UI構成：Chat Interface / Current State View / Thought Trace Viewer / Decision Panel / Memory Viewer。**Thought Trace Viewerは最重要UI**（ブラックボックス化防止・人間との協調・改善材料）。
- Decision Panel：Decision / Reason / Confidence / Approval（Accept / Modify / Reject）。
- MVP技術構成：Frontend Simple Web UI / Backend API Server / Storage Markdown Files + Git。Markdown First設計（可読性・編集容易性・Git管理・Claude Codeとの相性）。初期ではDBを必須にしない。
- MVP成功条件：人間が 1. AIの状態を理解できる 2. 判断理由を確認できる 3. 修正指示できる 4. 改善履歴を追える。目的は「AIを操作することではなく、**AIと一緒に考えること**」。

### 03_APIインターフェース設計書
- 「直接呼び出し」を避ける（Skill→Memory直接操作は禁止。Skill→Orchestrator→Memory Service）。
- 通信モデル：Human → Interface API → Orchestrator API → Workflow API → Skill API → Evaluation API → Memory API。
- 共通データ形式：Request（request_id / timestamp / source / payload）、Response（request_id / status / result / trace_id）、Error（status / error_type / message / trace_id）。
- API一覧：POST /goal、GET /state、POST /state/update、POST /decision（Orchestrator）、POST /workflow/run、POST /skill/run、POST /primitive/run、POST /evaluate、POST /memory/save、POST /memory/search、POST /trace/save、POST /approval（Human Approval）。
- 重要ルール：**すべての重要API実行はTraceを残す**（API Call → Trace → Evaluation → Memory）。
- MVP API範囲：/goal, /state, /decision, /skill/run, /evaluate, /memory/save。後回し：Agent API / Marketplace API / Distributed Memory API。
- API設計原則：Layer間依存を減らす / すべての判断は追跡可能にする / データ形式を長期保存可能にする / 将来拡張可能な境界を作る。最終定義：APIはデータ交換ではなく「**知能の各機能を協調させる神経系**」。

## 9. 08 データと技術仕様

### 01_技術仕様書
- 基本設計方針：MVPでは複雑な基盤を作らない（採用：Markdown・YAML・Git・軽量API）。データは人間が読める形式で保存（監査可能・修正可能・AI自身が理解可能）。各Layerの責務を分離。
- 推奨技術スタック：Runtime Python（AI処理との親和性・豊富なライブラリ・実験容易性）、API Framework FastAPI、Data Storage MVP=Markdown+YAML+Git（将来=SQLite→Vector Database→Knowledge Graph）、Frontend MVP=Simple Web UI（候補React/Next.js）。
- Core Module仕様：core/state（現在状態管理）、core/orchestrator（意思決定・入力goal/state/memory・出力action/reason/confidence）。
- 技術的品質基準：Maintainability / Explainability / Extensibility / Observability。
- 実装判断ルール：Layer責務は明確か / Memory化できるか / Evaluation可能か / 将来拡張できるか。
- 最終定義：目的は「AIを動かすコードを書くこと」ではなく「**成長する知能構造を壊さず実装すること**」。

### 02_データモデル設計仕様書
- 保存対象は「何を知っているか」だけでなく「**どう考えたか**」。
- データ階層：Memory → State / Thought Trace / Decision / Artifact / Evaluation / Pattern。
- 各Model：State Model（memory/state/current_state.yaml：goal, phase, confidence, unknown_level, current_action, timestamp）、Thought Trace Model（memory/traces/：Goal, Question, Analysis, Hypothesis, Decision, Confidence, Next Action）、Decision Model（Context, Options, Selected, Reason, Risk, Expected Outcome）、Artifact Model、Evaluation Model（quality, logic, creativity, value, risk, overall, feedback, improvement）、Pattern Model（最重要Memory：Situation, Problem, Lesson）。
- Memory Lifecycle：Experience → Trace → Decision → Evaluation → Pattern → Principle。
- **Raw MemoryとIntelligent Memory**の2種類：生データ（ログ・思考履歴・会話）と抽象化された知識（成功パターン・判断基準・原則）。Raw → Extraction → Intelligent。
- Memory品質管理：保存基準 = 重要性 × 再利用性 × 改善効果。保存しないもの：一時的情報・重複ログ・価値のない会話。
- MemoryもGit管理（decision_v1.md, decision_v2.md…）。判断の変化を見るため。
- MVP保存対象：current_state.yaml / thought_trace.md / decision_log.md / evaluation_report.md / pattern.md。

### 03_ユースケース設計書
- 利用モデル：Human Goal → 理解 → 分析 → 生成 → 評価 → 改善 → Memory化。
- ユースケース一覧：01 新規事業アイデア評価 / 02 文章・コンテンツ制作（小説・記事・脚本・SNS投稿）/ 03 AI開発支援（AI自身が開発プロセスを改善）/ 04 研究・調査支援 / 05 意思決定支援 / 06 個人知的アシスタント / 07 チーム知識共有（Individual Memory → Shared Pattern Memory → Organization Intelligence）/ 08 AI Agent管理（複数AIの協調制御）。
- MVP優先ユースケース：Priority 1 意思決定支援（EvaluationとMemoryの価値を確認しやすい）/ Priority 2 コンテンツ制作（生成→評価→改善が見えやすい）/ Priority 3 AI開発支援（自身の改善ループを検証できる）。
- 成功指標：判断品質向上 → 作業時間短縮 → 再利用性向上 → 継続的改善。
- **§14 受益者物語（テーゼの人間的価値への写像）**：物語1 起業家・野村（事業評価AIが評価のたびに賢くなる。思考経路の再利用・State=状態遷移に対応）、物語2 管理職・佐藤（判断理由が属人知から組織知へ。Thought Trace中心の記憶・透明性に対応）、物語3 作家・鈴木（直感が構造化され再現できる。unknown管理・評価→改善の循環に対応）。
- 最終ビジョン：目的は「AIに仕事をさせる」ではない。**人間とAIが共に考え、経験を蓄積し、より良い判断を生み出す知的協働環境**を作ること。中心価値：「答えを出すAIではなく、答えを磨き続けるAI」。

## 10. 09 セキュリティ

### 01_セキュリティ・ガバナンス仕様書（統合版）
- 「自律性」と「制御性」を両立。基本は AI提案 → 評価 → 承認 → 適用 のHuman-in-the-loop。
- セキュリティ対象：User Data / Memory / Thought Trace / Decision Log / Policy / Skill / Agent Permission。
- 基本原則：最小権限（各Layerは必要最低限の権限だけ。Layer間の直接操作は禁止：Skill→Memory直接変更はダメ、Skill→Memory API→保存が正）。
- 権限モデル（Level 0〜5）：0 閲覧のみ / 1 Memory更新 / 2 Skill実行 / 3 Workflow変更 / 4 Policy変更 / 5 System変更。**MVP推奨権限：Human Level 5 / AI Level 2**。
- Memory Security：重要MemoryはHash管理で改ざん検知。Thought Traceは「判断モデル」としてアクセス制限・Version管理・Audit Logで保護。
- Evaluation Governance：評価基準が変化するとAIの方向性が変わるため、Criteria変更履歴・評価結果・評価偏りを監視。
- External Tool Security：Agent → Tool Gateway → External Service の経路で管理（Tool → Permission → Execution Log）。
- **Prompt Injection対策**：外部入力は Validation → Context Isolation → Processing。重要：外部情報をSystem Policyとして扱わない。
- Data Isolation：User Data/User Memory と System Data/System Memory を分離。混在禁止。
- Secret Management：API Key・Token・Credentials は .env か Secret Manager に保存。コードへの直書き禁止。
- **自己改善ガバナンス**：自動許可（低リスク：Trace追加・Pattern保存・Memory整理）/ 承認制（中リスク：Workflow変更・Skill追加・Evaluation基準変更）/ 人間のみ（高リスク：Core Policy変更・Orchestrator変更・権限変更）。
- Change Proposal System：AIは直接変更ではなく提案する（# Change Proposal：Target / Change / Reason / Expected Effect / Risk）。
- 暴走防止設計（避けるもの）：自己目的化（品質改善より評価数値最大化を優先）/ 無限改善（成果物を作らず改善だけ続ける）/ 評価基準の乗っ取り（自分に有利な基準へ変更）。
- セキュリティ評価基準：Confidentiality / Integrity / Availability / Explainability / Controlability。
- MVP実装：governance/permissions.yaml, change_requests/, approvals/, audit_logs/。初期実装：Memory分離・Git Version管理・Audit Log・Human Approval・Secret管理。後期：Distributed Security / Agent Sandbox / Zero Trust Architecture。
- 将来拡張：Phase 2 Policy Version管理・Automatic Testing / Phase 3 Multi Agent監査・Independent Evaluator / Phase 4 Formal Verification。
- 目標は「AIを制限すること」ではなく「**安全に進化できるAIの環境を設計すること**」。

## 11. 10 環境とリポジトリ

### 02_最終リポジトリ構成仕様書（正版）
- リポジトリは「機能別」ではなく「**知能構造別**」に分割（Thinking → Planning → Execution → Evaluation → Learning）。
- 最終ディレクトリ構成：`.claude/`（CLAUDE.md, skills/：synapse-think, synapse-create, synapse-evaluate）、`core/`（orchestrator, state, decision）、`workflows/`（creation, research, problem-solving, learning）、`skills/`（cognitive, creation, evaluation, communication）、`primitives/`（decompose, compare, abstract, reframe, generate, synthesize, evaluate, reflect）、`agents/`（evaluator, researcher, specialist）、`evaluation/`（criteria, benchmarks, reports）、`memory/`（state, traces, decisions, patterns, knowledge）、`governance/`（permissions.yaml, policies/, audit/）、`interface/`（api, web）、`tests/`、`docs/`、`README.md`。
- 各Layer責務：core=中枢（状態管理・判断・制御）、orchestrator=最重要（次Action判断・Skill選択・Agent呼出判断）、workflows=目的達成までの流れ、skills=再利用可能な能力、primitives=最小思考操作、agents=専門判断主体。
- MVP削減版：.claude/ + core/orchestrator/ + skills/ + evaluation/ + memory/ + workflows/ + README.md。
- 初期実装順序：Step 1 Memory → Step 2 Orchestrator → Step 3 Evaluation → Step 4 Skill → Step 5 Workflow → Step 6 Interface。
- Git運用：**1 Decision = 1 Commit**（Commit例：`Add creation workflow / Reason: Improve reusable production flow`）。
- 開発原則：Layer間の責務を混ぜない / 判断はCoreへ / 能力はSkillへ / 経験はMemoryへ / 改善はEvaluationから始める。
- リポジトリの中心はコードではなく「**AIが成長するための構造設計**」。

### 03_開発環境構築仕様書
- 開発方針：Simple → Observable → Upgradeable。初期段階では高度なインフラより「思考構造を高速に改善できる環境」を優先。
- 推奨技術スタック：Python 3.12+ / FastAPI / MVPはSimple Web Interface（将来React→Next.js）/ DBは段階（Phase 1 Markdown+YAML → Phase 2 SQLite → Phase 3 Vector Database）。
- 必須ツール：Git・Python・VS Code・Claude Code。推奨：Docker・GitHub Actions・pytest・ruff。
- CLAUDE.md配置：`.claude/CLAUDE.md`（Project Vision / Architecture Rules / Coding Rules / Testing Rules / Security Rules）。AI開発者に設計思想を共有する。
- Git運用：ブランチ main（安定版）/ develop（開発統合）/ feature/*（機能追加）。Commit形式：feat: / fix: / docs: / refactor:。
- 開発用Memory：通常Memoryと分離（memory/runtime/ と memory/development/。developmentは設計判断・変更理由・技術選択を保存）。
- MVP開発開始条件：Repository / CLAUDE.md / Environment / Folder Structure / Basic Test / Configuration が完成していること。

### 01_リポジトリ構築ガイド
- 初期ディレクトリ作成手順（git init、`.claude/ core/ workflows/ skills/ primitives/ agents/ evaluation/ memory/ governance/ interface/ docs/` を作成）。最終形の正版は `02_最終リポジトリ構成仕様書`。

## 12. 11 実装計画とロードマップ

### 01_MVP実装仕様書
- MVPの定義：Goal入力 → Orchestrator判断 → Skill実行 → 成果物生成 → Evaluation → Memory保存、という一連のループが動作する状態。
- MVPで作らないもの：複雑なWeb UI / 完全自律エージェント / 独自LLM / ベクトルDB / 高度な強化学習 / 複雑なマルチエージェント制御（思考構造の検証を優先するため）。
- MVPコア構成：Orchestrator / Skill System / Primitive System / Memory System / Evaluation System / Workflow System。
- CLAUDE.mdの役割：Claude Codeに思想を理解させる（Rules例：Always record thought trace / Evaluate before finalizing / Prefer reusable patterns / Separate Skill and Primitive）。
- MVPで重要なファイル優先順位：CLAUDE.md（行動原則）→ policy.yaml（判断基準）→ current.md（現在状態）→ trace.md（思考履歴）。
- 技術選択：Language Markdown・YAML・Python(optional) / Execution Claude Code / Storage Git。
- **MVP成功条件（4条件）**：1. AIが判断理由を説明できる 2. 思考履歴が保存される 3. 評価結果から改善案が出る 4. 別テーマでも同じ構造で動く。
- 将来拡張：MVP → Tool Integration → Multi Agent Evaluation → Vector Memory → Autonomous Workflow Generation → AI Development Platform。

### 02_MVP実装計画書
- Phase 1 Foundation（core/state, orchestrator, decision）→ Phase 2 Memory System → Phase 3 Orchestrator（Goal解析・Phase判断・Cost判断・Skill選択）→ Phase 4 Evaluation Engine → Phase 5 Skill System → Phase 6 Workflow Engine → Phase 7 Claude Code Integration。
- 最初のデモシナリオ：「Insight Synapse自身を改善する」。
- MVP評価基準（4つ）：Criterion 1 判断理由が残る / Criterion 2 改善履歴が残る / Criterion 3 同じ問題で以前より良い判断ができる / Criterion 4 人間が途中介入できる。
- 開発期間目安：POC=数日（Memory・Decision・Simple Evaluation）、MVP=数週間（Skill・Workflow・Claude統合）、実用版=数ヶ月（UI・Agent・External Tools）。
- 最初にClaude Codeへ渡す指示の原則：判断理由を保存する / Layer責務を守る / 変更理由を記録する / 小さく実装する。

### 03_MVP完成判定基準書
- MVP必須機能：Goal Input / State Management / Orchestrator / Workflow Engine / Skill System / Primitive System / Evaluation Engine / Memory System。
- 合格条件：Functional（動作する・データ保存できる・結果を取得できる）/ Intelligence（判断理由がある・評価できる・改善案が出る）/ Memory（思考履歴が残る・パターン抽出できる・次回利用できる）。
- MVP品質基準：Explainability / Reproducibility / Extensibility / Safety。
- 次フェーズ移行条件（Phase 3へ）：End-to-End成功 / Memory蓄積確認 / Evaluation改善確認 / Human利用価値確認。
- 完成基準は「**機能数ではなく、知能循環が回ること**」。

### 04_Claude Code統合仕様書
- Claude Code=実行環境、Insight Synapse=思考システムとして分離。Claude Codeが担当：ファイル操作・コード生成・Skill呼び出し・Memory更新・Git操作。**担当しないもの：独自判断基準・長期記憶・評価基準**（これらはInsight Synapse側で管理）。
- CLAUDE.mdは基本人格ではなく「開発ルール」として利用。
- Claude Skill統合（3種）：`.claude/skills/synapse-think`（思考開始：Current State確認→Unknown抽出→Orchestrator判断→Next Action生成）、`synapse-create`（制作実行）、`synapse-evaluate`（評価実行）。
- コマンド：/synapse think / /synapse create / /synapse evaluate / /synapse status。
- Git連携：1 Action = 1 Commit。MVPでは大量Agentを作らない。
- 将来拡張：Phase 2 MCP連携・外部ツール接続・Vector Memory / Phase 3 Multi Agent Evaluation・Autonomous Workflow Generation / Phase 4 複数AI協調環境。
- 最終定義：Claude Codeは手足であり、Insight SynapseはAIの「考え方を管理する脳構造」。

### 05_Claude Code実装開始手順書
- 開発思想：コードを書く前に構造を理解する / 変更する前に理由を確認する / 実装より設計整合性を優先する。
- CLAUDE.md内容：Role・Mission（思考・制作・評価・改善を循環するAI基盤を構築）・Principles（1.設計思想を維持 2.Layer責務を混ぜない 3.判断理由を残す 4.小さく実装する 5.変更履歴を管理する）・Architecture（Core=判断 / Workflow=流れ / Skill=能力 / Primitive=思考操作 / Memory=経験保存 / Evaluation=改善）。
- AI開発時の禁止事項：巨大なコードを一度に作る / Layerを跨いだ直接依存 / 判断理由なしの変更。
- テスト方針：最初は機能テストより**思想テスト**を重視（この変更はInsight Synapseの思想に合っているか）。
- Development Memory：開発そのものも記録（memory/development/decisions, failures, lessons）。

### 06_Claude Code実装実行計画書
- Claude Codeの役割：設計理解 → 実装 → テスト → 改善提案 → 設計Memory更新。
- 実装フェーズ：Phase 0 Repository Setup → Phase 1 Memory Core（最初に作る。Insight Synapseの中心だから）→ Phase 2 Orchestrator → Phase 3 Evaluation Engine → Phase 4 Primitive Layer → Phase 5 Skill Layer → Phase 6 Workflow Engine → Phase 7 API Layer（POST /goal, /decision, /evaluate, /memory/save）→ Phase 8 First POC完成。
- Claude Code禁止事項：勝手な巨大設計変更 / 不要なFramework追加 / Memoryを無視した実装 / 判断理由を残さない変更。
- 開発サイクル：Issue → Design → Implementation → Test → Evaluation → Memory Update。
- 完成判定：POCが動作する / 思考Traceが残る / 判断理由が残る / 評価できる / Memoryを再利用できる。

### 07_開発ロードマップ仕様書（統合版）
- 開発基本方針：機能追加よりも 思考構造 → 判断精度 → 再利用性 → 自律性 の順番を優先。小さく作る→評価する→改善する→拡張する。
- 全体ロードマップ（6 Phase）：
  - **Phase 0 Concept Validation**（数日〜1週間・思想検証）：CLAUDE.md + Memory + Evaluation Template で最小検証。成功条件は出力品質ではなく「改善過程が見えるか」。
  - **Phase 1 POC / Thinking Core**：Memory + State + Decision + Evaluation。成功条件：1つの制作物について 作成→評価→改善→再作成 ができ、AIが「なぜ判断したか」「次に何をするか」を説明できる。
  - **Phase 2 MVP**（数週間〜1ヶ月）：Workflow（Creation/Research/Problem Solving）・Primitive追加・5軸Evaluation。成功条件：異なる分野（文章・コード・企画・研究）で利用可能。
  - **Phase 3 Practical System**（数ヶ月）：Human Interface・Agent System（Research/Critic/Specialist）・Tool Integration・Memory強化（Vector検索・Knowledge Graph）・評価強化・自動Workflow生成。成功条件：人間とAIが共同作業できる。
  - **Phase 4 Adaptive Intelligence / Autonomous Platform**：Self Workflow Generation・Self Skill Evolution・Policy Evolution・Memory Intelligence・Multi Agent Collaboration。成功条件：過去経験から未来判断が改善される。
  - **Phase 5 Intelligent Ecosystem**：Multi Agent Society・Shared Memory・Agent Marketplace。
- 実装優先順位：**1. Memory 2. Orchestrator 3. Evaluation 4. Skill 5. Workflow 6. Interface 7. Multi Agent**（知能の成長には生成能力より判断・評価・記憶が重要だから）。
- MVP開発スプリント：Sprint 1 Memory Foundation → 2 Decision Engine → 3 Evaluation Engine → 4 Skill System → 5 Workflow Engine → 6 Interface。
- 技術的負債管理（避ける）：巨大Framework化・複雑なAgent化・過剰なUI・早すぎるDB化。優先：「思想を壊さない単純さ」。
- **リスク管理**：Risk 1 複雑化→対策 Layer分離 / Risk 2 AI暴走→対策 Policy + Human Approval / Risk 3 Memory肥大化→対策 Pattern抽出 / Risk 4 Agent乱立→対策 追加基準。
- 最初の実験テーマ：「Insight Synapse自身をInsight Synapseで設計する」（自己適用・改善点が見える・Memory価値を検証）。具体例：アイデア評価AI。
- 成功指標：Intelligence（判断品質向上・改善速度）/ Efficiency（思考コスト削減・再利用性）/ Human Value（理解可能性・制御可能性）。
- 開発の目的は「最も強いAIを作ることではなく、**最も成長できるAI構造を作ること**」。

### 08_最初の実装タスク一覧
- タスク一覧：Task 001 Repository Foundation / 002 CLAUDE.md作成 / 003 Memory Foundation / 004 State Management / 005 Decision Logger / 006 Simple Orchestrator（Unknown High→Research、Unknown Low→Create）/ 007 Evaluation Prototype / 008 Primitive Prototype / 009 Skill Framework / 010 Workflow Prototype / 011 End-to-End Demo / 012 Improvement Loop（過去経験が次回判断に影響するか確認）。
- 最初のデモ成功基準：Goalを受け取れる / 状態判断できる / 次行動を決定できる / 理由を説明できる / 評価できる / Memory保存できる。
- 最初の目標：「Memoryを持った判断エンジンを作ること」。

### 09_最初の動く試作品設計書（POC）
- 目的：最小構成で「判断・評価・Memory化」という核となる循環の成立を検証。POCテーマは「アイデア評価AI」（判断品質を測定しやすい・Evaluationが活用できる・Memory効果を確認できる）。
- 最小システム構成：main.py / orchestrator/decision.py / skills/analysis.py / evaluation/evaluator.py / memory/(traces, decisions, patterns) / api/server.py / tests。
- 最初のAPI：POST /analyze（入力 idea → 出力 analysis / evaluation / memory_id）。
- POC評価基準：Functional（入力できる・判断できる・評価できる・保存できる）/ Intelligence（判断理由がある・改善案がある・次回利用できる）。
- POCで検証しないもの：完全自律Agent・複数AI協調・Vector Database・高度GUI・自己改造。
- **検証する仮説（単一反証可能）**：仮説H「unknownを明示管理し、Thought Traceを記憶として残すアーキテクチャは、同一のアイデア評価タスク群において、Memoryなしのベースラインより評価の成功率を**20%以上**向上させる」。
  - 反証条件：Memoryありの成功率がMemoryなしを下回る、または向上幅が**5%未満**（測定誤差の範囲内）→ 仮説Hは棄却され、テーゼ（思考管理が能力を改善する）そのものを再設計。
- **対照実験の設計**：同一の評価タスク集合を2条件（条件A Memoryなし=ベースライン / 条件B Memoryあり=Thought Trace + Decision Log + Pattern参照）で実行。タスク数 N=20（固定）、タスク順は条件間で交互に入れ替え（順序効果を排除）、評価は同一の5軸ルーブリックを使用。
  - 測定指標：1. 成功率（評価overall ≥ 0.70 となったタスクの割合）2. 評価分散（同一入力を2回評価した際のばらつき）3. 判断理由の質（根拠・代替案・リスクを含む割合）。
  - 判定基準：成功率向上 ≥ 20% → 仮説H支持・テーゼの実証とみなす / 向上 5%〜20% → 部分的に支持・設計の調整で再実験 / 向上 < 5% または低下 → 仮説Hは棄却・テーゼを再検討。
- POC成功後の追加：Workflow Engine → Skill拡張 → Pattern Memory → Agent Architecture。

## 13. 既存フレームワークとの差異化（01_01 §8）

Insight Synapseは既存の自己改善AI・エージェント・記憶管理手法の延長線上ではなく、「**思考そのものを管理対象・再利用対象にする**」点で異なる。

| フレームワーク | 中心思想 | Insight Synapseとの差異 |
|---|---|---|
| Reflexion | 失敗後に言語で振り返り、次の試行を改善 | 振り返りは改善ループの一部でしかない。State Model・unknown管理・思考経路の構造化保存を持たず、振り返りを「再利用可能な思考知識」として蓄積しない |
| Self-Refine | 同一生成内で feedback→improve を反復 | ループが単一タスク内で閉じる。タスクを跨ぐ長期記憶・判断基準の学習がなく、Orchestratorによる判断と実行の分離もない |
| MemGPT | コンテキスト窓を階層メモリで擬似的に拡張 | 目的は「記憶容量の拡張」。記憶を「思考経路の再利用」や「判断基準の改善」に使わず、Thought Traceを中心に置かない |
| Gödel machine | 自身のコードを数学的に証明付きで書き換える自己改善 | 理論上は完全だが実装困難。Insight SynapseはPOC対照実験による経験的検証と、人間承認（自己改善のLevel制約）による実践的自己改善を採用 |
| AutoGPT | 目的を分解しツールを自律実行 | 判断過程が暗黙的で、State・unknown・評価基準が構造化されない。評価→改善→学習の循環が第一級のレイヤーとして存在しない |

**差異化の3軸**：
- 軸1 思考 = 状態遷移 を明示的に扱う → State Model + unknown管理（未知を最重要情報にする）
- 軸2 思考経路そのものを再利用可能な知識にする → Thought Trace中心の記憶（「どう考えたか」を保存）
- 軸3 自己改善を「管理された改善」にする → 評価は改善のため・学習は制約付き・人間は方向調整者

要点：既存手法は「出力を良くする」「記憶を増やす」「自律させる」ことを目指す。Insight Synapseは「AIの考え方そのものを、人間が監督できる形で改善し続ける」ことを目指す。

## 14. 明記されている未定義事項・リスク・制約

- **明示管理された設計判断（unknown / unknown_level）**：`unknown`は未知項目のリスト（質的）、`unknown_level`は未知の度合い0〜1（量的、重要度重み付けで算出）。数値で未知度を表す場合は必ず `unknown_level` を使う。未知を最重要情報として明示管理する点が既存手法との差別化軸。
- **単一正版のルール**：数値は「提案」ではなく「規定」。変更する場合は `00_数値定義書` を改版し、影響を受ける文書に参照を追記する。他の文書が数値を再定義してはならない。
- **MVP・POCで明示的に作らないもの（制約）**：複雑なWeb UI / 完全自律エージェント / 独自LLM / ベクトルDB（Vector Database）/ 高度な強化学習 / 複雑なマルチエージェント制御 / 高度なKnowledge Graph / 完全自動自己改変 / 大規模DB / 分散システム / 複数ユーザー対応。
- **自己改善の制約（Level別の人間承認）**：Memory追加・Pattern追加=許可 / Workflow変更=要確認 / Core Policy変更=人間承認。完全自律変更は禁止（判断基準の暴走・不要な複雑化の防止）。
- **暴走防止の3リスク**：自己目的化（評価数値最大化）/ 無限改善（成果物なしで改善だけ）/ 評価基準の乗っ取り（自分に有利な基準へ変更）。
- **ロードマップ上の4リスク**：複雑化→Layer分離 / AI暴走→Policy+Human Approval / Memory肥大化→Pattern抽出 / Agent乱立→追加基準。
- **避けるべき方向**：Agent乱立（責務不明化）/ UI先行（本質は思考構造）/ 巨大Memory（検索不能）/ 巨大Framework化 / 早すぎるDB化 / Over Thinking（簡単な問題に大量推論）・Under Thinking（重要問題を浅く処理）。
- **開発判断基準（新機能追加前の確認）**：どのLayerに属するか / 既存能力で代替できないか / 将来再利用できるか / 思考能力向上につながるか / Memory価値を増やすか / 判断品質を上げるか。
- **評価のキャリブレーション**：評価者自身の偏りを監査（同一入力の複数回評価・分散記録）。評価スコアを数値だけで判断しない。
- **開発期間目安（制約）**：Phase 0-1 POC=数日〜1週間、Phase 2 MVP=数週間〜1ヶ月、Phase 3 実用版=数ヶ月。
- **POCの反証可能な仮説**：仮説Hが棄却された場合はテーゼそのものを再設計する（仮説を守る設計）。
- **セキュリティ上の未定義/後期項目**：MVPでは実装しない Distributed Security / Agent Sandbox / Zero Trust Architecture / Vector DB / Knowledge Graph / 複雑な検索基盤（semantic search は将来）。

---
- content_type: structured / domain: digital / mode: full
