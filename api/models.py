from __future__ import annotations
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
from pydantic import field_validator

# Constants
VALID_STATUS = {"todo", "doing", "done", "archived"}
VALID_PRIORITY = {"low", "normal", "high"}


class Task(SQLModel, table=True):
    """Task model with validation"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    
    priority: str = Field(default="normal", index=True)
    status: str = Field(default="todo", index=True)
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    completed_at: Optional[datetime] = None
    
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


# I/O Schemas
class TaskCreate(SQLModel):
    """Payload to create a task"""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: str = Field(default="normal")
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: str) -> str:
        if v not in VALID_PRIORITY:
            raise ValueError(f'Priority must be one of: {VALID_PRIORITY}')
        return v


class TaskUpdate(SQLModel):
    """Payload to update a task (all fields optional)"""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: Optional[str] = None
    status: Optional[str] = None
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_PRIORITY:
            raise ValueError(f'Priority must be one of: {VALID_PRIORITY}')
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_STATUS:
            raise ValueError(f'Status must be one of: {VALID_STATUS}')
        return v


class TaskOut(SQLModel):
    """API response with all fields"""
    id: int
    title: str
    description: Optional[str]
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]


class BulkDeletePayload(SQLModel):
    """Payload for bulk deletion"""
    ids: list[int] = Field(min_length=1, max_length=100)


# === GRADES ===

class Grade(SQLModel, table=True):
    """Grade model with validation"""

    id: Optional[int] = Field(default=None, primary_key=True)
    subject: str = Field(index=True, min_length=1, max_length=200)
    date: str = Field(max_length=50)  # Format: "13 Dec."
    value: float = Field(ge=0, le=20)  # Grade out of 20
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GradeCreate(SQLModel):
    """Payload to create a grade"""
    subject: str = Field(min_length=1, max_length=200)
    date: str = Field(max_length=50)
    value: float = Field(ge=0, le=20)


class GradeOut(SQLModel):
    """API response with all fields"""
    id: int
    subject: str
    date: str
    value: float
    created_at: datetime


class GradeImportPayload(SQLModel):
    """Payload for bulk grade import"""
    grades: list[GradeCreate] = Field(min_length=1, max_length=100)