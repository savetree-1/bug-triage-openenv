# ROLES.md — Team Roles & Responsibilities

---

## Role Definitions

### Environment Engineer
**Owns:** `server/environment.py`, `models.py`, data pipeline
- Implements `reset()`, `step()`, `state` following OpenEnv ABC
- Defines typed `Action`, `Observation`, `State` dataclasses
- Writes ground-truth data loader and reward computation logic
- Ensures `step()` is stateless-safe for concurrent sessions
- Writes unit tests for environment logic

### API / Infra Engineer
**Owns:** `server/app.py`, `server/Dockerfile`, `openenv.yaml`, `pyproject.toml`
- Wires `create_fastapi_app(env)` correctly
- Configures Dockerfile for `uvicorn` with `WORKERS`, `PORT` env vars
- Manages HF Spaces deployment (`openenv push`)
- Validates `/health`, `/reset`, `/step`, `/state` endpoints
- Configures scaling (workers, MAX_CONCURRENT_ENVS)

### Client Engineer
**Owns:** `client.py`
- Implements `HTTPEnvClient` subclass
- Implements `_step_payload()`, `_parse_result()`, `_parse_state()`
- Writes async and sync usage examples
- Ensures client works against both local Docker and HF Spaces URL

### Training Engineer
**Owns:** `train.py` / Colab notebook, `GRPOConfig`, rollout function
- Writes `rollout_func` that calls `env.reset()` + `env.step()` in loop
- Defines `GRPOConfig` (learning rate, batch size, vLLM settings)
- Registers all reward functions with `GRPOTrainer`
- Monitors training via trackio
- Pushes fine-tuned model to HF Hub

### Reward Designer
**Owns:** `REWARD_DESIGN.md`, reward function implementations
- Designs decomposed, float-returning reward functions
- Works with Environment Engineer to embed reward signals in `step()`
- Validates reward signal is non-sparse and well-shaped
- Documents reward composition and rationale

### QA / Evaluation Engineer
**Owns:** evaluation scripts, metrics
- Validates environment correctness (does `step()` behave deterministically?)
- Runs baseline policies to sanity-check reward range
- Evaluates fine-tuned model on held-out evaluation set
- Produces final metrics for hackathon submission

---

## Collaboration Rules
- All code must follow OpenEnv 5-step pattern (see ARCHITECTURE.md)
- No deviation from `step()` / `reset()` / `state` interface
- All reward functions must return `List[float]` for GRPOTrainer compatibility
- Docker image must pass `curl /health` before any deployment PR is merged
- HF Space URL must be live before training begins
