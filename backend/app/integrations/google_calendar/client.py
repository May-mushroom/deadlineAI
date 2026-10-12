"""Thin wrapper around the Google Calendar and Google Tasks APIs. The Google client is blocking,
so every call runs in a worker thread."""
import asyncio
from typing import Any, Optional

from googleapiclient.discovery import build

from app.integrations.base import SourceIntegration


class GoogleCalendarIntegration(SourceIntegration):
    name = "google_calendar"

    def __init__(self, credentials):
        self._creds = credentials

    def _service(self, api: str, version: str):
        return build(api, version, credentials=self._creds, cache_discovery=False)

    # ----- tasks (Google Tasks API: what Google Calendar shows as tasks) -----
    async def fetch(self, user_id: str, updated_min: Optional[str] = None) -> list[dict[str, Any]]:
        """All tasks (including completed and deleted) from every task list, optionally only those updated since `updated_min`."""
        return await asyncio.to_thread(self._fetch_tasks, updated_min)

    def _fetch_tasks(self, updated_min: Optional[str]) -> list[dict[str, Any]]:
        service = self._service("tasks", "v1")
        items: list[dict[str, Any]] = []
        for task_list in service.tasklists().list(maxResults=100).execute().get("items", []):
            page_token = None
            while True:
                params: dict[str, Any] = dict(tasklist=task_list["id"], showCompleted=True, showHidden=True,
                                              showDeleted=True, maxResults=100)
                if updated_min:
                    params["updatedMin"] = updated_min
                if page_token:
                    params["pageToken"] = page_token
                response = service.tasks().list(**params).execute()
                items.extend(response.get("items", []))
                page_token = response.get("nextPageToken")
                if not page_token:
                    break
        return items

    # ----- time blocks (Calendar events) -----
    async def list_events(self, time_min: str, time_max: str) -> list[dict[str, Any]]:
        """Events between two RFC 3339 timestamps, recurring events expanded."""
        def run():
            return self._service("calendar", "v3").events().list(
                calendarId="primary", timeMin=time_min, timeMax=time_max,
                singleEvents=True, orderBy="startTime", maxResults=250,
            ).execute().get("items", [])
        return await asyncio.to_thread(run)

    # ----- push notifications -----
    async def watch(self, channel_id: str, address: str, token: str) -> dict[str, Any]:
        """Ask Google to POST to `address` whenever the primary calendar changes."""
        body = {"id": channel_id, "type": "web_hook", "address": address, "token": token}
        return await asyncio.to_thread(
            lambda: self._service("calendar", "v3").events().watch(calendarId="primary", body=body).execute())

    async def stop_channel(self, channel_id: str, resource_id: str) -> None:
        body = {"id": channel_id, "resourceId": resource_id}
        await asyncio.to_thread(lambda: self._service("calendar", "v3").channels().stop(body=body).execute())
