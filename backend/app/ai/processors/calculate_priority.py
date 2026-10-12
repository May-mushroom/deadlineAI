from datetime import date
from typing import Optional

from app.ai.interfaces import TaskProcessor


class PriorityProcessor(TaskProcessor):
    """processor in calculating task's priority_score based on urgency and effort level. Process 1 task at a time """
    DEFAULT_CATEGORY_PRIORITY = {
        "work": 0.9,
        "school": 0.9,
        "health": 0.8,
        "finance": 0.7,
        "personal": 0.5,
        "chores": 0.4,
        "errands": 0.4,
        "leisure": 0.2,
    }

    NEUTRAL_CATEGORY_WEIGHT = 0.5

    SCORE_WEIGHTS = {
        "urgency": 0.35,
        "importance": 0.30,
        "category": 0.20,
        "effort": 0.15,
    }

    URGENCY_HORIZON_DAYS = 14
    EFFORT_CAP_HOURS = 8.0

    def __init__(self, category_priority: Optional[dict] = None):
        self.category_priority = (
            category_priority
            if category_priority is not None
            else self.DEFAULT_CATEGORY_PRIORITY.copy()
        )

    def process(
        self,
        task,
        estimated_effort: float,
        today: Optional[date] = None,
    ) -> float:
        today = today or date.today()

        urgency = self._urgency(task.deadline, today)
        importance = max(0, min(task.importance, 10)) / 10
        category = self.category_priority.get(
            task.category, self.NEUTRAL_CATEGORY_WEIGHT
        )
        effort = self._effort_factor(estimated_effort, urgency)

        weights = self.SCORE_WEIGHTS
        score = (
            weights["urgency"] * urgency
            + weights["importance"] * importance
            + weights["category"] * category
            + weights["effort"] * effort
        )

        return round(score * 100, 2)

    def _urgency(self, deadline: date, today: date) -> float:
        days_left = (deadline - today).days

        if days_left <= 0:
            return 1.0

        return max(0.0, 1.0 - days_left / self.URGENCY_HORIZON_DAYS)

    def _effort_factor(
        self, estimated_effort: float, urgency: float
    ) -> float:
        size = min(
            max(estimated_effort, 0.0), self.EFFORT_CAP_HOURS
        ) / self.EFFORT_CAP_HOURS

        return size * urgency