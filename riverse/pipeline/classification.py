"""Observation classification against existing profile."""

from __future__ import annotations

import json
from datetime import datetime

from riverse.llm.base import LLMClient
from riverse.pipeline.helpers import (
    format_profile_for_llm,
    parse_json_array,
    now_compact,
)
from riverse.prompts import get_prompt, get_label


def classify_observations(
    observations: list[dict],
    current_profile: list[dict],
    llm: LLMClient,
    language: str,
    timeline: list[dict] | None = None,
    trajectory: dict | None = None,
) -> list[dict]:
    """Classify each observation as support/contradict/evidence_against/new/irrelevant."""
    L = get_label
    if not observations:
        return []

    # Build observations text
    obs_text = ""
    for i, o in enumerate(observations):
        subj = o.get("subject", "")
        subj_tag = f" [subject:{subj}]" if subj else ""
        obs_text += f"[{i}] [{o.get('type', '?')}]{subj_tag} {o.get('content', '')}\n"

    profile_text = format_profile_for_llm(current_profile, timeline, language=language)

    traj_context = ""
    if trajectory and trajectory.get("life_phase"):
        traj_context = (
            f"\n{L('trajectory_ref', language)}:\n"
            f"  {L('current_phase', language)}: {trajectory.get('life_phase', '?')}\n"
            f"  {L('anchors_stable', language)}: {json.dumps(trajectory.get('key_anchors', []), ensure_ascii=False)}\n"
            f"  {L('volatile_areas', language)}: {json.dumps(trajectory.get('volatile_areas', []), ensure_ascii=False)}\n"
        )

    now = now_compact()
    user_content = (
        f"[system_time: {now}]\n\n"
        f"{L('current_profile', language)}:\n{profile_text}\n"
        f"{L('new_observations', language)}:\n{obs_text}"
        f"{traj_context}"
    )
    messages = [
        {"role": "system", "content": get_prompt("classify_observations", language)},
        {"role": "user", "content": user_content},
    ]
    raw = llm.chat(messages)
    results = parse_json_array(raw)
    cleaned = []
    for r in results:
        if not isinstance(r, dict):
            continue
        if not r.get("action"):
            r["action"] = "new"
            r.setdefault("reason", "Auto-classified as new")
        cleaned.append(r)
    return cleaned


def create_new_facts(
    new_observations: list[dict],
    existing_profile: list[dict],
    llm: LLMClient,
    language: str,
    trajectory: dict | None = None,
) -> list[dict]:
    """Ask LLM to create profile facts from new observations."""
    L = get_label
    if not new_observations:
        return []

    obs_text = ""
    for o in new_observations:
        subj_str = f" (subject: {o.get('subject', '')})" if o.get("subject") else ""
        obs_text += f"[{o.get('type', '?')}] {o.get('content', '')}{subj_str}\n"

    # Build existing categories block
    existing_cats = set()
    for p in existing_profile:
        existing_cats.add(f"  {p.get('category', '?')}: {p.get('subject', '?')}")
    default_cats = L("default_categories", language)
    if existing_cats:
        cat_block = f"{L('existing_naming', language)}:\n" + "\n".join(sorted(existing_cats)) + f"\n{L('reference', language)}: " + default_cats
    else:
        cat_block = default_cats

    # Build categorization history
    categorization_history = []
    for p in existing_profile:
        ev_raw = p.get("evidence", "[]")
        if isinstance(ev_raw, str):
            try:
                ev = json.loads(ev_raw)
            except (json.JSONDecodeError, ValueError):
                ev = []
        else:
            ev = ev_raw or []
        for e in ev:
            obs_text_ev = e.get("observation", "")
            if obs_text_ev:
                categorization_history.append(
                    f'  "{obs_text_ev}" → [{p.get("category", "?")}] {p.get("subject", "?")} = {p.get("value", "?")}'
                )
                break
    history_block = ""
    if categorization_history:
        history_block = f"{L('categorization_precedents', language)}" + "\n".join(categorization_history)

    year = datetime.utcnow().year
    prompt = get_prompt(
        "create_hypotheses", language,
        existing_categories=cat_block,
        categorization_history=history_block,
        birth_year=str(year),
    )

    now = now_compact()
    user_content = (
        f"[system_time: {now}]\n\n"
        f"{L('new_obs', language)}:\n{obs_text}"
    )
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_content},
    ]
    raw = llm.chat(messages)
    return parse_json_array(raw)
