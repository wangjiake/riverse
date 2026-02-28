"""Category and subject synonym mappings for fuzzy matching."""

from __future__ import annotations

# Category synonym groups — each set contains interchangeable names
_CATEGORY_SYNONYM_GROUPS: list[set[str]] = [
    # Chinese
    {"位置", "居住地", "居住城市", "地点", "住址", "居住", "所在地"},
    {"职业", "职位", "工作", "岗位"},
    {"教育", "教育背景", "学历"},
    {"家乡", "籍贯", "出生地", "老家"},
    {"兴趣", "爱好", "休闲活动", "休闲", "运动", "运动与锻炼"},
    {"感情", "恋爱", "情感", "婚恋"},
    {"出生年份", "年龄", "出生年"},
    {"专业", "学科", "主修"},
    {"娱乐", "游戏"},
    {"宠物", "养宠"},
    {"技能", "技术", "编程"},
    {"身份", "个人信息"},
    {"饮食", "饮食与美食", "美食"},
    # English
    {"location", "city", "residence", "living_city", "current_city"},
    {"career", "job", "occupation", "work", "job_title"},
    {"education", "school", "university", "college"},
    {"hometown", "birthplace", "home_city", "origin"},
    {"hobby", "hobbies", "interest", "interests", "leisure"},
    {"relationship", "romance", "dating", "love"},
    {"birth_year", "age", "born"},
    {"major", "field_of_study", "subject"},
    {"entertainment", "gaming", "games"},
    {"pets", "pet"},
    {"skills", "tech", "programming"},
    {"identity", "personal_info"},
    {"food", "cuisine", "diet"},
    # Japanese
    {"居住都市", "住所", "居住地域"},
    {"職業", "職位", "仕事"},
    {"学歴", "教育背景"},
    {"出身地", "故郷"},
    {"趣味", "趣味・興味"},
    {"恋愛", "交際"},
    {"生年", "年齢"},
    {"専攻", "学科"},
    {"ペット"},
    {"スキル", "技術"},
]

_SUBJECT_SYNONYM_GROUPS: list[set[str]] = [
    # Chinese
    {"居住地", "居住城市", "当前居住地", "所在城市"},
    {"职业", "当前职位", "工作", "职位", "岗位"},
    {"学校", "大学", "毕业学校"},
    {"专业", "主修", "学科"},
    {"家乡", "老家", "出生地"},
    {"运动", "体育", "锻炼"},
    {"游戏", "电子游戏"},
    {"出生年", "出生年份"},
    {"女朋友", "女友", "对象"},
    {"男朋友", "男友"},
    # English
    {"city", "current_city", "residence", "living_city"},
    {"job_title", "position", "role", "occupation"},
    {"university", "college", "school"},
    {"major", "field_of_study"},
    {"hometown", "home_city", "birthplace"},
    {"sports", "exercise", "fitness"},
    {"games", "gaming"},
    {"birth_year", "year_of_birth"},
    {"girlfriend", "partner", "gf"},
    {"boyfriend", "partner", "bf"},
    # Japanese
    {"居住都市", "現在の居住地", "住んでいる場所"},
    {"職位", "役職", "ポジション"},
    {"大学", "学校", "卒業校"},
    {"専攻", "学科"},
    {"出身地", "故郷"},
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
