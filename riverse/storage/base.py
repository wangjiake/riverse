"""Abstract storage backend interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class StorageBackend(ABC):
    """Abstract base class for Riverse storage backends."""

    # ── Conversations ──

    @abstractmethod
    def save_conversation(self, user_id: str, session_id: str, role: str, content: str) -> int:
        ...

    @abstractmethod
    def get_unprocessed_conversations(self, user_id: str) -> dict[str, list[dict]]:
        """Return {session_id: [messages]} for unprocessed conversations."""
        ...

    @abstractmethod
    def mark_processed(self, message_ids: list[int]) -> None:
        ...

    # ── Profile facts ──

    @abstractmethod
    def save_profile_fact(self, user_id: str, category: str, subject: str, value: str,
                          source_type: str = "stated", layer: str = "suspected",
                          decay_days: int | None = None, evidence: list | None = None,
                          start_time: str | None = None) -> int:
        ...

    @abstractmethod
    def add_evidence(self, fact_id: int, evidence_entry: dict, reference_time: str | None = None) -> None:
        ...

    @abstractmethod
    def confirm_fact(self, fact_id: int, reference_time: str | None = None) -> None:
        ...

    @abstractmethod
    def load_profile(self, user_id: str) -> list[dict]:
        """Load all active (non-rejected, non-ended) profile facts."""
        ...

    @abstractmethod
    def load_suspected(self, user_id: str) -> list[dict]:
        """Load suspected-layer facts."""
        ...

    @abstractmethod
    def load_timeline(self, user_id: str, category: str | None = None,
                      subject: str | None = None,
                      include_rejected: bool = False) -> list[dict]:
        ...

    @abstractmethod
    def load_disputed(self, user_id: str) -> list[dict]:
        """Load disputed fact pairs."""
        ...

    @abstractmethod
    def resolve_dispute(self, old_id: int, new_id: int, accept_new: bool,
                        resolution_time: str | None = None) -> None:
        ...

    @abstractmethod
    def close_fact(self, fact_id: int, end_time: str | None = None) -> None:
        ...

    @abstractmethod
    def update_decay(self, fact_id: int, new_decay_days: int, reference_time: str | None = None) -> None:
        ...

    @abstractmethod
    def get_expired(self, user_id: str, reference_time: str | None = None) -> list[dict]:
        ...

    @abstractmethod
    def find_current_fact(self, user_id: str, category: str, subject: str) -> dict | None:
        ...

    # ── Observations ──

    @abstractmethod
    def save_observation(self, user_id: str, session_id: str, obs_type: str, content: str,
                         subject: str | None = None, context: str | None = None) -> None:
        ...

    @abstractmethod
    def load_observations(self, user_id: str, session_id: str | None = None,
                          limit: int = 50) -> list[dict]:
        ...

    # ── Events ──

    @abstractmethod
    def save_event(self, user_id: str, category: str, summary: str,
                   session_id: str | None = None, importance: float = 0.5,
                   decay_days: int | None = None, reference_time: str | None = None) -> None:
        ...

    @abstractmethod
    def load_events(self, user_id: str, top_k: int = 10) -> list[dict]:
        ...

    # ── Relationships ──

    @abstractmethod
    def save_relationship(self, user_id: str, name: str | None, relation: str,
                          details: dict | None = None) -> int:
        ...

    @abstractmethod
    def load_relationships(self, user_id: str) -> list[dict]:
        ...

    # ── User model ──

    @abstractmethod
    def upsert_user_model(self, user_id: str, dimension: str, assessment: str,
                          evidence: str = "") -> None:
        ...

    @abstractmethod
    def load_user_model(self, user_id: str) -> list[dict]:
        ...

    # ── Trajectory ──

    @abstractmethod
    def save_trajectory(self, user_id: str, trajectory: dict, session_count: int = 0) -> None:
        ...

    @abstractmethod
    def load_trajectory(self, user_id: str) -> dict | None:
        ...

    # ── Strategies ──

    @abstractmethod
    def save_strategy(self, user_id: str, category: str, subject: str,
                      strategy_type: str, description: str,
                      trigger_condition: str = "", approach: str = "",
                      reference_time: str | None = None) -> bool:
        ...

    @abstractmethod
    def load_strategies(self, user_id: str) -> list[dict]:
        ...

    # ── Tags / Summaries ──

    @abstractmethod
    def save_session_tag(self, user_id: str, session_id: str, tag: str, summary: str = "") -> None:
        ...

    @abstractmethod
    def load_existing_tags(self, user_id: str, limit: int = 50) -> list[str]:
        ...

    @abstractmethod
    def save_session_summary(self, user_id: str, session_id: str, summary: str) -> None:
        ...

    @abstractmethod
    def get_session_count(self, user_id: str) -> int:
        ...

    # ── Fact edges ──

    @abstractmethod
    def delete_fact_edges_for(self, fact_id: int) -> None:
        """Delete all edges where fact_id is source or target."""
        ...

    # ── Memory snapshot ──

    @abstractmethod
    def save_memory_snapshot(self, user_id: str, text: str, profile_count: int = 0) -> None:
        ...

    @abstractmethod
    def load_memory_snapshot(self, user_id: str) -> dict | None:
        """Load latest snapshot: {"snapshot_text": str, "profile_count": int, "created_at": str}"""
        ...
