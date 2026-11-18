"""All SQL lives here."""
import sqlite3
from datetime import date, datetime, timezone

from app.models import Priority, Status, Task, TaskCreate, TaskUpdate

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

"""All SQL lives here."""
def _row_to_task(row: sqlite3.Row) -> Task:
    due = date.fromisoformat(row["due_date"]) if row["due_date"] else None
    return Task(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        priority=row["priority"],
        status=row["status"],
        due_date=due,
        tags=[t for t in row["tags"].split(",") if t],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        overdue=bool(due and row["status"] != "done" and due < date.today()),
    )


def _clean_tags(tags: list[str]) -> str:
    return ",".join(sorted({t.strip().lower() for t in tags if t.strip() and "," not in t}))


def create(db: sqlite3.Connection, data: TaskCreate) -> Task:
    now = _now()
    cur = db.execute(
        "INSERT INTO tasks (title, description, priority, due_date, tags, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
        (
            data.title.strip(),
            data.description,
            data.priority.value,
            data.due_date.isoformat() if data.due_date else None,
            _clean_tags(data.tags),
            now,
            now,
        ),
    )
    return get(db, cur.lastrowid)  # type: ignore[arg-type]


def get(db: sqlite3.Connection, task_id: int) -> Task | None:
    row = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return _row_to_task(row) if row else None


def list_tasks(
    db: sqlite3.Connection,
    *,
    status: Status | None = None,
    priority: Priority | None = None,
    tag: str | None = None,
    search: str | None = None,
    overdue: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Task]:
    tasks = [_row_to_task(r) for r in db.execute("SELECT * FROM tasks").fetchall()]
    if status:
        tasks = [t for t in tasks if t.status == status]
    if priority:
        tasks = [t for t in tasks if t.priority == priority]
    if tag:
        tasks = [t for t in tasks if tag.lower() in t.tags]
    if search:
        s = search.lower()
        tasks = [t for t in tasks if s in t.title.lower() or s in t.description.lower()]
    if overdue is not None:
        tasks = [t for t in tasks if t.overdue == overdue]
    tasks.sort(key=lambda t: (t.status == "done", PRIORITY_ORDER[t.priority.value], t.due_date or date.max, t.id))
    return tasks[offset : offset + limit]


def update(db: sqlite3.Connection, task_id: int, data: TaskUpdate) -> Task | None:
    current = get(db, task_id)
    if current is None:
        return None
    merged = current.model_copy(update=data.model_dump(exclude_unset=True))
    db.execute(
        "UPDATE tasks SET title=?, description=?, priority=?, status=?, due_date=?, tags=?, updated_at=? WHERE id=?",
        (
            merged.title.strip(),
            merged.description,
            merged.priority.value,
            merged.status.value,
            merged.due_date.isoformat() if merged.due_date else None,
            _clean_tags(merged.tags),
            _now(),
            task_id,
        ),
    )
    return get(db, task_id)


def delete(db: sqlite3.Connection, task_id: int) -> bool:
    return db.execute("DELETE FROM tasks WHERE id = ?", (task_id,)).rowcount > 0
