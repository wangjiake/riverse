"""Observation and event extraction from conversations."""

from __future__ import annotations

import json
from datetime import datetime

from riverse.llm.base import LLMClient
from riverse.pipeline.helpers import parse_json_array, parse_json_object, now_compact
from riverse.prompts import get_prompt, get_label
from riverse.storage.base import StorageBackend


def extract_observations_and_tags(
    conversations: list[dict],
    llm: LLMClient,
    language: str,
    existing_profile: list[dict] | None = None,
    existing_tags: list[str] | None = None,
) -> dict:
    """Extract observations, tags, and relationships from conversations.

    Returns: {"observations": [...], "tags": [...], "relationships": [...]}
    """
    L = get_label

    text = ""
    msg_index = 0
    for msg in conversations:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        ts = msg.get("created_at", "")
        prefix = f"[{ts}] " if ts else ""

        if role == "user":
            msg_index += 1
            text += f"{prefix}[msg-{msg_index}] {L('user', language)}: {content}\n"
        elif role == "assistant":
            reply = content
            if len(reply) > 200:
                reply = reply[:200] + "..."
            text += f"{prefix}{L('assistant', language)}: {reply}\n"
        text += "\n"

    if not text.strip():
        return {"observations": [], "tags": [], "relationships": []}

    # Build known info block
    known_lines = []
    if existing_profile:
        for p in existing_profile:
            layer = p.get("layer", "suspected")
            layer_tag = L("layer_confirmed", language) if layer == "confirmed" else L("layer_suspected", language)
            known_lines.append(
                f"  {layer_tag} [{p.get('category', '?')}] {p.get('subject', '?')}: {p.get('value', '?')}"
            )

    if known_lines:
        known_block = f"{L('known_info_header', language)}:\n" + "\n".join(known_lines)
    else:
        known_block = L("known_info_none", language)

    # Category hint
    if existing_profile:
        categories = sorted(set(p.get("category", "") for p in existing_profile if p.get("category")))
        category_hint = ", ".join(categories) if categories else L("none", language)
    else:
        category_hint = L("none", language)

    tag_hint = ", ".join(existing_tags) if existing_tags else L("none", language)

    prompt = get_prompt(
        "extract_observations_and_tags", language,
        known_info_block=known_block,
        existing_tags=tag_hint,
        category_list=category_hint,
    )

    now = now_compact()
    year = datetime.utcnow().year
    date_prefix = f"[system_time: {now}]\n\n"
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": date_prefix + text},
    ]
    raw = llm.chat(messages)
    result = parse_json_object(raw)

    obs = [o for o in result.get("observations", []) if isinstance(o, dict) and o.get("type") and o.get("content")]
    tags = [t for t in result.get("tags", []) if isinstance(t, dict) and t.get("tag")]
    rels = [r for r in result.get("relationships", []) if isinstance(r, dict) and r.get("relation")]

    return {"observations": obs, "tags": tags, "relationships": rels}


def extract_events(
    conversations: list[dict],
    llm: LLMClient,
    language: str,
) -> list[dict]:
    """Extract time-based events from conversations."""
    L = get_label
    dialogue = ""
    for msg in conversations:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            dialogue += f"{L('user', language)}: {content}\n"
        elif role == "assistant":
            dialogue += f"{L('assistant', language)}: {content}\n\n"

    if not dialogue.strip():
        return []

    now = now_compact()
    messages = [
        {"role": "system", "content": get_prompt("extract_event", language)},
        {"role": "user", "content": f"[system_time: {now}]\n\n{dialogue}"},
    ]
    raw = llm.chat(messages)
    events = parse_json_array(raw)
    return [e for e in events if isinstance(e, dict) and e.get("category") and e.get("summary")]
