from datetime import datetime, timezone
from typing import Optional, List, Any, cast

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select
from sqlalchemy import desc, asc, func

from models import (
    Task, TaskCreate, TaskUpdate, TaskOut, BulkDeletePayload,
    VALID_STATUS, VALID_PRIORITY
)
from db import get_session
from exceptions import TaskNotFoundException
from logger import setup_logger

router = APIRouter(prefix="/tasks", tags=["tasks"])
logger = setup_logger("tasks")

# Helper pour colonnes SQL
TBL = cast(Any, Task).__table__.c


@router.get("", response_model=List[TaskOut])
def list_tasks(
    q: Optional[str] = Query(None, max_length=200, description="Search in title"),
    status: Optional[str] = Query(None, description=f"Filter by status: {VALID_STATUS}"),
    priority: Optional[str] = Query(None, description=f"Filter by priority: {VALID_PRIORITY}"),
    sort: str = Query("-created_at", description="Sort field"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Liste les tâches avec filtres, recherche et tri"""
    stmt = select(Task)

    # Filtres
    if q:
        stmt = stmt.where(TBL.title.ilike(f"%{q}%"))
    if status:
        if status not in VALID_STATUS:
            raise HTTPException(400, f"Invalid status. Must be one of: {VALID_STATUS}")
        stmt = stmt.where(TBL.status == status)
    if priority:
        if priority not in VALID_PRIORITY:
            raise HTTPException(400, f"Invalid priority. Must be one of: {VALID_PRIORITY}")
        stmt = stmt.where(TBL.priority == priority)

    # Tri
    sort_map = {
        "created_at": asc(TBL.created_at),
        "-created_at": desc(TBL.created_at),
        "updated_at": asc(TBL.updated_at),
        "-updated_at": desc(TBL.updated_at),
        "priority": asc(TBL.priority),
        "-priority": desc(TBL.priority),
        "status": asc(TBL.status),
        "-status": desc(TBL.status),
        "title": asc(TBL.title),
        "-title": desc(TBL.title),
    }
    
    if sort not in sort_map:
        raise HTTPException(400, f"Invalid sort. Must be one of: {list(sort_map.keys())}")
    
    stmt = stmt.order_by(sort_map[sort])
    stmt = stmt.offset(offset).limit(limit)

    with get_session() as session:
        tasks = list(session.exec(stmt))
        logger.info(f"Listed {len(tasks)} tasks (filters: q={q}, status={status}, priority={priority})")
        return tasks


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    """Crée une nouvelle tâche"""
    task = Task(
        title=payload.title.strip(),
        description=payload.description.strip() if payload.description else None,
        priority=payload.priority,
        status="todo",
    )
    
    with get_session() as session:
        session.add(task)
        session.commit()
        session.refresh(task)
        logger.info(f"Created task #{task.id}: {task.title}")
        return task


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int):
    """Récupère une tâche par ID"""
    with get_session() as session:
        task = session.get(Task, task_id)
        if not task:
            raise TaskNotFoundException(task_id)
        return task


@router.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate):
    """Met à jour une tâche"""
    with get_session() as session:
        task = session.get(Task, task_id)
        if not task:
            raise TaskNotFoundException(task_id)

        # Mise à jour des champs
        if payload.title is not None:
            task.title = payload.title.strip()
        if payload.description is not None:
            task.description = payload.description.strip() if payload.description else None
        if payload.priority is not None:
            task.priority = payload.priority
        if payload.status is not None:
            old_status = task.status
            task.status = payload.status
            
            # Marquer comme complétée
            if payload.status == "done" and old_status != "done":
                task.completed_at = datetime.now(timezone.utc)
            elif payload.status != "done" and old_status == "done":
                task.completed_at = None

        task.updated_at = datetime.now(timezone.utc)
        session.add(task)
        session.commit()
        session.refresh(task)
        logger.info(f"Updated task #{task.id}")
        return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    """Supprime une tâche"""
    with get_session() as session:
        task = session.get(Task, task_id)
        if not task:
            raise TaskNotFoundException(task_id)
        session.delete(task)
        session.commit()
        logger.info(f"Deleted task #{task_id}")


@router.post("/bulk-delete", status_code=status.HTTP_204_NO_CONTENT)
def bulk_delete_tasks(payload: BulkDeletePayload):
    """Supprime plusieurs tâches"""
    with get_session() as session:
        stmt = select(Task).where(Task.id.in_(payload.ids))
        tasks = session.exec(stmt).all()
        
        count = len(tasks)
        for task in tasks:
            session.delete(task)
        
        session.commit()
        logger.info(f"Bulk deleted {count} tasks")


@router.get("/stats/summary", response_model=dict)
def get_stats():
    """Statistiques des tâches"""
    with get_session() as session:
        total = session.exec(select(func.count(Task.id))).one()
        
        by_status = {}
        for s in VALID_STATUS:
            count = session.exec(
                select(func.count(Task.id)).where(Task.status == s)
            ).one()
            by_status[s] = count
        
        by_priority = {}
        for p in VALID_PRIORITY:
            count = session.exec(
                select(func.count(Task.id)).where(Task.priority == p)
            ).one()
            by_priority[p] = count
        
        return {
            "total": total,
            "by_status": by_status,
            "by_priority": by_priority,
        }