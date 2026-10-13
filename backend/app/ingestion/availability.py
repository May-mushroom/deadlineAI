"""Available hours per day, fixed rule:

    24h - 7h sleep (12am-7am) - total Calendar event hours that day, floored at 0.

If Google Calendar isn't connected, the event deduction is skipped (24h - 7h for every day).
"""
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.google_sync import get_client
from app.ingestion.normalizer import normalize_google_event
from app.repositories.google_account_repository import get_account
from database.models.data_models import get_week_start

HOURS_PER_DAY = 24.0
SLEEP_HOURS = 7.0  # fixed rule: 12am-7am


def _duration_hours(start: str, end: str) -> float:
    """start/end are 'HH:MM' strings (end may be '24:00' for events crossing midnight)."""
    start_min = int(start[:2]) * 60 + int(start[3:5])
    end_min = 24 * 60 if end == "24:00" else int(end[:2]) * 60 + int(end[3:5])
    return max(0.0, (end_min - start_min) / 60)


async def get_available_hours(session: AsyncSession, user_id: str, week_start: date) -> list[dict]:
    """[{"day": date, "hours": float}, ...] for the 7 days (Mon-Sun) of week_start's week."""
    monday = get_week_start(week_start)
    days = [monday + timedelta(days=i) for i in range(7)]
    baseline = HOURS_PER_DAY - SLEEP_HOURS

    account = await get_account(session, user_id)
    if account is None:
        return [{"day": d, "hours": baseline} for d in days]

    client = await get_client(session, account)
    time_min = f"{monday}T00:00:00Z"
    time_max = f"{monday + timedelta(days=7)}T00:00:00Z"
    raw = await client.list_events(time_min, time_max)
    blocks = [b for b in (normalize_google_event(e) for e in raw) if b]

    committed: dict[date, float] = {}
    for b in blocks:
        d = date.fromisoformat(b["date"])
        committed[d] = committed.get(d, 0.0) + _duration_hours(b["start"], b["end"])

    return [{"day": d, "hours": max(0.0, baseline - committed.get(d, 0.0))} for d in days]