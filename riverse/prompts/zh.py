"""Chinese prompts and labels for Riverse."""

LABELS = {
    # Format labels
    "no_profile": "（暂无画像）",
    "no_trajectory": "\n人物轨迹总结：（暂无，首次分析）\n",
    "trajectory_header": "\n人物轨迹总结：\n",
    "phase": "  阶段: ",
    "characteristics": "  特征: ",
    "direction": "  方向: ",
    "stability": "  稳定性: ",
    "anchors": "  锚点: ",
    "volatile": "  易变区域: ",
    "momentum": "  近期动向: ",
    "summary": "  总结: ",
    "layer_conflict": "[矛盾中]",
    "layer_confirmed": "[核心]",
    "layer_suspected": "[怀疑]",
    "mention_fmt": "(提及{mc}次, source={src}, 开始={start}, 更新={updated}, 证据{ev}条",
    "challenged_by": ", 被#{sid}挑战",
    "challenges": ", 挑战#{sid}",
    "closed_periods_header": "\n已关闭的时间段（历史）：\n",
    "existing_model_header": "当前已有的用户模型：\n",
    "no_existing_model": "当前已有的用户模型：（暂无，这是首次分析）",
    "profile_overview_header": "\n用户画像（参考，帮助理解用户背景）：\n",
    # Pipeline labels
    "user": "用户",
    "assistant": "助手",
    "intent": "意图",
    "session": "会话",
    "latest": "最新",
    "known_info_header": "已知信息",
    "known_info_none": "暂无已知信息",
    "none": "无",
    "current_profile": "当前画像",
    "new_observations": "新观察",
    "trajectory_ref": "轨迹参考",
    "current_phase": "当前阶段",
    "anchors_stable": "稳定锚点",
    "volatile_areas": "易变区域",
    "existing_naming": "已有命名",
    "reference": "参考分类",
    "default_categories": "居住城市, 职业, 教育背景, 家乡, 兴趣, 感情, 出生年, 身份, 饮食, 宠物, 技能",
    "categorization_precedents": "分类先例：\n",
    "signal_hint": "行为信号提示",
    "maybe_is": "可能是{value}",
    "background_ref": "背景参考",
    "anchors_permanent": "永久锚点",
    "birth_year_note": "注意：用户说今年25岁 → {year}-25={result}年出生",
    "new_obs": "新观察",
    "contradiction": "矛盾",
    "old_value": "老值",
    "new_statement": "新述说",
    "original_text": "原始文本",
    "classify_reason": "分类原因",
    "historical_timeline": "历史时间线",
    "no_related_obs": "无相关观察",
    "no_historical_obs": "无历史观察",
    "related_historical_obs": "相关历史观察",
    "contradiction_details": "矛盾详情",
    "trajectory_ref_label": "轨迹参考",
    "changed_items": "变更项目",
    "user_profile_ref": "用户画像参考",
    "trajectory_ref_strategy": "轨迹参考（策略）",
    "user_comm_style": "用户沟通风格",
    "existing_model": "现有模型",
    "first_analysis": "（首次分析）",
    "user_profile_background": "用户画像背景",
    "current_profile_label": "当前画像",
    "recent_obs": "近期观察",
    "output_json_array": "输出JSON数组：",
    "fact_id": "fact_id",
    "mentions": "提及: ",
    "start": "开始",
    "updated": "更新",
    "evidence": "证据: ",
    "supersedes": "取代 #",
    "layer_equals": "层级=",
    "full_timeline": "完整时间线",
    "rejected": "[已驳回]",
    "closed": "[已关闭]",
    "until_now": "至今",
    "related_summaries": "相关摘要",
    "suspected_to_verify": "待验证的怀疑事实",
    "output_json": "输出JSON数组：",
    "core_profile": "[核心]",
    "suspected_profile": "[怀疑]",
    "trigger_text": "触发原文",
    "old_val": "老值",
    "new_val": "新值",
    "from_date_onwards": "从{date}开始",
    "contradiction_created": "矛盾产生时间",
    "pre_summaries": "矛盾前对话",
    "pre_summaries_none": "此时间段前无对话记录",
    "post_summaries": "矛盾后对话",
    "post_summaries_none": "矛盾后暂无新对话",
    "output_json_object": "输出JSON对象：",
    "dispute_action_hint": "accept_new/reject_new/keep",
    "dispute_reason_hint": "你的判断理由",
    "prev_trajectory": "上一次轨迹",
    "first_generation": "（首次生成）",
    "active_profile": "活跃画像",
    "historical_obs": "历史观察",
    "recent_events": "近期事件",
    "no_new_obs": "无新观察",
    "no_historical": "无历史数据",
    "no_events": "无事件",
    "statement_obs": "陈述观察",
    "current_all_profile": "当前完整画像",
    "sweep_traj_ref": "轨迹参考",
    "sweep_current_phase": "当前阶段",
    "sweep_anchors_stable": "稳定锚点",
    "dirty_value_prefix": "用户",
    "auto_classify_reason": "自动分类为new（LLM遗漏了此观察）",
    "counter_evidence_tag": "[反证]",
    "mention_again_reason": "再次提及",
    "strategy_behavioral_desc": "验证行为模式：{subj}可能是{inferred}",
    "strategy_topic_trigger": "当{subj}话题出现时",
    "strategy_clarify_approach": "自然地询问{inferred}",
    "strategy_expired_desc": "验证{subj}是否仍然有效",
    "strategy_verify_approach": "随意确认{subj}是否仍然相关",
    "layer_core": "[核心]",
    "layer_disputed": "[矛盾中]",
}

PROMPTS = {

"extract_observations_and_tags": """从对话中提取所有值得记录的观察，并为对话打上检索标签。

一、观察提取
观察类型：
- statement: 用户直接陈述的事实（"我叫小明""我搬到大阪了""我辞职了"）
- question: 用户问了什么话题（反映关注点）
- reaction: 用户对某事的反应（赞同/反对/回避）
- behavior: 用户的行为模式（连续问某类问题）
- contradiction: 与已知信息明确矛盾的内容

提取原则（重要！）：
- 对话中包含用户消息和助手回复，助手回复仅作为上下文参考，但只提取用户本人表达的信息
- 用户提问不算 statement，只算 question
- 每条用户消息可能包含多个独立事实 → 每个事实单独提取
- 重大生活变化必须提取：搬家/换城市、换工作/辞职、分手/恋爱、养宠物
- 身份信息必须提取：用户说出自己的名字 → 必须提取为 statement，subject="姓名"
- 与已知信息矛盾时用 contradiction 类型
- 每条 [msg-N] 用户消息必须至少产生一条观察

subject 命名规则：
- subject 必须优先复用已知画像中已有的 category 名称
- 已有 category 列表：{category_list}

about 字段（区分用户本人 vs 第三方）：
- about="user" — 关于用户本人的信息（默认）
- about="他人名字或称呼" — 关于别人的信息

{known_info_block}

二、会话标签
- 每个标签是简短的主题描述，纯闲聊不需要标签，最多 3 个
- 已有标签：{existing_tags}

三、人际关系提取
从对话中提取用户提到的人物关系。
- name: 人物名字（没有名字写 null）
- relation: 与用户的关系
- details: 关于此人的具体信息（键值对）

输出格式：
{{
  "observations": [
    {{"type":"statement", "content":"用户说回到北京了", "subject":"居住地", "about":"user"}}
  ],
  "tags": [{{"tag": "标签名", "summary": "一句话摘要"}}],
  "relationships": [
    {{"name":"老张", "relation":"同学", "details":{{"城市":"北京", "职业":"室内设计"}}}}
  ]
}}
没有内容返回 {{"observations": [], "tags": [], "relationships": []}}""",

"extract_event": """从这段对话中提取值得记录的时间性事件。
格式：[{{"category": "分类标签", "summary": "一句话摘要", "importance": 重要性, "decay_days": 过期天数, "status": "状态"}}]
没有值得记录的事件返回 []

- category: 简短中文标签（如"健康""工作""出行""学习"等）
- importance: 0.0-1.0
- decay_days: 你根据事件的时效性判断
- status（可选）：planning（打算做）、done（已完成）

注意：兴趣、偏好、关系人等信息不要在这里提取。只提取有实际意义的事件。""",

"classify_observations": """你会收到本次新观察和当前画像（双层：怀疑画像 + 核心画像）。
任务：对每条观察逐一分类。

分类类型：
- support: 支持某个已有画像事实 → 给出 fact_id 和 reason
- contradict: 与某个已有画像事实明确矛盾 → 给出 fact_id、new_value 和 reason
- evidence_against: 暗示某画像事实可能不再成立 → 给出 fact_id 和 reason
- new: 全新的用户个人信息 → 给出 reason
- irrelevant: 不包含用户个人信息

判断规则：
- 旅行/出差去某地 ≠ 住在某地
- 别人的信息 → irrelevant
- "好久没XX了" → evidence_against
- "搬到XX""到XX入职" → contradict
- 计划/愿望 → irrelevant
- new_value 必须是简短属性值

重要：每条观察都必须输出分类结果，输出数组长度必须等于输入观察数量。

输出JSON数组：
[
  {{"obs_index": 0, "action": "support", "fact_id": 129, "reason": "再次提到北京生活"}},
  {{"obs_index": 1, "action": "contradict", "fact_id": 129, "new_value": "上海", "reason": "用户说到上海入职"}},
  {{"obs_index": 2, "action": "new", "reason": "用户提到新的兴趣跑步"}},
  {{"obs_index": 3, "action": "irrelevant", "reason": "闲聊内容"}}
]""",

"create_hypotheses": """你会收到一批新观察，为每条创建画像事实。

═══ 标准 category: subject 命名 ═══
{existing_categories}

{categorization_history}

═══ 什么值得创建 ═══
判断标准：下个月用户再来聊天，知道这件事能帮我更好地回应他吗？

创建：
- 身份属性（姓名、年龄、性别、国籍、居住地）
- 持续状态（职业、健康问题、感情状态、正在进行的项目）
- 稳定偏好（饮食习惯、运动方式、购物偏好、沟通风格）
- 重要经历（搬家、换工作、生病、毕业）

不创建：
- 一次性知识提问（"XX是什么""怎么做XX"）→ 问完即忘，不是用户特征
- 对话中的临时指令（"帮我翻译这段""格式化这个JSON"）
- 他人信息、计划/愿望、未确认的观点/立场
- value 以"询问""了解""什么是"开头 → 这描述的是行为，不是属性

═══ 格式规则 ═══
- category 用最宽泛的人物画像一级分类（如：健康、职业、饮食、居住），细分领域写在 subject 里。不要把二级分类写进 category。
  正确：category="健康" subject="用药"　　错误：category="用药方法" subject="中药信息"
- value 写简短属性值，不写句子
- 年龄换算：用户说"今年22" → value="约{birth_year}年出生"
- 兴趣类：一个爱好一条记录
- decay_days：3650=身份/背景, 540=居住地/职业/长期爱好, 365=感情关系, 120-180=中期兴趣, 60=短期状态, 14-30=临时行为

没有需要创建的返回 []""",

"cross_validate": """你会收到矛盾信息。任务：判断这个矛盾是真实变化还是误判。

判断标准：
- 用户直接陈述变化 → 真实变化，confirm_change
- 只是旅行/出差 → 不是变化，reject
- 第三方信息混淆 → 不是变化，reject

new_value 必须是简短属性值。

输出JSON数组：
[{{"obs_index": 0, "action": "confirm_change", "fact_id": 129, "new_value": "上海", "reason": "用户明确说搬到上海"}}]
没有需要处理的返回 []""",

"generate_strategies": """你会收到本轮新建或发生变更的假设。
任务：为需要验证的假设设计自然的验证策略。

策略类型：
- verify: 直接确认
- probe: 投石问路
- clarify: 澄清细节
- deepen: 深入了解

只为推测得来的新假设和发生矛盾的假设生成策略。

输出JSON数组：
[{{"category": "位置", "subject": "居住地", "type": "probe", "description": "确认居住城市", "trigger": "当聊到生活话题时", "approach": "可以问最近生活怎么样"}}]
没有需要策略的返回 []""",

"cross_verify_suspected": """你会收到一批处于怀疑层的画像事实。
任务：判断哪些有足够的交叉证据可以晋升为核心画像。

确认条件：mention_count >= 2，或有佐证观察支持。
保持怀疑：只提及1次，无佐证。

输出：
[{{"fact_id": 123, "action": "confirm", "reason": "用户在两次对话中都提到在北京生活"}}]
没有需要处理的返回 []""",

"resolve_dispute": """你会收到矛盾争议对。任务：判断哪个值是正确的当前状态。

1. accept_new — 接受新值
2. reject_new — 驳回新值
3. keep — 继续等待

输出：
[{{"old_fact_id": 1, "new_fact_id": 2, "action": "accept_new", "reason": "用户明确说搬到深圳"}}]
没有需要处理的返回 []""",

"trajectory_summary": """你是人物分析专家。根据用户的全部画像、历史观察和事件记录，
生成人物轨迹总结。

输出：
{{
  "life_phase": "阶段名",
  "phase_characteristics": "特征（100字内）",
  "trajectory_direction": "方向",
  "stability_assessment": "稳定性评估",
  "key_anchors": ["锚点1", "锚点2"],
  "volatile_areas": ["易变区域1"],
  "recent_momentum": "近期动向",
  "full_summary": "200字以内的完整总结"
}}""",

"analyze_user_model": """根据对话历史，分析用户的沟通特征。

维度：
- communication_style: 直接/委婉/幽默/正式
- knowledge_areas: 用户最擅长/最常讨论的领域
- sensitivity: 敏感话题
- trust_level: 对AI的信任程度
- personality_hints: 性格线索

{existing_model_block}

输出：[{{"dimension": "...", "assessment": "...", "evidence": "..."}}]
没有可分析的返回 []""",

"behavioral_pattern": """你会收到近期观察记录和用户当前画像。
任务：发现跨观察的隐含行为模式。

重点模式：
1. 地理集中：多条观察涉及同一城市 → 可能搬迁
2. 兴趣萌芽：连续多次提到某个新活动 → 可能是新爱好
3. 关系信号：反复提到同一人 → 可能是新感情关系
4. 职业转变：工作内容系统性变化 → 可能换工作

至少3条观察指向同一推论才算模式。

输出：
[{{"pattern_type": "地理集中", "category": "位置", "subject": "居住地", "inferred_value": "深圳", "evidence_count": 3, "evidence_summary": "..."}}]
没有发现模式返回 []""",

"sweep_uncovered": """你会收到观察和当前所有画像。任务：找出未被画像覆盖的观察，为它们创建画像。

value 必须是简短属性值。
只为用户本人的信息创建画像。

decay_days：3650=身份, 540=生活状态, 365=感情, 120-180=中期兴趣, 60=短期, 14-30=临时

输出格式：
{{
  "new_facts": [{{"category":"感情", "subject":"女朋友", "value":"林小晴", "source_type":"stated", "decay_days": 365}}],
  "contradictions": [{{"fact_id": 129, "category": "居住地", "subject": "居住城市", "new_value": "杭州", "reason": "用户明确说搬到杭州了"}}]
}}
没有未覆盖的返回 {{"new_facts": [], "contradictions": []}}""",
}
