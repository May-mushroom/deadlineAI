import asyncio
import datetime as dt
import logging
from typing import Optional

import jwt
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.core.config import get_settings
from app.ingestion.google_sync import ensure_watch, get_client, sync_google_tasks, sync_user_in_background
from app.ingestion.normalizer import normalize_google_event
from app.integrations.google_auth import build_flow, make_state, read_state
from app.integrations.google_calendar.webhook import is_initial_sync, token_is_valid
from app.repositories.google_account_repository import get_account, get_account_by_channel, save_tokens
from database.session import get_session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/integrations/google", tags=["google"])


async def _require_account(session: AsyncSession, user_id: str):
    account = await get_account(session, user_id)
    if account is None:
        raise HTTPException(409, "Google is not connected")
    return account


@router.get("/connect")
async def connect(user: CurrentUser = Depends(get_current_user)):
    """Returns the Google consent URL; the frontend sends the browser there."""
    url, _ = build_flow().authorization_url(
        access_type="offline", prompt="consent", include_granted_scopes="true", state=make_state(user.id))
    return {"url": url}


@router.get("/callback")
async def callback(state: str, background: BackgroundTasks, code: Optional[str] = None,
                   error: Optional[str] = None, session: AsyncSession = Depends(get_session)):
    """Google redirects the browser here. No bearer token is available, so the signed `state` identifies the user."""
    frontend = get_settings().frontend_url
    try:
        user_id = read_state(state)
    except jwt.PyJWTError:
        raise HTTPException(400, "Invalid or expired OAuth state")
    if error or not code:
        return RedirectResponse(f"{frontend}?google=denied")
    flow = build_flow()
    await asyncio.to_thread(flow.fetch_token, code=code)
    await save_tokens(session, user_id, flow.credentials)
    background.add_task(sync_user_in_background, user_id)  # first sync + webhook channel
    return RedirectResponse(f"{frontend}?google=connected")


@router.get("/status")
async def status(session: AsyncSession = Depends(get_session), user: CurrentUser = Depends(get_current_user)):
    return {"connected": await get_account(session, user.id) is not None}


@router.post("/sync")
async def sync(session: AsyncSession = Depends(get_session), user: CurrentUser = Depends(get_current_user)):
    """Pull Google Tasks into the database now."""
    account = await _require_account(session, user.id)
    counts = await sync_google_tasks(session, account)
    try:
        await ensure_watch(session, account)
    except Exception:
        logger.warning("Could not create the Google webhook channel", exc_info=True)
    return counts


@router.get("/events")
async def events(week_start: dt.date, session: AsyncSession = Depends(get_session),
                 user: CurrentUser = Depends(get_current_user)):
    """Time blocks (timed Calendar events) for the week. Fetched live, not stored."""
    account = await _require_account(session, user.id)
    monday = week_start - dt.timedelta(days=week_start.weekday())
    # Pad the window by a day each side, then keep events whose date is inside the week.
    time_min = f"{monday - dt.timedelta(days=1)}T00:00:00Z"
    time_max = f"{monday + dt.timedelta(days=8)}T00:00:00Z"
    raw = await (await get_client(session, account)).list_events(time_min, time_max)
    week = {(monday + dt.timedelta(days=i)).isoformat() for i in range(7)}
    blocks = (normalize_google_event(e) for e in raw)
    return [b for b in blocks if b and b["date"] in week]


@router.post("/webhook")
async def webhook(request: Request, background: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    """Google Calendar push notifications. Public endpoint: guarded by the channel token instead of a login."""
    headers = request.headers
    if not token_is_valid(headers.get("x-goog-channel-token"), get_settings().google_webhook_token):
        raise HTTPException(403, "Invalid channel token")
    if is_initial_sync(headers.get("x-goog-resource-state")):
        return {"ok": True}
    account = await get_account_by_channel(session, headers.get("x-goog-channel-id", ""))
    if account is not None:
        background.add_task(sync_user_in_background, account.user_id)
    return {"ok": True}
