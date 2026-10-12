from typing import Any

from app.ai.interfaces import TaskProcessor


class NoOpProcessor(TaskProcessor):
    """Default processor: returns tasks unchanged."""

    async def process(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return tasks
