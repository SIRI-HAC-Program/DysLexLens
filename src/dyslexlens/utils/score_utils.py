# utils/score_utils.py
from typing import Optional


def score_color(score: Optional[float]) -> str:
    """
    Returns a hex color representing score quality.
    Used only for UI display.
    """
    if score is None:
        return "#888888"          # neutral / missing
    if score >= 0.85:
        return "#1D9E75"          # green
    if score >= 0.65:
        return "#BA7517"          # amber
    return "#993C1D"              # red


def score_text(score: Optional[float]) -> str:
    """
    Format a score value for display.
    """
    return f"{score:.2f}" if score is not None else "N/A"