import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from app import repo
from app.db import get_db
from app.models import Priority, Status, Task, TaskCreate, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=Task, status_code=201)
def create_task(data: TaskCreate, db: sqlite3.Connection = Depends(get_db)) -> Task:
    return repo.create(db, data)


@router.get("", response_model=list[Task])
def list_tasks(
    status: Status | None = None,
    priority: Priority | None = None,
    tag: str | None = None,
    search: str | None = Query(default=None, max_length=100),
    overdue: bool | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: sqlite3.Connection = Depends(get_db),
) -> list[Task]:
    return repo.list_tasks(
        db, status=status, priority=priority, tag=tag, search=search, overdue=overdue, limit=limit, offset=offset
    )


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int, db: sqlite3.Connection = Depends(get_db)) -> Task:
    task = repo.get(db, task_id)
    if task is None:
        raise HTTPException(404, "task not found")
    return task


@router.patch("/{task_id}", response_model=Task)
def update_task(task_id: int, data: TaskUpdate, db: sqlite3.Connection = Depends(get_db)) -> Task:
    task = repo.update(db, task_id, data)
    if task is None:
        raise HTTPException(404, "task not found")
    return task


@router.post("/{task_id}/complete", response_model=Task)
def complete_task(task_id: int, db: sqlite3.Connection = Depends(get_db)) -> Task:
    task = repo.update(db, task_id, TaskUpdate(status=Status.done))
    if task is None:
        raise HTTPException(404, "task not found")
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: sqlite3.Connection = Depends(get_db)) -> Response:
    if not repo.delete(db, task_id):
        raise HTTPException(404, "task not found")
    return Response(status_code=204)


@router.get("/overdue/list", response_model=list[Task])
def overdue_tasks(db: sqlite3.Connection = Depends(get_db)) -> list[Task]:
    """Tasks past their due date that are not done yet."""
    return [t for t in repo.list_tasks(db, limit=200) if t.overdue]
