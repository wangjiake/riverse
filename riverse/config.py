"""Configuration dataclass for Riverse."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class RiverseConfig:
    """All configuration for a Riverse instance."""

    # LLM
    api_key: str = ""
    api_base: str = "https://api.openai.com"
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 4096

    # Language
    language: str = "en"

    # Storage
    db_path: str = field(default_factory=lambda: os.path.expanduser("~/.riverse/memory.db"))

    # Sleep pipeline
    trajectory_update_interval: int = 3  # sessions between trajectory updates

    def llm_dict(self) -> dict:
        """Return a dict suitable for the LLM client."""
        return {
            "api_key": self.api_key,
            "api_base": self.api_base,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
