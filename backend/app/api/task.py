import datetime as dt
from types import SimpleNamespace
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.pipelines import AnalyzingTask, SchedulingPipeline
from app.ai.processors import SchedulingProcessor
from app.api.api_schema import TaskDoneRequest, TaskOut, TaskRequest
from app.core.auth import CurrentUser, get_current_user
from app.ingestion import service
from app.ingestion.availability import get_available_hours
from app.ingestion.normalizer import classify
from app.repositories import task_repository as repo
from app.repositories.google_account_repository import clear_schedule_stale
from database.models.data_models import get_week_start
from database.session import get_session

router = APIRouter(prefix="/task", tags=["task"])
analyzing_task = AnalyzingTask()
scheduling_pipeline = SchedulingPipeline(SchedulingProcessor())



async def _get_or_404(session: AsyncSession, user_id: str, task_id: str):
    row = await repo.get_task(session, user_id, task_id)
    if row is None:
        raise HTTPException(404, "Task not found")
    return row

 
## Retrieve data
@router.get("/today", response_model=list[TaskOut])
async def get_tasks_of_today(today: dt.date, session: AsyncSession = Depends(get_session),
                             user: CurrentUser = Depends(get_current_user)):
    """Tasks scheduled for one day."""
    return [TaskOut.from_models(t, d) for t, d in await repo.list_day(session, user.id, today)]


@router.get("/week", response_model=list[TaskOut])
async def get_tasks_of_week(week_start: dt.date, session: AsyncSession = Depends(get_session),
                            user: CurrentUser = Depends(get_current_user)):
    """Tasks scheduled in the week plus that week's pool. Any date inside the week works."""
    rows = await repo.list_week(session, user.id, get_week_start(week_start))
    return [TaskOut.from_models(t, d) for t, d in rows]
 

@router.get("/dashboard")
async def get_dashboard_data() -> object:
    raise HTTPException(501, "Dashboard is not implemented yet")

 
## CREATE TASK
@router.post("/add/{add_stream}", response_model=TaskOut, status_code=201)
async def add_task(add_stream: Literal["specific", "pool"], body: TaskRequest,
                   session: AsyncSession = Depends(get_session),
                   user: CurrentUser = Depends(get_current_user)):
    kind = classify(body.scheduled_date)
    if kind != add_stream:
        raise HTTPException(422, f"This is a '{kind}' task but it was sent to /add/{add_stream}")
    task, dist = await service.add_manual_task(session, user.id, body)
    return TaskOut.from_models(task, dist)


## GET TASK
@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: str, session: AsyncSession = Depends(get_session),
                   user: CurrentUser = Depends(get_current_user)):
    return TaskOut.from_models(*await _get_or_404(session, user.id, task_id))


## UPDATE TASK (edit fields and/or move it to another day or pool)
@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(task_id: str, body: TaskRequest, session: AsyncSession = Depends(get_session),
                      user: CurrentUser = Depends(get_current_user)):
    task, _ = await _get_or_404(session, user.id, task_id)
    return TaskOut.from_models(*await service.edit_task(session, task, body))


## MARK DONE / NOT DONE (status 3 = done)
@router.patch("/{task_id}/done", response_model=TaskOut)
async def set_task_done(task_id: str, body: TaskDoneRequest, session: AsyncSession = Depends(get_session),
                        user: CurrentUser = Depends(get_current_user)):
    task, dist = await _get_or_404(session, user.id, task_id)
    # TODO (task_repository.set_done, not included in this change set):
    # when body.done is False, status should revert to 0 (unassigned) if the
    # task has no TASK_DISTRIBUTION row (still pool/never distributed), or 1
    # (assigned) if it does (`dist` here tells you which). set_done currently
    # only takes a bool, so it needs to apply that rule itself, or this route
    # should pass the target status through once that signature changes.
    return TaskOut.from_models(*await repo.set_done(session, task, body.done))


## DISTRIBUTE (schedule this week's currently-unscheduled pool tasks onto available days)
## Only pool tasks move; tasks already assigned to a day are left untouched for now.
@router.post("/distribute")
async def distribute_week(week_start: dt.date, session: AsyncSession = Depends(get_session),
                          user: CurrentUser = Depends(get_current_user)):
    monday = get_week_start(week_start)
    pool_tasks = [t for t, d in await repo.list_week(session, user.id, monday) if d is None]
    if not pool_tasks:
        return {"scheduled": [], "unscheduled": []}

    assessments = []
    for task in pool_tasks:
        result = await analyzing_task.run(task)
        await repo.create_task_assessment(session, result)
        assessments.append(SimpleNamespace(
            task_id=task.task_id, task=task,
            estimated_effort=result["estimated_effort"], priority_score=result["priority_score"],
        ))

    available = await get_available_hours(session, user.id, monday)
    plan = scheduling_pipeline.run(available, assessments)

    scheduled_out = []
    for day_entry in plan["schedule"]:
        for task_id in day_entry["tasks"]:
            row = await repo.assign_to_day(session, task_id, monday.isoformat(), day_entry["day"])
            if row:
                scheduled_out.append(TaskOut.from_models(*row))

    await clear_schedule_stale(session, user.id)
    return {"scheduled": scheduled_out, "unscheduled": plan["unscheduled"]}


## DELETE TASK
@router.delete("/delete/{task_id}")
async def delete_task(task_id: str, session: AsyncSession = Depends(get_session),
                      user: CurrentUser = Depends(get_current_user)):
    if not await repo.delete_task(session, user.id, task_id):
        raise HTTPException(404, "Task not found")
    return {"deleted": task_id}