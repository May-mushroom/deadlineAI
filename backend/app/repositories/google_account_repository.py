from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import GoogleAccount


async def get_account(session: AsyncSession, user_id: str) -> Optional[GoogleAccount]:
    return await session.get(GoogleAccount, user_id)

 
async def get_account_by_channel(session: AsyncSession, channel_id: str) -> Optional[GoogleAccount]:
    return (await session.execute(
        select(GoogleAccount).where(GoogleAccount.channel_id == channel_id)
    )).scalars().first()


async def clear_schedule_stale(session: AsyncSession, user_id: str) -> None:
    account = await session.get(GoogleAccount, user_id)
    if account is not None:
        account.schedule_stale = False
        await session.commit()


async def save_tokens(session: AsyncSession, user_id: str, credentials) -> GoogleAccount:
    """Insert or update the OAuth tokens. A refresh token is only sent on first consent, so keep the old one."""
    account = await session.get(GoogleAccount, user_id)
    if account is None:
        account = GoogleAccount(user_id=user_id)
        session.add(account)
    account.access_token = credentials.token
    account.refresh_token = credentials.refresh_token or account.refresh_token
    account.token_expiry = credentials.expiry
    await session.commit()
    return account