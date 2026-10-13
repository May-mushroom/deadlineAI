"""Orchestrates normalize -> save for tasks entered by the user."""
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_schema import TaskRequest
from app.core.constants import STATUS_DONE
from app.ingestion.normalizer import normalize_manual, place
from app.repositories import task_repository as repo
from database.models import Task


async def add_manual_task(session: AsyncSession, user_id: str, req: TaskRequest):
    normalized = normalize_manual(req, user_id)
    return await repo.create_task(session, normalized.task, normalized.distribution)


async def edit_task(session: AsyncSession, task: Task, req: TaskRequest):
    fields: dict[str, Any] = {
        "task_title": req.title, "category": req.category, "importance": req.importance,
        "description": req.description,
    }
    # Move the task only when the request names a day or a week; otherwise keep where it is.
    placement = None
    if req.scheduled_date or req.pool_week:
        placement = place(req.scheduled_date, req.pool_week, done=task.status == STATUS_DONE)
    return await repo.update_task(session, task, fields, placement)
