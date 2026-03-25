<div align="center">

# Bug Triage OpenEnv

**A production-grade RL environment for automated software bug triage**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-e92063.svg)](https://docs.pydantic.dev/latest/)
[![OpenEnv](https://img.shields.io/badge/OpenEnv-compliant-brightgreen.svg)](https://github.com/OpenEnv-AI/openenv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Getting Started](#-getting-started) · [Tasks](#-tasks) · [API Reference](#-api-reference) · [Baseline](#-baseline-agent) · [Architecture](#-architecture) · [Deployment](#-deployment)

</div>

---

## Overview

**Bug Triage OpenEnv** simulates a real-world issue tracking system (like [Jira](https://www.atlassian.com/software/jira), [GitHub Issues](https://github.com/features/issues), or [Linear](https://linear.app)) where an AI agent must read incoming bug reports and make triage decisions:

1. **Classify** the bug type (crash, UI, security, etc.)
2. **Prioritize** the severity (low → critical)
3. **Route** to the right developer based on expertise
4. **Recommend** the appropriate action (fix immediately, schedule, etc.)

This environment is built for the [Meta × PyTorch Hackathon](https://pytorch.org/) using the [OpenEnv](https://github.com/OpenEnv-AI/openenv) framework, and is designed for training RL agents via [GRPO](https://arxiv.org/abs/2402.03300) (Group Relative Policy Optimization).

### Why Bug Triage?

| Real-World Impact | RL Suitability |
|---|---|
| Every software company triages 100s–1000s of bugs daily | Clear reward signal (correct vs incorrect triage) |
| Manual triage costs engineering hours | Partial credit for near-miss decisions |
| Misrouted bugs cause delays and outages | Increasing difficulty across 3 tasks |
| Ambiguous reports require reasoning | Rich text observations for LLM agents |

---

## Getting Started

### Prerequisites

- Python 3.10+
- [pip](https://pip.pypa.io/en/stable/) or [uv](https://github.com/astral-sh/uv)

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/bug-triage-env.git
cd bug-triage-env

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Quick Start

**1. Start the server:**

```bash
uvicorn bug_triage_env.server.app:app --host 0.0.0.0 --port 8000
```

**2. Verify it's running:**

```bash
curl http://localhost:8000/health
# → {"status": "healthy"}
```

**3. Run a full episode:**

```bash
# Reset (get a bug report)
curl -X POST http://localhost:8000/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "task_1"}'

# Step (submit your classification)
curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d '{"episode_id": "<id-from-reset>", "action": {"task_id": "task_1", "bug_type": "crash"}}'
```

**4. Use the Python client:**

```python
from bug_triage_env.client import BugTriageEnvClient
from bug_triage_env.models import BugTriageAction

with BugTriageEnvClient("http://localhost:8000") as env:
    obs = env.reset(task_id="task_3")
    action = BugTriageAction(
        task_id="task_3",
        bug_type="security",
        priority="critical",
        assigned_developer="Bob",
        suggested_action="fix_immediately",
    )
    result = env.step(obs["episode_id"], action)
    print(f"Score: {result['grader_score']}")  # 0.0 – 1.0
```

---

## Tasks

Three tasks of increasing difficulty, each with an automated grader returning scores in `[0.0, 1.0]`:

### Task 1: Bug Type Classification (Easy)

| | |
|---|---|
| **Goal** | Classify the bug into one of 6 categories |
| **Input** | Bug title, description, logs, environment |
| **Output** | `bug_type`: `crash` · `ui` · `performance` · `security` · `data_loss` · `compatibility` |
| **Scoring** | Exact match: `1.0`, Wrong: `0.0` |
| **Grader** | [`task1_grader.py`](bug_triage_env/graders/task1_grader.py) |

### Task 2: Priority Assignment (Medium)

| | |
|---|---|
| **Goal** | Assign the correct severity level |
| **Input** | Bug title, description, logs, environment |
| **Output** | `priority`: `low` · `medium` · `high` · `critical` |
| **Scoring** | Exact: `1.0`, 1-level off: `0.67`, 2-levels: `0.33`, 3-levels: `0.0` |
| **Grader** | [`task2_grader.py`](bug_triage_env/graders/task2_grader.py) |

### Task 3: Full Bug Triage (Hard)

| | |
|---|---|
| **Goal** | Complete triage: classify + prioritize + route + recommend action |
| **Output** | `bug_type` + `priority` + `assigned_developer` + `suggested_action` |
| **Developers** | `Alice` (crash/perf) · `Bob` (crash/security) · `Carol` (UI/compat) · `David` (security/data) · `Eve` (UI/perf/compat) |
| **Actions** | `fix_immediately` · `schedule_sprint` · `needs_more_info` · `wontfix` · `duplicate` |
| **Scoring** | Weighted composite — see [Reward Design](docs/REWARD_DESIGN.md) |
| **Grader** | [`task3_grader.py`](bug_triage_env/graders/task3_grader.py) |

> **Scoring Formula (Task 3):** `0.3 × type + 0.3 × priority + 0.2 × developer + 0.2 × action`

---

## API Reference

All endpoints follow the [OpenEnv specification](https://github.com/OpenEnv-AI/openenv).

### Standard OpenEnv Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | [`/health`](#get-health) | Liveness check |
| `POST` | [`/reset`](#post-reset) | Start a new episode |
| `POST` | [`/step`](#post-step) | Submit triage action |
| `GET` | [`/state`](#get-state) | Current episode metadata |

### Hackathon-Required Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | [`/tasks`](#get-tasks) | List all tasks + action schemas |
| `POST` | [`/grader`](#post-grader) | Grade a completed episode |
| `POST` | [`/baseline`](#post-baseline) | Run baseline inference |

---

### `GET /health`

```bash
curl http://localhost:8000/health
```

```json
{"status": "healthy"}
```

### `POST /reset`

Start a new episode. Returns an observation with a random bug report.

```bash
curl -X POST http://localhost:8000/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "task_1"}'
```

<details>
<summary>Response Schema</summary>

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
    "title": "Application crashes on login",
    "description": "...",
    "logs": "...",
    "environment": "macOS 14.2, Chrome 120",
    "reporter": "user_42",
    "created_at": "2024-01-15T09:30:00Z",
    "metadata": {}
  }
}
```

</details>

### `POST /step`

Submit a triage action. The episode ends immediately (single-step).

```bash
curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d '{
    "episode_id": "abc123",
    "action": {
      "task_id": "task_3",
      "bug_type": "crash",
      "priority": "critical",
      "assigned_developer": "Alice",
      "suggested_action": "fix_immediately"
    }
  }'
```

<details>
<summary>Response Schema</summary>

```json
{
  "done": true,
  "reward": 1.0,
  "grader_score": 1.0,
  "task_id": "task_3",
  "feedback": "Grader score: 1.00 | Bug type: ✓ | Priority: ✓ | Developer: ✓ | Action: ✓",
  "step_number": 1,
  "episode_id": "abc123"
}
```

</details>

### `GET /tasks`

```bash
curl http://localhost:8000/tasks
```

Returns all 3 tasks with their action schemas.

### `POST /grader`

```bash
curl -X POST http://localhost:8000/grader \
  -H "Content-Type: application/json" \
  -d '{"episode_id": "abc123", "task_id": "task_3"}'
```

```json
{
  "score": 0.8,
  "passed": true,
  "breakdown": {
    "bug_type_match": 1.0,
    "priority_match": 1.0,
    "developer_match": 0.0,
    "action_match": 1.0
  }
}
```

---

## Baseline Agent

The baseline supports two LLM providers with automatic fallback:

| Priority | Provider | Env Variable | Model |
|----------|----------|-------------|-------|
| 1 (primary) | [OpenAI](https://platform.openai.com/) | `OPENAI_API_KEY` | `gpt-4o-mini` |
| 2 (fallback) | [Google Gemini](https://ai.google.dev/gemini-api/docs) | `GEMINI_API_KEY` | `gemini-2.5-flash` |
| 3 (last resort) | Random | — | — |

### Running the Baseline

```bash
# Option A: OpenAI (spec-required)
export OPENAI_API_KEY="sk-..."
python -m bug_triage_env.baseline --all-tasks --episodes 5

# Option B: Gemini (free at https://aistudio.google.com/apikey)
export GEMINI_API_KEY="AI..."
python -m bug_triage_env.baseline --all-tasks --episodes 5

# Single task
python -m bug_triage_env.baseline --task task_1 --episodes 10

# JSON output for programmatic use
python -m bug_triage_env.baseline --all-tasks --json
```

### Baseline Results

| Task | Mean Score | Range | Description |
|------|-----------|-------|-------------|
| Task 1 | **0.80** | 0.00–1.00 | Bug type classification |
| Task 2 | **0.93** | 0.67–1.00 | Priority assignment |
| Task 3 | **0.78** | 0.60–1.00 | Full triage |
| **Overall** | **0.84** | | Weighted average |

> Without any API key, the baseline falls back to random actions (scores ~0.15).  
> Both providers include retry logic with exponential backoff for rate-limited API calls.

---

## Architecture

```
┌──────────────────────────────────────────┐
│              FastAPI Server              │
│  ┌────────┐  ┌────────┐  ┌───────────┐  │
│  │ /reset │  │ /step  │  │ /grader   │  │
│  └───┬────┘  └───┬────┘  └─────┬─────┘  │
│      │           │              │        │
│  ┌───▼───────────▼──────────────▼─────┐  │
│  │      BugTriageEnvironment          │  │
│  │  ┌──────────┐  ┌───────────────┐   │  │
│  │  │ Dataset  │  │ Episode Store │   │  │
│  │  │ 25 Bugs  │  │ (thread-safe) │   │  │
│  │  └──────────┘  └───────────────┘   │  │
│  └────────────────────┬───────────────┘  │
│                       │                  │
│  ┌────────────────────▼───────────────┐  │
│  │         Graders Registry           │  │
│  │  task1: exact match                │  │
│  │  task2: distance-based             │  │
│  │  task3: weighted composite         │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
         ▲                      ▲
         │ HTTP                 │ HTTP
    ┌────┴─────┐          ┌────┴──────────┐
    │  Client  │          │   Baseline    │
    │ (Python) │          │ OpenAI/Gemini │
    └──────────┘          └───────────────┘
```

### Observation Space

| Field | Type | Description |
|-------|------|-------------|
| `bug_report.title` | `str` | Short bug summary |
| `bug_report.description` | `str` | Detailed description |
| `bug_report.logs` | `str?` | Error logs / stack traces |
| `bug_report.environment` | `str?` | OS, browser, hardware |
| `bug_report.metadata` | `dict` | Extra context |
| `available_developers` | `list[str]` | 5 developer names |
| `done` | `bool` | Episode terminal state |
| `reward` | `float` | Training signal `[-0.5, 1.0]` |
| `grader_score` | `float?` | Evaluation score `[0.0, 1.0]` |

### Action Space

| Field | Task 1 | Task 2 | Task 3 |
|-------|--------|--------|--------|
| `bug_type` |  Required | — |  Required |
| `priority` | — |  Required |  Required |
| `assigned_developer` | — | — |  Required |
| `suggested_action` | — | — |  Required |
| `confidence` | Optional | Optional | Optional |
| `reasoning` | Optional | Optional | Optional |

### Reward Design

| Signal | Range | Purpose |
|--------|-------|---------|
| **Grader Score** | `[0.0, 1.0]` | Evaluation metric |
| **Shaped Reward** | `[-0.5, 1.0]` | Training signal for GRPO |
| **Calibration Bonus** | `[-0.15, +0.1]` | Confidence calibration reward |

> Formula: `reward = (grader_score × 1.5) - 0.5 + calibration_bonus`  
> This maps: score 0.0 → reward -0.5, score 0.33 → reward 0.0, score 1.0 → reward 1.0  
> See [docs/REWARD_DESIGN.md](docs/REWARD_DESIGN.md) for full details.

### Confidence Calibration (Novel Mechanic)

Agents can optionally provide a `confidence` score (0.0–1.0) alongside their triage decision. The environment rewards **well-calibrated** agents and penalizes **overconfident wrong** answers:

| Outcome | Confidence | Calibration Bonus | Why |
|---------|-----------|-------------------|-----|
| Correct + Confident | score≥0.8, conf≥0.8 | **+0.10** | Knows what it knows |
| Wrong + Overconfident | score<0.5, conf≥0.8 | **-0.15** | Dangerously wrong |
| Well-Calibrated | \|conf-score\|<0.2 | **+0.05** | Honest uncertainty |
| Poorly Calibrated | \|conf-score\|≥0.2 | **-0.05** | Miscalibrated |

This creates a genuine RL challenge: the agent must learn not just **what's correct**, but **when it's certain** — a critical skill for real-world deployment where overconfident wrong triage causes outages.

---

## Deployment

### Docker

```bash
# Build
docker build -t bug-triage-env .

# Run
docker run -d -p 8000:8000 -e OPENAI_API_KEY="sk-..." bug-triage-env

# Verify
curl http://localhost:8000/health
```

### Hugging Face Spaces

```bash
# Install OpenEnv CLI
pip install openenv

# Deploy
openenv push --repo-id <your-username>/bug-triage-env
```

---

## Project Structure

```
.
├── README.md                   ← You are here
├── Dockerfile                  ← Production container
├── openenv.yaml                ← OpenEnv manifest
├── pyproject.toml              ← Python package config
├── requirements.txt            ← Pinned dependencies
├── .dockerignore
│
├── bug_triage_env/             ← Main package
│   ├── __init__.py
│   ├── models.py               ← Typed Pydantic models
│   ├── client.py               ← Sync + Async HTTP clients
│   ├── baseline.py             ← OpenAI/Gemini inference
│   ├── data/
│   │   └── bugs.json           ← 25 real-world bug reports
│   ├── graders/
│   │   ├── task1_grader.py     ← Bug classification (exact match)
│   │   ├── task2_grader.py     ← Priority (distance-based)
│   │   └── task3_grader.py     ← Full triage (weighted composite)
│   └── server/
│       ├── environment.py      ← Core RL environment
│       └── app.py              ← FastAPI server
│
└── docs/
    ├── ARCHITECTURE.md
    ├── TASKS.md
    ├── REWARD_DESIGN.md
    └── IMPLEMENTATION_PLAN.md
```

---

## Testing

```bash
# Start the server
uvicorn bug_triage_env.server.app:app --port 8000 &

# Run all endpoint tests
curl http://localhost:8000/health                    # Health check
curl http://localhost:8000/tasks                     # List tasks
curl -X POST http://localhost:8000/reset \
  -d '{"task_id":"task_1"}'                          # Start episode
curl -X POST http://localhost:8000/step \
  -d '{"episode_id":"...", "action":{...}}'          # Submit action

# Run baseline (OpenAI or Gemini)
OPENAI_API_KEY="sk-..." python -m bug_triage_env.baseline --all-tasks
```

---

## References

- [OpenEnv Framework](https://github.com/OpenEnv-AI/openenv) — RL environment standard
- [Meta × PyTorch Hackathon](https://pytorch.org/) — Competition details
- [FastAPI Documentation](https://fastapi.tiangolo.com) — Web framework
- [Pydantic v2](https://docs.pydantic.dev/latest/) — Data validation
- [OpenAI API](https://platform.openai.com/docs) — Primary baseline LLM
- [Google Gemini API](https://ai.google.dev/gemini-api/docs) — Fallback baseline LLM
- [GRPO Paper](https://arxiv.org/abs/2402.03300) — Training algorithm
- [Hugging Face Spaces](https://huggingface.co/spaces) — Deployment platform

---

## License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

Built for the **Meta × PyTorch Hackathon**

[Back to Top](#bug-triage-openenv)

</div>
