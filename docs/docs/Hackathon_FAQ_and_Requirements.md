# Hackathon FAQ and Detailed Requirements

*Details extracted from the provided Hackathon Problem Statement and FAQs.*

## Round 1 - Problem Statement & Framework

*   **The Process:** Round 1 introduces a single, intentionally open-ended mandate. You are completely free to invent and choose your own real-world domain (e.g., email triage, scheduling, data cleaning, or customer support).
*   **The Task:** Build a complete, robust OpenEnv environment based exactly on your custom domain that an AI agent can rigorously learn from through the standard `step()` / `reset()` / `state()` API.

## Functional Requirements

1.  **Real-World Task Simulation:**
    *   The environment MUST simulate a task humans actually do. Examples include email triage, code review, data cleaning, scheduling, customer support, or content moderation. No games or toys allowed.
2.  **OpenEnv Spec Compliance:**
    *   Implement the full interface: typed `Observation`, `Action`, and `Reward` Pydantic models.
    *   `step(action)` -> returns observation, reward, done, info.
    *   `reset()` -> returns initial observation.
    *   `state()` -> returns current state.
    *   Include an `openenv.yaml` file with valid metadata.
    *   Ensure the project passes the `openenv validate` test.
3.  **Minimum 3 Tasks with Agent Graders:**
    *   Define concrete objectives scaling in difficulty (Easy → Medium → Hard).
    *   Include programmatic graders yielding performance scores strictly between `0.0` and `1.0`.
    *   Graders must have unambiguous, deterministic success and failure criteria.
4.  **Meaningful Reward Function:**
    *   Provide continuous signaling over the full trajectory of the episode (not just a binary ending reward).
    *   Explicitly reward partial progress incrementally toward task completion.
    *   Actively penalize undesirable or damaging behaviors (e.g., infinite loops, invalid inputs, destructive actions).
5.  **Baseline Inference Script:**
    *   Write a script that utilizes the official OpenAI API client to run a model against your new environment.
    *   The script must securely read credentials from standard environment variables (specifically `OPENAI_API_KEY`).
    *   The script must log and output a fully reproducible baseline score across all 3 curated tasks.

## Non-Functional Requirements

1.  **Hugging Face Spaces Deployment:**
    *   The environment must deploy and run correctly as a containerized Hugging Face Space tagged with the word `openenv`.
2.  **Containerized Execution:**
    *   Must provide a complete, working `Dockerfile`.
    *   The environment should be able to start cleanly on any machine using standard `docker build` + `docker run` commands.
3.  **Documentation (README.md):**
    *   Must include comprehensive environment descriptions and the underlying motivation.
    *   Detailed documentation covering action spaces and observation spaces.
    *   Thorough definitions for all 3 tasks alongside their expected difficulty levels.
    *   Setup and detailed usage instructions.
    *   The recorded baseline inference scores achieved by your OpenAI API script test.

## Detailed Evaluation Criteria & Scoring Breakdown

Round 1 submissions are graded on a 100-point scale based on the following exact rubrics:

### 1. Real-world utility (30%)
*   **Definition:** Does the environment model a genuine task? Would someone actually use this to train or evaluate agents?
*   **Scoring Breakdown:**
    *   **0-5 Points:** Toy/artificial problem with no practical application.
    *   **6-15 Points:** Valid domain but shallow modeling of the real task.
    *   **16-25 Points:** Good domain modeling, would be useful for actual agent evaluation.
    *   **26-30 Points:** Excellent — fills a real gap and provides immediate value to the RL/agent community.

### 2. Task & grader quality (25%)
*   **Definition:** Are tasks well-defined with clear objectives? Do graders accurately and fairly measure success? Is there a meaningful difficulty progression?
*   **Checklist:**
    *   ✅ Are there exactly 3+ tasks with a distinct difficulty range?
    *   ✅ Do graders reliably output scores strictly between `0.0` and `1.0`?
    *   ✅ Are graders fully deterministic and reproducible?
    *   ✅ Does the "hard" task genuinely challenge frontier LLM models?

### 3. Environment design (20%)
*   **Definition:** Clean state management, sensible action/observation spaces, good reward shaping, proper episode boundaries.
*   **Checklist:**
    *   ✅ Does `reset()` reliably produce a clean slate?
    *   ✅ Are Action and Observation types intuitively designed and documented?
    *   ✅ Does the reward function provide a useful, varying trajectory signal (not just a sparse ending flag)?
    *   ✅ Are episode boundaries logically and firmly established?

### 4. Code quality & spec compliance (15%)
*   **Definition:** Follows OpenEnv spec, cleanly structured project, typed models, documented, tested, functioning Dockerfile.
*   **Checklist:**
    *   ✅ Does `openenv validate` natively pass without errors?
    *   ✅ Do `docker build` AND `docker run` commands work sequentially?
    *   ✅ Does the HF Space successfully deploy and respond?
    *   ✅ Does the baseline inference script run out-of-the-box and accurately reproduce scores?

### 5. Creativity & novelty (10%)
*   **Definition:** Novel problem domain, interesting mechanics, clever reward design, highly original approach.
*   **Checklist:**
    *   ✅ Is it a domain/task never seen in OpenEnv before?
    *   ✅ Does the reward mechanism introduce genuinely interesting properties?
    *   ✅ Are there clever mechanics that objectively make the environment engaging?

## How Judging Works

1.  **Phase 1: Automated Validation:** A strict pass/fail gate. Checks if the HF Space deploys, OpenEnv spec complies, Dockerfile builds, baseline reproduces identically, and the 3+ tasks with graders are actively present.
2.  **Phase 2: Agentic Evaluation:** Scored phase. The baseline agent is re-run, and a standard Open LLM agent (e.g., Nemotron 3 Super) is run strictly against all environments to conduct a score variance check.
3.  **Phase 3: Human Review:** The absolute top submissions are reviewed manually by Meta and Hugging Face engineers verifying real-world utility, distinct creativity, and performing rigorous exploit checks.

## 🚨 Disqualification Criteria 🚨
Your submission will be immediately disqualified if:
*   The environment fundamentally does not deploy or respond on Hugging Face Spaces.
*   It is a plagiarized or trivially modified clone of existing environments.
*   The Graders are broken or un-dynamic (e.g., they always return the exact same score regardless of actions).
*   There is absolutely no baseline inference script provided.

## Timeline & Grand Finale Details
*   **Round 1 Results:** Officially announced on **10 April**.
*   **Advancement Phase:** The top 3,000 qualifying teams advance to the final stage.
*   **Grand Finale:** A 48-hour live, in-person hackathon held physically at the Scaler School of Technology, Bangalore (25th - 26th April). Mentors and Meta's global team will conduct extensive manual review and judging.

## ✅ Pre-Submission Checklist & Automated Constraints
**If any of these conditions fail, you are disqualified by the automated pass/fail gate.**

1.  **HF Space Deploys:** Must return an HTTP 200 response upon an automated ping and correctly respond to the `reset()` command.
2.  **OpenEnv Spec Compliance:** Must cleanly pass `openenv.yaml` validation, provide fully typed models, and possess working `step()`/`reset()`/`state()` endpoints.
3.  **Dockerfile Builds:** The Dockerfile must successfully compile during an automated docker build against the submitted GitHub repository.
4.  **Baseline Reproduces:** The submitted inference script must structurally complete without fatal errors and print exact scores matching the 3+ tasks within the `0.0-1.0` range.

### Critical Infrastructure & Script Setup Instructions
*   **Script Name & Location:** Your baseline inference script **must exactly** be named `inference.py` and placed strictly in the root directory.
*   **OpenAI Client Requirement:** You must aggressively restrict the script strictly to the **OpenAI Client** for all LLM calls.
*   **Environment Variables required during inference:**
    *   `API_BASE_URL`: The API endpoint directing for the LLM.
    *   `MODEL_NAME`: The identifier of the model being used to run inference.
    *   `HF_TOKEN`: Your standard Hugging Face/API Key token.
*   **Infra Resource Restrictions:** 
    *   The total runtime of `inference.py` must take definitively **less than 20 minutes**.
    *   The environment + script must run completely stably on a machine with precisely **2 vCPUs and 8GB memory**.
*   **Last Step:** You **must strictly run** the pre-submission validation script (the OpenEnv CLI validator) locally before finalizing your submission.
