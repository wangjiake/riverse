"""Fact promotion from suspected to confirmed layer."""

from __future__ import annotations

import json

from riverse.llm.base import LLMClient
from riverse.pipeline.helpers import parse_json_array, now_compact
from riverse.prompts import get_prompt, get_label


def cross_verify_suspected_facts(
    suspected_facts: list[dict],
    llm: LLMClient,
    language: str,
    trajectory: dict | None = None,
) -> list[dict]:
    """Ask LLM which suspected facts should be promoted to confirmed."""
    L = get_label
    if not suspected_facts:
        return []

    items_text = ""
    for f in suspected_facts:
        ev_raw = f.get("evidence", "[]")
        if isinstance(ev_raw, str):
            try:
                ev = json.loads(ev_raw)
            except (json.JSONDecodeError, ValueError):
                ev = []
        else:
            ev = ev_raw or []
        mention_count = f.get("mention_count", 1) or 1
        start = f.get("start_time", "?")
        if isinstance(start, str) and len(start) > 10:
            start = start[:10]
        updated = f.get("updated_at", "?")
        if isinstance(updated, str) and len(updated) > 10:
            updated = updated[:10]

        items_text += (
            f"{L('fact_id', language)}={f.get('id')}:\n"
            f"  [{f.get('category', '?')}] {f.get('subject', '?')}: {f.get('value', '?')}\n"
            f"  {L('mentions', language)}{mention_count}, source={f.get('source_type', 'stated')}, "
            f"{L('start', language)}={start}, {L('updated', language)}={updated}, {L('evidence', language)}{len(ev)}\n"
        )
        if ev:
            items_text += f"  {L('evidence', language)}: {json.dumps(ev, ensure_ascii=False)}\n"
        items_text += "\n"

    traj_context = ""
    if trajectory and trajectory.get("life_phase"):
        traj_context = (
            f"\n{L('trajectory_ref_label', language)}:\n"
            f"  {L('anchors_stable', language)}: {json.dumps(trajectory.get('key_anchors', []), ensure_ascii=False)}\n"
            f"  {L('volatile_areas', language)}: {json.dumps(trajectory.get('volatile_areas', []), ensure_ascii=False)}\n"
        )

    now = now_compact()
    user_content = (
        f"[system_time: {now}]\n\n"
        f"{L('suspected_to_verify', language)}:\n{items_text}"
        f"{traj_context}\n"
        f"{L('output_json', language)}\n"
    )
    messages = [
        {"role": "system", "content": get_prompt("cross_verify_suspected", language)},
        {"role": "user", "content": user_content},
    ]
    raw = llm.chat(messages)
    results = parse_json_array(raw)
    return [r for r in results if isinstance(r, dict) and r.get("fact_id") and r.get("action")]
