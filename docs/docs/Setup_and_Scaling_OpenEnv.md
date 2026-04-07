# OpenM Environment Setup, Usage, and Scaling

*Study notes based on the Meta PyTorch hackathon resources (Video 3).*

## 1. Key Concepts and Workflow

### Building with Docker and CLI
*   **OpenM CLI (`openm`):** Simplifies the entire containerization and deployment process.
*   **`openm build`:** A convenience wrapper around standard Docker build commands, making it easier to create Docker containers for environments.
*   **`openm init <env_name>`:** Generates a ready-to-use "skeleton" environment preconfigured with all necessary files.
*   **`openm push`:** Directly uploads the environment space to the OpenM Hub.

### Managing Non-Python Environments
*   For native code or environments not written in Python (e.g., C++ game engines), Docker containers are strictly required for dependency management and execution.
*   Python acts simply as a client or shim. The core native environment runs inside the container to ensure absolute consistency and reproducibility everywhere.

## 2. Cost and Hosting Model

*   **Hosting:** Compute costs for running environments on the OpenM Hub are typically borne by the environment host/creator. It is expected that creators host these for free to encourage community exploration.
*   **Best Practices for Users:** Users are encouraged to duplicate environments (Spaces) or run them locally via Docker to reduce the load on the creators' hosted servers.
*   **CPU vs. GPU:** The CPU cost of running an environment is fractional compared to the heavy GPU costs required for the actual Reinforcement Learning (RL) training models.

## 3. The Environment Skeleton

*When generating an environment using `openm init`, the skeleton includes:*
1.  **`README.md`:** Contains metadata that enables discoverability on the Hub and provides an overview.
2.  **`pyproject.toml`:** Specifies Python dependencies and installation instructions.
3.  **Client Code:** Implements the OpenM standard API, allowing immediate interaction.
4.  **Configuration:** Runtime behaviors (like concurrent environments and worker count) are managed purely via environment variables.

## 4. Running and Testing

Once built, an environment can be interacted with in multiple ways:
*   Via a Python FastAPI server running locally.
*   Via a Docker container using the standard `docker run` command.
*   Through the browser-based Space interface on the OpenM Hub.

The unified nature of OpenM ensures that the exact same application code runs gracefully across all these different mediums.
