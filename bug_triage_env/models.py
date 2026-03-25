"""
Typed Pydantic v2 models for action, observation, and state schemas.

All models follow the OpenEnv specification for RL environment interfaces.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# -- Domain enumerations --

class BugType(str, Enum):
    """Supported bug categories for classification."""

    CRASH = "crash"
    UI = "ui"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DATA_LOSS = "data_loss"
    COMPATIBILITY = "compatibility"


class Priority(str, Enum):
    """Severity levels ordered low to critical."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SuggestedAction(str, Enum):
    """Recommended triage actions."""

    FIX_IMMEDIATELY = "fix_immediately"
    SCHEDULE_SPRINT = "schedule_sprint"
    NEEDS_MORE_INFO = "needs_more_info"
    WONTFIX = "wontfix"
    DUPLICATE = "duplicate"


# -- Domain constants --

DEVELOPERS: list[str] = ["Alice", "Bob", "Carol", "David", "Eve"]

DEVELOPER_SPECIALIZATIONS: Dict[str, List[str]] = {
    "Alice": ["crash", "performance", "data_loss"],
    "Bob": ["crash", "security"],
    "Carol": ["ui", "compatibility"],
    "David": ["security", "data_loss"],
    "Eve": ["ui", "performance", "compatibility"],
}

PRIORITY_ORDER: Dict[str, int] = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "critical": 3,
}


# -- Action / Observation / State models --

class BugTriageAction(BaseModel):
    """Agent action submitted via the /step endpoint."""

    task_id: Literal["task_1", "task_2", "task_3"]
    bug_type: Optional[BugType] = None
    priority: Optional[Priority] = None
    assigned_developer: Optional[str] = None
    suggested_action: Optional[SuggestedAction] = None
    reasoning: Optional[str] = None
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description=(
            "Optional agent confidence in [0.0, 1.0]. "
            "Enables confidence-calibration bonus/penalty in reward."
        ),
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"use_enum_values": True}


class BugReport(BaseModel):
    """Structured representation of a software bug report."""

    bug_id: str
    title: str
    description: str
    logs: Optional[str] = None
    environment: Optional[str] = None
    reporter: Optional[str] = None
    created_at: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BugTriageObservation(BaseModel):
    """Observation returned by reset() and step()."""

    done: bool = False
    reward: float = 0.0
    task_id: str = ""
    bug_report: Optional[BugReport] = None
    available_developers: List[str] = Field(
        default_factory=lambda: list(DEVELOPERS)
    )
    step_number: int = 0
    feedback: str = ""
    grader_score: Optional[float] = None
    episode_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BugTriageState(BaseModel):
    """Episode-level metadata returned by the /state endpoint."""

    episode_id: Optional[str] = None
    step_count: int = 0
    task_id: str = ""
    bug_id: Optional[str] = None
    cumulative_reward: float = 0.0


# -- Request / Response models for FastAPI endpoints --

class ResetRequest(BaseModel):
    task_id: Literal["task_1", "task_2", "task_3"] = "task_1"


class StepRequest(BaseModel):
    episode_id: str
    action: BugTriageAction


class GraderRequest(BaseModel):
    episode_id: str
    task_id: Literal["task_1", "task_2", "task_3"]


class GraderResponse(BaseModel):
    task_id: str
    episode_id: str
    score: float
    breakdown: Dict[str, float]
    passed: bool


class BaselineResponse(BaseModel):
    baseline_model: str
    results: Dict[str, Dict[str, Any]]
    mean_score: float
