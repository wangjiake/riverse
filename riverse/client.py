"""Riverse main class — user-facing API."""

from __future__ import annotations

import uuid
from datetime import datetime

from riverse.config import RiverseConfig
from riverse.llm.openai_client import OpenAIClient
from riverse.storage.sqlite import SQLiteStorage


class Riverse:
    """High-level interface for the River Algorithm memory system."""

    def __init__(
        self,
        api_key: str = "",
        api_base: str = "https://api.openai.com",
        model: str = "gpt-4o-mini",
        language: str = "en",
        db_path: str = "~/.riverse/memory.db",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> None:
        self.config = RiverseConfig(
            api_key=api_key,
            api_base=api_base,
            model=model,
            language=language,
            db_path=db_path,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        self.storage = SQLiteStorage(self.config.db_path)
        self.llm = OpenAIClient(self.config)

    # ── Public API ──────────────────────────────────────────

    def add(
        self,
        messages: list[dict],
        user_id: str = "default",
        session_id: str | None = None,
    ) -> None:
        """Store conversation messages for later consolidation via sleep()."""
        if session_id is None:
            session_id = uuid.uuid4().hex[:12]
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if content:
                self.storage.save_conversation(user_id, session_id, role, content)

    def sleep(self, user_id: str = "default") -> dict:
        """Run the full River Algorithm consolidation pipeline.

        Returns a summary dict with counts of actions taken.
        """
        from riverse.pipeline.sleep import run_sleep

        return run_sleep(
            user_id=user_id,
            storage=self.storage,
            llm=self.llm,
            config=self.config,
        )

    def search(self, query: str, user_id: str = "default", top_k: int = 10) -> list[dict]:
        """Search memory for relevant profile facts, events, and observations."""
        results = []
        keywords = [w for w in query.lower().split() if len(w) >= 2]

        # Search profile facts
        profile = self.storage.load_profile(user_id)
        for fact in profile:
            text = f"{fact.get('category', '')} {fact.get('subject', '')} {fact.get('value', '')}".lower()
            if any(kw in text for kw in keywords):
                results.append({"type": "profile", **fact})

        # Search events
        events = self.storage.load_events(user_id, top_k=50)
        for ev in events:
            text = f"{ev.get('category', '')} {ev.get('summary', '')}".lower()
            if any(kw in text for kw in keywords):
                results.append({"type": "event", **ev})

        # Search observations
        observations = self.storage.load_observations(user_id, limit=100)
        for obs in observations:
            text = f"{obs.get('content', '')} {obs.get('subject', '')}".lower()
            if any(kw in text for kw in keywords):
                results.append({"type": "observation", **obs})

        return results[:top_k]

    def get_profile(self, user_id: str = "default") -> list[dict]:
        """Get all active profile facts for a user."""
        return self.storage.load_profile(user_id)

    def get_user_model(self, user_id: str = "default") -> dict:
        """Get user model (personality dimensions) and trajectory."""
        model = self.storage.load_user_model(user_id)
        trajectory = self.storage.load_trajectory(user_id)
        return {
            "dimensions": model,
            "trajectory": trajectory,
        }
