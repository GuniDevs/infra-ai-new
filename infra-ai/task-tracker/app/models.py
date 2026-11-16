from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Status(str, Enum):
    todo = "todo"
    doing = "doing"
    done = "done"


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)
    priority: Priority = Priority.medium
    due_date: date | None = None
    tags: list[str] = Field(default_factory=list, max_length=10)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    priority: Priority | None = None
    status: Status | None = None
    due_date: date | None = None
    tags: list[str] | None = Field(default=None, max_length=10)


class Task(BaseModel):
    id: int
    title: str
    description: str
    priority: Priority
    status: Status
    due_date: date | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime
    overdue: bool = False
