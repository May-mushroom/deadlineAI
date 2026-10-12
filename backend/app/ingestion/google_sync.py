"""Pulls Google Tasks into the database and keeps the Calendar push channel alive."""
import asyncio
import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.ingestion.normalizer import normalize_google_task
from app.integrations.google_auth import utcnow, valid_credentials
from app.integrations.google_calendar.client import GoogleCalendarIntegration
from app.repositories import task_repository as repo
from app.repositories.google_account_repository import get_account, save_tokens
from database.models import GoogleAccount
from database.session import get_sessionmaker
 
logger = logging.getLogger(__name__)
_locks: dict[str, asyncio.Lock] = {}  # one sync at a time per user (single-process; use a DB lock if you scale out)


async def get_client(session: AsyncSession, account: GoogleAccount) -> GoogleCalendarIntegration:
    creds, refreshed = await valid_credentials(account)
    if refreshed:
        await save_tokens(session, account.user_id, creds)
    return GoogleCalendarIntegration(creds)


async def sync_google_tasks(session: AsyncSession, account: GoogleAccount) -> dict[str, int]:
    async with _locks.setdefault(account.user_id, asyncio.Lock()):
        return await _sync_google_tasks(session, account)


async def _sync_google_tasks(session: AsyncSession, account: GoogleAccount) -> dict[str, int]:
    started = utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")  # taken before fetching so nothing is missed
    client = await get_client(session, account)
    counts = {"created": 0, "updated": 0, "deleted": 0}
    for raw in await client.fetch(account.user_id, updated_min=account.tasks_synced_at):
        if raw.get("deleted"):
            if await repo.delete_task(session, account.user_id, "gcal:" + raw["id"]):
                counts["deleted"] += 1
            continue
        counts[await repo.upsert_google_task(session, normalize_google_task(raw, account.user_id))] += 1
    account.tasks_synced_at = started
    await session.commit()
    return counts


async def ensure_watch(session: AsyncSession, account: GoogleAccount) -> bool:
    """Create (or renew) the Calendar push channel. Needs PUBLIC_BASE_URL and GOOGLE_WEBHOOK_TOKEN."""
    s = get_settings()
    if not (s.public_base_url and s.google_webhook_token):
        return False
    if account.channel_id and account.channel_expiry and account.channel_expiry - utcnow() > timedelta(days=1):
        return False
    client = await get_client(session, account)
    if account.channel_id and account.channel_resource_id:
        try:
            await client.stop_channel(account.channel_id, account.channel_resource_id)
        except Exception:
            logger.warning("Could not stop the old Google channel", exc_info=True)
    address = s.public_base_url.rstrip("/") + "/api/integrations/google/webhook"
    response = await client.watch(uuid.uuid4().hex, address, s.google_webhook_token)
    account.channel_id = response["id"]
    account.channel_resource_id = response.get("resourceId")
    expiry_ms = int(response["expiration"])  # epoch milliseconds
    account.channel_expiry = datetime.fromtimestamp(expiry_ms / 1000, timezone.utc).replace(tzinfo=None)
    await session.commit()
    return True


async def sync_user_in_background(user_id: str) -> None:
    """Runs after a webhook or the OAuth callback has already returned its response."""
    try:
        async with get_sessionmaker()() as session:
            account = await get_account(session, user_id)
            if account is not None:
                await sync_google_tasks(session, account)
                await ensure_watch(session, account)
    except Exception:
        logger.exception("Background Google sync failed for user %s", user_id)
