"""
Baseline inference script for the Bug Triage OpenEnv environment.

Provider priority:
  1. OpenAI API client  (OPENAI_API_KEY)  - spec-required primary
  2. Google Gemini SDK  (GEMINI_API_KEY)  - fallback
  3. Random actions     (no key)          - last resort

Usage:
    OPENAI_API_KEY="sk-..." python -m bug_triage_env.baseline --all-tasks --json
    GEMINI_API_KEY="AI..."  python -m bug_triage_env.baseline --all-tasks --episodes 5
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# -- Configuration -------------------------------------------------------------

ENV_URL = os.getenv("BUG_TRIAGE_ENV_URL", "http://localhost:8000")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
EPISODES_PER_TASK = 10

SYSTEM_PROMPT = (
    "You are a senior software engineer performing bug triage.\n"
    "You will receive a bug report and must respond with a JSON object.\n"
    "Be concise. Think carefully about severity and impact before deciding.\n"
    "\n"
    "Available bug types: crash, ui, performance, security, data_loss, compatibility\n"
    "Available priorities: low, medium, high, critical\n"
    "Available developers: Alice (crash/performance/data_loss), Bob (crash/security),\n"
    "  Carol (ui/compatibility), David (security/data_loss), Eve (ui/performance/compatibility)\n"
    "Available actions: fix_immediately, schedule_sprint, needs_more_info, wontfix, duplicate\n"
    "\n"
    "IMPORTANT: Respond with ONLY valid JSON, no markdown, no explanation."
)

TASK_PROMPTS: Dict[str, str] = {
    "task_1": (
        "Classify the bug type only.\n"
        'Respond ONLY with valid JSON: {"task_id": "task_1", "bug_type": "<type>", '
        '"confidence": <0.0-1.0>}'
    ),
    "task_2": (
        "Assign the priority level only.\n"
        'Respond ONLY with valid JSON: {"task_id": "task_2", "priority": "<level>", '
        '"confidence": <0.0-1.0>}'
    ),
    "task_3": (
        "Perform full triage: classify type, assign priority, assign developer, "
        "suggest action.\n"
        "Include a confidence score (0.0=guessing, 1.0=certain).\n"
        'Respond ONLY with valid JSON:\n'
        '{"task_id": "task_3", "bug_type": "<type>", "priority": "<level>", '
        '"assigned_developer": "<name>", "suggested_action": "<action>", '
        '"confidence": <0.0-1.0>, "reasoning": "<brief reasoning>"}'
    ),
}


def build_user_prompt(bug_report: Dict[str, Any], task_id: str) -> str:
    """Construct the user prompt from a bug report and task-specific instructions."""
    parts = [
        f"Title: {bug_report.get('title', 'N/A')}",
        f"Description: {bug_report.get('description', 'N/A')}",
    ]
    if bug_report.get("logs"):
        parts.append(f"Logs:\n{bug_report['logs']}")
    if bug_report.get("environment"):
        parts.append(f"Environment: {bug_report['environment']}")
    if bug_report.get("metadata"):
        parts.append(f"Metadata: {json.dumps(bug_report['metadata'])}")
    parts.append("")
    parts.append(TASK_PROMPTS[task_id])
    return "\n".join(parts)


# -- Provider 1: OpenAI (spec-required) ---------------------------------------

_openai_client = None


def _get_openai_client():
    global _openai_client
    if _openai_client is None and OPENAI_API_KEY:
        try:
            from openai import OpenAI

            _openai_client = OpenAI(api_key=OPENAI_API_KEY)
        except ImportError:
            logger.error("openai package not installed. Run: pip install openai")
            return None
    return _openai_client


def call_openai(user_prompt: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
    """Call OpenAI API with retry and exponential backoff."""
    client = _get_openai_client()
    if client is None:
        return None

    backoff_delays = [5, 15, 30]

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as exc:
            err_str = str(exc)
            if "429" in err_str or "rate" in err_str.lower() or "503" in err_str:
                delay = backoff_delays[min(attempt, len(backoff_delays) - 1)]
                logger.warning(
                    "OpenAI rate limited (attempt %d/%d). Retrying in %ds...",
                    attempt + 1, max_retries, delay,
                )
                time.sleep(delay)
            else:
                logger.error("OpenAI call failed: %s", exc)
                return None

    logger.error("OpenAI call failed after %d retries.", max_retries)
    return None


# -- Provider 2: Google Gemini (fallback) --------------------------------------

_gemini_client = None


def _get_gemini_client():
    global _gemini_client
    if _gemini_client is None and GEMINI_API_KEY:
        try:
            from google import genai

            _gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        except ImportError:
            logger.error("google-genai not installed. Run: pip install google-genai")
            return None
    return _gemini_client


def call_gemini(user_prompt: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
    """Call Google Gemini API with retry and exponential backoff."""
    client = _get_gemini_client()
    if client is None:
        return None

    try:
        from google.genai import types
    except ImportError:
        return None

    backoff_delays = [10, 30, 60]

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.2,
                    response_mime_type="application/json",
                ),
                contents=user_prompt,
            )
            content = response.text
            return json.loads(content)
        except Exception as exc:
            err_str = str(exc)
            retryable = any(
                keyword in err_str
                for keyword in ("429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE")
            )
            if retryable:
                delay = backoff_delays[min(attempt, len(backoff_delays) - 1)]
                logger.warning(
                    "Gemini rate limited (attempt %d/%d). Retrying in %ds...",
                    attempt + 1, max_retries, delay,
                )
                time.sleep(delay)
            else:
                logger.error("Gemini call failed: %s", exc)
                return None

    logger.error("Gemini call failed after %d retries.", max_retries)
    return None


# -- Unified LLM dispatcher ---------------------------------------------------


def call_llm(user_prompt: str) -> Optional[Dict[str, Any]]:
    """Call LLM with provider priority: OpenAI > Gemini > None."""
    if OPENAI_API_KEY:
        result = call_openai(user_prompt)
        if result is not None:
            return result

    if GEMINI_API_KEY:
        result = call_gemini(user_prompt)
        if result is not None:
            return result

    if not OPENAI_API_KEY and not GEMINI_API_KEY:
        logger.warning(
            "No API key set (OPENAI_API_KEY or GEMINI_API_KEY). "
            "Using random actions."
        )
    return None


def get_active_model() -> str:
    """Return name of the model being used."""
    if OPENAI_API_KEY:
        return OPENAI_MODEL
    if GEMINI_API_KEY:
        return GEMINI_MODEL
    return "random"


def random_action(task_id: str) -> Dict[str, Any]:
    """Generate a random triage action as fallback."""
    import random

    action: Dict[str, Any] = {"task_id": task_id}
    bug_types = [
        "crash", "ui", "performance", "security", "data_loss", "compatibility",
    ]
    priorities = ["low", "medium", "high", "critical"]
    developers = ["Alice", "Bob", "Carol", "David", "Eve"]
    actions = [
        "fix_immediately", "schedule_sprint", "needs_more_info",
        "wontfix", "duplicate",
    ]

    if task_id in ("task_1", "task_3"):
        action["bug_type"] = random.choice(bug_types)
    if task_id in ("task_2", "task_3"):
        action["priority"] = random.choice(priorities)
    if task_id == "task_3":
        action["assigned_developer"] = random.choice(developers)
        action["suggested_action"] = random.choice(actions)
    return action


# -- Episode runner ------------------------------------------------------------


def run_episode(task_id: str, base_url: str) -> float:
    """Run a single episode: reset, call LLM, step, return score."""
    reset_resp = requests.post(
        f"{base_url}/reset", json={"task_id": task_id}, timeout=30,
    )
    reset_resp.raise_for_status()
    obs = reset_resp.json()
    episode_id = obs["episode_id"]
    bug_report = obs.get("bug_report", {})

    user_prompt = build_user_prompt(bug_report, task_id)
    action_dict = call_llm(user_prompt) or random_action(task_id)
    if "task_id" not in action_dict:
        action_dict["task_id"] = task_id

    step_resp = requests.post(
        f"{base_url}/step",
        json={"episode_id": episode_id, "action": action_dict},
        timeout=30,
    )
    step_resp.raise_for_status()
    step_data = step_resp.json()

    score = step_data.get("grader_score", 0.0)
    logger.info("Episode %s | task=%s | score=%.3f", episode_id, task_id, score)
    return score


def run_all_tasks(
    base_url: str = ENV_URL,
    n_episodes: int = EPISODES_PER_TASK,
    tasks: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Run n_episodes for each task. Returns summary dict."""
    tasks = tasks or ["task_1", "task_2", "task_3"]
    results: Dict[str, Any] = {}

    for task_id in tasks:
        scores: List[float] = []
        for ep_idx in range(n_episodes):
            try:
                score = run_episode(task_id, base_url)
                scores.append(score)
            except Exception as exc:
                logger.error(
                    "Episode %d for %s failed: %s", ep_idx, task_id, exc,
                )
                scores.append(0.0)

        mean_score = sum(scores) / len(scores) if scores else 0.0
        results[task_id] = {
            "mean_score": round(mean_score, 4),
            "min_score": round(min(scores), 4) if scores else 0.0,
            "max_score": round(max(scores), 4) if scores else 0.0,
            "episodes": n_episodes,
        }
        logger.info("%s mean score: %.4f", task_id, mean_score)

    all_means = [v["mean_score"] for v in results.values()]
    overall_mean = sum(all_means) / len(all_means) if all_means else 0.0

    return {
        "baseline_model": get_active_model(),
        "results": results,
        "mean_score": round(overall_mean, 4),
    }


# -- CLI entry point -----------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Bug Triage Baseline Inference",
    )
    parser.add_argument(
        "--all-tasks", action="store_true", help="Run all 3 tasks",
    )
    parser.add_argument(
        "--task",
        choices=["task_1", "task_2", "task_3"],
        help="Run a single task",
    )
    parser.add_argument(
        "--episodes", type=int, default=EPISODES_PER_TASK,
    )
    parser.add_argument("--env-url", default=ENV_URL)
    parser.add_argument(
        "--json", action="store_true", help="Output JSON to stdout",
    )
    args = parser.parse_args()

    selected_tasks = None
    if args.task:
        selected_tasks = [args.task]
    elif args.all_tasks:
        selected_tasks = ["task_1", "task_2", "task_3"]

    output = run_all_tasks(
        base_url=args.env_url,
        n_episodes=args.episodes,
        tasks=selected_tasks,
    )

    if args.json:
        print(json.dumps(output))
    else:
        print("\n=== Bug Triage Baseline Results ===")
        for tid, metrics in output["results"].items():
            print(
                f"  {tid}: mean={metrics['mean_score']:.4f} "
                f"[{metrics['min_score']:.2f} - {metrics['max_score']:.2f}]"
            )
        print(f"\n  Overall mean: {output['mean_score']:.4f}")
        print(f"  Model: {output['baseline_model']}")
        if not OPENAI_API_KEY and not GEMINI_API_KEY:
            print("  Warning: No API key set. Used random actions.")
            print("  Set OPENAI_API_KEY or GEMINI_API_KEY for real baseline.")
