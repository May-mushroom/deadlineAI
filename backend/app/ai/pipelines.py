import asyncio
import uuid

from app.ai.processors import (
  EffortProcessor,
  PriorityProcessor,
  SchedulingProcessor,
)


class SchedulingPipeline:
  """Orchestrate the process of scheduling a pool of tasks onto available time blocks."""

  def __init__(self, scheduler: SchedulingProcessor):
    self.scheduler = scheduler

  def run(self, available_time: list[dict], task_assessments: list) -> dict:
    return self.scheduler.process(available_time, task_assessments)


class AnalyzingTask:
  """
  Orchestrate the process: task -> estimate effort (in hours) -> calculate priority score.

  Returns a dict ready to persist as a TaskAssessment row; the caller handles saving it.
  Works on 1 task at a time.
  """

  def __init__(self):
    self.effort_processor = EffortProcessor()
    self.priority_processor = PriorityProcessor()

  async def run(self, task) -> dict:
    # EffortProcessor.process() calls the (blocking) Ollama client, so it runs in a
    # worker thread instead of blocking the event loop.
    estimated_effort = await asyncio.to_thread(self.effort_processor.process, task)
    priority_score = self.priority_processor.process(task, estimated_effort)
    return {
      "assessment_id": uuid.uuid4().hex,
      "task_id": task.task_id,
      "estimated_effort": estimated_effort,
      "priority_score": priority_score,
    }