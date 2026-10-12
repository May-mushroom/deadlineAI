import datetime as dt
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_schema import TaskDoneRequest, TaskRequest, TaskResponse
from app.core.auth import CurrentUser, get_current_user
from app.ingestion import service
from app.ingestion.normalizer import classify
from app.repositories import task_repository as repo
from database.models.data_models import get_week_start
from database.session import get_session

router = APIRouter(prefix="/task", tags=["task"])

async def _get_or_404(session: AsyncSession, user_id: str, task_id: str):
    row = await repo.get_task(session, user_id, task_id)
    if row is None:
        raise HTTPException(404, "Task not found")
    return row

 
## Retrieve data
@router.get("/today", response_model=list[TaskResponse])
async def get_tasks_of_today(today: dt.date, session: AsyncSession = Depends(get_session),
                             user: CurrentUser = Depends(get_current_user)):
    """Tasks scheduled for one day."""
    return [TaskResponse.from_models(t, d) for t, d in await repo.list_day(session, user.id, today)]


@router.get("/week", response_model=list[TaskResponse])
async def get_tasks_of_week(week_start: dt.date, session: AsyncSession = Depends(get_session),
                            user: CurrentUser = Depends(get_current_user)):
    """Tasks scheduled in the week plus that week's pool. Any date inside the week works."""
    rows = await repo.list_week(session, user.id, get_week_start(week_start))
    return [TaskResponse.from_models(t, d) for t, d in rows]


@router.get("/dashboard")
async def get_dashboard_data() -> object:
    raise HTTPException(501, "Dashboard is not implemented yet")


## CREATE TASK
@router.post("/add/{add_stream}", response_model=TaskResponse, status_code=201)
async def add_task(add_stream: Literal["specific", "pool"], body: TaskRequest,
                   session: AsyncSession = Depends(get_session),
                   user: CurrentUser = Depends(get_current_user)):
    kind = classify(body.scheduled_date)
    if kind != add_stream:
        raise HTTPException(422, f"This is a '{kind}' task but it was sent to /add/{add_stream}")
    task, dist = await service.add_manual_task(session, user.id, body)
    return TaskResponse.from_models(task, dist)


## GET TASK
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, session: AsyncSession = Depends(get_session),
                   user: CurrentUser = Depends(get_current_user)):
    return TaskResponse.from_models(*await _get_or_404(session, user.id, task_id))


## UPDATE TASK (edit fields and/or move it to another day or pool)
@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, body: TaskRequest, session: AsyncSession = Depends(get_session),
                      user: CurrentUser = Depends(get_current_user)):
    task, _ = await _get_or_404(session, user.id, task_id)
    return TaskResponse.from_models(*await service.edit_task(session, task, body))


## MARK DONE / NOT DONE (status 3 = done)
@router.patch("/{task_id}/done", response_model=TaskResponse)
async def set_task_done(task_id: str, body: TaskDoneRequest, session: AsyncSession = Depends(get_session),
                        user: CurrentUser = Depends(get_current_user)):
    task, _ = await _get_or_404(session, user.id, task_id)
    return TaskResponse.from_models(*await repo.set_done(session, task, body.done))


## DELETE TASK
@router.delete("/delete/{task_id}")
async def delete_task(task_id: str, session: AsyncSession = Depends(get_session),
                      user: CurrentUser = Depends(get_current_user)):
    if not await repo.delete_task(session, user.id, task_id):
        raise HTTPException(404, "Task not found")
    return {"deleted": task_id}
