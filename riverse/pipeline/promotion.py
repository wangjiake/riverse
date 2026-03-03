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

    # Rule preprocessing: stated + mention_count>=2 → auto-confirm
    rule_results = []
    llm_candidates = []
    for f in suspected_facts:
        mc = f.get("mention_count") or 1
        if f.get("source_type") == "stated" and mc >= 2:
            rule_results.append({"fact_id": f.get("id"), "action": "confirm",
                                 "reason": "rule: stated+mention>=2"})
        else:
            llm_candidates.append(f)

    if not llm_candidates:
        return rule_results

    # Sort by mention_count desc, limit to 80 for LLM
    llm_candidates.sort(key=lambda f: -(f.get("mention_count") or 1))
    llm_candidates = llm_candidates[:80]

    items_text = ""
    for f in llm_candidates:
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
    llm_results = parse_json_array(raw)
    llm_results = [r for r in llm_results if isinstance(r, dict) and r.get("fact_id") and r.get("action")]
    return rule_results + llm_results
