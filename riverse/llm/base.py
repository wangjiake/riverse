"""Abstract LLM client interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


def is_llm_error(text: str) -> bool:
    """Check if text is an LLM error message."""
    return bool(text) and text.startswith("[LLM ")


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def chat(self, messages: list[dict]) -> str:
        """Send messages and return the assistant's reply text."""
        ...
