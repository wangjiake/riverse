"""Abstract LLM client interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def chat(self, messages: list[dict]) -> str:
        """Send messages and return the assistant's reply text."""
        ...
