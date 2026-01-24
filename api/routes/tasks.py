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

TBL = cast(Any, Task).__table__.c


def task_to_out(task: Task, subtasks: List[Task] = None) -> TaskOut:
    return TaskOut(
        id=task.id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        status=task.status,
        due_date=task.due_date,
        tags=task.tags,
        parent_id=task.parent_id,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
        subtasks=[task_to_out(st) for st in (subtasks or [])]
    )


@router.get("", response_model=List[TaskOut])
def list_tasks(
    q: Optional[str] = Query(None, max_length=200, description="Search in title"),
    status: Optional[str] = Query(None, description=f"Filter by status: {VALID_STATUS}"),
    priority: Optional[str] = Query(None, description=f"Filter by priority: {VALID_PRIORITY}"),
    sort: str = Query("-created_at", description="Sort field"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    include_subtasks: bool = Query(True, description="Include subtasks in response"),
):
    stmt = select(Task).where(TBL.parent_id == None)

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

        if include_subtasks:
            task_ids = [t.id for t in tasks]
            subtasks_stmt = select(Task).where(Task.parent_id.in_(task_ids))
            all_subtasks = list(session.exec(subtasks_stmt))
            subtasks_map = {}
            for st in all_subtasks:
                if st.parent_id not in subtasks_map:
                    subtasks_map[st.parent_id] = []
                subtasks_map[st.parent_id].append(st)

            result = [task_to_out(t, subtasks_map.get(t.id, [])) for t in tasks]
        else:
            result = [task_to_out(t) for t in tasks]

        logger.info(f"Listed {len(tasks)} tasks (filters: q={q}, status={status}, priority={priority})")
        return result


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    with get_session() as session:
        if payload.parent_id:
            parent = session.get(Task, payload.parent_id)
            if not parent:
                raise HTTPException(400, f"Parent task {payload.parent_id} not found")

        task = Task(
            title=payload.title.strip(),
            description=payload.description.strip() if payload.description else None,
            priority=payload.priority,
            status="todo",
            parent_id=payload.parent_id,
            due_date=payload.due_date,
            tags=payload.tags,
        )

        session.add(task)
        session.commit()
        session.refresh(task)
        logger.info(f"Created task #{task.id}: {task.title}" + (f" (subtask of #{payload.parent_id})" if payload.parent_id else ""))
        return task_to_out(task)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int):
    with get_session() as session:
        task = session.get(Task, task_id)
        if not task:
            raise TaskNotFoundException(task_id)

        subtasks_stmt = select(Task).where(Task.parent_id == task_id)
        subtasks = list(session.exec(subtasks_stmt))

        return task_to_out(task, subtasks)


@router.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate):
    with get_session() as session:
        task = session.get(Task, task_id)
        if not task:
            raise TaskNotFoundException(task_id)

        if payload.title is not None:
            task.title = payload.title.strip()
        if payload.description is not None:
            task.description = payload.description.strip() if payload.description else None
        if payload.priority is not None:
            task.priority = payload.priority
        if payload.status is not None:
            old_status = task.status
            task.status = payload.status

            if payload.status == "done" and old_status != "done":
                task.completed_at = datetime.now(timezone.utc)
            elif payload.status != "done" and old_status == "done":
                task.completed_at = None
        if payload.due_date is not None:
            task.due_date = payload.due_date
        if payload.tags is not None:
            task.tags = payload.tags

        task.updated_at = datetime.now(timezone.utc)
        session.add(task)
        session.commit()
        session.refresh(task)

        subtasks_stmt = select(Task).where(Task.parent_id == task_id)
        subtasks = list(session.exec(subtasks_stmt))

        logger.info(f"Updated task #{task.id}")
        return task_to_out(task, subtasks)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    with get_session() as session:
        task = session.get(Task, task_id)
        if not task:
            raise TaskNotFoundException(task_id)

        subtasks_stmt = select(Task).where(Task.parent_id == task_id)
        subtasks = list(session.exec(subtasks_stmt))
        for st in subtasks:
            session.delete(st)

        session.delete(task)
        session.commit()
        logger.info(f"Deleted task #{task_id} and {len(subtasks)} subtasks")


@router.post("/bulk-delete", status_code=status.HTTP_204_NO_CONTENT)
def bulk_delete_tasks(payload: BulkDeletePayload):
    with get_session() as session:
        stmt = select(Task).where(Task.id.in_(payload.ids))
        tasks = session.exec(stmt).all()

        count = len(tasks)
        for task in tasks:
            subtasks_stmt = select(Task).where(Task.parent_id == task.id)
            subtasks = list(session.exec(subtasks_stmt))
            for st in subtasks:
                session.delete(st)
            session.delete(task)

        session.commit()
        logger.info(f"Bulk deleted {count} tasks")


@router.get("/stats/summary", response_model=dict)
def get_stats():
    with get_session() as session:
        total = session.exec(select(func.count(Task.id)).where(Task.parent_id == None)).one()

        by_status = {}
        for s in VALID_STATUS:
            count = session.exec(
                select(func.count(Task.id)).where(Task.status == s, Task.parent_id == None)
            ).one()
            by_status[s] = count

        by_priority = {}
        for p in VALID_PRIORITY:
            count = session.exec(
                select(func.count(Task.id)).where(Task.priority == p, Task.parent_id == None)
            ).one()
            by_priority[p] = count

        return {
            "total": total,
            "by_status": by_status,
            "by_priority": by_priority,
        }
