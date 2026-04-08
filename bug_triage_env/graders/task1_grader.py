"""
Task 1 Grader: Bug Type Classification.

Scoring: 1.0 for exact match, 0.0 otherwise.
"""

from typing import Any, Dict, List


def grade(episode_log: List[Dict[str, Any]], ground_truth: Dict[str, Any]) -> float:
    """
    Evaluate a completed Task 1 episode.

    Args:
        episode_log: List of agent actions (dicts with ``bug_type`` key).
        ground_truth: Dict with expected ``bug_type`` string.

    Returns:
        Score in [0.0, 1.0].
    """
    if not episode_log:
        return 0.01

    last_action = episode_log[-1]
    predicted = (last_action.get("bug_type") or "").strip().lower()
    expected = (ground_truth.get("bug_type") or "").strip().lower()

    if not predicted:
        return 0.01

    return 0.99 if predicted == expected else 0.01
