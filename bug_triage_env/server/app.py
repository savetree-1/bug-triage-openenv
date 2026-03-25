"""
FastAPI server exposing the Bug Triage OpenEnv endpoints.

Standard OpenEnv endpoints:  /health  /reset  /step  /state
Hackathon-required endpoints: /tasks  /grader  /baseline
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ..models import (
    DEVELOPERS,
    BaselineResponse,
    BugTriageObservation,
    BugTriageState,
    GraderRequest,
    GraderResponse,
    ResetRequest,
    StepRequest,
)
from .environment import BugTriageEnvironment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -- Application setup ---------------------------------------------------------

app = FastAPI(
    title="Bug Triage OpenEnv",
    description="Bug Triage RL Environment following the OpenEnv spec.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

env = BugTriageEnvironment()


# -- Standard OpenEnv endpoints ------------------------------------------------


@app.get("/health")
def health() -> Dict[str, str]:
    """Liveness check. Returns 200 with status=healthy."""
    return {"status": "healthy"}


@app.post("/reset", response_model=BugTriageObservation)
def reset(body: ResetRequest = ResetRequest()) -> BugTriageObservation:
    """Start a new episode. Returns an initial observation with a bug report."""
    try:
        return env.reset(task_id=body.task_id)
    except Exception as exc:
        logger.error("reset() error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/step", response_model=BugTriageObservation)
def step(body: StepRequest) -> BugTriageObservation:
    """Execute one triage action. Requires episode_id from /reset."""
    try:
        return env.step(action=body.action, episode_id=body.episode_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("step() error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/state", response_model=BugTriageState)
def state() -> BugTriageState:
    """Return current episode metadata."""
    return env.state


# -- Hackathon-required endpoints ----------------------------------------------

TASKS_REGISTRY = [
    {
        "task_id": "task_1",
        "name": "Bug Type Classification",
        "description": (
            "Given a bug report (title, description, logs, environment "
            "metadata), classify the bug into one of: crash, ui, "
            "performance, security, data_loss, compatibility."
        ),
        "difficulty": "easy",
        "action_schema": {
            "task_id": "task_1",
            "bug_type": (
                "one of: crash | ui | performance | security "
                "| data_loss | compatibility"
            ),
            "confidence": "optional float in [0.0, 1.0]",
            "reasoning": "optional string",
        },
    },
    {
        "task_id": "task_2",
        "name": "Priority Assignment",
        "description": (
            "Given a bug report, assign the correct priority level: "
            "low, medium, high, or critical. "
            "Partial credit awarded for near-miss levels."
        ),
        "difficulty": "medium",
        "action_schema": {
            "task_id": "task_2",
            "priority": "one of: low | medium | high | critical",
            "confidence": "optional float in [0.0, 1.0]",
            "reasoning": "optional string",
        },
    },
    {
        "task_id": "task_3",
        "name": "Full Bug Triage",
        "description": (
            "Complete triage: classify bug type, assign priority, "
            "route to the correct developer, and suggest the "
            "appropriate action. "
            f"Available developers: {', '.join(DEVELOPERS)}."
        ),
        "difficulty": "hard",
        "action_schema": {
            "task_id": "task_3",
            "bug_type": (
                "one of: crash | ui | performance | security "
                "| data_loss | compatibility"
            ),
            "priority": "one of: low | medium | high | critical",
            "assigned_developer": f"one of: {' | '.join(DEVELOPERS)}",
            "suggested_action": (
                "one of: fix_immediately | schedule_sprint "
                "| needs_more_info | wontfix | duplicate"
            ),
            "confidence": "optional float in [0.0, 1.0]",
            "reasoning": "optional string",
        },
    },
]


@app.get("/tasks")
def get_tasks() -> Dict[str, Any]:
    """Return available tasks and action schemas."""
    return {"tasks": TASKS_REGISTRY}


@app.post("/grader", response_model=GraderResponse)
def grader(body: GraderRequest) -> GraderResponse:
    """Return grader score [0.0, 1.0] for a completed episode."""
    result = env.grade_episode(
        episode_id=body.episode_id, task_id=body.task_id
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    score = result["score"]
    return GraderResponse(
        task_id=body.task_id,
        episode_id=body.episode_id,
        score=score,
        breakdown=result.get("breakdown", {}),
        passed=score >= 0.5,
    )


@app.post("/baseline", response_model=BaselineResponse)
def baseline() -> BaselineResponse:
    """Run baseline inference script against all tasks. Returns scores."""
    try:
        result = subprocess.run(
            [
                "python", "-m", "bug_triage_env.baseline",
                "--all-tasks", "--json", "--episodes", "3",
            ],
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ},
        )
        if result.returncode != 0:
            logger.error("baseline script error: %s", result.stderr)
            raise HTTPException(
                status_code=500,
                detail=f"Baseline script failed: {result.stderr[:300]}",
            )

        data = json.loads(result.stdout)
        return BaselineResponse(**data)

    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=504, detail="Baseline script timed out (>300s)"
        )
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500, detail=f"Baseline output parse error: {exc}"
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("/baseline error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
