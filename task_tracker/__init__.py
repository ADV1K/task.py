from datetime import datetime
from enum import StrEnum, auto
from typing import Optional

from pydantic import BaseModel, Field

TaskID = Tag = str


class ProgressStatus(StrEnum):
    TODO = auto()
    ACTIVE = auto()
    DONE = auto()


class Task(BaseModel):
    description: str = ""
    status: ProgressStatus = ProgressStatus.TODO
    tags: set[Tag] = Field(default_factory=set)
    created_at: datetime = Field(default_factory=datetime.now)
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    description: Optional[str]
    status: Optional[ProgressStatus]
    created_at: Optional[datetime]
    due_date: Optional[datetime]

    class Config:
        from_attributes = True


class Base(Exception):
    pass


class StorageError(Base):
    pass


class TaskNotFoundError(Base):
    pass


class TaskUpdateError(Base):
    pass
