"""JSON parsing and formatting helpers for the pipeline."""

from __future__ import annotations

import json
import re
from datetime import datetime

from riverse.prompts import get_label


def parse_json_array(raw: str) -> list[dict]:
    """Parse a JSON array from LLM output, handling markdown fences and messy output."""
    text = raw.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    start = text.find("[")
    end = text.rfind("]") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end])
        except (json.JSONDecodeError, ValueError):
            pass
    # Fallback: try to find any JSON arrays
    merged = []
    for m in re.finditer(r'\[.*?\]', text, re.DOTALL):
        try:
            arr = json.loads(m.group())
            if isinstance(arr, list):
                merged.extend(arr)
        except (json.JSONDecodeError, ValueError):
            continue
    return merged


def parse_json_object(raw: str) -> dict:
    """Parse a JSON object from LLM output."""
    text = raw.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        text = text[start:end]
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return {}


def format_profile_for_llm(profile: list[dict], timeline: list[dict] | None = None,
                           language: str = "en") -> str:
    """Format profile facts into a text block for LLM consumption."""
    L = get_label
    if not profile:
        return L("no_profile", language) + "\n"

    text = ""
    for p in profile:
        ev_raw = p.get("evidence", "[]")
        if isinstance(ev_raw, str):
            try:
                ev = json.loads(ev_raw)
            except (json.JSONDecodeError, ValueError):
                ev = []
        else:
            ev = ev_raw or []
        layer = p.get("layer", "suspected")
        mention_count = p.get("mention_count", 1) or 1
        start = p.get("start_time", "?")
        if isinstance(start, str) and len(start) > 10:
            start = start[:10]
        updated = p.get("updated_at", "?")
        if isinstance(updated, str) and len(updated) > 10:
            updated = updated[:10]
        fact_id = p.get("id", "?")

        if p.get("superseded_by"):
            layer_tag = L("layer_conflict", language)
        elif layer == "confirmed":
            layer_tag = L("layer_confirmed", language)
        else:
            layer_tag = L("layer_suspected", language)

        line = (
            f"#{fact_id} {layer_tag} [{p.get('category', '?')}] {p.get('subject', '?')}: {p.get('value', '?')} "
            f"({L('mentions', language)}{mention_count}, source={p.get('source_type', 'stated')}, "
            f"{L('start', language)}={start}, {L('updated', language)}={updated}, {L('evidence', language)}{len(ev)}"
        )
        if p.get("superseded_by"):
            line += f", {L('challenged_by', language).replace('{sid}', str(p['superseded_by']))}"
        if p.get("supersedes"):
            line += f", {L('challenges', language).replace('{sid}', str(p['supersedes']))}"
        line += ")\n"
        text += line

    if timeline:
        closed = [t for t in timeline if t.get("end_time") or t.get("rejected")]
        if closed:
            text += f"\n{L('closed_periods_header', language)}\n"
            for t in closed:
                start_t = t.get("start_time", "?")
                if isinstance(start_t, str) and len(start_t) > 10:
                    start_t = start_t[:10]
                if t.get("rejected"):
                    text += f"  [{t.get('category', '?')}] {t.get('subject', '?')}: {t.get('value', '?')} ({start_t}, rejected)\n"
                else:
                    end_t = t.get("end_time", "?")
                    if isinstance(end_t, str) and len(end_t) > 10:
                        end_t = end_t[:10]
                    text += f"  [{t.get('category', '?')}] {t.get('subject', '?')}: {t.get('value', '?')} ({start_t} ~ {end_t})\n"
    return text


def format_trajectory_block(trajectory: dict | None, language: str = "en") -> str:
    """Format trajectory into a text block for LLM consumption."""
    L = get_label
    if not trajectory or not trajectory.get("life_phase"):
        return L("no_trajectory", language)
    return (
        L("trajectory_header", language)
        + f"{L('phase', language)}{trajectory.get('life_phase', '?')}\n"
        + f"{L('characteristics', language)}{trajectory.get('phase_characteristics', '?')}\n"
        + f"{L('direction', language)}{trajectory.get('trajectory_direction', '?')}\n"
        + f"{L('stability', language)}{trajectory.get('stability_assessment', '?')}\n"
        + f"{L('anchors', language)}{json.dumps(trajectory.get('key_anchors', []), ensure_ascii=False)}\n"
        + f"{L('volatile', language)}{json.dumps(trajectory.get('volatile_areas', []), ensure_ascii=False)}\n"
        + f"{L('momentum', language)}{trajectory.get('recent_momentum', '?')}\n"
        + f"{L('summary', language)}{trajectory.get('full_summary', '?')}\n"
    )


def now_str() -> str:
    """Return current UTC time as string."""
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def now_compact() -> str:
    """Return current UTC time in compact format for prompts."""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M")
