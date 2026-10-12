"""Shared Google OAuth helpers. OAuth runs in the backend so tokens never reach the browser."""
import asyncio
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

from app.core.config import get_settings

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
TASKS_SCOPES = ["https://www.googleapis.com/auth/tasks.readonly"]
ALL_SCOPES = GMAIL_SCOPES + CALENDAR_SCOPES
SYNC_SCOPES = CALENDAR_SCOPES + TASKS_SCOPES  # what the connect flow asks for today
TOKEN_URI = "https://oauth2.googleapis.com/token"

_PROCESS_SECRET = secrets.token_urlsafe(32)  # fallback for signing `state` when OAUTH_STATE_SECRET is unset


def utcnow() -> datetime:
    """Naive UTC now, the format google-auth uses for token expiry."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def build_flow(scopes: Optional[list[str]] = None) -> Flow:
    s = get_settings()
    if s.app_env == "development":
        os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")  # allow http://localhost redirects
    os.environ.setdefault("OAUTHLIB_RELAX_TOKEN_SCOPE", "1")  # Google may return extra scopes
    return Flow.from_client_config(
        {
            "web": {
                "client_id": s.google_client_id,
                "client_secret": s.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": TOKEN_URI,
                "redirect_uris": [s.google_redirect_uri],
            }
        },
        scopes=scopes or SYNC_SCOPES,
        redirect_uri=s.google_redirect_uri,
        # The connect and callback requests build separate Flow objects, so PKCE's verifier would be lost.
        autogenerate_code_verifier=False,
    )


def _state_secret() -> str:
    return get_settings().oauth_state_secret or _PROCESS_SECRET


def make_state(user_id: str) -> str:
    """Signed, short-lived `state` that carries the user id through Google's redirect."""
    exp = datetime.now(timezone.utc) + timedelta(minutes=10)
    return jwt.encode({"sub": user_id, "exp": exp}, _state_secret(), algorithm="HS256")


def read_state(state: str) -> str:
    """Return the user id from `state`. Raises jwt.PyJWTError if it is invalid or expired."""
    return jwt.decode(state, _state_secret(), algorithms=["HS256"])["sub"]


async def valid_credentials(account) -> tuple[Credentials, bool]:
    """Build Credentials from a stored GoogleAccount, refreshing them if expired.
    Returns (credentials, refreshed) so the caller can persist new tokens."""
    s = get_settings()
    creds = Credentials(
        token=account.access_token, refresh_token=account.refresh_token, token_uri=TOKEN_URI,
        client_id=s.google_client_id, client_secret=s.google_client_secret,
        scopes=SYNC_SCOPES, expiry=account.token_expiry,
    )
    if creds.expired and creds.refresh_token:
        await asyncio.to_thread(creds.refresh, Request())
        return creds, True
    return creds, False
