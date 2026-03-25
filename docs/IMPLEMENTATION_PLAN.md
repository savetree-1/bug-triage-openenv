# IMPLEMENTATION_PLAN.md — Bug Triage Build Plan

> **Deadline:** April 7, 2026, 11:59 PM IST

---

## Build Status

| Component | File | Status |
|-----------|------|--------|
| Typed models | `models.py` |  Done |
| Bug dataset (15 reports) | `data/bugs.json` |  Done |
| Task 1 grader | `graders/task1_grader.py` |  Done |
| Task 2 grader | `graders/task2_grader.py` |  Done |
| Task 3 grader | `graders/task3_grader.py` |  Done |
| Environment | `server/environment.py` |  Done |
| FastAPI server | `server/app.py` |  Done |
| Client | `client.py` |  Done |
| Baseline script | `baseline.py` |  Done |
| Dockerfile | `server/Dockerfile` |  Done |
| openenv.yaml | `openenv.yaml` |  Done |
| requirements.txt | `requirements.txt` |  Done |
| pyproject.toml | `pyproject.toml` |  Done |

---

## Remaining: Test + Deploy

### Step 1 — Install dependencies
```bash
cd /Users/anks/Desktop/Meta-Pytorch-Hackathon
pip install -r bug_triage_env/requirements.txt
```

### Step 2 — Run server locally
```bash
uvicorn bug_triage_env.server.app:app --host 0.0.0.0 --port 8000 --reload
```

### Step 3 — Verify all endpoints
```bash
curl http://localhost:8000/health
curl http://localhost:8000/tasks
curl -X POST http://localhost:8000/reset -H "Content-Type: application/json" -d '{"task_id":"task_1"}'
```

### Step 4 — Run a full episode
```bash
# 1. Reset
EPISODE=$(curl -s -X POST http://localhost:8000/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id":"task_1"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['episode_id'])")

# 2. Step
curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d "{\"episode_id\":\"$EPISODE\",\"action\":{\"task_id\":\"task_1\",\"bug_type\":\"crash\"}}"
```

### Step 5 — Docker build + test
```bash
cd bug_triage_env
docker build -f server/Dockerfile -t bug-triage-env .
docker run -d -p 8000:8000 --name bug-triage-env bug-triage-env
curl http://localhost:8000/health
```

### Step 6 — Run baseline
```bash
export OPENAI_API_KEY="your-key"
python -m bug_triage_env.baseline --all-tasks --episodes 5
```

### Step 7 — Deploy to HF Spaces
```bash
openenv push --repo-id <hf-username>/bug-triage-env
```

### Step 8 — Submit
Paste HF Spaces URL before April 7, 11:59 PM IST.
