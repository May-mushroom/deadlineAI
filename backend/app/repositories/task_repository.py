"""Database operations for Task and TaskDistribution. Every function that writes commits."""
import uuid
from datetime import date, timedelta
from typing import Any, Optional

from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import STATUS_ASSIGNED, STATUS_DONE, STATUS_UNASSIGNED
from database.models import Task, TaskAssessment, TaskDistribution

Row = tuple[Task, Optional[TaskDistribution]]


async def _next_task_number(session: AsyncSession) -> int:
    # max + 1 is fine for a single user; use a database sequence if writes become concurrent.
    return (await session.execute(select(func.coalesce(func.max(Task.task_number), 0)))).scalar_one() + 1


async def get_distribution(session: AsyncSession, task_id: str) -> Optional[TaskDistribution]:
    return (await session.execute(
        select(TaskDistribution).where(TaskDistribution.task_id == task_id)
    )).scalars().first()


async def get_task(session: AsyncSession, user_id: str, task_id: str) -> Optional[Row]:
    stmt = (select(Task, TaskDistribution)
            .outerjoin(TaskDistribution, TaskDistribution.task_id == Task.task_id)
            .where(Task.user_id == user_id, Task.task_id == task_id))
    row = (await session.execute(stmt)).first()
    return (row[0], row[1]) if row else None
 
async def list_week(session: AsyncSession, user_id: str, week_start: date) -> list[Row]:
    """Tasks scheduled in the week, plus the week's pool (no distribution, deadline inside the week)."""
    stmt = (select(Task, TaskDistribution)
            .outerjoin(TaskDistribution, TaskDistribution.task_id == Task.task_id)
            .where(Task.user_id == user_id)
            .where(or_(
                TaskDistribution.week_start == week_start.isoformat(),
                and_(TaskDistribution.task_id.is_(None),
                     Task.deadline.between(week_start, week_start + timedelta(days=6))),
            ))
            # .order_by(Task.task_number)
            )
    return [(t, d) for t, d in (await session.execute(stmt)).all()]


async def list_day(session: AsyncSession, user_id: str, day: date) -> list[Row]:
    week_start = day - timedelta(days=day.weekday())
    # day_of_week actually stores the full scheduled date (see normalizer.place()),
    # not a 0-6 weekday index, so it's compared to `day` directly.
    return [(t, d) for t, d in await list_week(session, user_id, week_start)
            if d is not None and d.day_of_week == day]


async def create_task(session: AsyncSession, task: Task, distribution: Optional[TaskDistribution]) -> Row:
    # task.task_number = await _next_task_number(session)
    session.add(task)
    await session.flush()
    if distribution is not None:
        session.add(distribution)
    await session.commit()
    return task, distribution


async def _set_distribution(session: AsyncSession, task_id: str, week_start: str, day_of_week: int) -> TaskDistribution:
    dist = await get_distribution(session, task_id)
    if dist is None:
        dist = TaskDistribution(distribution_id=uuid.uuid4().hex, task_id=task_id,
                                week_start=week_start, day_of_week=day_of_week)
        session.add(dist)
    else:
        dist.week_start, dist.day_of_week = week_start, day_of_week
    return dist


async def update_task(session: AsyncSession, task: Task, fields: dict[str, Any], placement=None) -> Row:
    """Apply edited fields; `placement` (from ingestion.normalizer.place) moves the task to a day or a pool."""
    for key, value in fields.items():
        setattr(task, key, value)
    dist = await get_distribution(session, task.task_id)
    if placement is not None:
        task.deadline, task.status = placement.deadline, placement.status
        if placement.week_start is not None:
            dist = await _set_distribution(session, task.task_id, placement.week_start, placement.day_of_week)
        elif dist is not None:
            await session.delete(dist)
            dist = None
    await session.commit()
    return task, dist


async def set_done(session: AsyncSession, task: Task, done: bool) -> Row:
    dist = await get_distribution(session, task.task_id)
    task.status = STATUS_DONE if done else (STATUS_ASSIGNED if dist else STATUS_UNASSIGNED)
    await session.commit()
    return task, dist


async def delete_task(session: AsyncSession, user_id: str, task_id: str) -> bool:
    if await get_task(session, user_id, task_id) is None:
        return False
    await session.execute(delete(TaskDistribution).where(TaskDistribution.task_id == task_id))
    await session.execute(delete(TaskAssessment).where(TaskAssessment.task_id == task_id))
    await session.execute(delete(Task).where(Task.task_id == task_id))
    await session.commit()
    return True


async def upsert_google_task(session: AsyncSession, normalized) -> str:
    """Create or refresh a task that came from Google Tasks. Returns 'created' or 'updated'."""
    new, new_dist = normalized.task, normalized.distribution
    row = await get_task(session, new.user_id, new.task_id)
    if row is None:
        await create_task(session, new, new_dist)
        return "created"
    task, dist = row
    task.task_title, task.description = new.task_title, new.description
    if new.status == STATUS_DONE:
        task.status = STATUS_DONE
    elif task.status == STATUS_DONE:
        task.status = STATUS_ASSIGNED if (dist or new_dist) else STATUS_UNASSIGNED
    if new_dist is not None:  # Google has a due date; with none, keep any placement chosen locally
        task.deadline = new.deadline
        await _set_distribution(session, task.task_id, new_dist.week_start, new_dist.day_of_week)
        if task.status != STATUS_DONE:
            task.status = STATUS_ASSIGNED
    await session.commit()
    return "updated"

async def create_task_assessment(session: AsyncSession, assessment: dict) -> TaskAssessment:
    """Insert or refresh the TaskAssessment for assessment['task_id'] (one row per task)."""
    existing = (await session.execute(
        select(TaskAssessment).where(TaskAssessment.task_id == assessment["task_id"])
    )).scalars().first()
    if existing is None:
        existing = TaskAssessment(
            assessment_id=assessment["assessment_id"],
            task_id=assessment["task_id"],
            priority_score=assessment["priority_score"],
            estimated_effort=assessment["estimated_effort"],
        )
        session.add(existing)
    else:
        existing.priority_score = assessment["priority_score"]
        existing.estimated_effort = assessment["estimated_effort"]
    await session.commit()
    return existing


async def assign_to_day(session: AsyncSession, task_id: str, week_start: str, day: date) -> Optional[Row]:
    """Apply one Distribute result: give the task a specific day and mark it assigned."""
    task = (await session.execute(select(Task).where(Task.task_id == task_id))).scalars().first()
    if task is None:
        return None
    dist = await _set_distribution(session, task_id, week_start, day)
    task.status = STATUS_ASSIGNED
    await session.commit()
    return task, dist