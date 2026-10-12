"""Request/response formats shared by the frontend, the API and the repositories."""
import datetime as dt
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from database.models import Task, TaskDistribution
from database.models.data_models import get_week_start

class TaskRequest(BaseModel):
    """Body for adding or editing a task. Set `scheduled_date` for a specific day,
    or `pool_week` (any date inside the target week) for a week pool task."""

    title: str = Field(min_length=1, max_length=100)
    category: str = Field("", max_length=100)
    deadlines: date
    importance: int = Field(5, ge=0, le=10)
    description: str = Field("", max_length=100)
    note: str = Field("", max_length=100)
    scheduled_date: Optional[dt.date] = None
    pool_week: Optional[dt.date] = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("title must not be blank")
        return v

    @model_validator(mode="after")
    def one_placement(self):
        if self.scheduled_date and self.pool_week:
            raise ValueError("send either scheduled_date or pool_week, not both")
        return self


class TaskDoneRequest(BaseModel):
    done: bool


class TaskResponse(BaseModel):
    task_id: str
    task_number: int
    title: str
    src: str
    category: str
    deadline: dt.date
    importance: int
    status: int  # 0 unassigned, 1 assigned, 2 pending, 3 done
    created_at: dt.date
    description: str
    note: str
    # From TASK_DISTRIBUTION (None for week pool tasks)
    week_start: Optional[str] = None
    day_of_week: Optional[int] = None
    scheduled_date: Optional[dt.date] = None
    # Monday of the pool week (None once the task has a specific day)
    pool_week_start: Optional[dt.date] = None

    @classmethod
    def from_models(cls, task: Task, dist: Optional[TaskDistribution] = None) -> "TaskResponse":
        scheduled = None
        if dist is not None:
            scheduled = dt.date.fromisoformat(dist.week_start) + dt.timedelta(days=dist.day_of_week)
        return cls(
            task_id=task.task_id,
            task_number=task.task_number,
            title=task.task_title,
            src=task.src,
            category=task.category,
            deadline=task.deadline,
            importance=task.importance,
            status=task.status,
            created_at=task.created_at,
            description=task.description,
            note=task.note,
            week_start=dist.week_start if dist else None,
            day_of_week=dist.day_of_week if dist else None,
            scheduled_date=scheduled,
            pool_week_start=None if dist else get_week_start(task.deadline),
        )
