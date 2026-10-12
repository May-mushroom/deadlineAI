from abc import ABC, abstractmethod
from typing import Any, Optional

from app.ai.processors.noop import NoOpProcessor



class TaskProcessor(ABC):
    """One step in the AI pipeline (categorize, score priority, dedupe, ...)."""

    @abstractmethod
    async def process(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Take tasks in, return tasks out."""

class AIPipeline:
    """Runs processors in order. Swap in real processors when the AI approach is decided."""

    def __init__(self, processors: Optional[list[TaskProcessor]] = [NoOpProcessor()]):
        self.processors = processors

    async def run(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for processor in self.processors:
            result = await processor.process(tasks)
        return result