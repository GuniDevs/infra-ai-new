# Task Tracker API

A small FastAPI + SQLite service, used to test the Infra AI GitHub App.

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m uvicorn app.main:app --reload
```

Docs at http://localhost:8000/docs. Tests: `python -m pytest`.

Endpoints: `POST/GET /tasks`, `GET/PATCH/DELETE /tasks/{id}`, `POST /tasks/{id}/complete`, `GET /stats`, `GET /healthz`.
List filters: `status`, `priority`, `tag`, `search`, `overdue`, `limit`, `offset`.
"# infra-ai" 
