from datetime import date

from app.ai.interfaces import TaskProcessor

"""
available_time = [
    {"day": date(2026, 10, 12), "hours": 4},
    {"day": date(2026, 10, 13), "hours": 6},
]
remaining = {
    date(2026, 10, 12): 4,
    date(2026, 10, 13): 6,
}
"""
class SchedulingProcessor(TaskProcessor):
    def process(
        self,
        available_time: list,
        task_assessments: list,
    ) -> dict:
        remaining = {
            slot["day"]: slot["hours"]
            for slot in available_time
        }
        schedule = {day: [] for day in remaining}
        unscheduled = []

        rows = [self._task_fields(a) for a in task_assessments]
        rows.sort(key=lambda r: r[3], reverse=True)

        for task_id, deadline, estimated_effort, _score in rows:
            candidates = sorted(
                (
                    day for day in remaining
                    if day <= deadline
                    and remaining[day] >= estimated_effort
                ),
                key=lambda day: remaining[day],
            )

            if not candidates:
                unscheduled.append({
                    "task_id": task_id,
                    "reason": "not enough available time before the deadline",
                })
                continue

            day = candidates[0]
            remaining[day] -= estimated_effort
            schedule[day].append(task_id)

        return {
            "schedule": [
                {"day": day, "tasks": tasks}
                for day, tasks in schedule.items()
            ],
            "unscheduled": unscheduled,
        }

    def _task_fields(self, assessment):
        """Extract scheduling fields from a TaskAssessment."""
        try:
            task_id = assessment.task_id
            deadline = assessment.task.deadline
        except Exception as exc:
            raise ValueError(
                "TaskAssessment.task must be loaded before scheduling."
            ) from exc

        return (
            task_id,
            deadline,
            assessment.estimated_effort,
            assessment.priority_score,
        )