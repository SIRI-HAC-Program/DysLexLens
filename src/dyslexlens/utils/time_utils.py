# utils/time_utils.py
from datetime import datetime


def iso_now() -> str:
    """
    Returns the current local time in ISO-8601 format
    with second-level precision.

    Example:
        2026-05-11T18:53:03
    """
    return datetime.now().isoformat(timespec="seconds")