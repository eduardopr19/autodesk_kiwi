from __future__ import annotations

from datetime import datetime, timezone

from pydantic import field_validator
from sqlmodel import Field, SQLModel

VALID_STATUS = {"todo", "doing", "done", "archived"}
VALID_PRIORITY = {"low", "normal", "high"}
VALID_RECURRENCE = {"daily", "weekly", "monthly", None}


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)

    priority: str = Field(default="normal", index=True)
    status: str = Field(default="todo", index=True)
    due_date: datetime | None = Field(default=None, index=True)
    tags: str | None = Field(default=None, max_length=500)
    parent_id: int | None = Field(default=None, foreign_key="task.id", index=True)
    recurrence: str | None = Field(default=None, index=True)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    completed_at: datetime | None = None

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: str) -> str:
        if v not in VALID_PRIORITY:
            raise ValueError(f'Priority must be one of: {VALID_PRIORITY}')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in VALID_STATUS:
            raise ValueError(f'Status must be one of: {VALID_STATUS}')
        return v

    @field_validator('recurrence')
    @classmethod
    def validate_recurrence(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_RECURRENCE:
            raise ValueError(f'Recurrence must be one of: {VALID_RECURRENCE}')
        return v


class TaskCreate(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    priority: str = Field(default="normal")
    due_date: datetime | None = None
    tags: str | None = Field(default=None, max_length=500)
    parent_id: int | None = None
    recurrence: str | None = None

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: str) -> str:
        if v not in VALID_PRIORITY:
            raise ValueError(f'Priority must be one of: {VALID_PRIORITY}')
        return v

    @field_validator('recurrence')
    @classmethod
    def validate_recurrence(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_RECURRENCE:
            raise ValueError(f'Recurrence must be one of: {VALID_RECURRENCE}')
        return v


class TaskUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    priority: str | None = None
    status: str | None = None
    due_date: datetime | None = None
    tags: str | None = Field(default=None, max_length=500)
    parent_id: int | None = None
    recurrence: str | None = None

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_PRIORITY:
            raise ValueError(f'Priority must be one of: {VALID_PRIORITY}')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_STATUS:
            raise ValueError(f'Status must be one of: {VALID_STATUS}')
        return v

    @field_validator('recurrence')
    @classmethod
    def validate_recurrence(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_RECURRENCE:
            raise ValueError(f'Recurrence must be one of: {VALID_RECURRENCE}')
        return v


class TaskOut(SQLModel):
    id: int
    title: str
    description: str | None
    priority: str
    status: str
    due_date: datetime | None
    tags: str | None
    parent_id: int | None
    recurrence: str | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    subtasks: list[TaskOut] = []


class BulkDeletePayload(SQLModel):
    ids: list[int] = Field(min_length=1, max_length=100)


class Grade(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    subject: str = Field(index=True, min_length=1, max_length=200)
    date: str = Field(max_length=50)
    value: float = Field(ge=0, le=20)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GradeCreate(SQLModel):
    subject: str = Field(min_length=1, max_length=200)
    date: str = Field(max_length=50)
    value: float = Field(ge=0, le=20)


class GradeOut(SQLModel):
    id: int
    subject: str
    date: str
    value: float
    created_at: datetime


class GradeImportPayload(SQLModel):
    grades: list[GradeCreate] = Field(min_length=1, max_length=100)
