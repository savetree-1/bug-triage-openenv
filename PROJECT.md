# PROJECT.md — OpenEnv Environment Project

## 🎯 Project Overview

**Environment Name:** `[ENV_NAME]`
**Domain:** `[DOMAIN]` _(e.g., Software Engineering / Finance / Healthcare / Legal)_
**Task Summary:** `[ONE_SENTENCE_DESCRIPTION_OF_REAL_WORLD_TASK]`

> ⚠️ This must be a **real-world task** — not a game or toy environment.

---

## 🔗 Official OpenEnv References (Always Follow)

| # | Tutorial |
|---|---------|
| 1 | [01-environments.md](https://github.com/meta-pytorch/OpenEnv/blob/main/tutorial/01-environments.md) |
| 2 | [02-deployment.md](https://github.com/meta-pytorch/OpenEnv/blob/main/tutorial/02-deployment.md) |
| 3 | [03-scaling.md](https://github.com/meta-pytorch/OpenEnv/blob/main/tutorial/03-scaling.md) |
| 4 | [04-training.md](https://github.com/meta-pytorch/OpenEnv/blob/main/tutorial/04-training.md) |

---

## 🚀 High-Level Pipeline

```
[REAL_WORLD_TASK / DATA_SOURCE]
          │
          ▼
OpenEnv Environment  (server/environment.py)
          │   FastAPI (server/app.py)  ←→  Docker
          ▼
HTTPEnvClient (client.py)
          │   reset() / step() / state()
          ▼
GRPO Training (TRL + vLLM)
          │
          ▼
Fine-tuned LLM → pushed to Hugging Face Hub
```

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Environment server | FastAPI + Uvicorn |
| Containerisation | Docker |
| Deployment | Hugging Face Spaces |
| Training framework | TRL (GRPOTrainer) |
| Model backend | vLLM (colocate mode) |
| Base model | `[BASE_MODEL]` _(e.g., Qwen/Qwen3-1.7B)_ |
| Package manager | `uv` |

---

## 📁 Repository Layout

```
[ENV_NAME]/
├── server/
│   ├── app.py            ← FastAPI entry point
│   ├── environment.py    ← Core environment logic
│   └── Dockerfile
├── models.py             ← Typed Action / Observation / State
├── client.py             ← HTTPEnvClient subclass
├── openenv.yaml          ← Manifest (required)
└── pyproject.toml
```

---

## ✅ Definition of Done

- [ ] `openenv init` scaffold created
- [ ] `models.py` — typed `Action`, `Observation`, `State` defined
- [ ] `environment.py` — `reset()`, `step()`, `state` implemented
- [ ] `server/app.py` — uses `create_fastapi_app(env)`
- [ ] `curl /health` → `{"status": "healthy"}`
- [ ] Docker image builds and runs locally
- [ ] Pushed to HF Spaces via `openenv push`
- [ ] GRPO training runs end-to-end
- [ ] Fine-tuned model pushed to HF Hub
- [ ] Evaluation metrics recorded
