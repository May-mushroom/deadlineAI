from datetime import date

import pytest
from pydantic import ValidationError

from app.api.api_schema import TaskRequest
from app.ingestion.normalizer import classify, normalize_google_event, normalize_google_task, normalize_manual, place

TODAY = date(2026, 10, 7)  # a Wednesday; its week starts Monday 2026-10-05


def test_classify():
    assert classify(date(2026, 10, 9)) == "specific"
    assert classify(None) == "pool"


def test_specific_day_gets_status_1_and_a_distribution():
    n = normalize_manual(TaskRequest(title="Write report", scheduled_date=date(2026, 10, 11)), "u1", TODAY)
    assert n.task.status == 1 and n.task.src == "manual"
    assert n.task.deadline == date(2026, 10, 11)
    # Sunday is the last day of the Monday-based week
    assert (n.distribution.week_start, n.distribution.day_of_week) == ("2026-10-05", 6)


def test_pool_task_gets_status_0_and_no_distribution():
    n = normalize_manual(TaskRequest(title="Someday"), "u1", TODAY)
    assert n.task.status == 0 and n.distribution is None
    assert n.task.deadline == date(2026, 10, 11)  # last day of the current week


def test_other_week_pool_uses_that_weeks_last_day():
    n = normalize_manual(TaskRequest(title="Later", pool_week=date(2026, 10, 14)), "u1", TODAY)
    assert n.task.deadline == date(2026, 10, 18)


def test_defaults_fill_not_null_columns():
    t = normalize_manual(TaskRequest(title="x"), "u1", TODAY).task
    assert (t.category, t.description, t.note, t.importance, t.created_at) == ("", "", "", 5, TODAY)


def test_place_done_keeps_status_3():
    assert place(date(2026, 10, 9), None, done=True, today=TODAY).status == 3
    assert place(None, None, done=True, today=TODAY).status == 3


@pytest.mark.parametrize("bad", [
    {"title": "  "}, {"title": "x" * 101}, {"title": "x", "importance": 11},
    {"title": "x", "scheduled_date": "2026-10-09", "pool_week": "2026-10-05"},
])
def test_request_validation(bad):
    with pytest.raises(ValidationError):
        TaskRequest(**bad)


def test_google_task_with_due_date_is_specific():
    raw = {"id": "abc", "title": "Pay rent", "notes": "n", "due": "2026-10-09T00:00:00.000Z", "status": "needsAction"}
    n = normalize_google_task(raw, "u1", TODAY)
    assert (n.task.task_id, n.task.src, n.task.status) == ("gcal:abc", "google_calendar", 1)
    assert n.distribution.day_of_week == 4  # Friday


def test_google_task_without_due_goes_to_this_weeks_pool_and_completed_is_done():
    n = normalize_google_task({"id": "x", "title": "", "status": "completed"}, "u1", TODAY)
    assert n.task.task_title == "(untitled)" and n.task.status == 3 and n.distribution is None


def test_google_event_to_time_block():
    ev = {"id": "e", "summary": "Standup", "start": {"dateTime": "2026-10-06T09:30:00-04:00"},
          "end": {"dateTime": "2026-10-06T10:00:00-04:00"}}
    assert normalize_google_event(ev) == {"id": "e", "title": "Standup", "date": "2026-10-06", "start": "09:30", "end": "10:00"}
    assert normalize_google_event({"id": "a", "start": {"date": "2026-10-06"}, "end": {"date": "2026-10-07"}}) is None
    overnight = {"id": "o", "start": {"dateTime": "2026-10-06T22:00:00Z"}, "end": {"dateTime": "2026-10-07T01:00:00Z"}}
    assert normalize_google_event(overnight)["end"] == "24:00"
