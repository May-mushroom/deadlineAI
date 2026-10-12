# ensure database/models/__init__.py imports your model classes. 
# This helps register all tables with SQLAlchemy metadata
from .base import Base
from .data_models import (
  GoogleAccount,
  Task,
  TaskAssessment,
  TaskDistribution,
  WeeklyStatistics,
)

__all__ = [
  "Base",
  "GoogleAccount",
  "Task",
  "TaskAssessment",
  "TaskDistribution",
  "WeeklyStatistics",
]