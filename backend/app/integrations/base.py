from abc import ABC, abstractmethod
from typing import Any


class SourceIntegration(ABC):
    """A place tasks come from (Gmail, Calendar, ...). Fetches raw items; ingestion normalizes them."""

    name: str

    @abstractmethod
    async def fetch(self, user_id: str) -> list[dict[str, Any]]:
        """Return raw items from the external service for this user."""
