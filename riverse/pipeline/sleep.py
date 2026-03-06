"""Sleep consolidation pipeline — the core of River Algorithm.

This orchestrates the full 14-step memory consolidation process:
1. Load unprocessed conversations
2. Extract observations, tags, relationships
3. Extract events
4. Classify observations against existing profile
5. Create new facts from new observations
6. Handle contradictions (cross-validate)
7. Generate verification strategies
8. Cross-verify suspected facts → promote to confirmed
9. Resolve disputed fact pairs
10. Handle expired facts
11. Update maturity decay
12. Analyze user communication model
13. Generate/update trajectory summary
14. Mark conversations as processed
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

from riverse.config import RiverseConfig
from riverse.llm.base import LLMClient
from riverse.pipeline.classification import classify_observations, create_new_facts
from riverse.pipeline.contradiction import cross_validate_contradictions, resolve_disputes_with_llm
from riverse.pipeline.extraction import extract_observations_and_tags, extract_events
from riverse.pipeline.helpers import now_str
from riverse.pipeline.maturity import calculate_maturity_decay
from riverse.pipeline.profile_filter import prepare_profile, format_profile_text
from riverse.pipeline.promotion import cross_verify_suspected_facts
from riverse.pipeline.synthesis import (
    analyze_user_model,
    generate_strategies,
    generate_trajectory_summary,
)
from riverse.prompts import get_label
from riverse.storage.base import StorageBackend


def run_sleep(
    user_id: str,
    storage: StorageBackend,
    llm: LLMClient,
    config: RiverseConfig,
) -> dict:
    """Run the full sleep consolidation pipeline.

    Returns a summary dict with counts of actions taken.
    """
    language = config.language
    L = get_label

    # ── Step 1: Load unprocessed conversations ──
    session_convs = storage.get_unprocessed_conversations(user_id)
    if not session_convs:
        return {"status": "no_conversations", "processed": 0}

    all_msg_ids: list[int] = []
    all_convs: list[dict] = []
    all_observations: list[dict] = []

    existing_profile = storage.load_profile(user_id)
    trajectory = storage.load_trajectory(user_id)
    if trajectory and not trajectory.get("life_phase"):
        trajectory = None

    existing_tags = storage.load_existing_tags(user_id)

    # ── Step 2-3: Process each session ──
    total_session_count = len(session_convs)
    for session_idx, (session_id, convs) in enumerate(session_convs.items(), 1):
        msg_ids = [c["id"] for c in convs]
        all_msg_ids.extend(msg_ids)
        all_convs.extend(convs)

        # Step 2: Extract observations and tags (truncated profile → top 25)
        extract_profile, _ = prepare_profile(existing_profile, max_entries=25, language=language)
        result = extract_observations_and_tags(
            convs, llm, language,
            existing_profile=extract_profile,
            existing_tags=existing_tags,
        )
        observations_raw = result.get("observations", [])
        tags = result.get("tags", [])
        relationships = result.get("relationships", [])

        # Separate user observations from third-party
        observations = []
        for o in observations_raw:
            about = o.get("about", "user")
            if about in ("user", "", None, "null"):
                observations.append(o)

        # Save observations
        for o in observations:
            storage.save_observation(
                user_id=user_id,
                session_id=session_id,
                obs_type=o.get("type", "statement"),
                content=o.get("content", ""),
                subject=o.get("subject"),
            )

        all_observations.extend(observations)

        # Save relationships
        for r in relationships:
            name = r.get("name")
            relation = r.get("relation", "")
            details = r.get("details", {})
            if relation:
                storage.save_relationship(user_id, name, relation, details)

        # Save tags
        for t in tags:
            storage.save_session_tag(user_id, session_id, t["tag"], t.get("summary", ""))

        # Step 3: Extract events
        events = extract_events(convs, llm, language)
        for e in events:
            storage.save_event(
                user_id=user_id,
                category=e["category"],
                summary=e["summary"],
                session_id=session_id,
                importance=e.get("importance", 0.5),
                decay_days=e.get("decay_days"),
            )

    # ── Step 4-7: Classify and process observations ──
    current_profile = storage.load_profile(user_id)
    timeline = storage.load_timeline(user_id)

    new_fact_count = 0
    contradict_count = 0
    strategy_count = 0
    changed_items: list[dict] = []
    affected_fact_ids: set = set()  # 增量 cross_verify / resolve_disputes 用
    now = now_str()

    def _find_fact(fid) -> dict | None:
        if not fid:
            return None
        for p in current_profile:
            if p.get("id") == fid:
                return p
        return None

    if all_observations:
        # Step 4: Classify — dynamic profile range
        obs_subjects = set(o.get("subject", "") for o in all_observations if o.get("subject"))
        has_contradictions = any(o.get("type") == "contradiction" for o in all_observations)

        if has_contradictions:
            classify_profile = current_profile
        elif len(obs_subjects) <= 3:
            obs_categories = set(o.get("category", "") or "" for o in all_observations)
            try:
                three_months_ago = datetime.strptime(now, "%Y-%m-%d %H:%M:%S") - timedelta(days=90)
                three_months_str = three_months_ago.strftime("%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                three_months_str = ""
            classify_profile = [
                p for p in current_profile
                if p.get("subject") in obs_subjects
                or p.get("category") in obs_categories
                or (p.get("updated_at") and str(p["updated_at"]) >= three_months_str)
            ] or current_profile
        else:
            classify_profile, _ = prepare_profile(
                current_profile, max_entries=80, language=language
            )

        classifications = classify_observations(
            all_observations, classify_profile, llm, language,
            timeline=timeline, trajectory=trajectory,
        )

        # Fill missing classifications
        classified_indices = {c.get("obs_index") for c in classifications if c.get("obs_index") is not None}
        for idx in range(len(all_observations)):
            if idx not in classified_indices:
                obs = all_observations[idx]
                if obs.get("type") in ("statement", "contradiction"):
                    classifications.append({"obs_index": idx, "action": "new",
                                            "reason": L("auto_classify_reason", language)})

        supports = [c for c in classifications if c.get("action") == "support"]
        contradictions = [c for c in classifications if c.get("action") == "contradict"]
        evidence_against_list = [c for c in classifications if c.get("action") == "evidence_against"]
        new_obs_cls = [c for c in classifications if c.get("action") == "new"]

        # 收集本轮受影响的 fact_id（供增量 cross_verify / resolve_disputes）
        for s in supports:
            fid = s.get("fact_id")
            if fid:
                affected_fact_ids.add(fid)
        for c in contradictions:
            fid = c.get("fact_id")
            if fid:
                affected_fact_ids.add(fid)
        for ea in evidence_against_list:
            fid = ea.get("fact_id")
            if fid:
                affected_fact_ids.add(fid)

        # Process supports
        for s in supports:
            fact = _find_fact(s.get("fact_id"))
            if fact:
                storage.add_evidence(fact["id"], {"reason": s.get("reason", "")}, reference_time=now)

        # Process evidence_against
        for ea in evidence_against_list:
            fact = _find_fact(ea.get("fact_id"))
            if fact:
                storage.add_evidence(
                    fact["id"],
                    {"reason": f"{L('counter_evidence_tag', language)} {ea.get('reason', '')}"},
                    reference_time=now,
                )

        # Step 5: Create new facts
        if new_obs_cls:
            new_obs_data = []
            for c in new_obs_cls:
                idx = c.get("obs_index")
                if isinstance(idx, int) and 0 <= idx < len(all_observations):
                    new_obs_data.append(all_observations[idx])

            if new_obs_data:
                create_profile, _ = prepare_profile(current_profile, max_entries=15, language=language)
                new_facts = create_new_facts(
                    new_obs_data, create_profile, llm, language,
                    trajectory=trajectory,
                )
                for nf in new_facts:
                    value = nf.get("value") or nf.get("claim")
                    subject = nf.get("subject") or nf.get("name")
                    if subject:
                        nf["subject"] = subject
                    if not nf.get("category") or not subject or not value:
                        continue
                    if value.startswith(L("dirty_value_prefix", language)) or len(value) > 80:
                        continue
                    # Match source observation for evidence
                    src_obs = ""
                    for _o in new_obs_data:
                        _cnt = _o.get("content") or ""
                        if _cnt and (value in _cnt or _cnt in value):
                            src_obs = _cnt
                            break
                    evidence = [{"observation": src_obs}] if src_obs else None
                    fact_id = storage.save_profile_fact(
                        user_id=user_id,
                        category=nf["category"],
                        subject=nf["subject"],
                        value=value,
                        source_type=nf.get("source_type", "stated"),
                        decay_days=nf.get("decay_days"),
                        evidence=evidence,
                        start_time=now,
                    )
                    new_fact_count += 1
                    if fact_id:
                        affected_fact_ids.add(fact_id)
                    changed_items.append({
                        "change_type": "new",
                        "category": nf["category"],
                        "subject": nf["subject"],
                        "claim": value,
                        "source_type": nf.get("source_type", "stated"),
                    })

        # Step 6: Handle contradictions
        if contradictions:
            for c in contradictions:
                fid = c.get("fact_id")
                fact = _find_fact(fid)
                new_val = c.get("new_value")
                if not fact or not new_val:
                    continue
                if new_val.strip().lower() == (fact.get("value") or "").strip().lower():
                    storage.add_evidence(fact["id"], {"reason": L("mention_again_reason", language)},
                                         reference_time=now)
                    continue
                if new_val.startswith(L("dirty_value_prefix", language)) or len(new_val) > 40:
                    continue
                obs_idx = c.get("obs_index")
                obs = all_observations[obs_idx] if isinstance(obs_idx, int) and 0 <= obs_idx < len(all_observations) else {}
                evidence_entry = {"reason": c.get("reason", "")}
                if obs.get("content"):
                    evidence_entry["observation"] = obs["content"]
                new_id = storage.save_profile_fact(
                    user_id=user_id,
                    category=fact.get("category", ""),
                    subject=fact.get("subject", ""),
                    value=new_val,
                    source_type="stated",
                    decay_days=fact.get("decay_days"),
                    evidence=[evidence_entry],
                    start_time=now,
                )
                contradict_count += 1
                if new_id:
                    affected_fact_ids.add(new_id)
                changed_items.append({
                    "change_type": "contradict",
                    "category": fact.get("category", ""),
                    "subject": fact.get("subject", ""),
                    "claim": f"{fact.get('value', '?')}→{new_val}",
                })

        # Step 7: Generate strategies (truncated profile → top 15)
        if changed_items:
            strategy_profile, _ = prepare_profile(current_profile, max_entries=15, language=language)
            strategies = generate_strategies(
                changed_items, llm, language,
                current_profile=strategy_profile,
                trajectory=trajectory,
            )
            for s in strategies:
                cat = s.get("category")
                subj = s.get("subject")
                if not cat or not subj:
                    continue
                try:
                    storage.save_strategy(
                        user_id=user_id,
                        category=cat,
                        subject=subj,
                        strategy_type=s.get("type", "probe"),
                        description=s.get("description", ""),
                        trigger_condition=s.get("trigger", ""),
                        approach=s.get("approach", ""),
                        reference_time=now,
                    )
                    strategy_count += 1
                except Exception:
                    logger.error("Save strategy failed", exc_info=True)

    # ── Step 8: Cross-verify suspected facts ──
    suspected_facts = storage.load_suspected(user_id)
    confirmed_count = 0
    if suspected_facts:
        judgments = cross_verify_suspected_facts(suspected_facts, llm, language, trajectory=trajectory)
        judgment_map = {j["fact_id"]: j for j in judgments}
        for f in suspected_facts:
            j = judgment_map.get(f.get("id"))
            if not j:
                continue
            if j["action"] == "confirm":
                storage.confirm_fact(f["id"], reference_time=now)
                confirmed_count += 1
                affected_fact_ids.add(f["id"])

    # ── Step 9: Resolve disputes ──
    disputed_pairs = storage.load_disputed(user_id)
    dispute_resolved = 0
    if disputed_pairs:
        judgments = resolve_disputes_with_llm(disputed_pairs, llm, language, trajectory=trajectory)
        for j in judgments:
            old_fid = j["old_fact_id"]
            new_fid = j["new_fact_id"]
            action = j["action"]
            if action == "accept_new":
                storage.resolve_dispute(old_fid, new_fid, accept_new=True, resolution_time=now)
                storage.delete_fact_edges_for(old_fid)
                affected_fact_ids.add(new_fid)
                dispute_resolved += 1
            elif action == "reject_new":
                storage.resolve_dispute(old_fid, new_fid, accept_new=False, resolution_time=now)
                storage.delete_fact_edges_for(new_fid)
                affected_fact_ids.add(old_fid)
                dispute_resolved += 1

    # ── Step 10: Handle expired facts ──
    expired_facts = storage.get_expired(user_id, reference_time=now)
    stale_count = 0
    for f in expired_facts:
        if f.get("superseded_by") or f.get("supersedes"):
            continue
        storage.close_fact(f["id"], end_time=now)
        storage.delete_fact_edges_for(f["id"])
        stale_count += 1

    # ── Step 11: Maturity decay ──
    all_living = storage.load_profile(user_id)
    key_anchors = []
    if trajectory and trajectory.get("key_anchors"):
        key_anchors = [str(a).lower() for a in trajectory["key_anchors"]]

    maturity_count = 0
    for f in all_living:
        start = f.get("start_time")
        updated = f.get("updated_at")
        if not start or not updated:
            continue
        try:
            start_dt = datetime.strptime(start, "%Y-%m-%d %H:%M:%S") if isinstance(start, str) else start
            updated_dt = datetime.strptime(updated, "%Y-%m-%d %H:%M:%S") if isinstance(updated, str) else updated
            span_days = (updated_dt - start_dt).days
        except (ValueError, TypeError):
            continue
        ev_raw = f.get("evidence", "[]")
        if isinstance(ev_raw, str):
            try:
                ev = json.loads(ev_raw)
            except (json.JSONDecodeError, ValueError):
                ev = []
        else:
            ev = ev_raw or []
        evidence_count = len(ev)
        current_decay = f.get("decay_days") or 90

        subj_lower = (f.get("subject") or "").lower()
        value_lower = (f.get("value") or "").lower()
        in_anchors = any(
            subj_lower in a or value_lower in a or a in subj_lower or a in value_lower
            for a in key_anchors
        )

        new_decay = calculate_maturity_decay(span_days, evidence_count, current_decay, in_anchors)
        if new_decay > current_decay:
            storage.update_decay(f["id"], new_decay, reference_time=now)
            maturity_count += 1

    # ── Step 12: Analyze user model (truncated profile → top 20, convs → last 50) ──
    model_count = 0
    if all_convs:
        model_convs = all_convs[-50:] if len(all_convs) > 50 else all_convs
        current_profile_for_model, _ = prepare_profile(
            storage.load_profile(user_id), max_entries=20, language=language
        )
        existing_model = storage.load_user_model(user_id)
        model_results = analyze_user_model(
            model_convs, llm, language,
            current_profile=current_profile_for_model,
            existing_model=existing_model,
        )
        for m in model_results:
            storage.upsert_user_model(
                user_id=user_id,
                dimension=m["dimension"],
                assessment=m["assessment"],
                evidence=m.get("evidence", ""),
            )
            model_count += 1

    # ── Step 13: Trajectory update (significant change + ≥2 sessions, or fallback ≥10) ──
    trajectory_updated = False
    total_sessions = storage.get_session_count(user_id) + len(session_convs)
    prev_session_count = trajectory.get("session_count", 0) if trajectory else 0
    sessions_since_update = total_sessions - prev_session_count

    if not trajectory:
        current_p = storage.load_profile(user_id)
        should_update = bool(current_p)
    else:
        _significant_categories = {
            "career", "family", "education", "health", "location",
            "职业", "家庭", "教育", "健康", "居住", "住所",
        }
        has_significant_change = (
            confirmed_count > 0
            or dispute_resolved > 0
            or contradict_count > 0
            or any(
                (item.get("category", "").lower() in _significant_categories)
                for item in changed_items
            )
        )
        should_update = (
            (has_significant_change and sessions_since_update >= 2)
            or sessions_since_update >= 10
        )

    if should_update:
        current_p = storage.load_profile(user_id)
        if current_p:
            trajectory_result = generate_trajectory_summary(
                current_p, llm, language,
                storage=storage,
                user_id=user_id,
                new_observations=all_observations,
            )
            if trajectory_result and trajectory_result.get("life_phase"):
                storage.save_trajectory(user_id, trajectory_result, session_count=total_sessions)
                trajectory_updated = True

    # ── Profile dedup: merge same (category, subject) entries ──
    if new_fact_count > 0 or dispute_resolved > 0:
        _consolidate_profile(user_id, storage, now)

    # ── Generate memory snapshot ──
    final_profile = storage.load_profile(user_id)
    if final_profile:
        snapshot_text = format_profile_text(
            final_profile, max_entries=40, detail="full", language=language,
        )
        user_model_data = storage.load_user_model(user_id)
        if user_model_data:
            model_lines = [f"  {m.get('dimension', '?')}: {m.get('assessment', '?')}" for m in user_model_data]
            snapshot_text += "\n\nUser traits:\n" + "\n".join(model_lines)

        active_events = storage.load_events(user_id, top_k=5)
        if active_events:
            event_lines = [f"  [{e.get('category', '?')}] {e.get('summary', '')}" for e in active_events]
            snapshot_text += "\n\nRecent events:\n" + "\n".join(event_lines)

        rels = storage.load_relationships(user_id)
        if rels:
            rel_lines = [f"  {r.get('relation', '?')}: {r.get('name', '?')}" for r in rels[:10]]
            snapshot_text += "\n\nRelationships:\n" + "\n".join(rel_lines)

        storage.save_memory_snapshot(user_id, snapshot_text, profile_count=len(final_profile))

    # ── Step 14: Mark processed ──
    storage.mark_processed(all_msg_ids)

    return {
        "status": "ok",
        "processed": len(all_msg_ids),
        "sessions": len(session_convs),
        "observations": len(all_observations),
        "new_facts": new_fact_count,
        "contradictions": contradict_count,
        "confirmed": confirmed_count,
        "disputes_resolved": dispute_resolved,
        "expired_closed": stale_count,
        "maturity_upgrades": maturity_count,
        "strategies": strategy_count,
        "model_dimensions": model_count,
        "trajectory_updated": trajectory_updated,
    }


def _consolidate_profile(user_id: str, storage: StorageBackend, now: str) -> None:
    """Merge duplicate (category, subject) profile entries, keeping the newest."""
    all_profile = storage.load_profile(user_id)

    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for p in all_profile:
        groups[(p.get("category", ""), p.get("subject", ""))].append(p)

    for (cat, subj), entries in groups.items():
        if len(entries) <= 1:
            continue
        # Sort by updated_at descending, keep newest
        entries.sort(
            key=lambda x: x.get("updated_at") or x.get("created_at") or "",
            reverse=True,
        )
        keeper = entries[0]
        for old in entries[1:]:
            if old.get("id") == keeper.get("id"):
                continue
            if old.get("superseded_by") or old.get("end_time"):
                continue
            if old.get("value", "").strip().lower() != keeper.get("value", "").strip().lower():
                continue
            # Merge evidence from old into keeper
            storage.add_evidence(keeper["id"], {"merged_from": old["id"]}, reference_time=now)
            # Close old entry
            storage.close_fact(old["id"], end_time=now)
            storage.delete_fact_edges_for(old["id"])
