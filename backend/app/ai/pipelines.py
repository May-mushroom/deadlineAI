import uuid

from ai.processors import (
  EffortProcessor,
  PriorityProcessor,
  SchedulingProcessor
) 
from database.models import TaskAssessment

class SchedulingPipeline:
  """
  Orchestrate the process of scheduling a pool of tasks.

  Each task undergoes: estimate efforts (in hours) -> calculate priority score -> schedule to available time block
  """

  def __init__(self, scheduler: SchedulingProcessor): self.scheduler = scheduler

  def run(available_time: list[dict], task_assessments: list[TaskAssessment]) -> dict: 
    final_schedule = self.scheduler.process(available_time, task_assessments)
    return final_schedule


class AnalyzingTask: 
  """
    Orchestrate the process: task -> estimate efforts (in hours) -> calculate priority score 
    -> update task assessments to database

    This processor works on 1 task at a time
  """
  def __init__(self):
    self.effort_processor = EffortProcessor(),
    self.priority_processor = PriorityProcessor(),

  def run(task) -> TaskAssessment: 
    estimated_effort = self.effort_processor.process(task)
    priority_score = self.priority_processor.process(task, estimated_effort)
    task_assessment= {
      "assessment_id": uuid.uuid4(),
      "task_id": task["task_id"] ,
      "estimated_effort": estimated_effort,
      "priority_score": priority_score
    }     
    return task_assessment


    

