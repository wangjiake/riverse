"""Category and subject synonym mappings for fuzzy matching."""

from __future__ import annotations

# Category synonym groups — each set merges zh/en/ja interchangeable names
_CATEGORY_SYNONYM_GROUPS: list[set[str]] = [
    {"位置", "居住地", "居住城市", "地点", "住址", "居住", "所在地",
     "location", "city", "residence", "living_city", "current_city",
     "居住都市", "住所", "居住地域"},
    {"职业", "职位", "工作", "岗位",
     "career", "job", "occupation", "work", "job_title", "profession",
     "職業", "職位", "仕事", "キャリア"},
    {"教育", "教育背景", "学历",
     "education", "school", "university", "college", "academic background",
     "学歴"},
    {"家乡", "籍贯", "出生地", "老家",
     "hometown", "birthplace", "home_city", "origin", "home town",
     "出身地", "故郷", "地元"},
    {"兴趣", "爱好", "休闲活动", "休闲", "运动", "运动与锻炼",
     "hobby", "hobbies", "interest", "interests", "leisure", "sports",
     "趣味", "趣味・興味", "興味", "スポーツ"},
    {"感情", "恋爱", "情感", "婚恋",
     "relationship", "romance", "dating", "love",
     "恋愛", "交際", "恋愛関係"},
    {"出生年份", "年龄", "出生年",
     "birth_year", "age", "born", "birth year",
     "生年", "年齢", "生まれ年", "誕生年"},
    {"专业", "学科", "主修",
     "major", "field_of_study", "subject", "field of study",
     "専攻", "学科", "専門"},
    {"娱乐", "游戏",
     "entertainment", "gaming", "games",
     "娯楽", "ゲーム", "エンタメ"},
    {"宠物", "养宠",
     "pets", "pet",
     "ペット", "飼育"},
    {"技能", "技术", "编程",
     "skills", "tech", "programming", "technology",
     "スキル", "技術", "プログラミング"},
    {"身份", "个人信息",
     "identity", "personal_info", "personal info",
     "身元", "個人情報", "アイデンティティ"},
    {"饮食", "饮食与美食", "美食",
     "food", "cuisine", "diet",
     "食事", "食べ物", "グルメ", "料理"},
    {"家庭", "家人",
     "family",
     "家族", "家庭"},
    {"健康",
     "health",
     "健康状態"},
    {"健身",
     "fitness",
     "フィットネス", "筋トレ"},
    {"旅行", "出行",
     "travel", "traveling",
     "旅行", "旅"},
]

_SUBJECT_SYNONYM_GROUPS: list[set[str]] = [
    {"居住地", "居住城市", "当前居住地", "所在城市",
     "city", "current_city", "residence", "living_city",
     "居住都市", "現在の居住地", "住んでいる場所", "住んでいる都市"},
    {"职业", "当前职位", "工作", "职位", "岗位",
     "job_title", "position", "role", "occupation", "career", "current position", "job", "work",
     "職業", "職位", "役職", "ポジション", "現在の職位", "仕事"},
    {"学校", "大学", "毕业学校",
     "university", "college", "school", "alma mater",
     "大学", "学校", "卒業校"},
    {"专业", "主修", "学科",
     "major", "field_of_study", "subject", "field of study",
     "専攻", "学科", "専門"},
    {"家乡", "老家", "出生地",
     "hometown", "home_city", "birthplace", "home town",
     "出身地", "故郷", "実家"},
    {"运动", "体育", "锻炼",
     "sports", "exercise", "fitness", "workout", "athletics",
     "スポーツ", "運動", "エクササイズ"},
    {"游戏", "电子游戏",
     "games", "gaming", "video games",
     "ゲーム", "ビデオゲーム", "テレビゲーム"},
    {"出生年", "出生年份",
     "birth_year", "year_of_birth", "birth year",
     "生まれ年", "誕生年"},
    {"女朋友", "女友", "对象",
     "girlfriend", "partner", "gf", "significant other",
     "彼女", "恋人", "パートナー"},
    {"男朋友", "男友",
     "boyfriend", "bf",
     "彼氏"},
]

# Build lookup maps
_CAT_SYNONYM_MAP: dict[str, set[str]] = {}
for _group in _CATEGORY_SYNONYM_GROUPS:
    for _name in _group:
        _CAT_SYNONYM_MAP[_name] = _group

_SUBJ_SYNONYM_MAP: dict[str, set[str]] = {}
for _group in _SUBJECT_SYNONYM_GROUPS:
    for _name in _group:
        _SUBJ_SYNONYM_MAP[_name] = _group


def get_category_synonyms(category: str) -> set[str]:
    """Get all synonyms for a category, including the category itself."""
    return _CAT_SYNONYM_MAP.get(category, {category})


def get_subject_synonyms(subject: str) -> set[str]:
    """Get all synonyms for a subject, including the subject itself."""
    return _SUBJ_SYNONYM_MAP.get(subject, {subject})
