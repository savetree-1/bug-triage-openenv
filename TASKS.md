# TASKS.md — Environment Task Definition

> Senior OpenEnv Engineer Rule: **Real-world task. No toys. No games.**

---

## 🎯 Chosen Environment: Code Review Environment

**Name:** `code_review_env`  
**Domain:** Software Engineering / Developer Tooling  
**Task:** The agent acts as a code reviewer. Given a code diff or snippet, the agent must produce a structured, high-quality review identifying bugs, style issues, and improvement suggestions.

---

## Why This Is Real-World ✅
- Code review is a high-value, daily engineering task
- Clear, measurable correctness signals (bug found / not found, severity match)
- Rich feedback loop: agent learns what good reviews look like
- Direct production utility — can be deployed in CI/CD pipelines

---

## Episode Structure

```
reset()
  │
  └── Agent receives: code snippet + task context
        (e.g., language, PR description, critical path flag)

step(action)
  │
  └── Agent sends: structured review
        (issues: List[Issue], summary: str, severity: Severity)

  └── Environment returns:
        reward (float), feedback (str), done (bool)
```

---

## Action Space

```python
@dataclass
class CodeReviewAction(Action):
    issues: List[str]          # List of identified issues
    summary: str               # Overall review summary
    severity: str              # "low" | "medium" | "high" | "critical"
    metadata: Dict[str, Any]   # Optional extra context
```

---

## Observation Space

```python
@dataclass
class CodeReviewObservation(Observation):
    done: bool
    reward: float
    code_snippet: str          # Code to review (current step)
    language: str              # e.g., "python", "javascript"
    context: str               # PR description or task context
    ground_truth_issues: List[str]   # Hidden during training rollout
    feedback: str              # Human-readable feedback on last action
    step_number: int
```

---

## State

```python
@dataclass
class CodeReviewState(State):
    episode_id: Optional[str]
    step_count: int
    total_snippets: int        # How many snippets in this episode
    cumulative_reward: float
    language: str
```

---

## Episode Flow

| Step | Agent Receives | Agent Sends | Env Returns |
|------|---------------|-------------|-------------|
| 1    | Code snippet #1 + context | Structured review | Reward + feedback |
| 2    | Code snippet #2 (harder) | Structured review | Reward + feedback |
| … | … | … | … |
| N    | Final snippet | Final review | Terminal reward, done=True |

---

## Data Sources
- [CodeSearchNet](https://github.com/github/CodeSearchNet) — multi-language code samples
- Synthetic bug injection (off-by-one, null dereference, SQL injection, etc.)
- Human-curated review gold standards (severity labels)

---

## Difficulty Levels
| Level | Description |
|-------|-------------|
| Easy | Obvious syntax error or unused variable |
| Medium | Logic bug, missing edge case handling |
| Hard | Security vulnerability, concurrency issue |
| Critical | Data corruption / memory leak pattern |
