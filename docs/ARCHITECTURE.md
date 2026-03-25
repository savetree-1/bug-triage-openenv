# ARCHITECTURE.md — Bug Triage OpenEnv System Architecture

---

## 1. Core Abstractions (OpenEnv Spec)

### Server-side (Docker)
```
BugTriageEnvironment(Environment)
├── reset(task_id)  →  BugTriageObservation   # New bug report episode
├── step(action)    →  BugTriageObservation   # Agent triages; grader fires; done=True
└── state @property →  BugTriageState         # Episode metadata
```

### Client-side (Training code)
```
BugTriageEnvClient
├── reset(task_id)  →  dict   # POST /reset
├── step(ep_id, action) → dict  # POST /step
└── state()  →  dict           # GET  /state
```

---

## 2. State Model

```python
class BugTriageState:
    episode_id: str         # Unique per episode
    step_count: int         # 0 after reset, 1 after step
    task_id: str            # "task_1" | "task_2" | "task_3"
    bug_id: str             # Which bug report is active
    cumulative_reward: float
```

---

## 3. Observation Model

```python
class BugTriageObservation:
    done: bool                        # True after step()
    reward: float                     # Shaped reward [-0.5, 1.0]
    task_id: str

    bug_report: BugReport             # Title, description, logs, env, reporter, metadata
    available_developers: List[str]   # ["Alice", "Bob", "Carol", "David", "Eve"]
    step_number: int
    feedback: str                     # Human-readable grader feedback
    grader_score: Optional[float]     # [0.0-1.0] — only when done=True
    episode_id: str
```

**BugReport fields the agent reads:**
| Field | Type | Example |
|-------|------|---------|
| title | str | "App crashes on iOS 17 uploading >50MB" |
| description | str | Full description with context |
| logs | str? | Stack traces, error output |
| environment | str? | "iOS 17.2, iPhone 15 Pro, App v3.2.1" |
| reporter | str? | "enterprise_client_a" |
| metadata | dict | `{"component": "file_upload", "affected_users": 847}` |

---

## 4. Action Model

```python
class BugTriageAction:
    task_id: str                                    # Required always

    # Task 1 (Easy)
    bug_type: Optional[str]                         # crash|ui|performance|security|data_loss|compatibility

    # Task 2 (Medium)
    priority: Optional[str]                         # low|medium|high|critical

    # Task 3 (Hard) — all of the above plus:
    assigned_developer: Optional[str]               # Alice|Bob|Carol|David|Eve
    suggested_action: Optional[str]                 # fix_immediately|schedule_sprint|needs_more_info|wontfix|duplicate
    reasoning: Optional[str]                        # Chain-of-thought (not graded)
```

---

## 5. Episode Flow

```
reset(task_id="task_1")
  │
  └── Returns BugTriageObservation:
        - bug_report = random bug from dataset (15 bugs)
        - done = False
        - episode_id = "abc123"

step(action=BugTriageAction(task_id="task_1", bug_type="crash"))
  │
  ├── Grader fires immediately (single-step episode)
  │     task1_grader.grade([action], ground_truth) → 1.0
  │
  └── Returns BugTriageObservation:
        - done = True
        - reward = 1.0 (shaped from grader score)
        - grader_score = 1.0
        - feedback = "Bug type: ✓ (predicted=crash, expected=crash)"
```

**Key design:** Episodes are **single-step** — agent reads bug, makes one decision, episode ends. This matches real-world triage (you don't re-classify the same bug iteratively).

---

## 6. File Layout

```
bug_triage_env/
├── __init__.py            ← Package exports
├── models.py              ← Pydantic typed Action/Observation/State
├── client.py              ← Sync + Async HTTP clients
├── baseline.py            ← OpenAI GPT-4o-mini inference script
├── openenv.yaml           ← Manifest
├── pyproject.toml
├── requirements.txt
│
├── data/
│   └── bugs.json          ← 15 real-world bug reports + ground truth
│
├── graders/
│   ├── __init__.py        ← GRADERS registry
│   ├── task1_grader.py    ← Bug type exact match [0/1]
│   ├── task2_grader.py    ← Priority distance scoring [0-1]
│   └── task3_grader.py    ← Weighted composite [0-1]
│
└── server/
    ├── __init__.py
    ├── environment.py     ← BugTriageEnvironment(Environment)
    ├── app.py             ← FastAPI (standard + hackathon endpoints)
    └── Dockerfile
```

---

## 7. API Endpoints

### Standard OpenEnv
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | → `{"status": "healthy"}` |
| POST | `/reset` | Body: `{"task_id": "task_1"}` → observation with bug report |
| POST | `/step` | Body: `{"episode_id": "...", "action": {...}}` → scored observation |
| GET | `/state` | → current episode metadata |
| GET | `/docs` | Swagger UI |

### Hackathon Required
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/tasks` | → 3 tasks with action schemas |
| POST | `/grader` | Body: `{"episode_id":"...","task_id":"task_1"}` → score [0.0-1.0] |
| POST | `/baseline` | Runs baseline.py → all task scores |

---

## 8. Developer Specialization Matrix

| Developer | Crash | UI | Perf | Security | Data Loss | Compat |
|-----------|-------|----|------|----------|-----------|--------|
| Alice | ✓ | | ✓ | | ✓ | |
| Bob | ✓ | | | ✓ | | |
| Carol | | ✓ | | | | ✓ |
| David | | | | ✓ | ✓ | |
| Eve | | ✓ | ✓ | | | ✓ |

This matrix is used by the Task 3 grader for **partial credit** on developer assignment — if the agent picks the wrong person but someone with the right specialization, it gets 0.5 instead of 0.0.

---

## 9. Scaling

| Deployment | Workers | Max Sessions |
|------------|---------|-------------|
| Local | 8 | ~2000 |
| HF Spaces Free | 2 | ~128 |
| HF Spaces Upgrade | 4-8 | ~512 |

Thread-safe: `BugTriageEnvironment` uses a `threading.Lock` for concurrent episode storage.
