"""Japanese prompts and labels for Riverse."""

LABELS = {
    "no_profile": "（プロフィールなし）",
    "no_trajectory": "\n人物軌跡要約：（なし、初回分析）\n",
    "trajectory_header": "\n人物軌跡要約：\n",
    "phase": "  段階: ",
    "characteristics": "  特徴: ",
    "direction": "  方向: ",
    "stability": "  安定性: ",
    "anchors": "  アンカー: ",
    "volatile": "  変動領域: ",
    "momentum": "  最近の動向: ",
    "summary": "  要約: ",
    "layer_conflict": "[矛盾中]",
    "layer_confirmed": "[確定]",
    "layer_suspected": "[疑い]",
    "mention_fmt": "(言及{mc}回, source={src}, 開始={start}, 更新={updated}, 証拠{ev}件",
    "challenged_by": ", #{sid}に挑戦されている",
    "challenges": ", #{sid}に挑戦中",
    "closed_periods_header": "\n終了した期間（履歴）：\n",
    "existing_model_header": "現在のユーザーモデル：\n",
    "no_existing_model": "現在のユーザーモデル：（なし、初回分析です）",
    "profile_overview_header": "\nユーザープロフィール（参考）：\n",
    "user": "ユーザー",
    "assistant": "アシスタント",
    "intent": "意図",
    "session": "セッション",
    "latest": "最新",
    "known_info_header": "既知情報",
    "known_info_none": "既知情報なし",
    "none": "なし",
    "current_profile": "現在のプロフィール",
    "new_observations": "新しい観察",
    "trajectory_ref": "軌跡参考",
    "current_phase": "現在の段階",
    "anchors_stable": "安定アンカー",
    "volatile_areas": "変動領域",
    "existing_naming": "既存の命名",
    "reference": "参考カテゴリ",
    "default_categories": "居住都市, 職業, 学歴, 出身地, 趣味, 恋愛, 生年, 身元, 食事, ペット, スキル",
    "categorization_precedents": "分類の前例：\n",
    "signal_hint": "行動シグナルのヒント",
    "maybe_is": "おそらく{value}",
    "background_ref": "背景参考",
    "anchors_permanent": "永久アンカー",
    "birth_year_note": "注意：ユーザーが25歳と言った場合 → {year}-25={result}年生まれ",
    "new_obs": "新しい観察",
    "contradiction": "矛盾",
    "old_value": "旧値",
    "new_statement": "新しい主張",
    "original_text": "元のテキスト",
    "classify_reason": "分類理由",
    "historical_timeline": "履歴タイムライン",
    "no_related_obs": "関連する観察なし",
    "no_historical_obs": "過去の観察なし",
    "related_historical_obs": "関連する過去の観察",
    "contradiction_details": "矛盾の詳細",
    "trajectory_ref_label": "軌跡参考",
    "changed_items": "変更項目",
    "user_profile_ref": "ユーザープロフィール参考",
    "trajectory_ref_strategy": "軌跡参考（戦略）",
    "user_comm_style": "ユーザーコミュニケーションスタイル",
    "existing_model": "既存モデル",
    "first_analysis": "（初回分析）",
    "user_profile_background": "ユーザープロフィール背景",
    "current_profile_label": "現在のプロフィール",
    "recent_obs": "最近の観察",
    "output_json_array": "出力JSON配列：",
    "fact_id": "fact_id",
    "mentions": "言及: ",
    "start": "開始",
    "updated": "更新",
    "evidence": "証拠: ",
    "supersedes": "置き換え #",
    "layer_equals": "レイヤー=",
    "full_timeline": "完全なタイムライン",
    "rejected": "[却下]",
    "closed": "[終了]",
    "until_now": "現在まで",
    "related_summaries": "関連要約",
    "suspected_to_verify": "検証待ちの疑い事実",
    "output_json": "出力JSON配列：",
    "core_profile": "[確定]",
    "suspected_profile": "[疑い]",
    "trigger_text": "トリガーテキスト",
    "old_val": "旧値",
    "new_val": "新値",
    "from_date_onwards": "{date}から",
    "contradiction_created": "矛盾発生日",
    "pre_summaries": "矛盾前の会話",
    "pre_summaries_none": "この期間前の会話なし",
    "post_summaries": "矛盾後の会話",
    "post_summaries_none": "矛盾後の会話なし",
    "output_json_object": "出力JSONオブジェクト：",
    "dispute_action_hint": "accept_new/reject_new/keep",
    "dispute_reason_hint": "判断理由",
    "prev_trajectory": "前回の軌跡",
    "first_generation": "（初回生成）",
    "active_profile": "アクティブプロフィール",
    "historical_obs": "過去の観察",
    "recent_events": "最近のイベント",
    "no_new_obs": "新しい観察なし",
    "no_historical": "過去のデータなし",
    "no_events": "イベントなし",
    "statement_obs": "陳述観察",
    "current_all_profile": "現在の全プロフィール",
    "sweep_traj_ref": "軌跡参考",
    "sweep_current_phase": "現在の段階",
    "sweep_anchors_stable": "安定アンカー",
    "dirty_value_prefix": "ユーザー",
    "auto_classify_reason": "自動分類（LLMが見逃した観察）",
    "counter_evidence_tag": "[反証]",
    "mention_again_reason": "再度言及",
    "strategy_behavioral_desc": "行動パターンを検証：{subj}は{inferred}かもしれない",
    "strategy_topic_trigger": "{subj}の話題が出た時",
    "strategy_clarify_approach": "自然に{inferred}について聞く",
    "strategy_expired_desc": "{subj}がまだ有効か検証",
    "strategy_verify_approach": "{subj}がまだ関連するか確認",
    "layer_core": "[確定]",
    "layer_disputed": "[矛盾中]",
}

PROMPTS = {

"extract_observations_and_tags": """会話からすべての記録すべき観察を抽出し、検索タグを付けてください。

一、観察抽出
観察タイプ：
- statement: ユーザーが直接述べた事実
- question: ユーザーが質問したトピック
- reaction: 何かに対するユーザーの反応
- behavior: ユーザーの行動パターン
- contradiction: 既知情報と明確に矛盾する内容

抽出原則：
- ユーザー本人が表現した情報のみ抽出
- 各ユーザーメッセージには複数の事実が含まれる場合がある → 個別に抽出
- 重大なライフイベントは必ず抽出
- すべての [msg-N] は少なくとも1つの観察を生成

subject 命名規則：
- 既存 category 名を優先的に再利用
- 既存 category リスト：{category_list}

about フィールド：
- about="user" — ユーザー本人（デフォルト）
- about="人物名" — 他人の情報

{known_info_block}

二、セッションタグ（最大3個）
- 既存タグ：{existing_tags}

三、人間関係抽出

出力形式：
{{
  "observations": [{{"type":"statement", "content":"...", "subject":"...", "about":"user"}}],
  "tags": [{{"tag": "...", "summary": "..."}}],
  "relationships": [{{"name":"...", "relation":"...", "details":{{}}}}]
}}
抽出するものがなければ {{"observations": [], "tags": [], "relationships": []}} を返す""",

"extract_event": """この会話から記録すべき時間性イベントを抽出してください。
形式：[{{"category": "カテゴリ", "summary": "一行要約", "importance": 重要度, "decay_days": 有効日数, "status": "状態"}}]
記録すべきイベントがなければ [] を返す""",

"classify_observations": """新しい観察と現在のプロフィールを受け取ります。各観察を分類してください。

分類タイプ：
- support: 既存事実を支持 → fact_id と reason
- contradict: 既存事実と矛盾 → fact_id、new_value、reason
- evidence_against: 事実がもう成立しない可能性 → fact_id と reason
- new: 完全に新しい情報 → reason
- irrelevant: 個人情報を含まない

意味的マッチング（重要！字面だけでなく、行動が暗示する属性を理解すること）：
- 「メガネを拭いている」→ 既存の視力/メガネ関連 fact を support
- 「上野で食事した」「秋葉原に行った」→ 既存の「居住都市: 東京」を support
- 「カロリーを計算」→ 既存のダイエット/食事管理 fact を support
- 「日本語の語彙を議論」→ 既存の日本語学習 fact を support
- 行動が暗示する属性が既存 fact と意味的に関連する場合、new ではなく support を優先

すべての観察に分類結果を出力、スキップ不可。

出力JSON配列：
[
  {{"obs_index": 0, "action": "support", "fact_id": 129, "reason": "再び東京在住に言及"}},
  {{"obs_index": 1, "action": "new", "reason": "新しい趣味"}}
]""",

"create_hypotheses": """新しい観察のバッチを受け取ります。各観察にプロフィール事実を作成。

═══ 命名規則 ═══
{existing_categories}
{categorization_history}

═══ 作成すべきもの ═══
判断基準：来月ユーザーが戻ってきた時、この情報を知っていればより良い対応ができるか？

作成する：
- 身元属性（名前、年齢、性別、国籍、居住地）
- 継続的な状態（職業、健康問題、恋愛状況、進行中のプロジェクト）
- 安定した嗜好（食習慣、運動方法、買い物の好み、コミュニケーションスタイル）
- 重要な経験（引っ越し、転職、病気、卒業）

作成しない：
- 一回限りの知識質問（「XXとは」「XXのやり方」）→ 聞いて終わり、ユーザー特徴ではない
- 会話中の一時的な指示（「これを翻訳して」「このJSONを整形して」）
- 他人の情報、計画/願望、未確認の意見
- valueが「質問」「調べ」「とは何か」で始まる → 行動の記述であり、属性ではない
- 毎日の数値変動（今日の体重XX、今日の体脂率XX）→ 毎回新しい fact を作成しない、classify 段階で既存記録を support

═══ 行動→属性の推論（重要！）═══
観察が行動を記述している場合、行動そのものではなく、その行動が暗示する持続的な属性を抽出する：
- 「ユーザーがメガネを洗った」→ category="身体特徴" subject="視力" value="メガネ着用"
- 「ユーザーがコンビニで日本語で話した」→ category="言語" subject="日本語レベル" value="日常会話可能"
- 「ユーザーがジムの器具について話した」→ category="フィットネス" subject="運動方法" value="ジムで筋トレ"
- 「ユーザーがカロリーを計算した」→ 作成しない（classify で既存のダイエット fact を support）

═══ フォーマットルール ═══
- category は最も広い一次分類を使う（例：健康、職業、食事、居住）。細分はsubjectに書く。二次分類をcategoryに入れない。
  正しい：category="健康" subject="服薬"　誤り：category="服薬方法" subject="漢方情報"
- value は簡潔な属性値。decay_days：3650=アイデンティティ, 540=居住地/職業, 365=恋愛, 120-180=中期趣味

作成するものがなければ [] を返す""",

"cross_validate": """矛盾情報を受け取ります。本当の変化か誤判断かを判断。

- ユーザーが直接変化を述べた → confirm_change
- 旅行/出張 → reject

出力JSON配列：
[{{"obs_index": 0, "action": "confirm_change", "fact_id": 129, "new_value": "大阪", "reason": "..."}}]
処理するものがなければ [] を返す""",

"generate_strategies": """変更された仮説に対して検証戦略を設計。
出力：[{{"category": "...", "subject": "...", "type": "probe", "description": "...", "trigger": "...", "approach": "..."}}]
戦略不要なら [] を返す""",

"cross_verify_suspected": """疑い事実のバッチを受け取ります。確定に昇格させるか判断。
出力：[{{"fact_id": 123, "action": "confirm", "reason": "..."}}]
処理するものがなければ [] を返す""",

"resolve_dispute": """矛盾争議ペアを受け取ります。
1. accept_new 2. reject_new 3. keep
出力：[{{"old_fact_id": 1, "new_fact_id": 2, "action": "accept_new", "reason": "..."}}]
処理するものがなければ [] を返す""",

"trajectory_summary": """人物分析の専門家として、軌跡要約を生成してください。
出力：
{{
  "life_phase": "段階名",
  "phase_characteristics": "特徴",
  "trajectory_direction": "方向",
  "stability_assessment": "安定性評価",
  "key_anchors": ["アンカー1"],
  "volatile_areas": ["変動領域1"],
  "recent_momentum": "最近の動向",
  "full_summary": "200字以内の要約"
}}""",

"analyze_user_model": """会話履歴に基づき、ユーザーのコミュニケーション特性を分析。

{existing_model_block}

出力：[{{"dimension": "...", "assessment": "...", "evidence": "..."}}]
分析するものがなければ [] を返す""",

"behavioral_pattern": """最近の観察から行動パターンを発見。
少なくとも3つの観察が同じ推論を指す場合のみパターン。
出力：[{{"pattern_type": "...", "category": "...", "subject": "...", "inferred_value": "...", "evidence_count": 3, "evidence_summary": "..."}}]
パターンがなければ [] を返す""",

"sweep_uncovered": """観察と全プロフィールを受け取り、未カバーの観察を見つけて新規作成。
出力：
{{
  "new_facts": [{{"category":"...", "subject":"...", "value":"...", "source_type":"stated", "decay_days": 365}}],
  "contradictions": [{{"fact_id": 129, "new_value": "...", "reason": "..."}}]
}}
未カバーがなければ {{"new_facts": [], "contradictions": []}} を返す""",
}
