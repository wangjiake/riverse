"""Multilingual prompt system for Riverse."""

from __future__ import annotations


def get_prompt(name: str, language: str = "en", **kwargs) -> str:
    """Get a prompt template by name and language, with variable substitution."""
    prompts = _load_prompts(language)
    template = prompts.get(name)
    if not template:
        # Fallback to English
        prompts = _load_prompts("en")
        template = prompts.get(name)
    if not template:
        raise KeyError(f"Unknown prompt: {name}")
    if kwargs:
        return template.format(**kwargs)
    return template


def get_label(name: str, language: str = "en") -> str:
    """Get a UI/format label by name and language."""
    labels = _load_labels(language)
    result = labels.get(name)
    if result is None:
        labels = _load_labels("en")
        result = labels.get(name, name)
    return result


def _load_prompts(language: str) -> dict[str, str]:
    """Load all prompts for a language."""
    if language == "zh":
        from riverse.prompts.zh import PROMPTS
        return PROMPTS
    elif language == "ja":
        from riverse.prompts.ja import PROMPTS
        return PROMPTS
    else:
        from riverse.prompts.en import PROMPTS
        return PROMPTS


def _load_labels(language: str) -> dict[str, str]:
    """Load all format labels for a language."""
    if language == "zh":
        from riverse.prompts.zh import LABELS
        return LABELS
    elif language == "ja":
        from riverse.prompts.ja import LABELS
        return LABELS
    else:
        from riverse.prompts.en import LABELS
        return LABELS
