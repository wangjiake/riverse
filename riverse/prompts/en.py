"""English prompts and labels for Riverse."""

LABELS = {
    # Format labels
    "no_profile": "(No profile yet)",
    "no_trajectory": "\nTrajectory summary: (None yet, first analysis)\n",
    "trajectory_header": "\nTrajectory summary:\n",
    "phase": "  Phase: ",
    "characteristics": "  Characteristics: ",
    "direction": "  Direction: ",
    "stability": "  Stability: ",
    "anchors": "  Anchors: ",
    "volatile": "  Volatile areas: ",
    "momentum": "  Recent momentum: ",
    "summary": "  Summary: ",
    "layer_conflict": "[Disputed]",
    "layer_confirmed": "[Confirmed]",
    "layer_suspected": "[Suspected]",
    "mention_fmt": "(mentioned {mc}x, source={src}, start={start}, updated={updated}, {ev} evidence",
    "challenged_by": ", challenged by #{sid}",
    "challenges": ", challenges #{sid}",
    "closed_periods_header": "\nClosed time periods (history):\n",
    "existing_model_header": "Current user model:\n",
    "no_existing_model": "Current user model: (None yet, this is the first analysis)",
    "profile_overview_header": "\nUser profile (reference, to help understand user background):\n",
    # Pipeline labels
    "user": "User",
    "assistant": "Assistant",
    "intent": "intent",
    "session": "session",
    "latest": "latest",
    "known_info_header": "Already known information",
    "known_info_none": "No known information yet",
    "none": "none",
    "current_profile": "Current profile",
    "new_observations": "New observations",
    "trajectory_ref": "Trajectory reference",
    "current_phase": "Current phase",
    "anchors_stable": "Stable anchors",
    "volatile_areas": "Volatile areas",
    "existing_naming": "Existing naming conventions",
    "reference": "Reference categories",
    "default_categories": "city, career, education, hometown, hobby, relationship, birth_year, identity, food, pets, skills",
    "categorization_precedents": "Categorization precedents:\n",
    "signal_hint": "Behavioral signal hints",
    "maybe_is": "possibly {value}",
    "background_ref": "Background reference",
    "anchors_permanent": "Permanent anchors",
    "birth_year_note": "Note: if user says they're 25, they were born around {year}-25={result}",
    "new_obs": "New observations",
    "contradiction": "Contradiction",
    "old_value": "Old value",
    "new_statement": "New statement",
    "original_text": "Original text",
    "classify_reason": "Classification reason",
    "historical_timeline": "Historical timeline",
    "no_related_obs": "No related observations",
    "no_historical_obs": "No historical observations",
    "related_historical_obs": "Related historical observations",
    "contradiction_details": "Contradiction details",
    "trajectory_ref_label": "Trajectory reference",
    "changed_items": "Changed items",
    "user_profile_ref": "User profile reference",
    "trajectory_ref_strategy": "Trajectory reference (for strategy)",
    "user_comm_style": "User communication style",
    "existing_model": "Existing model",
    "first_analysis": "(First analysis)",
    "user_profile_background": "User profile background",
    "current_profile_label": "Current profile",
    "recent_obs": "Recent observations",
    "output_json_array": "Output JSON array:",
    "fact_id": "fact_id",
    "mentions": "mentions: ",
    "start": "start",
    "updated": "updated",
    "evidence": "evidence: ",
    "supersedes": "supersedes #",
    "layer_equals": "layer=",
    "full_timeline": "full timeline",
    "rejected": "[rejected]",
    "closed": "[closed]",
    "until_now": "now",
    "related_summaries": "related summaries",
    "suspected_to_verify": "Suspected facts to verify",
    "output_json": "Output JSON array:",
    "core_profile": "[Confirmed]",
    "suspected_profile": "[Suspected]",
    "trigger_text": "Trigger text",
    "old_val": "Old value",
    "new_val": "New value",
    "from_date_onwards": "from {date} onwards",
    "contradiction_created": "Contradiction created",
    "pre_summaries": "Conversations before contradiction",
    "pre_summaries_none": "No conversations before this period",
    "post_summaries": "Conversations after contradiction",
    "post_summaries_none": "No conversations after contradiction yet",
    "output_json_object": "Output JSON object:",
    "dispute_action_hint": "accept_new/reject_new/keep",
    "dispute_reason_hint": "your reasoning",
    "prev_trajectory": "Previous trajectory",
    "first_generation": "(First generation)",
    "active_profile": "Active profile",
    "historical_obs": "Historical observations",
    "recent_events": "Recent events",
    "no_new_obs": "No new observations",
    "no_historical": "No historical data",
    "no_events": "No events",
    "statement_obs": "Statement observations",
    "current_all_profile": "Current full profile",
    "sweep_traj_ref": "Trajectory reference",
    "sweep_current_phase": "Current phase",
    "sweep_anchors_stable": "Stable anchors",
    "dirty_value_prefix": "User",
    "auto_classify_reason": "Auto-classified as new (LLM missed this observation)",
    "counter_evidence_tag": "[counter-evidence]",
    "mention_again_reason": "Mentioned again",
    "strategy_behavioral_desc": "Verify behavioral pattern: {subj} might be {inferred}",
    "strategy_topic_trigger": "When {subj} topic comes up",
    "strategy_clarify_approach": "Ask naturally about {inferred}",
    "strategy_expired_desc": "Verify if {subj} is still current",
    "strategy_verify_approach": "Casually check if {subj} is still relevant",
    "layer_core": "[Confirmed]",
    "layer_disputed": "[Disputed]",
}

PROMPTS = {

# ── Extract observations and tags ──
"extract_observations_and_tags": """Extract all noteworthy observations from the conversation, and generate retrieval tags.

I. Observation Extraction
Observation types:
- statement: Facts directly stated by the user ("I'm Jake" "I moved to Austin" "I quit my job")
- question: Topics the user asked about (reflects interests)
- reaction: User's reaction to something (agreement/disagreement/avoidance)
- behavior: User's behavioral patterns (repeatedly asking about certain topics)
- contradiction: Content that clearly contradicts known information (compare with known info below)

Extraction principles (important!):
- The conversation includes user messages and assistant replies. Assistant replies are only for context — only extract information expressed by the user themselves
- User questions are NOT statements, classify them as question
- Each user message may contain multiple independent facts → extract each as a separate observation
  Example: "Moved back to NYC and rejoined the publisher" → 2 observations (location + job)
- Major life changes MUST be extracted: moving cities, changing jobs/quitting, breakup/new relationship, getting a pet
- Identity info MUST be extracted: user states their name → MUST extract as statement, subject="name"
- Use contradiction type when it contradicts known info; when uncertain, use statement
- Every [msg-N] user message must produce at least one observation, do not skip any

subject naming rules:
- subject must reuse existing category names from the known profile
- Only create new subject names for genuinely new dimensions
- Existing category list: {category_list}

about field (most important! distinguish user vs third party):
- about="user" — information about the user themselves (default)
- about="person's name or title" — information about someone else
- Key: where others work/live/study ≠ where the user works/lives/studies

{known_info_block}

II. Session Tags
- Each tag is a brief topic description (e.g. "React form components" "moving plans")
- Pure small talk doesn't need tags, max 3 tags
- Existing tags: {existing_tags}
- If continuing an existing topic, reuse the existing tag name

III. Relationship Extraction
Extract people mentioned by the user. Only extract explicitly mentioned people, don't speculate.
- name: Person's name (write null if no name)
- relation: Relationship to user (classmate, roommate, colleague, girlfriend, boyfriend, parents, friend, etc.)
- details: Specific info about this person (key-value pairs)

Output format:
{{
  "observations": [
    {{"type":"statement", "content":"User moved back to NYC", "subject":"city", "about":"user"}},
    {{"type":"statement", "content":"Buddy Mike works at Google", "subject":"third_party_info", "about":"Mike"}}
  ],
  "tags": [{{"tag": "tag_name", "summary": "one-line summary"}}],
  "relationships": [
    {{"name":"Mike", "relation":"college friend", "details":{{"city":"Oakland", "company":"Google"}}}}
  ]
}}
Return {{"observations": [], "tags": [], "relationships": []}} if nothing to extract""",

# ── Extract events ──
"extract_event": """Extract noteworthy time-based events from this conversation.
Format: [{{"category": "category_label", "summary": "one-line summary", "importance": importance, "decay_days": expiry_days, "status": "status"}}]
Return [] if no events worth recording

- category: You decide the category name (short English label, e.g. "health" "work" "travel" "study")
- importance: 0.0-1.0, judge based on impact on user's life
- decay_days: Judge based on how long the information remains relevant
- status (optional): planning (intending to do) or done (completed)

Note: Interests, preferences, and relationships should NOT be extracted here (handled by the profile system).
Only extract events with real significance. Casual chat and knowledge Q&A don't need extraction.""",

# ── Classify observations ──
"classify_observations": """You will receive new observations and the current profile (two layers: suspected + confirmed).
Task: Classify each observation one by one.

Classification types:
- support: Supports an existing profile fact (consistent or supplementary) → provide fact_id and reason
- contradict: Clearly contradicts an existing profile fact (different value) → provide fact_id, new_value, and reason
- evidence_against: Suggests a profile fact may no longer hold (e.g. "haven't done X in ages") → provide fact_id and reason
- new: Entirely new personal information with no matching profile → provide reason
- irrelevant: Contains no personal user information (small talk/knowledge Q&A/others' info)

Judgment rules:
- Traveling/business trip to a place ≠ living there, not a contradiction of residence
- Nostalgia/memories ≠ current state ("Haven't watched shows in forever" is evidence_against, not support)
- Others' info (friend/colleague's job/city) → irrelevant, do not attribute to user's profile
- "Haven't done X in ages" "Stopped doing X" → evidence_against (corresponding hobby profile)
- User says "moved to X" "started work at X" "back in X" → contradict (residence/job profile)
- Plans/wishes ("want to go" "planning to learn") → irrelevant, don't create profile
- new_value must be a brief attribute value (city name/job title), not a sentence

Hometown vs current city (important! These are two different categories):
- category="hometown" is a permanent anchor, moving cities NEVER contradicts hometown
- category="city" → if profile has category="city" then contradict; if not then new
- "job_title" only stores the role name, not city names

Note time order: Observations are sorted by session time, newer = more representative of current state.
Every observation must have a classification result (including irrelevant), do not skip any.
Output array length must equal input observation count.

Output JSON array:
[
  {{"obs_index": 0, "action": "support", "fact_id": 129, "reason": "Mentioned living in NYC again"}},
  {{"obs_index": 1, "action": "contradict", "fact_id": 129, "new_value": "Austin", "reason": "User said they moved to Austin"}},
  {{"obs_index": 2, "action": "new", "reason": "User mentioned new hobby: rock climbing"}},
  {{"obs_index": 3, "action": "evidence_against", "fact_id": 135, "reason": "User said haven't played guitar in months"}},
  {{"obs_index": 4, "action": "irrelevant", "reason": "Small talk, no personal info"}}
]""",

# ── Create new hypotheses ──
"create_hypotheses": """You will receive a batch of new observations. Create a profile fact for each one.

═══ Standard category: subject naming ═══
{existing_categories}

{categorization_history}

═══ Rules ═══
- value should be a brief attribute value (city name/job title/school name), not a sentence
- Do not create facts for others' info or plans/wishes
- Age conversion: user says "I'm 22" → value="born around {birth_year}"
- Hobbies: one record per hobby
- decay_days: 3650=identity/background (name, gender, birth year, hometown, school, major), 540=residence/career/long-term hobbies/pets, 365=relationships, 120-180=medium-term interests, 60=short-term states, 14-30=temporary behaviors

═══ Examples ═══
Observation: "Went to UC Berkeley for computer science, 28 years old, from Portland"
Output:
[{{"category":"education", "subject":"university", "value":"UC Berkeley", "source_type":"stated", "decay_days": 3650}},
 {{"category":"education", "subject":"major", "value":"computer science", "source_type":"stated", "decay_days": 3650}},
 {{"category":"birth_year", "subject":"birth_year", "value":"born around {birth_year}", "source_type":"inferred", "decay_days": 3650}},
 {{"category":"hometown", "subject":"hometown", "value":"Portland", "source_type":"stated", "decay_days": 3650}}]

Return [] if nothing to create""",

# ── Cross-validate contradictions ──
"cross_validate": """You will receive contradiction information containing:
1. Old value and its time range (when it started, when contradicted, how many times mentioned)
2. New claim and its start time
3. Timeline history for this subject (if any)
4. Related historical observations for this subject (with timestamps)

Task: Based on the complete timeline, judge whether this contradiction is a real change or a false alarm.

Judgment criteria:
- User directly states a change ("I moved to X" "started work at X" "quit") → real change, confirm_change
- Multiple timeline evidence supports new value → real change
- Old value lasted long with many mentions, new value appeared once with no corroboration → be cautious
- Just traveling/business trip mentioning a place → not a change, reject
- Nostalgia/memories → not a change, reject
- Third-party info confusion → not a change, reject

new_value must be a brief attribute value (city name/job title), not a sentence.

Output JSON array:
[{{"obs_index": 0, "action": "confirm_change", "fact_id": 129, "new_value": "Austin", "reason": "User explicitly said moved to Austin"}}]
For false contradictions:
[{{"obs_index": 1, "action": "reject", "fact_id": 129, "reason": "Just a business trip to Denver"}}]
Return [] if nothing to process""",

# ── Generate strategies ──
"generate_strategies": """You will receive newly created or changed hypotheses this round.
Task: Design natural verification strategies for hypotheses that need validation.

Strategy types:
- verify: Direct confirmation — only when user brings up the topic
- probe: Indirect exploration — subtle probing
- clarify: Clarify details
- deepen: Learn more

Strategy principle: Must feel completely natural, user should not feel interrogated.

Only generate strategies for:
- Inferred new hypotheses (need secondary confirmation)
- Contradicted hypotheses (need to verify the change)
No strategy needed for: Facts directly stated by user (source_type=stated)

Output JSON array:
[{{"category": "location", "subject": "city", "type": "probe", "description": "Confirm current city", "trigger": "When chatting about lifestyle or city topics", "approach": "Ask how life has been lately"}}]
Return [] if no strategies needed""",

# ── Cross-verify suspected facts ──
"cross_verify_suspected": """You will receive a batch of suspected profile facts, each with evidence.
Task: Judge which suspected facts have enough cross-evidence to be promoted to confirmed.

═══ Judgment criteria ═══
1. confirm — Enough cross-evidence, can be confirmed
2. keep — Not enough evidence yet, keep as suspected

Confirmation conditions (confirm):
- User mentioned the same fact in multiple sessions (mention_count >= 2)
- Corroborating observations support it
- User directly stated it clearly with no contradiction (source_type=stated and mention_count >= 2)

Keep as suspected (keep):
- Only mentioned once, no corroboration
- From inference (inferred), not yet confirmed by user

Important:
- Suspected facts are trusted by default, just unverified
- The bar is not high: 2 mentions or 1 clear statement + 1 corroboration is enough
- Do not reject — suspected facts can only be closed by contradictions, not rejected

Output:
[{{"fact_id": 123, "action": "confirm", "reason": "User mentioned living in Austin in two conversations"}}]
Return [] if nothing to process""",

# ── Resolve disputes ──
"resolve_dispute": """You will receive a contradiction dispute pair containing:
- Old value: Existing value in the profile
- New value: Newly observed contradicting value
- Trigger text: The original observation that produced the new value
- Conversation context

Task: Judge which value is the correct current state.

═══ Judgment criteria ═══
1. accept_new — Accept new value, close old value
2. reject_new — Reject new value, keep old value
3. keep — Not enough evidence to judge, keep waiting

Accept new (accept_new):
- User directly stated the change
- Post-contradiction context shows user's life center has shifted

Reject new (reject_new):
- Trigger text was about others' info, mislabeled as user's
- New value from travel/trip mention, not residence change

Output:
[{{"old_fact_id": 1, "new_fact_id": 2, "action": "accept_new", "reason": "User explicitly said moved to Austin"}}]
Return [] if nothing to process""",

# ── Trajectory summary ──
"trajectory_summary": """You are a character analysis expert. Based on the user's full profile, historical observations, and event records,
generate a trajectory summary describing what life phase this person is in, what they're experiencing, and where they're heading.

Output:
{{
  "life_phase": "Phase name (e.g. 'career exploration' 'startup phase' 'settling down')",
  "phase_characteristics": "Characteristics of this phase (under 100 words)",
  "trajectory_direction": "Where this person is currently heading",
  "stability_assessment": "Overall stability assessment (hobbies, residence, work, relationship)",
  "key_anchors": ["anchor1", "anchor2"],
  "volatile_areas": ["volatile_area1", "volatile_area2"],
  "recent_momentum": "Recent developments and momentum",
  "full_summary": "Complete trajectory summary under 200 words"
}}

Important:
- Write based on facts and observations, don't fabricate
- Focus on change trends, not just listing attributes
- key_anchors are things unlikely to change (hometown, school, core identity)
- volatile_areas are things currently changing or about to change
- If there's a previous trajectory summary, update it, don't rewrite from scratch""",

# ── Analyze user model ──
"analyze_user_model": """Based on conversation history, analyze the user's communication characteristics.

Dimensions (not limited to these):
- communication_style: direct/indirect/humorous/formal
- knowledge_areas: Topics the user discusses most frequently
- sensitivity: Which topics are sensitive
- trust_level: Level of trust in AI
- personality_hints: Personality clues

Important:
- knowledge_areas should reflect the user's most frequently discussed areas
- Only output dimensions with clear evidence

{existing_model_block}

Output: [{{"dimension": "...", "assessment": "...", "evidence": "..."}}]
Return [] if nothing to analyze""",

# ── Behavioral pattern analysis ──
"behavioral_pattern": """You will receive recent observation records and the user's current profile.
Task: Discover implicit behavioral patterns across observations.

Focus on these patterns:
1. Geographic concentration: Multiple observations involving the same city → possible relocation
2. Interest emergence: Repeatedly mentioning a new activity → possible new hobby
3. Relationship signals: Repeatedly mentioning the same person + positive emotions → possible new relationship
4. Career shift: Systematic changes in work content → possible job change

Rules:
- Only output patterns that contradict or fill gaps in current profile
- At least 3 observations pointing to the same inference counts as a pattern
- evidence_count = number of observations supporting the inference

Output:
[{{"pattern_type": "geographic_concentration", "category": "location", "subject": "city", "inferred_value": "Austin", "evidence_count": 3, "evidence_summary": "Last 3 sessions mentioned Austin BBQ, East Austin, and Austin Bouldering Project"}}]
Return [] if no patterns found""",

# ── Sweep uncovered observations ──
"sweep_uncovered": """You will receive:
1. A batch of statement/contradiction observations
2. All current profile facts (with ID, category, subject, value, layer)

value must be a brief attribute value, not a descriptive sentence.

Task: Find which observations are not covered by any profile fact, and create profiles for them.

"Already covered" criteria:
- Existing profile's subject semantically matches the observation → covered
- But if existing profile value contradicts observation → needs update, output as contradiction

Distinguish user vs third party:
- Only create profiles for user's own information

decay_days (required):
- 3650: Core identity and background
- 540: Life status and long-term hobbies/pets
- 365: Relationships
- 120-180: Medium-term hobbies
- 60: Short-term states
- 14-30: Temporary behaviors

Output format:
{{
  "new_facts": [{{"category":"relationship", "subject":"girlfriend", "value":"Sophie", "source_type":"stated", "decay_days": 365}}],
  "contradictions": [{{"fact_id": 129, "category": "location", "subject": "city", "new_value": "Austin", "reason": "User explicitly said moved to Austin"}}]
}}
Return {{"new_facts": [], "contradictions": []}} if nothing uncovered""",
}
