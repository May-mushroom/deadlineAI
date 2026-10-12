import asyncio

from app.ingestion import google_sync
from app.core.config import get_settings
from database.models import GoogleAccount

MON = "2026-10-05"


class FakeGoogle:
    def __init__(self, tasks=(), events=()):
        self.tasks, self.events = list(tasks), list(events)

    async def fetch(self, user_id, updated_min=None):
        return self.tasks

    async def list_events(self, time_min, time_max):
        return self.events


def run_sync(maker, monkeypatch, fake):
    async def go():
        async with maker() as session:
            account = await session.get(GoogleAccount, "dev-user")
            if account is None:
                account = GoogleAccount(user_id="dev-user", access_token="t")
                session.add(account)
                await session.commit()

            async def fake_client(*_):
                return fake
            monkeypatch.setattr(google_sync, "get_client", fake_client)
            return await google_sync.sync_google_tasks(session, account)
    return asyncio.run(go())


def titles(client, week_start):
    return {t["task_id"]: t for t in client.get("/api/task/week", params={"week_start": week_start}).json()}


def test_sync_creates_updates_and_deletes(client, maker, monkeypatch):
    due = "2026-10-09T00:00:00.000Z"
    counts = run_sync(maker, monkeypatch, FakeGoogle(tasks=[
        {"id": "a", "title": "With due", "due": due, "status": "needsAction"},
        {"id": "b", "title": "No due", "status": "needsAction"},
    ]))
    assert counts == {"created": 2, "updated": 0, "deleted": 0}
    tasks = titles(client, MON)
    assert tasks["gcal:a"]["status"] == 1 and tasks["gcal:a"]["src"] == "google_calendar"
    assert tasks["gcal:a"]["day_of_week"] == 4

    counts = run_sync(maker, monkeypatch, FakeGoogle(tasks=[
        {"id": "a", "title": "Renamed", "due": "2026-10-12T00:00:00.000Z", "status": "completed"},
        {"id": "b", "deleted": True},
    ]))
    assert counts == {"created": 0, "updated": 1, "deleted": 1}
    moved = titles(client, "2026-10-12")["gcal:a"]
    assert (moved["title"], moved["status"], moved["scheduled_date"]) == ("Renamed", 3, "2026-10-12")
    assert "gcal:b" not in titles(client, MON)


def test_events_endpoint_returns_only_timed_events_of_the_week(client, monkeypatch):
    fake = FakeGoogle(events=[
        {"id": "in", "summary": "Standup", "start": {"dateTime": "2026-10-06T09:30:00-04:00"}, "end": {"dateTime": "2026-10-06T10:00:00-04:00"}},
        {"id": "allday", "summary": "Holiday", "start": {"date": "2026-10-06"}, "end": {"date": "2026-10-07"}},
        {"id": "out", "summary": "Next week", "start": {"dateTime": "2026-10-12T09:00:00-04:00"}, "end": {"dateTime": "2026-10-12T10:00:00-04:00"}},
    ])
    async def fake_client(*_):
        return fake
    monkeypatch.setattr("app.api.google.get_client", fake_client)
    assert client.get("/api/integrations/google/events", params={"week_start": MON}).status_code == 409  # not connected

    # pretend an account is connected
    import app.api.google as g
    async def account(*_): return GoogleAccount(user_id="dev-user", access_token="t")
    monkeypatch.setattr(g, "get_account", account)
    r = client.get("/api/integrations/google/events", params={"week_start": MON})
    assert r.json() == [{"id": "in", "title": "Standup", "date": "2026-10-06", "start": "09:30", "end": "10:00"}]


def test_status_and_connect(client):
    assert client.get("/api/integrations/google/status").json() == {"connected": False}
    url = client.get("/api/integrations/google/connect").json()["url"]
    assert "tasks.readonly" in url and "calendar.readonly" in url and "state=" in url and "access_type=offline" in url


def test_callback_rejects_bad_state_and_handles_denial(client):
    assert client.get("/api/integrations/google/callback", params={"state": "nope", "code": "c"}).status_code == 400
    from app.integrations.google_auth import make_state
    r = client.get("/api/integrations/google/callback", params={"state": make_state("dev-user"), "error": "access_denied"},
                   follow_redirects=False)
    assert r.status_code == 307 and r.headers["location"].endswith("?google=denied")


def test_webhook_checks_token_and_ignores_initial_sync(client, monkeypatch):
    monkeypatch.setenv("GOOGLE_WEBHOOK_TOKEN", "secret")
    get_settings.cache_clear()
    calls = []
    monkeypatch.setattr("app.api.google.sync_user_in_background", lambda uid: calls.append(uid))
    try:
        url = "/api/integrations/google/webhook"
        assert client.post(url).status_code == 403
        assert client.post(url, headers={"X-Goog-Channel-Token": "wrong"}).status_code == 403
        ok = {"X-Goog-Channel-Token": "secret", "X-Goog-Channel-ID": "ch1"}
        assert client.post(url, headers={**ok, "X-Goog-Resource-State": "sync"}).status_code == 200
        assert client.post(url, headers={**ok, "X-Goog-Resource-State": "exists"}).status_code == 200
        assert calls == []  # no stored account owns channel "ch1"
    finally:
        get_settings.cache_clear()
