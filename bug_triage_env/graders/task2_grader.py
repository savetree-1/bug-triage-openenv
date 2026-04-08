"""
Task 2 Grader: Priority Assignment.

Scoring applies partial credit based on priority level distance.
Exact match: 1.0, off by 1: 0.67, off by 2: 0.33, off by 3: 0.0.
"""

from typing import Any, Dict, List

PRIORITY_ORDER: Dict[str, int] = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "critical": 3,
}


def grade(episode_log: List[Dict[str, Any]], ground_truth: Dict[str, Any]) -> float:
    """
    Evaluate a completed Task 2 episode.

    Args:
        episode_log: List of actions with 'priority'.
        ground_truth: Expected 'priority' dictionary.

    Returns:
        float score in [0.0, 1.0].
    """
    if not episode_log:
        return 0.01

    last_action = episode_log[-1]
    predicted = (last_action.get("priority") or "").strip().lower()
    expected = (ground_truth.get("priority") or "").strip().lower()

    if not predicted or predicted not in PRIORITY_ORDER:
        return 0.01
    if expected not in PRIORITY_ORDER:
        return 0.01

    diff = abs(PRIORITY_ORDER[predicted] - PRIORITY_ORDER[expected])
    score = 1.0 - diff * (1.0 / 3.0)
    return max(0.01, min(0.99, score))
