"""Contradiction detection and resolution."""

from __future__ import annotations

import json

from riverse.llm.base import LLMClient
from riverse.pipeline.helpers import parse_json_array, parse_json_object, now_compact
from riverse.prompts import get_prompt, get_label
from riverse.storage.base import StorageBackend


def cross_validate_contradictions(
    contradictions: list[dict],
    observations: list[dict],
    current_profile: list[dict],
    llm: LLMClient,
    language: str,
    storage: StorageBackend | None = None,
    user_id: str = "default",
    trajectory: dict | None = None,
) -> list[dict]:
    """Cross-validate contradictions using historical data."""
    L = get_label
    if not contradictions:
        return []

    profile_map = {p.get("id"): p for p in current_profile}

    items_text = ""
    for c in contradictions:
        obs_idx = c.get("obs_index", "?")
        obs = observations[obs_idx] if isinstance(obs_idx, int) and obs_idx < len(observations) else {}
        fid = c.get("fact_id")
        fact = profile_map.get(fid, {})

        fact_start = fact.get("start_time", "?")
        if isinstance(fact_start, str) and len(fact_start) > 10:
            fact_start = fact_start[:10]
        fact_mentions = fact.get("mention_count", 1)

        items_text += (
            f"[{L('contradiction', language)}{obs_idx}] [{fact.get('category', '?')}] {fact.get('subject', '?')}\n"
            f"  {L('old_value', language)}: \"{fact.get('value', '?')}\" (from {fact_start}, {L('mentions', language)}{fact_mentions})\n"
            f"  {L('new_statement', language)}: \"{c.get('new_value', '?')}\"\n"
            f"  {L('original_text', language)}: {obs.get('content', '?')}\n"
            f"  {L('classify_reason', language)}: {c.get('reason', '')}\n\n"
        )

    now = now_compact()
    user_content = (
        f"[system_time: {now}]\n\n"
        f"{L('contradiction_details', language)}:\n{items_text}"
    )
    messages = [
        {"role": "system", "content": get_prompt("cross_validate", language)},
        {"role": "user", "content": user_content},
    ]
    raw = llm.chat(messages)
    return parse_json_array(raw)


def resolve_disputes_with_llm(
    disputed_pairs: list[dict],
    llm: LLMClient,
    language: str,
    trajectory: dict | None = None,
) -> list[dict]:
    """Resolve disputed fact pairs using LLM."""
    L = get_label
    if not disputed_pairs:
        return []

    all_results = []
    now = now_compact()

    for pair in disputed_pairs:
        old = pair["old"]
        new = pair["new"]

        old_layer = old.get("layer", "suspected")
        old_layer_tag = L("core_profile", language) if old_layer == "confirmed" else L("suspected_profile", language)

        # Extract trigger text from new fact's evidence
        trigger_text = ""
        new_evidence_raw = new.get("evidence", "[]")
        if isinstance(new_evidence_raw, str):
            try:
                new_evidence = json.loads(new_evidence_raw)
            except (json.JSONDecodeError, ValueError):
                new_evidence = []
        else:
            new_evidence = new_evidence_raw or []
        for ev in new_evidence:
            if isinstance(ev, dict) and ev.get("observation"):
                trigger_text = ev["observation"]
                break
        trigger_line = f"{L('trigger_text', language)}: \"{trigger_text}\"\n" if trigger_text else ""

        item_text = (
            f"{L('old_val', language)}: \"{old.get('value', '?')}\" ({old_layer_tag}, "
            f"{L('mentions', language)}{old.get('mention_count', 1)})\n"
            f"{L('new_val', language)}: \"{new.get('value', '?')}\" ({L('suspected_profile', language)}, "
            f"{L('mentions', language)}{new.get('mention_count', 1)})\n"
            f"{trigger_line}"
        )

        user_content = (
            f"[system_time: {now}]\n\n"
            f"{L('contradiction', language)}: [{old.get('category', '?')}] {old.get('subject', '?')}\n"
            f"{item_text}\n"
            f"old_fact_id={old.get('id')}, new_fact_id={new.get('id')}\n"
        )
        messages = [
            {"role": "system", "content": get_prompt("resolve_dispute", language)},
            {"role": "user", "content": user_content},
        ]
        raw = llm.chat(messages)

        result = parse_json_object(raw)
        if not result:
            arr = parse_json_array(raw)
            result = arr[0] if arr else None

        if result and isinstance(result, dict):
            if not result.get("old_fact_id"):
                result["old_fact_id"] = old.get("id")
            if not result.get("new_fact_id"):
                result["new_fact_id"] = new.get("id")
            if result.get("action") in ("accept_new", "reject_new", "keep"):
                all_results.append(result)

    return all_results
