"""OpenAI-compatible LLM client for Riverse."""

from __future__ import annotations

from riverse.config import RiverseConfig
from riverse.llm.base import LLMClient


class OpenAIClient(LLMClient):
    """LLM client using the OpenAI Python SDK (works with any compatible API)."""

    def __init__(self, config: RiverseConfig) -> None:
        from openai import OpenAI

        self.config = config
        # Ensure api_base ends properly for the SDK
        base = config.api_base.rstrip("/")
        if not base.endswith("/v1"):
            base = base + "/v1"
        self.client = OpenAI(
            api_key=config.api_key or "dummy",
            base_url=base,
        )

    def chat(self, messages: list[dict]) -> str:
        """Send messages via chat completions and return the text response."""
        model = self.config.model

        # Handle newer models that use max_completion_tokens
        is_new_model = any(k in model for k in ("gpt-5", "o1", "o3", "o4"))
        kwargs: dict = {"model": model, "messages": messages}

        if is_new_model:
            kwargs["max_completion_tokens"] = self.config.max_tokens
        else:
            kwargs["max_tokens"] = self.config.max_tokens
            kwargs["temperature"] = self.config.temperature

        try:
            resp = self.client.chat.completions.create(**kwargs)
            return resp.choices[0].message.content or ""
        except Exception as e:
            return f"[LLM Error] {e}"
