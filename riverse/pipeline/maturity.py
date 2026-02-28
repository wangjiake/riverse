"""Maturity decay calculation — pure algorithm, no LLM needed."""

from __future__ import annotations

# (min_span_days, min_evidence_count, target_decay_days)
_MATURITY_TIERS = [
    (730, 10, 730),
    (365, 6, 365),
    (90, 3, 180),
]


def calculate_maturity_decay(
    span_days: int,
    evidence_count: int,
    current_decay: int,
    in_key_anchors: bool = False,
) -> int:
    """Calculate whether a fact's decay should be upgraded based on its maturity.

    Args:
        span_days: Days between first_seen and last_updated.
        evidence_count: Number of evidence entries.
        current_decay: Current decay_days value.
        in_key_anchors: Whether the subject/value appears in trajectory key_anchors.

    Returns:
        The new decay_days value (only increases, never decreases).
    """
    boost = 0.6 if in_key_anchors else 1.0

    for min_span, min_ev, target in _MATURITY_TIERS:
        if (
            span_days >= min_span * boost
            and evidence_count >= max(1, int(min_ev * boost))
            and target > current_decay
        ):
            return target

    return current_decay
