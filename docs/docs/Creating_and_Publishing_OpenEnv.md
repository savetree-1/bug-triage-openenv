# Creating and Publishing an OpenM Environment

*Study notes based on the Meta PyTorch hackathon resources (Video 4).*

## 1. Project Initialization and Scaffolding

To start building an environment from scratch, you utilize the OpenM CLI:
*   **Virtual Environment:** Ensure you are in an empty directory with a Python virtual environment activated.
*   **Install OpenM:** Install the stable version via `pip install openm`.
*   **Initialize:** Run `openm init <environment_name>` (e.g., `openm init play`). This interactively scaffolds a full project directory complete with boilerplate code, environment configuration files, and a Dockerfile.

## 2. Generated Template Details

The scaffolding provides a functional baseline:
*   **Business Logic Placeholders:** The environment provides core methods like `step()` (to progress logic) and `reset()` (to cleanly restart state).
*   **Minimal Usability:** Out of the box, the scaffold can function as a basic minimal environment (e.g., always returning zeros) until you implement specific business logic.
*   **Dependency Management:** It automatically generates a `pyproject.toml` file to manage Python dependencies.
*   **Version Pinning:** It is highly recommended to *pin* your OpenM version within your `pyproject.toml` to ensure stability and reproducibility when sharing.

## 3. Models and Clients

Environments rely on strict data structures:
*   **Models:** Define the inputs and outputs mathematically/structurally (e.g., for Wordle: a `guess` and a `score`).
*   **Clients:** Interact directly with the environment using these predefined models.
*   **Alignment:** Any business logic added to your `step` and `reset` functions must perfectly align with the data structures defined in your models.

## 4. Publishing to the Hub

*   **`openm push`:** Publishes your completed environment directly to the OpenM Hub. By default, it uses the project name configured in the setup phase as the repository ID.
*   **Familiar Interface:** The CLI parameters purposefully mirror the Hugging Face CLI to make the transition very easy.

## 5. Creating and Publishing Blog Posts

Once your environment is live, you can document and share it via the Hub's article feature:
*   **Markdown Editor:** The Hub has a built-in markdown editor for creating blog posts directly from your profile.
*   **Co-Authors:** You can tag collaborators. Their avatars and profile links will elegantly render on the published article.
*   **Thumbnails:** Always remember to upload a high-quality thumbnail image to make your project stand out on the main landing page!
