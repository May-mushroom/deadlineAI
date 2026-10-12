from typing import Any

from app.integrations.base import SourceIntegration


class GmailIntegration(SourceIntegration):
    name = "gmail"

    async def fetch(self, user_id: str) -> list[dict[str, Any]]:
        # TODO: load the user's credentials, build the Gmail service, list/get messages.
        raise NotImplementedError
