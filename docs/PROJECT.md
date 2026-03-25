# PROJECT.md — Bug Triage OpenEnv Environment

> **Round 1 opens:** April 1, 2026 | **Deadline:** April 7, 2026, 11:59 PM IST

---

## Problem Statement

Software teams receive hundreds of bug reports daily. Manually triaging each report —
classifying the bug type, assigning a priority level, routing to the right developer,
and deciding the appropriate action — is slow, error-prone, and a significant cost
to engineering velocity.

**This environment** trains an LLM agent to perform **automated bug triage** at
production scale, simulating real-world issue tracking systems like Jira and GitHub
Issues. The agent reads raw bug reports (title, description, stack traces, metadata)
and must classify, prioritize, and route each issue accurately.

---

## Real-World Relevance

| Dimension | Detail |
|-----------|--------|
| **Domain** | Software Engineering / DevOps / Issue Tracking |
| **Industry use** | Every software company with a bug tracker (GitHub Issues, Jira, Linear, etc.) |
| **Scale** | Large teams process 100–500+ bug reports per week |
| **Cost of wrong triage** | Critical bugs missed → outages; low-priority spamming senior devs → waste |
| **Current solutions** | Manual labels, basic keyword rules, ML classifiers (limited context) |
| **LLM advantage** | Can reason over free-text descriptions, logs, and metadata together |

---

## Users

| User | Need |
|------|------|
| **Developers** | Only receive bugs relevant to their specialization |
| **QA Engineers** | Know which bugs to test first (priority-ordered) |
| **Project Managers** | Accurate sprint planning based on classified backlogs |
| **Engineering Leads** | Automated triage frees team from manual label overhead |

---

## Example Scenario

```
Bug Reported:
  Title:       "App crashes on iOS 17 when uploading files > 50MB"
  Description: "Consistently crashes immediately on upload tap. Blocking 
                3 enterprise customers."
  Logs:        "FATAL: EXC_BAD_ACCESS KERN_INVALID_ADDRESS 0x0000000000000000
                Stack: FileUploadManager.upload(url:size:)"
  Environment: "iOS 17.2, iPhone 15 Pro, App v3.2.1"

Agent Must Output:
  bug_type:           crash          ← Task 1
  priority:           critical       ← Task 2
  assigned_developer: Alice          ← Task 3 (crash specialist)
  suggested_action:   fix_immediately ← Task 3
```

---

## Real-World Constraints the Agent Must Handle

- **Ambiguous descriptions** — reporters with varying technical skill
- **Incomplete logs** — stack traces cut off or missing
- **Priority inflation** — reporters who label everything as "critical"
- **Routing uncertainty** — cross-cutting bugs (e.g., security + crash)
- **Missing environment info** — agent must infer from context

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Environment server | FastAPI + Uvicorn |
| Containerisation | Docker |
| Deployment | Hugging Face Spaces |
| Training | TRL GRPOTrainer + vLLM |
| Base model | Qwen/Qwen3-1.7B |
| Package manager | uv |
| Validation | Pydantic v2 |
| Baseline LLM | OpenAI GPT-4o-mini (via `OPENAI_API_KEY`) |

---

## Repository Layout

```
bug_triage_env/
├── models.py             ← Pydantic-typed Action / Observation / State
├── client.py             ← HTTP client for training code
├── baseline.py           ← OpenAI-backed inference script
├── openenv.yaml          ← Manifest
├── pyproject.toml
├── requirements.txt
├── data/
│   └── bugs.json         ← 15 diverse real-world bug reports
├── graders/
│   ├── task1_grader.py   ← Bug type classification [0.0–1.0]
│   ├── task2_grader.py   ← Priority assignment [0.0–1.0]
│   └── task3_grader.py   ← Full triage [0.0–1.0]
└── server/
    ├── environment.py    ← OpenEnv Environment ABC implementation
    ├── app.py            ← FastAPI (standard + hackathon endpoints)
    └── Dockerfile
```

---

## Hackathon Compliance Checklist

| Requirement | Status |
|-------------|--------|
| HF Space deploys + `/reset` returns 200 | ☐ |
| `openenv.yaml` present | ☐ |
| Typed models (`Action`, `Observation`, `State`) | ☐ |
| `step()` / `reset()` / `state()` implemented | ☐ |
| Dockerfile builds | ☐ |
| `/tasks` — task list + action schema | ☐ |
| `/grader` — score in `[0.0, 1.0]` | ☐ |
| `/baseline` — OpenAI inference, all 3 tasks | ☐ |
| 3+ graded tasks with varying scores | ☐ |
| `baseline.py` runs without error | ☐ |
