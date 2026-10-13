from sqlalchemy import String, Text, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import date, datetime, timedelta
from typing import Optional

from .base import Base

## TASK MODELS
class Task(Base):
  __tablename__ = "TASK"
  user_id: Mapped[str] = mapped_column()
  task_id: Mapped[str] = mapped_column(
    primary_key=True,
    nullable=False   
  )

  task_title: Mapped[str] = mapped_column(String(100), nullable=False)
  category: Mapped[str] = mapped_column(String(100))
  deadline: Mapped[date] = mapped_column()

  importance: Mapped[int] = mapped_column() # on scale of 10
  status: Mapped[int] = mapped_column() # 0:unassigned, 1:assigned, 2:pending 3:done

  created_at: Mapped[date] = mapped_column() 
  description: Mapped[str] = mapped_column(String(100))

  __table_args__ = (
    CheckConstraint("importance BETWEEN 0 AND 10", name="check importance"),
    CheckConstraint("status BETWEEN 0 AND 3", name="check status")
  )
  task_assessment: Mapped["TaskAssessment | None"]= relationship(back_populates="task") 

      ## FUTURE PLAN
  # task_number: Mapped[int] = mapped_column(unique=True)
  # src: Mapped[str] = mapped_column(String(100), nullable=False)
  # note: Mapped[str] = mapped_column(String(100))

class TaskAssessment(Base):
  __tablename__ = "TASK_ASSESSMENT"
  assessment_id: Mapped[str] = mapped_column(primary_key=True, nullable=False)
  task_id:  Mapped[str] = mapped_column(
    ForeignKey("TASK.task_id"),
    unique=True,
    nullable=False
  )
  priority_score: Mapped[float] = mapped_column()
  estimated_effort: Mapped[int] = mapped_column() # in hours 

  task: Mapped["Task"] = relationship(back_populates="task_assessment")

# this table later on maybe data source for fine-tuning workflow
class WeeklyStatistics(Base):
  __tablename__ = "WEEKLY_STATISTICS"
  stat_id: Mapped[str] = mapped_column(
    String(100),
    primary_key=True,
    nullable=False
  )
  week_start: Mapped[date] = mapped_column(
    String(100),
    unique=True,
    nullable=False
  )
  total_task_created: Mapped[int] = mapped_column()
  total_task_completed: Mapped[int] = mapped_column()
  total_late: Mapped[int] = mapped_column()
  average_delay: Mapped[float] = mapped_column()

  __table_args__ = (
    CheckConstraint("total_task_created >= 0", name="check total_task_created"),
    CheckConstraint("total_task_completed >= 0", name="check total_task_completed"),
    CheckConstraint("total_late >= 0", name="check total_late"),
    CheckConstraint("average_delay >= 0", name="check average_delay")
  )

class TaskDistribution(Base):
  __tablename__ = "TASK_DISTRIBUTION"
  distribution_id: Mapped[str] = mapped_column(
    String(100),
    primary_key=True,
    nullable=False
  )
  week_start: Mapped[date] = mapped_column(
    String(100),
    nullable=False
  )
  task_id: Mapped[str] = mapped_column(
    ForeignKey("TASK.task_id"),
    nullable=False
  )
  day_of_week: Mapped[date] = mapped_column()  # map later 0=Monday, 6=Sunday

## AUTH SYSTEM (to be implemented later)
class User(Base):
  __tablename__ = "USER"
  user_id: Mapped[str] = mapped_column(
    String(100),
    primary_key=True
  )
  username: Mapped[str] = mapped_column(
    String(100),
    unique=True
  )
  password: Mapped[str] = mapped_column(
    String(100),
    unique=True
  )



## GOOGLE INTEGRATION
class GoogleAccount(Base):
  """OAuth tokens and sync state for one user's connected Google account."""
  __tablename__ = "GOOGLE_ACCOUNT"
  user_id: Mapped[str] = mapped_column(String(100), primary_key=True)
  access_token: Mapped[str] = mapped_column(Text)
  refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
  token_expiry: Mapped[Optional[datetime]] = mapped_column(nullable=True)  # naive UTC
  tasks_synced_at: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # RFC 3339, Google Tasks updatedMin
  channel_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Calendar push channel
  channel_resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
  channel_expiry: Mapped[Optional[datetime]] = mapped_column(nullable=True)  # naive UTC
  # True once a Calendar webhook fires; cleared after the next successful /task/distribute call.
  schedule_stale: Mapped[bool] = mapped_column(default=False)

## HELPER FUNCTIONS
def get_week_start(d: date) -> date:
    return d - timedelta(days=d.weekday())