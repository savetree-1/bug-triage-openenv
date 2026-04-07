---
title: Bug Triage OpenEnv
emoji: 🐛
colorFrom: red
colorTo: yellow
sdk: docker
app_port: 8000
tags:
  - openenv
---

# Bug Triage OpenEnv

A production-grade reinforcement learning environment for automated software bug triage, built on the [OpenEnv](https://github.com/OpenEnv-AI/openenv) framework.

| | |
|---|---|
| **Live Space** | [huggingface.co/spaces/savetrees/bug-triage-openenv](https://huggingface.co/spaces/savetrees/bug-triage-openenv) |
| **Repository** | [github.com/savetree-1/bug-triage-openenv](https://github.com/savetree-1/bug-triage-openenv) |
| **Framework** | [FastAPI](https://fastapi.tiangolo.com) + [Pydantic v2](https://docs.pydantic.dev/latest/) |
| **License** | MIT |

---

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Tasks](#tasks)
- [API Reference](#api-reference)
- [Observation Space](#observation-space)
- [Action Space](#action-space)
- [Reward Design](#reward-design)
- [Baseline Agent](#baseline-agent)
- [Architecture](#architecture)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [References](#references)

---

## Overview

**Bug Triage OpenEnv** simulates a real-world issue tracking system (comparable to [Jira](https://www.atlassian.com/software/jira), [GitHub Issues](https://github.com/features/issues), or [Linear](https://linear.app)) where an AI agent must read incoming bug reports and make triage decisions:

1. **Classify** the bug type (crash, UI, security, performance, data loss, compatibility)
2. **Prioritize** the severity (low, medium, high, critical)
3. **Route** to the correct developer based on their domain expertise
4. **Recommend** the appropriate action (fix immediately, schedule for sprint, etc.)

The environment includes 25 carefully crafted bug reports drawn from real-world software engineering workflows, each designed to test different reasoning capabilities of frontier language models.

### Motivation

| Problem | Why It Matters |
|---|---|
| Every software company triages hundreds to thousands of bugs daily | High-volume, repetitive task ideal for automation |
| Manual triage costs senior engineering hours | Direct cost savings from accurate automation |
| Misrouted bugs cause cascading delays and outages | Incorrect triage has measurable downstream impact |
| Ambiguous bug reports require deep contextual reasoning | LLM agents must parse unstructured text and infer intent |

This environment was built for the [Meta x PyTorch Hackathon](https://pytorch.org/) and is designed for training RL agents via [GRPO](https://arxiv.org/abs/2402.03300) (Group Relative Policy Optimization).

---

## Getting Started

### Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/)
- [Docker](https://docs.docker.com/get-docker/) (optional, for containerized deployment)

### Installation

```bash
git clone https://github.com/savetree-1/bug-triage-openenv.git
cd bug-triage-openenv

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

### Quick Start

Start the server:

```bash
uvicorn bug_triage_env.server.app:app --host 0.0.0.0 --port 8000
```

Verify that the server is running:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status": "healthy"}
```

Run a complete episode (reset, then step):

```bash
curl -X POST http://localhost:8000/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "task_1"}'
```

Submit a triage action using the `episode_id` returned from `/reset`:

```bash
curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d '{"episode_id": "<episode_id>", "action": {"task_id": "task_1", "bug_type": "crash"}}'
```

### Python Client

A synchronous and asynchronous client is provided for programmatic access:

```python
from bug_triage_env.client import BugTriageEnvClient
from bug_triage_env.models import BugTriageAction

with BugTriageEnvClient("http://localhost:8000") as client:
    obs = client.reset(task_id="task_3")

    action = BugTriageAction(
        task_id="task_3",
        bug_type="security",
        priority="critical",
        assigned_developer="Bob",
        suggested_action="fix_immediately",
    )

    result = client.step(obs["episode_id"], action)
    print(f"Grader score: {result['grader_score']}")
```

---

## Tasks

The environment defines three tasks of increasing difficulty. Each task has a deterministic grader that returns a score in the range `[0.0, 1.0]`.

### Task 1: Bug Type Classification (Easy)

Given a bug report, classify it into one of six categories.

| Property | Value |
|---|---|
| Input | Bug title, description, logs, environment metadata |
| Output | `bug_type`: one of `crash`, `ui`, `performance`, `security`, `data_loss`, `compatibility` |
| Scoring | Exact match = 1.0; incorrect = 0.0 |
| Grader | [task1_grader.py](bug_triage_env/graders/task1_grader.py) |

### Task 2: Priority Assignment (Medium)

Given a bug report, assign the correct severity level.

| Property | Value |
|---|---|
| Input | Bug title, description, logs, environment metadata |
| Output | `priority`: one of `low`, `medium`, `high`, `critical` |
| Scoring | Exact = 1.0; 1 level off = 0.67; 2 levels = 0.33; 3 levels = 0.0 |
| Grader | [task2_grader.py](bug_triage_env/graders/task2_grader.py) |

### Task 3: Full Bug Triage (Hard)

Perform complete triage: classify the bug type, assign priority, route to the correct developer, and recommend an action.

| Property | Value |
|---|---|
| Output | `bug_type` + `priority` + `assigned_developer` + `suggested_action` |
| Developers | Alice (crash, performance), Bob (crash, security), Carol (UI, compatibility), David (security, data loss), Eve (UI, performance, compatibility) |
| Actions | `fix_immediately`, `schedule_sprint`, `needs_more_info`, `wontfix`, `duplicate` |
| Scoring | Weighted composite: `0.3 * type + 0.3 * priority + 0.2 * developer + 0.2 * action` |
| Grader | [task3_grader.py](bug_triage_env/graders/task3_grader.py) |

---

## API Reference

All endpoints conform to the [OpenEnv specification](https://github.com/OpenEnv-AI/openenv).

### Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness probe. Returns `{"status": "healthy"}`. |
| `POST` | `/reset` | Start a new episode. Accepts optional `{"task_id": "task_1"}`. Returns an observation containing a bug report. |
| `POST` | `/step` | Submit a triage action. Requires `episode_id` and `action`. Returns observation with reward and grader score. |
| `GET` | `/state` | Returns metadata about active episodes. |
| `GET` | `/tasks` | Lists all available tasks with their action schemas. |
| `POST` | `/grader` | Re-grade a completed episode. Requires `episode_id` and `task_id`. |
| `POST` | `/baseline` | Trigger baseline inference (requires `OPENAI_API_KEY` or `GEMINI_API_KEY`). |
| `GET` | `/docs` | Auto-generated [Swagger UI](https://swagger.io/tools/swagger-ui/) documentation. |

### POST /reset

Request:

```json
{"task_id": "task_1"}
```

Response (abbreviated):

```json
{
  "done": false,
  "reward": 0.0,
  "task_id": "task_1",
  "episode_id": "abc123",
  "step_number": 0,
  "feedback": "New bug report received. Please triage.",
  "available_developers": ["Alice", "Bob", "Carol", "David", "Eve"],
  "bug_report": {
    "bug_id": "BUG-001",
    "title": "Application crashes on login with SSO enabled",
    "description": "...",
    "logs": "...",
    "environment": "macOS 14.2, Chrome 120",
    "reporter": "user_42",
    "created_at": "2024-01-15T09:30:00Z",
    "metadata": {}
  }
}
```

### POST /step

Request:

```json
{
  "episode_id": "abc123",
  "action": {
    "task_id": "task_3",
    "bug_type": "crash",
    "priority": "critical",
    "assigned_developer": "Alice",
    "suggested_action": "fix_immediately"
  }
}
```

Response:

```json
{
  "done": true,
  "reward": 1.0,
  "grader_score": 1.0,
  "task_id": "task_3",
  "feedback": "Grader score: 1.00 | Bug type: correct | Priority: correct | Developer: correct | Action: correct",
  "step_number": 1,
  "episode_id": "abc123"
}
```

---

## Observation Space

Each observation returned by `/reset` and `/step` contains the following fields:

| Field | Type | Description |
|---|---|---|
| `bug_report.bug_id` | string | Unique bug identifier (e.g., `BUG-001`) |
| `bug_report.title` | string | Short summary of the bug |
| `bug_report.description` | string | Detailed description of the issue |
| `bug_report.logs` | string or null | Error logs, stack traces, or crash output |
| `bug_report.environment` | string or null | OS, browser, hardware, and version details |
| `bug_report.reporter` | string | Username of the person who filed the bug |
| `bug_report.created_at` | string | ISO 8601 timestamp |
| `bug_report.metadata` | object | Additional context (component, affected users, regression flag) |
| `available_developers` | array of strings | The 5 developers available for routing |
| `done` | boolean | Whether the episode has ended |
| `reward` | float | Shaped reward signal for RL training |
| `grader_score` | float or null | Raw evaluation score in `[0.0, 1.0]` (null before stepping) |
| `episode_id` | string | Unique episode identifier |
| `step_number` | integer | Current step count (0 after reset, 1 after step) |
| `feedback` | string | Human-readable feedback about the triage result |

---

## Action Space

Actions are submitted as JSON objects to the `/step` endpoint. Required fields vary by task:

| Field | Type | Task 1 | Task 2 | Task 3 |
|---|---|---|---|---|
| `task_id` | string | Required | Required | Required |
| `bug_type` | string | Required | -- | Required |
| `priority` | string | -- | Required | Required |
| `assigned_developer` | string | -- | -- | Required |
| `suggested_action` | string | -- | -- | Required |
| `confidence` | float (0.0-1.0) | Optional | Optional | Optional |
| `reasoning` | string | Optional | Optional | Optional |

Valid values:

- **bug_type**: `crash`, `ui`, `performance`, `security`, `data_loss`, `compatibility`
- **priority**: `low`, `medium`, `high`, `critical`
- **assigned_developer**: `Alice`, `Bob`, `Carol`, `David`, `Eve`
- **suggested_action**: `fix_immediately`, `schedule_sprint`, `needs_more_info`, `wontfix`, `duplicate`

---

## Reward Design

The environment provides two distinct signals:

| Signal | Range | Purpose |
|---|---|---|
| **Grader Score** | `[0.0, 1.0]` | Deterministic evaluation metric for benchmarking |
| **Shaped Reward** | `[-0.5, 1.0]` | Continuous training signal optimized for [GRPO](https://arxiv.org/abs/2402.03300) |

The shaped reward is derived from the grader score using the following formula:

```
reward = (grader_score * 1.5) - 0.5 + calibration_bonus
```

This mapping ensures:
- A score of 0.0 produces a reward of -0.5 (penalizes random guessing)
- A score of 0.33 produces a reward of 0.0 (breakeven point)
- A score of 1.0 produces a reward of 1.0 (maximum)

### Confidence Calibration

Agents may optionally submit a `confidence` value (float between 0.0 and 1.0) with their action. The environment applies a calibration bonus or penalty based on how well the agent's confidence aligns with its actual performance:

| Condition | Bonus | Description |
|---|---|---|
| Correct and confident (score >= 0.8, confidence >= 0.8) | +0.10 | Rewards agents that are confident and right |
| Wrong and overconfident (score < 0.5, confidence >= 0.8) | -0.15 | Penalizes dangerous overconfidence |
| Well-calibrated (absolute difference < 0.2) | +0.05 | Rewards honest uncertainty estimation |
| Poorly calibrated (absolute difference >= 0.2) | -0.05 | Penalizes miscalibrated confidence |

This mechanic introduces a genuine RL challenge: the agent must learn not only what is correct, but also when it is certain. In production bug triage, overconfident misrouting of a critical outage has severe downstream consequences.

---

## Baseline Agent

The baseline inference script supports two LLM providers with automatic fallback:

| Priority | Provider | Environment Variable | Default Model |
|---|---|---|---|
| Primary | [OpenAI](https://platform.openai.com/docs) | `OPENAI_API_KEY` | gpt-4o-mini |
| Fallback | [Google Gemini](https://ai.google.dev/gemini-api/docs) | `GEMINI_API_KEY` | gemini-2.5-flash |
| Last resort | Random | -- | Random valid action |

Both providers implement exponential backoff with retry logic for HTTP 429 (rate limit) and 503 (service unavailable) responses.

### Running the Baseline

```bash
# Using OpenAI (required by hackathon spec)
export OPENAI_API_KEY="sk-..."
python -m bug_triage_env.baseline --all-tasks --episodes 5

# Using Gemini (free tier available at https://aistudio.google.com/apikey)
export GEMINI_API_KEY="AI..."
python -m bug_triage_env.baseline --all-tasks --episodes 5

# Single task with more episodes
python -m bug_triage_env.baseline --task task_1 --episodes 10

# JSON output
python -m bug_triage_env.baseline --all-tasks --json
```

### Baseline Scores

| Task | Mean Score | Range | Description |
|---|---|---|---|
| Task 1 (Easy) | 0.80 | 0.00 - 1.00 | Bug type classification |
| Task 2 (Medium) | 0.93 | 0.67 - 1.00 | Priority assignment |
| Task 3 (Hard) | 0.78 | 0.60 - 1.00 | Full triage pipeline |
| **Overall** | **0.84** | | Weighted average across all tasks |

Without any API key configured, the baseline falls back to random actions and achieves an average score of approximately 0.15.

### Hackathon Inference Script

The root-level [`inference.py`](inference.py) is the hackathon-mandated entry point. It:

- Uses the [OpenAI Python client](https://github.com/openai/openai-python) exclusively
- Reads `API_BASE_URL`, `MODEL_NAME`, and `HF_TOKEN` from the environment
- Emits structured `[START]`, `[STEP]`, and `[END]` logs to stdout
- Completes in under 20 minutes on 2 vCPU / 8 GB RAM

---

## Architecture

```
+------------------------------------------+
|              FastAPI Server              |
|  +--------+  +--------+  +-----------+  |
|  | /reset |  | /step  |  | /grader   |  |
|  +---+----+  +---+----+  +-----+-----+  |
|      |           |              |        |
|  +---v-----------v--------------v-----+  |
|  |      BugTriageEnvironment          |  |
|  |  +----------+  +---------------+   |  |
|  |  | Dataset  |  | Episode Store |   |  |
|  |  | 25 Bugs  |  | (thread-safe) |   |  |
|  |  +----------+  +---------------+   |  |
|  +--------------------+---------------+  |
|                       |                  |
|  +--------------------v---------------+  |
|  |         Graders Registry           |  |
|  |  task1: exact match                |  |
|  |  task2: distance penalty           |  |
|  |  task3: weighted composite         |  |
|  +------------------------------------+  |
+------------------------------------------+
         ^                      ^
         | HTTP                 | HTTP
    +----+-----+          +----+----------+
    |  Client  |          |   Baseline    |
    | (Python) |          | OpenAI/Gemini |
    +----------+          +---------------+
```

Key implementation details:

- **Thread safety**: The episode store uses Python `threading.Lock` to support concurrent requests from multiple agents.
- **Single-step episodes**: Each episode consists of one reset (observation) and one step (action). The episode terminates immediately after the step.
- **Deterministic grading**: All three graders produce identical scores for identical inputs. No randomness is involved in evaluation.
- **Dataset**: 25 bug reports stored in [`bugs.json`](bug_triage_env/data/bugs.json), covering crash reports, security vulnerabilities, performance regressions, UI glitches, data corruption, and compatibility issues.

---

## Deployment

### Docker

```bash
docker build -t bug-triage-env .

docker run -d -p 8000:8000 \
  -e OPENAI_API_KEY="sk-..." \
  bug-triage-env

curl http://localhost:8000/health
```

The Dockerfile uses Python 3.11-slim, installs only production dependencies, and includes a built-in health check.

### Hugging Face Spaces

The environment is deployed as a Docker-based [Hugging Face Space](https://huggingface.co/docs/hub/spaces):

```bash
pip install huggingface_hub
python3 -c "
from huggingface_hub import HfApi
api = HfApi()
api.create_repo(repo_id='<username>/bug-triage-openenv', repo_type='space', space_sdk='docker', exist_ok=True)
api.upload_folder(folder_path='.', repo_id='<username>/bug-triage-openenv', repo_type='space')
"
```

The live deployment is accessible at:
**[https://huggingface.co/spaces/savetrees/bug-triage-openenv](https://huggingface.co/spaces/savetrees/bug-triage-openenv)**

---

## Project Structure

```
bug-triage-openenv/
|-- README.md                    Documentation
|-- Dockerfile                   Production container (Python 3.11-slim)
|-- openenv.yaml                 OpenEnv environment manifest
|-- inference.py                 Hackathon inference entry point
|-- pyproject.toml               Python package configuration
|-- requirements.txt             Pinned production dependencies
|-- .dockerignore                Files excluded from Docker build
|-- .gitignore                   Files excluded from version control
|
|-- bug_triage_env/              Main Python package
|   |-- __init__.py              Package initialization
|   |-- models.py                Pydantic v2 data models (Action, Observation, State)
|   |-- client.py                Synchronous and asynchronous HTTP client
|   |-- baseline.py              Dual-provider LLM baseline (OpenAI + Gemini)
|   |
|   |-- data/
|   |   |-- __init__.py          Dataset loader
|   |   |-- bugs.json            25 curated real-world bug reports
|   |
|   |-- graders/
|   |   |-- __init__.py          Grader registry
|   |   |-- task1_grader.py      Bug classification grader (exact match)
|   |   |-- task2_grader.py      Priority assignment grader (distance penalty)
|   |   |-- task3_grader.py      Full triage grader (weighted composite)
|   |
|   |-- server/
|       |-- __init__.py          Server package initialization
|       |-- app.py               FastAPI application with all 8 endpoints
|       |-- environment.py       Core RL environment (reset, step, state)
```

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | For baseline | (none) | [OpenAI API key](https://platform.openai.com/api-keys) for primary baseline inference |
| `GEMINI_API_KEY` | For fallback | (none) | [Google Gemini API key](https://aistudio.google.com/apikey) for fallback inference |
| `API_BASE_URL` | For hackathon | `https://api.openai.com/v1` | LLM API endpoint (used by `inference.py`) |
| `MODEL_NAME` | For hackathon | `gpt-4o-mini` | Model identifier (used by `inference.py`) |
| `HF_TOKEN` | For hackathon | (none) | Hugging Face token (used by `inference.py`) |
| `PORT` | No | `8000` | Server port |
| `HOST` | No | `0.0.0.0` | Server bind address |
| `WORKERS` | No | `4` | Number of Uvicorn worker processes |

---

## References

- [OpenEnv Framework](https://github.com/OpenEnv-AI/openenv) -- Standardized RL environment specification
- [FastAPI](https://fastapi.tiangolo.com) -- High-performance Python web framework
- [Pydantic v2](https://docs.pydantic.dev/latest/) -- Data validation using Python type annotations
- [OpenAI API](https://platform.openai.com/docs) -- Primary LLM provider for baseline inference
- [Google Gemini API](https://ai.google.dev/gemini-api/docs) -- Fallback LLM provider
- [GRPO (Group Relative Policy Optimization)](https://arxiv.org/abs/2402.03300) -- RL training algorithm
- [Hugging Face Spaces](https://huggingface.co/docs/hub/spaces) -- Deployment platform for ML applications
- [Docker](https://docs.docker.com/) -- Containerization platform

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
