# OpenEnv Project Context

You must ALWAYS follow official OpenEnv references: And clone

1. https://github.com/meta-pytorch/OpenEnv/blob/main/tutorial/01-environments.md
2. https://github.com/meta-pytorch/OpenEnv/blob/main/tutorial/02-deployment.md
3. https://github.com/meta-pytorch/OpenEnv/blob/main/tutorial/03-scaling.md
4. https://github.com/meta-pytorch/OpenEnv/blob/main/tutorial/04-training.md

Rules:
- Follow OpenEnv spec strictly
- Use step(), reset(), state()
- Use typed models (Observation, Action, Reward)
- Ensure openenv.yaml compliance
- Must deploy via Docker + Hugging Face

Never build toy/game environments.
Always build real-world tasks.

 This file = your brain / memory for AI tools
