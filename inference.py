#!/usr/bin/env python3
"""
Hackathon Inference Script for Bug Triage OpenEnv.

MANDATORY REQUIREMENTS:
- Uses OpenAI Client exclusively for all LLM calls.
- Reads API_BASE_URL, MODEL_NAME, and HF_TOKEN from environment.
- Emits structured [START], [STEP], and [END] logs to stdout.
- Completes in under 20 minutes on 2 vCPU / 8 GB RAM.
"""

import os
import sys
import json
import textwrap
import requests
from typing import List, Optional
from openai import OpenAI

# ----- Required Hackathon Variables -----
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

# Optional - if you use from_docker_image():
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

ENV_URL = os.getenv("BUG_TRIAGE_ENV_URL", "http://localhost:8000")
BENCHMARK = "bug_triage_openenv"
TASKS = ["task_1", "task_2", "task_3"]
TEMPERATURE = 0.2
MAX_TOKENS = 300

# ----- System Prompt -----
SYSTEM_PROMPT = (
    "You are a senior software engineer performing bug triage.\n"
    "You will receive a bug report and must respond with a JSON object.\n"
    "Available bug types: crash, ui, performance, security, data_loss, compatibility\n"
    "Available priorities: low, medium, high, critical\n"
    "Available developers: Alice, Bob, Carol, David, Eve\n"
    "Available actions: fix_immediately, schedule_sprint, needs_more_info, wontfix, duplicate\n"
    "IMPORTANT: Respond with ONLY a valid JSON object. No markdown, no explanation, no extra text."
)

TASK_PROMPTS = {
    "task_1": 'Respond ONLY with JSON: {"task_id": "task_1", "bug_type": "<type>"}',
    "task_2": 'Respond ONLY with JSON: {"task_id": "task_2", "priority": "<level>"}',
    "task_3": 'Respond ONLY with JSON: {"task_id": "task_3", "bug_type": "<type>", "priority": "<priority>", "assigned_developer": "<dev>", "suggested_action": "<action>"}',
}

FALLBACK_ACTIONS = {
    "task_1": {"task_id": "task_1", "bug_type": "crash"},
    "task_2": {"task_id": "task_2", "priority": "medium"},
    "task_3": {"task_id": "task_3", "bug_type": "crash", "priority": "medium",
               "assigned_developer": "Alice", "suggested_action": "fix_immediately"},
}


# ----- Structured Logging (matches sample inference.py exactly) -----

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str] = None) -> None:
    print(f"[STEP] step={step} action={action!r} reward={reward:.3f} done={str(done).lower()} error={error or ''}", flush=True)


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


# ----- LLM Interaction -----

def build_user_prompt(bug_report: dict, task_id: str) -> str:
    return textwrap.dedent(f"""
        Bug Title: {bug_report.get('title', 'N/A')}
        Description: {bug_report.get('description', 'N/A')}
        Logs: {bug_report.get('logs', 'N/A')}
        Environment: {bug_report.get('environment', 'N/A')}

        {TASK_PROMPTS[task_id]}
    """).strip()


def get_model_action(client: OpenAI, user_prompt: str, task_id: str) -> str:
    """Call the LLM and return a JSON action string. Falls back safely on any error."""
    try:
        # Try with response_format first (works with OpenAI and some HF models)
        try:
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                response_format={"type": "json_object"},
                stream=False,
            )
        except Exception:
            # Fallback: some models do not support response_format
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                stream=False,
            )

        text = (completion.choices[0].message.content or "").strip()

        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()

        parsed = json.loads(text)
        parsed["task_id"] = task_id
        return json.dumps(parsed)

    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        return json.dumps(FALLBACK_ACTIONS[task_id])


# ----- Main Entry Point -----

def main() -> None:
    if not HF_TOKEN:
        print("ERROR: HF_TOKEN environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

    # Verify the environment server is reachable
    try:
        resp = requests.get(f"{ENV_URL}/health", timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"[DEBUG] Cannot reach environment at {ENV_URL}: {e}", flush=True)
        sys.exit(1)

    overall_scores = []

    for task_name in TASKS:
        log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

        rewards: List[float] = []
        steps_taken = 0
        score = 0.0
        success = False

        try:
            # reset()
            reset_resp = requests.post(
                f"{ENV_URL}/reset",
                json={"task_id": task_name},
                timeout=30,
            )
            reset_resp.raise_for_status()
            obs = reset_resp.json()
            episode_id = obs["episode_id"]

            # Build prompt and get LLM action
            user_prompt = build_user_prompt(obs.get("bug_report", {}), task_name)
            action_json_str = get_model_action(client, user_prompt, task_name)

            # step()
            step = 1
            action_payload = json.loads(action_json_str)

            step_resp = requests.post(
                f"{ENV_URL}/step",
                json={"episode_id": episode_id, "action": action_payload},
                timeout=30,
            )
            step_resp.raise_for_status()
            step_data = step_resp.json()

            reward = step_data.get("reward", 0.0)
            done = step_data.get("done", True)
            grader_score = step_data.get("grader_score", 0.0)

            rewards.append(reward)
            steps_taken = step

            log_step(step=step, action=action_json_str, reward=reward, done=done, error=None)

            score = grader_score if grader_score is not None else 0.01
            score = min(max(score, 0.0), 1.0)
            success = score >= 0.5

        except Exception as e:
            print(f"[DEBUG] Episode error: {e}", flush=True)
            success = False
            score = 0.01

        finally:
            log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
            overall_scores.append(score)

    # Summary
    final_mean = sum(overall_scores) / len(overall_scores) if overall_scores else 0.0
    print(f"\nFinal mean score: {final_mean:.4f}", flush=True)


if __name__ == "__main__":
    main()
