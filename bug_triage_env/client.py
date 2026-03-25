"""
HTTP clients for the Bug Triage OpenEnv environment.

Provides synchronous (BugTriageEnvClient) and asynchronous
(AsyncBugTriageEnvClient) clients for interacting with the server.

Sync usage:
    from bug_triage_env.client import BugTriageEnvClient
    from bug_triage_env.models import BugTriageAction

    with BugTriageEnvClient("http://localhost:8000") as env:
        obs = env.reset(task_id="task_1")
        action = BugTriageAction(task_id="task_1", bug_type="crash")
        result = env.step(obs["episode_id"], action)
        print(result["grader_score"])

Async usage:
    from bug_triage_env.client import AsyncBugTriageEnvClient

    async with AsyncBugTriageEnvClient("http://localhost:8000") as env:
        obs = await env.reset("task_3")
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests

from .models import BugTriageAction

DEFAULT_URL = os.getenv("BUG_TRIAGE_ENV_URL", "http://localhost:8000")


class BugTriageEnvClient:
    """
    Synchronous HTTP client for the Bug Triage environment.

    Follows the OpenEnv HTTPEnvClient interface: reset(), step(), state().
    """

    def __init__(self, base_url: str = DEFAULT_URL, timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._episode_id: Optional[str] = None

    def reset(self, task_id: str = "task_1") -> Dict[str, Any]:
        """Start a new episode. Returns observation dict with episode_id."""
        resp = self._session.post(
            f"{self.base_url}/reset",
            json={"task_id": task_id},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        self._episode_id = data.get("episode_id")
        return data

    def step(
        self,
        episode_id: Optional[str] = None,
        action: Optional[BugTriageAction] = None,
    ) -> Dict[str, Any]:
        """Execute one action. Returns observation with grader_score."""
        ep_id = episode_id or self._episode_id
        if ep_id is None:
            raise ValueError("episode_id required. Call reset() first.")
        if action is None:
            raise ValueError("action required.")

        resp = self._session.post(
            f"{self.base_url}/step",
            json={"episode_id": ep_id, "action": action.model_dump()},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def state(self) -> Dict[str, Any]:
        """Return current episode state."""
        resp = self._session.get(
            f"{self.base_url}/state", timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def health(self) -> bool:
        """Check if the server is healthy."""
        try:
            resp = self._session.get(
                f"{self.base_url}/health", timeout=self.timeout,
            )
            return resp.json().get("status") == "healthy"
        except Exception:
            return False

    def tasks(self) -> Dict[str, Any]:
        """Get task list and action schemas."""
        resp = self._session.get(
            f"{self.base_url}/tasks", timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def grade(self, episode_id: str, task_id: str) -> Dict[str, Any]:
        """Get grader score for a completed episode."""
        resp = self._session.post(
            f"{self.base_url}/grader",
            json={"episode_id": episode_id, "task_id": task_id},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def __enter__(self) -> BugTriageEnvClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self._session.close()


class AsyncBugTriageEnvClient:
    """
    Async HTTP client using aiohttp.

    Designed for use with GRPO training and vLLM colocate mode.
    """

    def __init__(self, base_url: str = DEFAULT_URL, timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._episode_id: Optional[str] = None
        self._session: Any = None

    async def __aenter__(self) -> AsyncBugTriageEnvClient:
        import aiohttp

        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self._session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._session:
            await self._session.close()

    async def reset(self, task_id: str = "task_1") -> Dict[str, Any]:
        """Start a new episode."""
        async with self._session.post(
            f"{self.base_url}/reset",
            json={"task_id": task_id},
        ) as resp:
            data = await resp.json()
            self._episode_id = data.get("episode_id")
            return data

    async def step(
        self,
        episode_id: Optional[str] = None,
        action: Optional[BugTriageAction] = None,
    ) -> Dict[str, Any]:
        """Execute one triage action."""
        ep_id = episode_id or self._episode_id
        if ep_id is None:
            raise ValueError("Call reset() first.")
        if action is None:
            raise ValueError("action required.")
        async with self._session.post(
            f"{self.base_url}/step",
            json={"episode_id": ep_id, "action": action.model_dump()},
        ) as resp:
            return await resp.json()

    async def state(self) -> Dict[str, Any]:
        """Return current episode state."""
        async with self._session.get(f"{self.base_url}/state") as resp:
            return await resp.json()
