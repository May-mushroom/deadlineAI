"""Pure functions (no database access): classify a task and build the data models from any source."""
import uuid
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Optional

from app.api.api_schema import TaskRequest
from app.core.constants import SRC_GOOGLE, SRC_MANUAL, STATUS_ASSIGNED, STATUS_DONE, STATUS_UNASSIGNED
from database.models import Task, TaskDistribution
from database.models.data_models import get_week_start


@dataclass
class Placement:
    """Where a task lives. Known date -> a day (status 1 + distribution). Unknown date -> a week pool (status 0)."""
 
    deadline: date
    status: int
    week_start: Optional[str]  # ISO Monday, only for known-date tasks
    day_of_week: Optional[int]  # 0 = Monday, only for known-date tasks


@dataclass
class NormalizedTask:
    task: Task
    distribution: Optional[TaskDistribution]


def classify(scheduled_date: Optional[date]) -> str:
    """'specific' = known date, 'pool' = unknown date."""
    return "specific" if scheduled_date else "pool"


def place(scheduled_date: Optional[date], pool_week: Optional[date], done: bool = False,
          today: Optional[date] = None) -> Placement:
    """deadline = the chosen day, or the last day (Sunday) of the chosen week for pool tasks."""
    today = today or date.today()
    if classify(scheduled_date) == "specific":
        return Placement(
            deadline=scheduled_date,
            status=STATUS_DONE if done else STATUS_ASSIGNED,
            week_start=get_week_start(scheduled_date).isoformat(),
            # day_of_week=scheduled_date.weekday(),
             day_of_week=scheduled_date,

        )
    week = get_week_start(pool_week or today)
    return Placement(week + timedelta(days=6), STATUS_DONE if done else STATUS_UNASSIGNED, None, None)


def _build(user_id: str, task_id: str, title: str, category: str, importance: int,
           description: str, placement: Placement, today: date) -> NormalizedTask:
    task = Task(
        user_id=user_id, task_id=task_id, task_title=title, category=category,
        deadline=placement.deadline, importance=importance, status=placement.status,
        created_at=today, description=description,
    )
    dist = None
    if placement.week_start is not None:
        dist = TaskDistribution(
            distribution_id=uuid.uuid4().hex, week_start=placement.week_start,
            task_id=task_id, day_of_week=placement.day_of_week,
        )
    return NormalizedTask(task, dist)


def normalize_manual(req: TaskRequest, user_id: str, today: Optional[date] = None) -> NormalizedTask:
    today = today or date.today()
    placement = place(req.scheduled_date, req.pool_week, False, today)
    return _build(user_id, uuid.uuid4().hex, req.title, req.category, req.importance,
                  req.description, placement, today)


def normalize_google_task(raw: dict[str, Any], user_id: str, today: Optional[date] = None) -> NormalizedTask:
    """Google Tasks item -> Task. A due date means a specific day; no due date means this week's pool."""
    today = today or date.today()
    due = raw.get("due")  # RFC 3339; Google only keeps the date part
    scheduled = date.fromisoformat(due[:10]) if due else None
    placement = place(scheduled, None, raw.get("status") == "completed", today)
    return _build(user_id, "gcal:" + raw["id"], SRC_GOOGLE, (raw.get("title") or "(untitled)")[:100], "", 5,
                  (raw.get("notes") or "")[:100], "", placement, today)


def normalize_google_event(raw: dict[str, Any]) -> Optional[dict[str, str]]:
    """Calendar event -> time block for the UI. All-day and cancelled events are skipped."""
    start = (raw.get("start") or {}).get("dateTime")
    end = (raw.get("end") or {}).get("dateTime")
    if not start or not end or raw.get("status") == "cancelled":
        return None
    # Google returns wall-clock times in the calendar's time zone, so slice instead of converting.
    return {
        "id": raw["id"],
        "title": raw.get("summary") or "(No title)",
        "date": start[:10],
        "start": start[11:16],
        "end": end[11:16] if end[:10] == start[:10] else "24:00",
    }
