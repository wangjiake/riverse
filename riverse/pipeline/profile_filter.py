"""Profile filtering and truncation for optimized LLM token usage."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta

from riverse.prompts import get_label


def prepare_profile(
    profile: list[dict],
    query_text: str | None = None,
    max_entries: int = 30,
    language: str = "en",
) -> tuple[list[dict], str]:
    """Filter → score → truncate profile entries.

    1. Filter: remove superseded entries
    2. Score: confirmed +3, recent 30 days +2, mention_count >= 3 +1
    3. Truncate to max_entries
    4. Summarize the rest by category counts

    Returns: (top_entries, rest_summary)
    """
    active = [p for p in profile if not p.get("superseded_by")]
    if not active:
        return [], ""

    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)

    def _score(p: dict) -> int:
        score = 0
        if p.get("layer") == "confirmed":
            score += 3
        updated = p.get("updated_at")
        if updated:
            if isinstance(updated, str):
                try:
                    updated_dt = datetime.strptime(updated[:19], "%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError):
                    updated_dt = None
            else:
                updated_dt = updated
            if updated_dt and updated_dt >= thirty_days_ago:
                score += 2
        mc = p.get("mention_count") or 0
        if mc >= 3:
            score += 1
        return score

    active.sort(key=_score, reverse=True)
    top = active[:max_entries]
    rest = active[max_entries:]

    rest_summary = ""
    if rest:
        cat_counts = Counter(p.get("category", "?") for p in rest)
        parts = [f"{cat}×{cnt}" for cat, cnt in cat_counts.most_common()]
        rest_summary = f"(+{len(rest)} more: " + ", ".join(parts) + ")"

    return top, rest_summary


def format_profile_text(
    profile: list[dict],
    max_entries: int = 30,
    detail: str = "full",
    language: str = "en",
) -> str:
    """Prepare profile + format as text.

    detail="full": includes layer tag, category, subject, value
    detail="light": category + subject + value only
    """
    L = get_label
    top, rest_summary = prepare_profile(profile, max_entries=max_entries, language=language)

    if not top:
        return ""

    lines = []
    for p in top:
        if detail == "full":
            layer = p.get("layer", "suspected")
            if layer == "confirmed":
                layer_tag = L("layer_confirmed", language)
            else:
                layer_tag = L("layer_suspected", language)
            lines.append(
                f"  {layer_tag} [{p.get('category', '?')}] {p.get('subject', '?')}: {p.get('value', '?')}"
            )
        else:
            lines.append(
                f"  [{p.get('category', '?')}] {p.get('subject', '?')}: {p.get('value', '?')}"
            )

    text = "\n".join(lines)
    if rest_summary:
        text += f"\n  {rest_summary}"
    return text
