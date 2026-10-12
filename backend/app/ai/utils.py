"""AI logic helpers (prompts, scoring utilities, scheduling)."""
import json
from datetime import date
from typing import Optional

from ollama import chat

MODEL_INFO = {
    "model": "qwen3:4b",
    "format": "json",
}

def estimate_effort(task) -> float:
  PROMPT = f"""
      Analyze this task: {task.title}
      tasks description: {task.description}

      Return a JSON object containing:
      - category: short task category
      - estimated_hours: estimated focused work hours (not deadline)
      - importance: integer from 1 to 5
      - reason: brief explanation

      Use reasonable assumptions for missing details.
  """
  response = chat(
    **MODEL_INFO,
    messages = [
        {"role": "system", "content": PROMPT}
    ])
  data = json.loads(response.message.content)
  return data['estimated_hours']
 

# ---------------------------------------------------------------------------
# Priority scoring
# ---------------------------------------------------------------------------

# Per-category priority weight (0-1). There's no category table yet, so this is a hardcoded
# placeholder; pass category_priority= to override it until categories are user-configurable.
DEFAULT_CATEGORY_PRIORITY: dict = {
    "work": 0.9,
    "school": 0.9,
    "health": 0.8,
    "finance": 0.7,
    "personal": 0.5,
    "chores": 0.4,
    "errands": 0.4,
    "leisure": 0.2,
}
NEUTRAL_CATEGORY_WEIGHT = 0.5  # used when a task's category isn't in the map above

# How much each factor contributes to the final 0-100 score. Should sum to 1.
SCORE_WEIGHTS = {
    "urgency": 0.35,     # how close the deadline is
    "importance": 0.30,  # the task's own importance (0-10); can outweigh a low-priority category
    "category": 0.20,
    "effort": 0.15,      # a big task with a close deadline needs to be scheduled sooner
}

URGENCY_HORIZON_DAYS = 14  # a deadline this far out (or further) scores ~0 urgency; overdue scores 1.0
EFFORT_CAP_HOURS = 8.0  # the effort factor saturates at this many hours


def _urgency(deadline: date, today: date) -> float:
    """1.0 for an overdue or due-today task, decaying linearly to 0.0 by URGENCY_HORIZON_DAYS out."""
    days_left = (deadline - today).days
    if days_left <= 0:
        return 1.0
    return max(0.0, 1.0 - days_left / URGENCY_HORIZON_DAYS)


def _effort_factor(estimated_effort: float, urgency: float) -> float:
    """Bigger tasks matter more as their deadline nears; a big task with a far-off deadline isn't urgent yet."""
    size = min(max(estimated_effort, 0.0), EFFORT_CAP_HOURS) / EFFORT_CAP_HOURS
    return size * urgency


def calculate_priority_score(
    task,
    estimated_effort: float,
    category_priority: Optional[dict] = None,
    today: Optional[date] = None,
) -> float:
    """Rule-based priority score, 0-100, highest = schedule first.

    Weighted sum of deadline urgency, the task's own importance, its category's weight, and its
    size, rather than a hard override — so a high `importance` pulls the score up even in a
    low-priority category, without a low-importance task in a high-priority category being
    ignored outright. The weights in SCORE_WEIGHTS are the knob to retune, or to later fit with
    a learned model instead of this rule-based version.
    """
    today = today or date.today()
    category_priority = category_priority or DEFAULT_CATEGORY_PRIORITY

    urgency = _urgency(task.deadline, today)
    importance_norm = max(0, min(task.importance, 10)) / 10
    category_weight = category_priority.get(task.category, NEUTRAL_CATEGORY_WEIGHT)
    effort = _effort_factor(estimated_effort, urgency)

    score = (
        SCORE_WEIGHTS["urgency"] * urgency
        + SCORE_WEIGHTS["importance"] * importance_norm
        + SCORE_WEIGHTS["category"] * category_weight
        + SCORE_WEIGHTS["effort"] * effort
    )
    return round(score * 100, 2)


# ---------------------------------------------------------------------------
# Scheduling
# ---------------------------------------------------------------------------

def _task_fields(assessment):
    """Pull (task_id, deadline, estimated_effort, priority_score) out of a TaskAssessment row.

    `assessment.task` must already be loaded (e.g. the caller used
    `selectinload(TaskAssessment.task)`) before this runs outside an active async session,
    otherwise accessing it here raises.
    """
    try:
        task_id = assessment.task_id
        deadline = assessment.task.deadline
    except Exception as exc:
        raise ValueError(
            "task_assessments entries must have `.task` already loaded "
            "(eager-load it, e.g. with selectinload(TaskAssessment.task))"
        ) from exc
    return task_id, deadline, assessment.estimated_effort, assessment.priority_score


def scheduling_algorithm(available_time: list, task_assessments: list) -> dict:
    """Greedy day assignment: highest priority_score first, best-fit day (least leftover
    capacity after the assignment) among the days on or before the task's deadline. A task is
    never split across days, and never scheduled past its deadline.

    available_time: [{"day": date, "hours": float}, ...]
    task_assessments: TaskAssessment rows (see _task_fields for what must be loaded)

    Returns:
        {"schedule": [{"day": date, "tasks": [task_id, ...]}, ...],
         "unscheduled": [{"task_id": str, "reason": str}, ...]}
    `unscheduled` lists tasks that don't fit any day before their deadline, so the caller can
    flag them as at risk and notify the user, instead of them silently slipping past the deadline.
    """
    remaining = {slot["day"]: slot["hours"] for slot in available_time}
    schedule = {day: [] for day in remaining}
    unscheduled = []

    rows = [_task_fields(a) for a in task_assessments]
    rows.sort(key=lambda r: r[3], reverse=True)  # priority_score, highest first

    for task_id, deadline, estimated_effort, _score in rows:
        candidates = sorted(
            (day for day in remaining if day <= deadline and remaining[day] >= estimated_effort),
            key=lambda day: remaining[day],  # best fit: least leftover capacity after assignment
        )
        if not candidates:
            unscheduled.append({"task_id": task_id, "reason": "not enough available time before the deadline"})
            continue
        day = candidates[0]
        remaining[day] -= estimated_effort
        schedule[day].append(task_id)

    return {
        "schedule": [{"day": day, "tasks": tasks} for day, tasks in schedule.items()],
        "unscheduled": unscheduled,
    }