"""User model analysis and trajectory synthesis."""

from __future__ import annotations

import json

from riverse.llm.base import LLMClient
from riverse.pipeline.helpers import parse_json_array, parse_json_object, now_compact
from riverse.prompts import get_prompt, get_label
from riverse.storage.base import StorageBackend


def analyze_user_model(
    conversations: list[dict],
    llm: LLMClient,
    language: str,
    current_profile: list[dict] | None = None,
    existing_model: list[dict] | None = None,
) -> list[dict]:
    """Analyze user communication model from conversation history."""
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

    if existing_model:
        model_lines = [f"  {m.get('dimension', '?')}: {m.get('assessment', '?')}" for m in existing_model]
        existing_block = f"{L('existing_model_header', language)}\n" + "\n".join(model_lines)
    else:
        existing_block = L("no_existing_model", language)

    profile_block = ""
    if current_profile:
        profile_lines = []
        for p in current_profile:
            layer_tag = L("layer_confirmed", language) if p.get("layer") == "confirmed" else L("layer_suspected", language)
            profile_lines.append(f"  {layer_tag} [{p.get('category', '?')}] {p.get('subject', '?')}: {p.get('value', '?')}")
        profile_block = f"\n{L('profile_overview_header', language)}\n" + "\n".join(profile_lines) + "\n"

    prompt = get_prompt("analyze_user_model", language, existing_model_block=existing_block)

    now = now_compact()
    user_content = f"[system_time: {now}]\n\n{dialogue}{profile_block}"
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_content},
    ]
    raw = llm.chat(messages)
    results = parse_json_array(raw)
    return [r for r in results if isinstance(r, dict) and r.get("dimension") and r.get("assessment")]


def generate_trajectory_summary(
    current_profile: list[dict],
    llm: LLMClient,
    language: str,
    storage: StorageBackend,
    user_id: str,
    new_observations: list[dict] | None = None,
) -> dict:
    """Generate a trajectory summary from profile, observations, and events."""
    L = get_label

    # Build profile text
    profile_text = ""
    if current_profile:
        for p in current_profile:
            layer_tag = L("layer_confirmed", language) if p.get("layer") == "confirmed" else L("layer_suspected", language)
            profile_text += f"  {layer_tag} [{p.get('category', '?')}] {p.get('subject', '?')}: {p.get('value', '?')}\n"
    else:
        profile_text = f"{L('no_profile', language)}\n"

    # New observations
    new_obs_text = ""
    if new_observations:
        for o in new_observations:
            obs_type = o.get("type") or o.get("observation_type", "?")
            content = o.get("content", "")
            new_obs_text += f"  [{obs_type}] {content}\n"
    else:
        new_obs_text = f"{L('no_new_obs', language)}\n"

    # Historical observations
    historical_obs = storage.load_observations(user_id, limit=80)
    hist_obs_text = ""
    if historical_obs:
        for o in historical_obs:
            time_str = o.get("created_at", "?")
            if isinstance(time_str, str) and len(time_str) > 10:
                time_str = time_str[:10]
            hist_obs_text += f"  [{time_str}] [{o.get('observation_type', '?')}] {o.get('content', '')}\n"
    else:
        hist_obs_text = f"{L('no_historical', language)}\n"

    # Events
    events = storage.load_events(user_id, top_k=10)
    event_text = ""
    if events:
        for e in events:
            event_text += f"  [{e.get('category', '?')}] {e.get('summary', '')}\n"
    else:
        event_text = f"{L('no_events', language)}\n"

    # Previous trajectory
    prev_trajectory = storage.load_trajectory(user_id)
    prev_text = ""
    if prev_trajectory and prev_trajectory.get("life_phase"):
        prev_text = (
            f"{L('prev_trajectory', language)}:\n"
            f"  {L('phase', language)}{prev_trajectory.get('life_phase', '')}\n"
            f"  {L('characteristics', language)}{prev_trajectory.get('phase_characteristics', '')}\n"
            f"  {L('direction', language)}{prev_trajectory.get('trajectory_direction', '')}\n"
            f"  {L('stability', language)}{prev_trajectory.get('stability_assessment', '')}\n"
            f"  {L('momentum', language)}{prev_trajectory.get('recent_momentum', '')}\n"
            f"  {L('summary', language)}{prev_trajectory.get('full_summary', '')}\n"
        )
    else:
        prev_text = f"{L('prev_trajectory', language)}: {L('first_generation', language)}\n"

    now = now_compact()
    user_content = (
        f"[system_time: {now}]\n\n"
        f"{L('active_profile', language)}:\n{profile_text}\n"
        f"{L('new_observations', language)}:\n{new_obs_text}\n"
        f"{L('historical_obs', language)}:\n{hist_obs_text}\n"
        f"{L('recent_events', language)}:\n{event_text}\n"
        f"{prev_text}"
    )
    messages = [
        {"role": "system", "content": get_prompt("trajectory_summary", language)},
        {"role": "user", "content": user_content},
    ]
    raw = llm.chat(messages)
    return parse_json_object(raw)


def generate_strategies(
    changed_items: list[dict],
    llm: LLMClient,
    language: str,
    current_profile: list[dict] | None = None,
    trajectory: dict | None = None,
) -> list[dict]:
    """Generate verification strategies for changed profile items."""
    L = get_label
    if not changed_items:
        return []

    items_text = ""
    for item in changed_items:
        items_text += (
            f"[{item.get('change_type', '?')}] [{item.get('category', '?')}] "
            f"{item.get('subject', '?')}: {item.get('claim', '?')}"
        )
        if item.get("source_type"):
            items_text += f" (source={item['source_type']})"
        items_text += "\n"

    now = now_compact()
    user_content = f"[system_time: {now}]\n\n{L('changed_items', language)}:\n{items_text}"
    messages = [
        {"role": "system", "content": get_prompt("generate_strategies", language)},
        {"role": "user", "content": user_content},
    ]
    raw = llm.chat(messages)
    return parse_json_array(raw)
