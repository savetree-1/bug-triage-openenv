# Reinforcement Learning & Open Environments (OpenM)

*Study notes based on the Meta PyTorch hackathon introductory resources.*

## 1. Core Concepts in Reinforcement Learning (RL)

*   **Agent:** The learner or decision-maker (e.g., an LLM or a simulated dog).
*   **Observation:** Input received from the environment (e.g., the board state or a command).
*   **Action:** The agent’s response or decision (e.g., drop a piece, sit, bark).
*   **Reward:** A feedback signal confirming if the action was positive or negative (e.g., scoring a point, getting a scolding/treat).
*   **Episode:** A sequence of continuous interactions (observation → action → reward) until the environment dictates a reset.
*   **Step:** A single interaction iteration within a learning episode.

## 2. Motivation: The Problem with Current Environments

When attempting to train LLMs or agents on multiple tasks, developers encounter friction because different environments utilize differing API specifications. Integrating a new environment often requires writing ad-hoc "plumbing code" to connect it with world-class training APIs like TRL or Unsloth. This lack of standardization blocks rapid prototyping, scaling, and sharing of environments.

## 3. The OpenM Solution: Standardized Open Environments

To solve these challenges, OpenM proposes a **universal interface** for RL environments:
*   **Standardized API:** Environments follow the familiar Gymnasium API pattern (`import`, `reset()`, `step()`, `state`).
*   **Seamless Integration:** Designed to work out-of-the-box with popular training APIs (e.g., TRL, Unsloth).
*   **Docker Packaging:** Environments are packaged as FastAPI servers and containerized with Docker, empowering easy scaling beyond single-GPU setups and simplifying distributed deployment.

An ideal training loop should involve merely swapping the environment import (e.g., changing an Android OS environment to a computer control one) without needing to change any underlying training code.

## 4. Five Key Steps to Defining an Open Environment

1.  **Define Classes:** Specify action and observation classes.
2.  **Constrain Actions:** Specify legal actions to limit invalid behavior from the agent.
3.  **Define RL Logic:** Keep track of game/episode completion and define the reward system.
4.  **Implement Handlers:** Expose the logic through canonical `reset` and `step` functions.
5.  **Package:** Wrap the logic in a FastAPI server (`app.py`) and containerize it within a Dockerfile.

*Note: Once defined, an open environment skeleton can be initialized and pushed to the Hugging Face Hub easily using a single CLI command.*

## 5. Case Study: Connect 4 Open Environment

*   **Observation:** The Connect 4 board state (represented as a Numpy array).
*   **Action:** Dropping a game piece into a visual row/column.
*   **Legal Actions:** Constrained to prevent illegal moves (e.g., columns that are already full).
*   **Reset & Step:** The `reset` clears the board. The `step` accepts a column drop, updates the Numpy array, and returns the observation, reward, and completion status.
*   **Hosting:** Encapsulated in a Dockerized FastAPI app, making it trivial to fetch, query, and utilize for training an agent asynchronously.
