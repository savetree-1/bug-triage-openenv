"""
Task 3 Grader: Full Triage.

Classify + prioritize + assign + suggest.
Uses a weighted composite score with partial credit.
"""

from typing import Any, Dict, List

PRIORITY_ORDER: Dict[str, int] = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "critical": 3,
}

DEVELOPER_SPECIALIZATIONS: Dict[str, List[str]] = {
    "Alice": ["crash", "performance", "data_loss"],
    "Bob": ["crash", "security"],
    "Carol": ["ui", "compatibility"],
    "David": ["security", "data_loss"],
    "Eve": ["ui", "performance", "compatibility"],
}

# Actions close enough to award partial credit
ACTION_PARTIAL: Dict[str, List[str]] = {
    "fix_immediately": ["schedule_sprint"],
    "schedule_sprint": ["fix_immediately", "needs_more_info"],
    "needs_more_info": ["schedule_sprint"],
    "wontfix": ["duplicate"],
    "duplicate": ["wontfix"],
}

WEIGHTS: Dict[str, float] = {
    "bug_type": 0.30,
    "priority": 0.30,
    "developer": 0.20,
    "action": 0.20,
}


def _score_bug_type(predicted: str, expected: str) -> float:
    return 1.0 if predicted == expected else 0.0


def _score_priority(predicted: str, expected: str) -> float:
    if predicted not in PRIORITY_ORDER or expected not in PRIORITY_ORDER:
        return 0.0
    diff = abs(PRIORITY_ORDER[predicted] - PRIORITY_ORDER[expected])
    return max(0.0, 1.0 - diff * (1.0 / 3.0))


def _score_developer(predicted: str, expected: str, bug_type: str) -> float:
    if predicted == expected:
        return 1.0
    pred_specs = DEVELOPER_SPECIALIZATIONS.get(predicted, [])
    if bug_type in pred_specs:
        return 0.5  # right specialization, wrong person
    return 0.0


def _score_action(predicted: str, expected: str) -> float:
    if predicted == expected:
        return 1.0
    if predicted in ACTION_PARTIAL.get(expected, []):
        return 0.5
    return 0.0


def grade(episode_log: List[Dict[str, Any]], ground_truth: Dict[str, Any]) -> float:
    """
    Evaluate a completed Task 3 episode (full triage).

    Weights:
        bug_type  30% - exact match
        priority  30% - distance penalty
        developer 20% - exact or specialization partial credit
        action    20% - exact or adjacent partial credit

    Args:
        episode_log: Agent actions list.
        ground_truth: Expected dictionary.

    Returns:
        float score in [0.0, 1.0].
    """
    if not episode_log:
        return 0.0

    action = episode_log[-1]

    pred_type = (action.get("bug_type") or "").strip().lower()
    pred_prio = (action.get("priority") or "").strip().lower()
    pred_dev = (action.get("assigned_developer") or "").strip()
    pred_act = (action.get("suggested_action") or "").strip().lower()

    exp_type = (ground_truth.get("bug_type") or "").strip().lower()
    exp_prio = (ground_truth.get("priority") or "").strip().lower()
    exp_dev = (ground_truth.get("assigned_developer") or "").strip()
    exp_act = (ground_truth.get("suggested_action") or "").strip().lower()

    s_type = _score_bug_type(pred_type, exp_type)
    s_prio = _score_priority(pred_prio, exp_prio)
    s_dev = _score_developer(pred_dev, exp_dev, pred_type)
    s_act = _score_action(pred_act, exp_act)

    score = (
        WEIGHTS["bug_type"] * s_type
        + WEIGHTS["priority"] * s_prio
        + WEIGHTS["developer"] * s_dev
        + WEIGHTS["action"] * s_act
    )

    return max(0.0, min(1.0, round(score, 4)))
