import sqlite3
from collections import Counter

from fastapi import APIRouter, Depends

from app import repo
from app.db import get_db

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("")
def stats(db: sqlite3.Connection = Depends(get_db)) -> dict:
    tasks = repo.list_tasks(db, limit=200)
    total = len(tasks)
    done = sum(1 for t in tasks if t.status == "done")
    return {
        "total": total,
        "by_status": dict(Counter(t.status.value for t in tasks)),
        "by_priority": dict(Counter(t.priority.value for t in tasks)),
        "overdue": sum(1 for t in tasks if t.overdue),
        "completion_rate": round(done / total, 2) if total else 0.0,
        "top_tags": Counter(tag for t in tasks for tag in t.tags).most_common(5),
    }
