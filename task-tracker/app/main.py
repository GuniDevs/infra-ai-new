from fastapi import FastAPI

from app.routers import stats, tasks

app = FastAPI(title="Task Tracker v2", version="0.1.0")
app.include_router(tasks.router)
app.include_router(stats.router)

"""HI please chal jao"""
@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}

