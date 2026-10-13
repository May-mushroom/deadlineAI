from typing import Any, Optional
import json
from datetime import date

from ollama import chat

from app.ai.interfaces import TaskProcessor

class EffortProcessor(TaskProcessor):
    """Estimate task effort (in hours) using an LLM. 
    The Processor works 1 task at a time"""

    MODEL_INFO = { 
        "model": "qwen3:4b",
        "format": "json",
    }

    def process(self, task: object) -> float:
        PROMPT = f"""
            Analyze this task: {task.task_title}
            tasks description: {task.description}
    
            Return a JSON object containing:
            - category: short task category
            - estimated_hours: estimated focused work hours (not deadline)
            - importance: integer from 1 to 5
            - reason: brief explanation
    
            Use reasonable assumptions for missing details.
        """

        response = chat(
            **self.MODEL_INFO,
            messages=[{"role": "user", "content": PROMPT}],
        )

        result = json.loads(response.message.content)
        estimated_effort = result["estimated_hours"]

        return estimated_effort


if __name__ == "__main__":
    class TestTask:
        task_title = "Build login page"
        description = "Create a login page with validation."

    processor = EffortProcessor()
    print(processor.process(TestTask()))