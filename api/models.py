from __future__ import annotations
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
from pydantic import field_validator

# Constantes
VALID_STATUS = {"todo", "doing", "done", "archived"}
VALID_PRIORITY = {"low", "normal", "high"}


class Task(SQLModel, table=True):
    """Modèle de tâche avec validation"""
    
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


# Schémas E/S
class TaskCreate(SQLModel):
    """Payload pour créer une tâche"""
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
    """Payload pour mettre à jour une tâche (tous champs optionnels)"""
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
    """Réponse API avec tous les champs"""
    id: int
    title: str
    description: Optional[str]
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]


class BulkDeletePayload(SQLModel):
    """Payload pour suppression groupée"""
    ids: list[int] = Field(min_length=1, max_length=100)