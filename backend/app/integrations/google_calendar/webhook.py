"""Helpers for Google Calendar push notifications (no database access here)."""
import secrets
from typing import Optional


def token_is_valid(received: Optional[str], expected: str) -> bool:
    """Google echoes back the token we set when creating the channel (X-Goog-Channel-Token)."""
    return bool(expected) and bool(received) and secrets.compare_digest(received, expected)


def is_initial_sync(resource_state: Optional[str]) -> bool:
    """Google sends one 'sync' message right after a channel is created; it is not a change."""
    return resource_state == "sync"
