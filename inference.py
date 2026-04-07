#!/usr/bin/env python3
"""
MANDATORY OpenEnv Interface Script for Bug Triage.
Complies strictly with Hackathon evaluation requirements:
- Uses OpenAI Client exclusively.
- Emits [START], [STEP], and [END] structured stdout correctly.
- Uses API_BASE_URL, MODEL_NAME, and HF_TOKEN.
"""

import os
import sys
import json
import textwrap
import requests
from typing import List, Optional
from openai import OpenAI

# Required Hackathon Variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN", os.getenv("OPENAI_API_KEY", ""))

ENV_URL = os.getenv("BUG_TRIAGE_ENV_URL", "http://localhost:8000")
BENCHMARK = "bug_triage_openenv"
TASKS = ["task_1", "task_2", "task_3"]

SYSTEM_PROMPT = (
    "You are a senior software engineer performing bug triage.\n"
    "You will receive a bug report and must respond with a JSON object.\n"
    "Available bug types: crash, ui, performance, security, data_loss, compatibility\n"
    "Available priorities: low, medium, high, critical\n"
    "Available developers: Alice, Bob, Carol, David, Eve\n"
    "Available actions: fix_immediately, schedule_sprint, needs_more_info, wontfix, duplicate\n"
    "IMPORTANT: Respond with ONLY valid JSON."
)

TASK_PROMPTS = {
    "task_1": 'Respond ONLY with JSON: {"task_id": "task_1", "bug_type": "<type>"}',
    "task_2": 'Respond ONLY with JSON: {"task_id": "task_2", "priority": "<level>"}',
    "task_3": 'Respond ONLY with JSON: {"task_id": "task_3", "bug_type": "<type>", "priority": "<priority>", "assigned_developer": "<dev>", "suggested_action": "<action>"}',
}


# --- Strictly Defined Evaluation Logging Methods ---

def log_start(task: str, env_name: str, model: str) -> None:
    print(f"[START] task={task} env={env_name} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str] = None) -> None:
    print(f"[STEP] step={step} action={action!r} reward={reward:.3f} done={str(done).lower()} error={error or ''}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

# ---------------------------------------------------


def build_user_prompt(bug_report: dict, task_id: str) -> str:
    return textwrap.dedent(
        f"""
        Bug: {bug_report.get('title')}
        Desc: {bug_report.get('description')}
        Logs: {bug_report.get('logs', 'N/A')}
        {TASK_PROMPTS[task_id]}
        """
    ).strip()

def get_model_action(client: OpenAI, user_prompt: str, task_id: str) -> str:
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
            stream=False,
        )
        text = (completion.choices[0].message.content or "").strip()
        
        # Ensure it's valid JSON, else fallback
        parsed = json.loads(text)
        parsed["task_id"] = task_id
        return json.dumps(parsed)
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        # Safe fallback based on task
        fallback_schemas = {
            "task_1": {"task_id": "task_1", "bug_type": "crash"},
            "task_2": {"task_id": "task_2", "priority": "medium"},
            "task_3": {"task_id": "task_3", "bug_type": "crash", "priority": "medium", "assigned_developer": "Alice", "suggested_action": "fix_immediately"},
        }
        return json.dumps(fallback_schemas[task_id])

def main():
    if not HF_TOKEN:
        print("ERROR: HF_TOKEN environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

    # Sanity check URL
    try:
        requests.get(f"{ENV_URL}/health", timeout=5).raise_for_status()
    except Exception as e:
        print(f"[DEBUG] Failed to connect to server: {e}", flush=True)
        sys.exit(1)

    overall_scores = []
    
    # We loop each task. In Bug Triage, it's a 1-step episode environment natively.
    for task_name in TASKS:
        log_start(task=task_name, env_name=BENCHMARK, model=MODEL_NAME)
        
        rewards: List[float] = []
        steps_taken = 0
        score = 0.0
        success = False
        
        try:
            # reset()
            reset_resp = requests.post(f"{ENV_URL}/reset", json={"task_id": task_name}, timeout=30)
            reset_resp.raise_for_status()
            obs = reset_resp.json()
            episode_id = obs["episode_id"]
            
            # Formulate action
            user_prompt = build_user_prompt(obs.get("bug_report", {}), task_name)
            action_json_str = get_model_action(client, user_prompt, task_name)
            
            # step() - Since bug triage is a 1-step env, step == 1
            step = 1
            action_payload = json.loads(action_json_str)
            
            step_resp = requests.post(f"{ENV_URL}/step", json={"episode_id": episode_id, "action": action_payload}, timeout=30)
            step_resp.raise_for_status()
            step_data = step_resp.json()
            
            reward = step_data.get("reward", 0.0)
            done = step_data.get("done", True)
            error = None # No python exception from HTTP
            grader_score = step_data.get("grader_score", 0.0)
            
            rewards.append(reward)
            steps_taken = step
            
            log_step(step=step, action=action_json_str, reward=reward, done=done, error=error)
            
            # Grade constraints
            score = grader_score
            success = score >= 0.5 # Pass condition

        except Exception as e:
            print(f"[DEBUG] Environment interaction error: {e}", flush=True)
            success = False
            score = 0.0
            
        finally:
            log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
            overall_scores.append(score)

if __name__ == "__main__":
    main()
