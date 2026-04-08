"""
Core RL environment implementing the OpenEnv interface.

Provides reset(), step(), and state for the Bug Triage environment.
Thread-safe episode store for concurrent HTTP sessions.
"""

from __future__ import annotations

import json
import logging
import random
import threading
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from core.env_server import Environment as _OpenEnvBase
except ImportError:

    class _OpenEnvBase:  # type: ignore[no-redef]
        pass


from ..graders import GRADERS
from ..models import (
    DEVELOPERS,
    BugReport,
    BugTriageAction,
    BugTriageObservation,
    BugTriageState,
)

logger = logging.getLogger(__name__)

DATA_PATH = Path(__file__).parent.parent / "data" / "bugs.json"


class BugTriageEnvironment(_OpenEnvBase):
    """
    Bug Triage RL Environment.

    Each episode:
      1. reset(task_id) - selects a random bug report
      2. step(action)   - agent triages the bug; grader scores; done=True
      3. state          - returns episode metadata

    Episode store is thread-safe for concurrent HTTP sessions.
    """

    def __init__(self, data_path: Path = DATA_PATH) -> None:
        self._bugs: List[Dict[str, Any]] = self._load_data(data_path)
        self._episodes: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._current_episode_id: Optional[str] = None
        logger.info("Loaded %d bug reports.", len(self._bugs))

    # -- OpenEnv interface -----------------------------------------------------

    def reset(self, task_id: str = "task_1") -> BugTriageObservation:
        """Start a new episode. Returns initial observation."""
        bug = random.choice(self._bugs)
        episode_id = uuid.uuid4().hex[:12]

        episode: Dict[str, Any] = {
            "episode_id": episode_id,
            "task_id": task_id,
            "bug": bug,
            "ground_truth": bug["ground_truth"],
            "actions": [],
            "done": False,
        }

        with self._lock:
            self._episodes[episode_id] = episode
            self._current_episode_id = episode_id

        bug_report = self._make_bug_report(bug)
        logger.info(
            "Episode %s | task=%s | bug=%s", episode_id, task_id, bug["bug_id"]
        )

        return BugTriageObservation(
            done=False,
            reward=0.0,
            task_id=task_id,
            bug_report=bug_report,
            available_developers=list(DEVELOPERS),
            step_number=0,
            feedback="New bug report received. Please triage.",
            episode_id=episode_id,
        )

    def step(
        self,
        action: BugTriageAction,
        episode_id: Optional[str] = None,
    ) -> BugTriageObservation:
        """Execute one triage action. Episode terminates immediately."""
        ep_id = episode_id or self._current_episode_id
        if ep_id is None:
            raise ValueError("No active episode. Call reset() first.")

        with self._lock:
            ep = self._episodes.get(ep_id)

        if ep is None:
            raise ValueError(f"Unknown episode_id: {ep_id}")
        if ep["done"]:
            raise ValueError(f"Episode {ep_id} is already done.")

        ep["actions"].append(action.model_dump())
        ep["done"] = True

        # Score via task-specific grader
        grader_fn = GRADERS.get(ep["task_id"], GRADERS["task_1"])
        grader_score = grader_fn(ep["actions"], ep["ground_truth"])

        # Shaped reward: map [0, 1] to [-0.5, 1.0] for GRPO training
        reward = (grader_score * 1.5) - 0.5

        # Confidence calibration bonus/penalty
        calibration_bonus = self._compute_calibration_bonus(
            action.confidence, grader_score
        )
        reward += calibration_bonus
        reward = max(-0.65, min(1.1, reward))

        # Build feedback string
        feedback = self._build_feedback(
            action, ep["ground_truth"], ep["task_id"], grader_score
        )
        if action.confidence is not None:
            feedback += (
                f" | confidence={action.confidence:.2f}"
                f" (calibration={calibration_bonus:+.2f})"
            )

        bug_report = self._make_bug_report(ep["bug"])

        log_msg = "Episode %s | score=%.3f | reward=%.3f"
        log_args: list[Any] = [ep_id, grader_score, reward]
        if action.confidence is not None:
            log_msg += " | cal=%+.2f"
            log_args.append(calibration_bonus)
        logger.info(log_msg, *log_args)

        return BugTriageObservation(
            done=True,
            reward=round(reward, 4),
            task_id=ep["task_id"],
            bug_report=bug_report,
            available_developers=list(DEVELOPERS),
            step_number=1,
            feedback=feedback,
            grader_score=round(grader_score, 4),
            episode_id=ep_id,
        )

    @property
    def state(self) -> BugTriageState:
        """Return current episode metadata."""
        ep_id = self._current_episode_id
        if ep_id is None:
            return BugTriageState()

        with self._lock:
            ep = self._episodes.get(ep_id, {})

        return BugTriageState(
            episode_id=ep_id,
            step_count=len(ep.get("actions", [])),
            task_id=ep.get("task_id", ""),
            bug_id=ep.get("bug", {}).get("bug_id"),
        )

    # -- Grading ---------------------------------------------------------------

    def grade_episode(self, episode_id: str, task_id: str) -> Dict[str, Any]:
        """Grade a completed episode. Used by the /grader endpoint."""
        with self._lock:
            ep = self._episodes.get(episode_id)

        if ep is None:
            return {"score": 0.01, "breakdown": {}, "error": "episode_not_found"}
        if not ep["actions"]:
            return {"score": 0.01, "breakdown": {}, "error": "no_actions"}

        grader_fn = GRADERS.get(task_id, GRADERS["task_1"])
        score = grader_fn(ep["actions"], ep["ground_truth"])

        last_action = ep["actions"][-1]
        gt = ep["ground_truth"]
        breakdown: Dict[str, float] = {
            "bug_type_match": float(
                last_action.get("bug_type") == gt.get("bug_type")
            ),
            "priority_match": float(
                last_action.get("priority") == gt.get("priority")
            ),
        }
        if task_id == "task_3":
            breakdown["developer_match"] = float(
                last_action.get("assigned_developer")
                == gt.get("assigned_developer")
            )
            breakdown["action_match"] = float(
                last_action.get("suggested_action")
                == gt.get("suggested_action")
            )

        return {"score": round(score, 4), "breakdown": breakdown}

    # -- Private helpers -------------------------------------------------------

    @staticmethod
    def _load_data(path: Path) -> List[Dict[str, Any]]:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    @staticmethod
    def _make_bug_report(bug: Dict[str, Any]) -> BugReport:
        return BugReport(
            bug_id=bug["bug_id"],
            title=bug["title"],
            description=bug["description"],
            logs=bug.get("logs"),
            environment=bug.get("environment"),
            reporter=bug.get("reporter"),
            created_at=bug.get("created_at"),
            metadata=bug.get("metadata", {}),
        )

    @staticmethod
    def _compute_calibration_bonus(
        confidence: Optional[float],
        grader_score: float,
    ) -> float:
        """
        Compute reward adjustment based on confidence calibration.

        Returns a bonus in [-0.15, +0.10] or 0.0 if confidence is not provided.
        """
        if confidence is None:
            return 0.0

        calibration_error = abs(confidence - grader_score)

        if grader_score >= 0.8 and confidence >= 0.8:
            return 0.10  # correct and confident
        if grader_score < 0.5 and confidence >= 0.8:
            return -0.15  # wrong and overconfident
        if calibration_error < 0.2:
            return 0.05  # well-calibrated
        return -0.05  # poorly calibrated

    @staticmethod
    def _build_feedback(
        action: BugTriageAction,
        ground_truth: Dict[str, Any],
        task_id: str,
        score: float,
    ) -> str:
        parts: list[str] = [f"score={score:.2f}"]

        if task_id in ("task_1", "task_3"):
            match = action.bug_type == ground_truth.get("bug_type")
            parts.append(
                f"bug_type={'ok' if match else 'wrong'}"
                f" (pred={action.bug_type}, expected={ground_truth.get('bug_type')})"
            )
        if task_id in ("task_2", "task_3"):
            match = action.priority == ground_truth.get("priority")
            parts.append(
                f"priority={'ok' if match else 'wrong'}"
                f" (pred={action.priority}, expected={ground_truth.get('priority')})"
            )
        if task_id == "task_3":
            match = action.assigned_developer == ground_truth.get(
                "assigned_developer"
            )
            parts.append(
                f"developer={'ok' if match else 'wrong'}"
                f" (pred={action.assigned_developer},"
                f" expected={ground_truth.get('assigned_developer')})"
            )
            match = action.suggested_action == ground_truth.get(
                "suggested_action"
            )
            parts.append(
                f"action={'ok' if match else 'wrong'}"
                f" (pred={action.suggested_action},"
                f" expected={ground_truth.get('suggested_action')})"
            )

        return " | ".join(parts)
