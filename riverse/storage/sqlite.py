"""SQLite storage backend for Riverse."""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timedelta
from importlib.resources import files as pkg_files

from riverse.storage.base import StorageBackend


def _now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


class SQLiteStorage(StorageBackend):
    """SQLite-backed storage for the River Algorithm."""

    def __init__(self, db_path: str) -> None:
        db_path = os.path.expanduser(db_path)
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_db(self) -> None:
        schema_path = pkg_files("riverse.storage").joinpath("schema.sql")
        schema_sql = schema_path.read_text(encoding="utf-8")
        conn = self._conn()
        try:
            conn.executescript(schema_sql)
            conn.commit()
        finally:
            conn.close()

    # ── Conversations ──

    def save_conversation(self, user_id: str, session_id: str, role: str, content: str) -> int:
        conn = self._conn()
        try:
            cur = conn.execute(
                "INSERT INTO conversations (user_id, session_id, role, content, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (user_id, session_id, role, content, _now()),
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def get_unprocessed_conversations(self, user_id: str) -> dict[str, list[dict]]:
        conn = self._conn()
        try:
            rows = conn.execute(
                "SELECT id, session_id, role, content, created_at "
                "FROM conversations "
                "WHERE user_id = ? AND processed = 0 "
                "ORDER BY id",
                (user_id,),
            ).fetchall()
            sessions: dict[str, list[dict]] = {}
            for row in rows:
                sid = row["session_id"]
                if sid not in sessions:
                    sessions[sid] = []
                sessions[sid].append(dict(row))
            return sessions
        finally:
            conn.close()

    def mark_processed(self, message_ids: list[int]) -> None:
        if not message_ids:
            return
        conn = self._conn()
        try:
            placeholders = ",".join("?" for _ in message_ids)
            conn.execute(
                f"UPDATE conversations SET processed = 1 WHERE id IN ({placeholders})",
                message_ids,
            )
            conn.commit()
        finally:
            conn.close()

    # ── Profile facts ──

    def save_profile_fact(self, user_id: str, category: str, subject: str, value: str,
                          source_type: str = "stated", layer: str = "suspected",
                          decay_days: int | None = None, evidence: list | None = None,
                          start_time: str | None = None) -> int:
        now = start_time or _now()
        if decay_days is None or decay_days <= 0:
            decay_days = 90
        expires_at_dt = datetime.strptime(now, "%Y-%m-%d %H:%M:%S") + timedelta(days=decay_days)
        expires_at = expires_at_dt.strftime("%Y-%m-%d %H:%M:%S")
        evidence_json = json.dumps(evidence or [], ensure_ascii=False)

        # Check for existing active fact with same category+subject (fuzzy via synonyms)
        from riverse.synonyms import get_category_synonyms, get_subject_synonyms
        existing = self._find_existing_fact(user_id, category, subject)

        conn = self._conn()
        try:
            if existing:
                eid = existing["id"]
                existing_value = existing["value"].strip().lower()
                new_value = value.strip().lower()

                if existing_value == new_value:
                    # Same value — add evidence, bump mention count
                    old_ev = json.loads(existing["evidence"] or "[]")
                    if evidence:
                        old_ev.extend(evidence)
                    new_mc = (existing["mention_count"] or 1) + 1
                    new_expires = (datetime.strptime(now, "%Y-%m-%d %H:%M:%S") +
                                   timedelta(days=existing.get("decay_days") or decay_days))
                    conn.execute(
                        "UPDATE user_profile SET evidence = ?, mention_count = ?, "
                        "updated_at = ?, expires_at = ? WHERE id = ?",
                        (json.dumps(old_ev, ensure_ascii=False), new_mc, now,
                         new_expires.strftime("%Y-%m-%d %H:%M:%S"), eid),
                    )
                    conn.commit()
                    return eid
                else:
                    # Different value — create new fact that supersedes old one
                    cur = conn.execute(
                        "INSERT INTO user_profile "
                        "(user_id, category, subject, value, layer, source_type, "
                        " start_time, decay_days, expires_at, evidence, mention_count, "
                        " created_at, updated_at, supersedes) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)",
                        (user_id, category, subject, value, layer, source_type,
                         now, decay_days, expires_at, evidence_json,
                         now, now, eid),
                    )
                    new_id = cur.lastrowid
                    conn.execute(
                        "UPDATE user_profile SET superseded_by = ? WHERE id = ?",
                        (new_id, eid),
                    )
                    conn.commit()
                    return new_id
            else:
                cur = conn.execute(
                    "INSERT INTO user_profile "
                    "(user_id, category, subject, value, layer, source_type, "
                    " start_time, decay_days, expires_at, evidence, mention_count, "
                    " created_at, updated_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)",
                    (user_id, category, subject, value, layer, source_type,
                     now, decay_days, expires_at, evidence_json,
                     now, now),
                )
                conn.commit()
                return cur.lastrowid
        finally:
            conn.close()

    def _find_existing_fact(self, user_id: str, category: str, subject: str) -> dict | None:
        """Find an existing active fact with matching category+subject (with synonym matching)."""
        from riverse.synonyms import get_category_synonyms, get_subject_synonyms

        conn = self._conn()
        try:
            # Exact match first
            row = conn.execute(
                "SELECT * FROM user_profile "
                "WHERE user_id = ? AND category = ? AND subject = ? "
                "AND rejected = 0 AND end_time IS NULL AND superseded_by IS NULL "
                "LIMIT 1",
                (user_id, category, subject),
            ).fetchone()
            if row:
                return dict(row)

            # Synonym match
            cat_syns = get_category_synonyms(category)
            subj_syns = get_subject_synonyms(subject)

            if len(cat_syns) > 1 or len(subj_syns) > 1:
                cat_placeholders = ",".join("?" for _ in cat_syns)
                subj_placeholders = ",".join("?" for _ in subj_syns)
                row = conn.execute(
                    f"SELECT * FROM user_profile "
                    f"WHERE user_id = ? AND category IN ({cat_placeholders}) "
                    f"AND subject IN ({subj_placeholders}) "
                    f"AND rejected = 0 AND end_time IS NULL AND superseded_by IS NULL "
                    f"LIMIT 1",
                    [user_id] + list(cat_syns) + list(subj_syns),
                ).fetchone()
                if row:
                    return dict(row)

            # Fuzzy subject match
            row = conn.execute(
                "SELECT * FROM user_profile "
                "WHERE user_id = ? AND rejected = 0 AND end_time IS NULL AND superseded_by IS NULL "
                "AND (subject LIKE '%' || ? || '%' OR ? LIKE '%' || subject || '%') "
                "LIMIT 1",
                (user_id, subject, subject),
            ).fetchone()
            if row:
                return dict(row)

            return None
        finally:
            conn.close()

    def add_evidence(self, fact_id: int, evidence_entry: dict, reference_time: str | None = None) -> None:
        now = reference_time or _now()
        conn = self._conn()
        try:
            row = conn.execute("SELECT evidence, mention_count, decay_days FROM user_profile WHERE id = ?",
                               (fact_id,)).fetchone()
            if not row:
                return
            MAX_EVIDENCE = 10
            ev = json.loads(row["evidence"] or "[]")
            ev.append(evidence_entry)
            if len(ev) > MAX_EVIDENCE:
                ev = ev[-MAX_EVIDENCE:]
            mc = (row["mention_count"] or 1) + 1
            decay = row["decay_days"] or 90
            new_expires = (datetime.strptime(now, "%Y-%m-%d %H:%M:%S") + timedelta(days=decay))
            conn.execute(
                "UPDATE user_profile SET evidence = ?, mention_count = ?, "
                "updated_at = ?, expires_at = ? WHERE id = ?",
                (json.dumps(ev, ensure_ascii=False), mc, now,
                 new_expires.strftime("%Y-%m-%d %H:%M:%S"), fact_id),
            )
            conn.commit()
        finally:
            conn.close()

    def confirm_fact(self, fact_id: int, reference_time: str | None = None) -> None:
        now = reference_time or _now()
        conn = self._conn()
        try:
            conn.execute(
                "UPDATE user_profile SET layer = 'confirmed', confirmed_at = ?, updated_at = ? "
                "WHERE id = ?",
                (now, now, fact_id),
            )
            conn.commit()
        finally:
            conn.close()

    def load_profile(self, user_id: str) -> list[dict]:
        conn = self._conn()
        try:
            rows = conn.execute(
                "SELECT * FROM user_profile "
                "WHERE user_id = ? AND rejected = 0 AND end_time IS NULL AND superseded_by IS NULL "
                "ORDER BY layer DESC, updated_at DESC",
                (user_id,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def load_suspected(self, user_id: str) -> list[dict]:
        conn = self._conn()
        try:
            rows = conn.execute(
                "SELECT * FROM user_profile "
                "WHERE user_id = ? AND layer = 'suspected' "
                "AND rejected = 0 AND end_time IS NULL AND superseded_by IS NULL "
                "ORDER BY updated_at DESC",
                (user_id,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def load_timeline(self, user_id: str, category: str | None = None,
                      subject: str | None = None,
                      include_rejected: bool = False) -> list[dict]:
        conn = self._conn()
        try:
            conditions = ["user_id = ?"]
            params: list = [user_id]
            if not include_rejected:
                conditions.append("rejected = 0")
            if category:
                conditions.append("category = ?")
                params.append(category)
            if subject:
                conditions.append("subject = ?")
                params.append(subject)
            where = " AND ".join(conditions)
            rows = conn.execute(
                f"SELECT * FROM user_profile WHERE {where} ORDER BY start_time ASC",
                params,
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def load_disputed(self, user_id: str) -> list[dict]:
        conn = self._conn()
        try:
            # Find pairs where A superseded_by B and B supersedes A
            rows = conn.execute(
                "SELECT old.id as old_id, new.id as new_id "
                "FROM user_profile old "
                "JOIN user_profile new ON old.superseded_by = new.id "
                "WHERE old.user_id = ? AND old.rejected = 0 AND new.rejected = 0 "
                "AND old.end_time IS NULL AND new.end_time IS NULL",
                (user_id,),
            ).fetchall()
            pairs = []
            for row in rows:
                old_row = conn.execute("SELECT * FROM user_profile WHERE id = ?",
                                       (row["old_id"],)).fetchone()
                new_row = conn.execute("SELECT * FROM user_profile WHERE id = ?",
                                       (row["new_id"],)).fetchone()
                if old_row and new_row:
                    pairs.append({"old": dict(old_row), "new": dict(new_row)})
            return pairs
        finally:
            conn.close()

    def resolve_dispute(self, old_id: int, new_id: int, accept_new: bool,
                        resolution_time: str | None = None) -> None:
        now = resolution_time or _now()
        conn = self._conn()
        try:
            if accept_new:
                # Close old fact, clear superseded_by link
                conn.execute(
                    "UPDATE user_profile SET end_time = ?, updated_at = ? WHERE id = ?",
                    (now, now, old_id),
                )
                # Remove supersedes link from new fact
                conn.execute(
                    "UPDATE user_profile SET supersedes = NULL, updated_at = ? WHERE id = ?",
                    (now, new_id),
                )
            else:
                # Reject new fact, restore old
                conn.execute(
                    "UPDATE user_profile SET rejected = 1, updated_at = ? WHERE id = ?",
                    (now, new_id),
                )
                conn.execute(
                    "UPDATE user_profile SET superseded_by = NULL, updated_at = ? WHERE id = ?",
                    (now, old_id),
                )
            conn.commit()
        finally:
            conn.close()

    def close_fact(self, fact_id: int, end_time: str | None = None) -> None:
        now = end_time or _now()
        conn = self._conn()
        try:
            conn.execute(
                "UPDATE user_profile SET end_time = ?, updated_at = ? WHERE id = ?",
                (now, now, fact_id),
            )
            conn.commit()
        finally:
            conn.close()

    def update_decay(self, fact_id: int, new_decay_days: int, reference_time: str | None = None) -> None:
        now = reference_time or _now()
        new_expires = (datetime.strptime(now, "%Y-%m-%d %H:%M:%S") + timedelta(days=new_decay_days))
        conn = self._conn()
        try:
            conn.execute(
                "UPDATE user_profile SET decay_days = ?, expires_at = ?, updated_at = ? WHERE id = ?",
                (new_decay_days, new_expires.strftime("%Y-%m-%d %H:%M:%S"), now, fact_id),
            )
            conn.commit()
        finally:
            conn.close()

    def get_expired(self, user_id: str, reference_time: str | None = None) -> list[dict]:
        now = reference_time or _now()
        conn = self._conn()
        try:
            rows = conn.execute(
                "SELECT * FROM user_profile "
                "WHERE user_id = ? AND expires_at IS NOT NULL AND expires_at < ? "
                "AND rejected = 0 AND end_time IS NULL "
                "ORDER BY expires_at ASC",
                (user_id, now),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def find_current_fact(self, user_id: str, category: str, subject: str) -> dict | None:
        return self._find_existing_fact(user_id, category, subject)

    # ── Observations ──

    def save_observation(self, user_id: str, session_id: str, obs_type: str, content: str,
                         subject: str | None = None, context: str | None = None) -> None:
        conn = self._conn()
        try:
            conn.execute(
                "INSERT INTO observations "
                "(user_id, session_id, observation_type, content, subject, context, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, session_id, obs_type, content, subject, context, _now()),
            )
            conn.commit()
        finally:
            conn.close()

    def load_observations(self, user_id: str, session_id: str | None = None,
                          limit: int = 50) -> list[dict]:
        conn = self._conn()
        try:
            conditions = ["user_id = ?", "rejected = 0"]
            params: list = [user_id]
            if session_id:
                conditions.append("session_id = ?")
                params.append(session_id)
            where = " AND ".join(conditions)
            params.append(limit)
            rows = conn.execute(
                f"SELECT * FROM observations WHERE {where} "
                f"ORDER BY created_at DESC LIMIT ?",
                params,
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    # ── Events ──

    def save_event(self, user_id: str, category: str, summary: str,
                   session_id: str | None = None, importance: float = 0.5,
                   decay_days: int | None = None, reference_time: str | None = None) -> None:
        now = reference_time or _now()
        expires_at = None
        if decay_days and decay_days > 0:
            expires_at_dt = datetime.strptime(now, "%Y-%m-%d %H:%M:%S") + timedelta(days=decay_days)
            expires_at = expires_at_dt.strftime("%Y-%m-%d %H:%M:%S")

        conn = self._conn()
        try:
            # Check for similar existing event
            rows = conn.execute(
                "SELECT id, summary FROM events "
                "WHERE user_id = ? AND category = ? "
                "AND (expires_at IS NULL OR expires_at > ?) "
                "ORDER BY created_at DESC LIMIT 5",
                (user_id, category, now),
            ).fetchall()
            for row in rows:
                if self._is_similar_event(row["summary"], summary):
                    conn.execute(
                        "UPDATE events SET expires_at = ?, importance = ? WHERE id = ?",
                        (expires_at, importance, row["id"]),
                    )
                    conn.commit()
                    return

            conn.execute(
                "INSERT INTO events (user_id, category, summary, importance, "
                "session_id, decay_days, expires_at, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, category, summary, importance, session_id,
                 decay_days, expires_at, now),
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def _is_similar_event(existing: str, new: str) -> bool:
        stopwords = {"the", "a", "an", "is", "was", "are", "in", "at", "to", "for",
                     "user", "very", "really", "likes", "interested"}
        def clean(s: str) -> str:
            s = s.strip().lower()
            for w in stopwords:
                s = s.replace(w, "")
            return s.strip()
        a, b = clean(existing), clean(new)
        if not a or not b:
            return False
        return a == b or a in b or b in a

    def load_events(self, user_id: str, top_k: int = 10) -> list[dict]:
        now = _now()
        conn = self._conn()
        try:
            rows = conn.execute(
                "SELECT * FROM events "
                "WHERE user_id = ? AND (expires_at IS NULL OR expires_at > ?) "
                "ORDER BY importance DESC, created_at DESC "
                "LIMIT ?",
                (user_id, now, top_k),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    # ── Relationships ──

    def save_relationship(self, user_id: str, name: str | None, relation: str,
                          details: dict | None = None) -> int:
        details_json = json.dumps(details or {}, ensure_ascii=False)
        now = _now()
        conn = self._conn()
        try:
            # Check existing
            if name:
                row = conn.execute(
                    "SELECT id, mention_count FROM relationships "
                    "WHERE user_id = ? AND name = ? AND status = 'active' LIMIT 1",
                    (user_id, name),
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT id, mention_count FROM relationships "
                    "WHERE user_id = ? AND relation = ? AND name IS NULL AND status = 'active' LIMIT 1",
                    (user_id, relation),
                ).fetchone()

            if row:
                conn.execute(
                    "UPDATE relationships SET details = ?, mention_count = ?, "
                    "last_mentioned_at = ? WHERE id = ?",
                    (details_json, (row["mention_count"] or 1) + 1, now, row["id"]),
                )
                conn.commit()
                return row["id"]

            cur = conn.execute(
                "INSERT INTO relationships "
                "(user_id, name, relation, details, mention_count, "
                " first_mentioned_at, last_mentioned_at) "
                "VALUES (?, ?, ?, ?, 1, ?, ?)",
                (user_id, name, relation, details_json, now, now),
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def load_relationships(self, user_id: str) -> list[dict]:
        conn = self._conn()
        try:
            rows = conn.execute(
                "SELECT * FROM relationships WHERE user_id = ? AND status = 'active' "
                "ORDER BY last_mentioned_at DESC",
                (user_id,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    # ── User model ──

    def upsert_user_model(self, user_id: str, dimension: str, assessment: str,
                          evidence: str = "") -> None:
        now = _now()
        conn = self._conn()
        try:
            conn.execute(
                "INSERT INTO user_model (user_id, dimension, assessment, evidence_summary, updated_at) "
                "VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(user_id, dimension) DO UPDATE SET "
                "assessment = excluded.assessment, "
                "evidence_summary = excluded.evidence_summary, "
                "updated_at = excluded.updated_at",
                (user_id, dimension, assessment, evidence, now),
            )
            conn.commit()
        finally:
            conn.close()

    def load_user_model(self, user_id: str) -> list[dict]:
        conn = self._conn()
        try:
            rows = conn.execute(
                "SELECT * FROM user_model WHERE user_id = ? ORDER BY dimension",
                (user_id,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    # ── Trajectory ──

    def save_trajectory(self, user_id: str, trajectory: dict, session_count: int = 0) -> None:
        now = _now()
        conn = self._conn()
        try:
            existing = conn.execute(
                "SELECT id FROM trajectory WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1",
                (user_id,),
            ).fetchone()
            if existing:
                conn.execute(
                    "UPDATE trajectory SET life_phase = ?, phase_characteristics = ?, "
                    "trajectory_direction = ?, stability_assessment = ?, "
                    "key_anchors = ?, volatile_areas = ?, recent_momentum = ?, "
                    "full_summary = ?, session_count = ?, updated_at = ? "
                    "WHERE id = ?",
                    (trajectory.get("life_phase"),
                     trajectory.get("phase_characteristics"),
                     trajectory.get("trajectory_direction"),
                     trajectory.get("stability_assessment"),
                     json.dumps(trajectory.get("key_anchors", []), ensure_ascii=False),
                     json.dumps(trajectory.get("volatile_areas", []), ensure_ascii=False),
                     trajectory.get("recent_momentum"),
                     trajectory.get("full_summary"),
                     session_count, now, existing["id"]),
                )
            else:
                conn.execute(
                    "INSERT INTO trajectory "
                    "(user_id, life_phase, phase_characteristics, trajectory_direction, "
                    " stability_assessment, key_anchors, volatile_areas, recent_momentum, "
                    " full_summary, session_count, created_at, updated_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (user_id,
                     trajectory.get("life_phase"),
                     trajectory.get("phase_characteristics"),
                     trajectory.get("trajectory_direction"),
                     trajectory.get("stability_assessment"),
                     json.dumps(trajectory.get("key_anchors", []), ensure_ascii=False),
                     json.dumps(trajectory.get("volatile_areas", []), ensure_ascii=False),
                     trajectory.get("recent_momentum"),
                     trajectory.get("full_summary"),
                     session_count, now, now),
                )
            conn.commit()
        finally:
            conn.close()

    def load_trajectory(self, user_id: str) -> dict | None:
        conn = self._conn()
        try:
            row = conn.execute(
                "SELECT * FROM trajectory WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1",
                (user_id,),
            ).fetchone()
            if not row:
                return None
            result = dict(row)
            # Parse JSON fields
            for key in ("key_anchors", "volatile_areas"):
                if isinstance(result.get(key), str):
                    try:
                        result[key] = json.loads(result[key])
                    except (json.JSONDecodeError, ValueError):
                        result[key] = []
            return result
        finally:
            conn.close()

    # ── Strategies ──

    def save_strategy(self, user_id: str, category: str, subject: str,
                      strategy_type: str, description: str,
                      trigger_condition: str = "", approach: str = "",
                      reference_time: str | None = None) -> bool:
        now = reference_time or _now()
        conn = self._conn()
        try:
            conn.execute(
                "INSERT INTO strategies "
                "(user_id, category, subject, strategy_type, description, "
                " trigger_condition, approach, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, category, subject, strategy_type, description,
                 trigger_condition, approach, now),
            )
            conn.commit()
            return True
        finally:
            conn.close()

    def load_strategies(self, user_id: str) -> list[dict]:
        conn = self._conn()
        try:
            rows = conn.execute(
                "SELECT * FROM strategies "
                "WHERE user_id = ? AND status = 'pending' "
                "ORDER BY priority DESC, created_at DESC",
                (user_id,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    # ── Fact edges ──

    def delete_fact_edges_for(self, fact_id: int) -> None:
        conn = self._conn()
        try:
            conn.execute(
                "DELETE FROM fact_edges WHERE source_fact_id = ? OR target_fact_id = ?",
                (fact_id, fact_id),
            )
            conn.commit()
        except sqlite3.OperationalError:
            pass  # table may not exist yet
        finally:
            conn.close()

    # ── Tags / Summaries ──

    def save_session_tag(self, user_id: str, session_id: str, tag: str, summary: str = "") -> None:
        conn = self._conn()
        try:
            conn.execute(
                "INSERT INTO session_tags (user_id, session_id, tag, summary, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (user_id, session_id, tag, summary, _now()),
            )
            conn.commit()
        finally:
            conn.close()

    def load_existing_tags(self, user_id: str, limit: int = 50) -> list[str]:
        conn = self._conn()
        try:
            rows = conn.execute(
                "SELECT DISTINCT tag FROM session_tags "
                "WHERE user_id = ? ORDER BY tag LIMIT ?",
                (user_id, limit),
            ).fetchall()
            return [row["tag"] for row in rows]
        finally:
            conn.close()

    def save_session_summary(self, user_id: str, session_id: str, summary: str) -> None:
        conn = self._conn()
        try:
            conn.execute(
                "INSERT INTO session_summaries (user_id, session_id, intent_summary, created_at) "
                "VALUES (?, ?, ?, ?) "
                "ON CONFLICT(session_id) DO UPDATE SET intent_summary = excluded.intent_summary",
                (user_id, session_id, summary, _now()),
            )
            conn.commit()
        finally:
            conn.close()

    def get_session_count(self, user_id: str) -> int:
        conn = self._conn()
        try:
            row = conn.execute(
                "SELECT COUNT(DISTINCT session_id) as cnt FROM conversations "
                "WHERE user_id = ? AND processed = 1",
                (user_id,),
            ).fetchone()
            return row["cnt"] if row else 0
        finally:
            conn.close()

    # ── Memory snapshot ──

    def save_memory_snapshot(self, user_id: str, text: str, profile_count: int = 0) -> None:
        conn = self._conn()
        try:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS memory_snapshot ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "user_id TEXT NOT NULL, "
                "snapshot_text TEXT NOT NULL, "
                "profile_count INTEGER DEFAULT 0, "
                "created_at TEXT DEFAULT (datetime('now')))"
            )
            conn.execute(
                "INSERT INTO memory_snapshot (user_id, snapshot_text, profile_count, created_at) "
                "VALUES (?, ?, ?, ?)",
                (user_id, text, profile_count, _now()),
            )
            conn.commit()
        finally:
            conn.close()

    def load_memory_snapshot(self, user_id: str) -> dict | None:
        conn = self._conn()
        try:
            try:
                row = conn.execute(
                    "SELECT snapshot_text, profile_count, created_at "
                    "FROM memory_snapshot WHERE user_id = ? "
                    "ORDER BY created_at DESC LIMIT 1",
                    (user_id,),
                ).fetchone()
            except sqlite3.OperationalError:
                return None
            if not row:
                return None
            return {
                "snapshot_text": row["snapshot_text"],
                "profile_count": row["profile_count"],
                "created_at": row["created_at"],
            }
        finally:
            conn.close()
