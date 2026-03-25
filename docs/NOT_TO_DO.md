# NOT_TO_DO.md — Bug Triage Environment Anti-Patterns

>  Violations here = disqualification or severe score penalty.

---

## Disqualification Risks

1. **Hardcoded grader scores** — Grader must evaluate actual agent output against ground truth. If every episode returns the same score, DQ.
2. **Missing endpoints** — `/tasks`, `/grader`, `/baseline` are mandatory hackathon endpoints. Missing any = DQ.
3. **Non-running baseline** — `baseline.py` must execute without error. If it crashes on import or at runtime = DQ.
4. **Docker build failure** — `Dockerfile` must build cleanly. Always test `docker build` before submission.
5. **`/reset` returns error** — This is the first thing evaluators test.

---

## Technical Anti-Patterns

| Don't | Why | Do Instead |
|-------|-----|-----------|
| Expose `ground_truth` in observation | Agent sees answers → invalid training | Only return bug report fields |
| Use hardcoded bug selection | Same bug every episode → DQ | `random.choice(self._bugs)` |
| Return reward outside [-0.5, 1.0] | Breaks GRPO training stability | Clamp: `max(-0.5, min(1.0, reward))` |
| Grader score outside [0.0, 1.0] | Violates spec | `max(0.0, min(1.0, score))` |
| Skip Pydantic validation | Runtime crashes in production | All models use `BaseModel` |
| Use mutable default args | Shared state bugs | `Field(default_factory=...)` |
| Forget `model_config = {"use_enum_values": True}` | Enums serialize as objects instead of strings | Set on BugTriageAction |

---

## Bug Triage Specific Don'ts

| Don't | Why |
|-------|-----|
| Accept any string for `bug_type` | Use `BugType` enum — only 6 valid values |
| Accept any developer name | Validate against `DEVELOPERS` list |
| Mix up reward vs grader | Reward = training signal. Grader = eval score. Different ranges. |
| Build a classifier model | We're building an RL *environment*, not a model |
| Train during hackathon eval | Environment must serve episodes, not train |

---

## Pre-Submission Validation (Run Before Submitting)

```bash
# 1. Health check
curl http://localhost:8000/health
# → {"status":"healthy"}

# 2. Reset all 3 tasks
curl -X POST http://localhost:8000/reset -d '{"task_id":"task_1"}'
curl -X POST http://localhost:8000/reset -d '{"task_id":"task_2"}'
curl -X POST http://localhost:8000/reset -d '{"task_id":"task_3"}'

# 3. Tasks endpoint
curl http://localhost:8000/tasks
# → 3 tasks with action schemas

# 4. Full episode (reset → step → grader)
EP=$(curl -s -X POST http://localhost:8000/reset -d '{"task_id":"task_1"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['episode_id'])")
curl -X POST http://localhost:8000/step -d "{\"episode_id\":\"$EP\",\"action\":{\"task_id\":\"task_1\",\"bug_type\":\"crash\"}}"
curl -X POST http://localhost:8000/grader -d "{\"episode_id\":\"$EP\",\"task_id\":\"task_1\"}"

# 5. Baseline
GEMINI_API_KEY="..." python -m bug_triage_env.baseline --all-tasks --episodes 3

# 6. Docker build
docker build -f bug_triage_env/server/Dockerfile -t bug-triage-env .
docker run -d -p 8000:8000 bug-triage-env
curl http://localhost:8000/health
```
