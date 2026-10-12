from datetime import date

MON = "2026-10-05"  # Monday of the test week


def add(client, stream, **body):
    body.setdefault("title", "Task")
    return client.post(f"/api/task/add/{stream}", json=body)


def week(client, week_start=MON):
    return client.get("/api/task/week", params={"week_start": week_start}).json()


def test_add_specific_creates_task_and_distribution(client):
    r = add(client, "specific", scheduled_date="2026-10-09", importance=8)
    assert r.status_code == 201
    t = r.json()
    assert (t["status"], t["week_start"], t["day_of_week"], t["scheduled_date"]) == (1, MON, 4, "2026-10-09")
    assert t["pool_week_start"] is None and t["task_number"] == 1


def test_add_pool_creates_task_only(client):
    t = add(client, "pool", pool_week="2026-10-14").json()
    assert (t["status"], t["week_start"], t["scheduled_date"]) == (0, None, None)
    assert (t["deadline"], t["pool_week_start"]) == ("2026-10-18", "2026-10-12")


def test_stream_must_match_payload(client):
    assert add(client, "pool", scheduled_date="2026-10-09").status_code == 422
    assert add(client, "specific").status_code == 422
    assert add(client, "specific", title="", scheduled_date="2026-10-09").status_code == 422


def test_week_returns_scheduled_and_pool_tasks_of_that_week_only(client):
    add(client, "specific", title="Fri", scheduled_date="2026-10-09")
    add(client, "pool", title="Pool now", pool_week=MON)
    add(client, "pool", title="Pool next", pool_week="2026-10-12")
    add(client, "specific", title="Next Mon", scheduled_date="2026-10-12")
    assert [t["title"] for t in week(client)] == ["Fri", "Pool now"]
    assert [t["title"] for t in week(client, "2026-10-14")] == ["Pool next", "Next Mon"]  # any date in the week works
    assert [t["title"] for t in client.get("/api/task/today", params={"today": "2026-10-09"}).json()] == ["Fri"]


def test_task_numbers_increase(client):
    assert [add(client, "pool").json()["task_number"] for _ in range(3)] == [1, 2, 3]


def test_edit_moves_between_pool_and_day(client):
    tid = add(client, "pool", title="Move me").json()["task_id"]
    t = client.patch(f"/api/task/{tid}", json={"title": "Moved", "scheduled_date": "2026-10-08"}).json()
    assert (t["title"], t["status"], t["day_of_week"], t["deadline"]) == ("Moved", 1, 3, "2026-10-08")
    t = client.patch(f"/api/task/{tid}", json={"title": "Moved", "pool_week": "2026-10-12"}).json()
    assert (t["status"], t["week_start"], t["pool_week_start"]) == (0, None, "2026-10-12")
    # no placement sent -> only fields change
    t = client.patch(f"/api/task/{tid}", json={"title": "Renamed", "importance": 2}).json()
    assert (t["title"], t["importance"], t["pool_week_start"]) == ("Renamed", 2, "2026-10-12")


def test_done_sets_status_3_and_undo_restores(client):
    day = add(client, "specific", scheduled_date="2026-10-09").json()["task_id"]
    pool = add(client, "pool").json()["task_id"]
    assert client.patch(f"/api/task/{day}/done", json={"done": True}).json()["status"] == 3
    assert client.patch(f"/api/task/{day}/done", json={"done": False}).json()["status"] == 1
    assert client.patch(f"/api/task/{pool}/done", json={"done": True}).json()["status"] == 3
    assert client.patch(f"/api/task/{pool}/done", json={"done": False}).json()["status"] == 0


def test_edit_keeps_done_status(client):
    tid = add(client, "specific", scheduled_date="2026-10-09").json()["task_id"]
    client.patch(f"/api/task/{tid}/done", json={"done": True})
    assert client.patch(f"/api/task/{tid}", json={"title": "x", "scheduled_date": "2026-10-10"}).json()["status"] == 3


def test_get_and_delete(client):
    tid = add(client, "specific", scheduled_date="2026-10-09").json()["task_id"]
    assert client.get(f"/api/task/{tid}").json()["task_id"] == tid
    assert client.delete(f"/api/task/delete/{tid}").json() == {"deleted": tid}
    assert client.get(f"/api/task/{tid}").status_code == 404
    assert client.delete(f"/api/task/delete/{tid}").status_code == 404
    assert week(client) == []
