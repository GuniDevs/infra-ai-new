from datetime import date, timedelta


def make(client, **kw):
    body = {"title": "Write docs", **kw}
    r = client.post("/tasks", json=body)
    assert r.status_code == 201, r.text
    return r.json()


def test_health(client):
    assert client.get("/healthz").json() == {"status": "ok"}


def test_create_and_get(client):
    t = make(client, priority="high", tags=["Work", " work ", "home"])
    assert t["status"] == "todo" and t["tags"] == ["home", "work"]
    assert client.get(f"/tasks/{t['id']}").json()["title"] == "Write docs"


def test_validation(client):
    assert client.post("/tasks", json={"title": ""}).status_code == 422
    assert client.post("/tasks", json={"title": "x", "priority": "urgent"}).status_code == 422


def test_not_found(client):
    assert client.get("/tasks/999").status_code == 404
    assert client.patch("/tasks/999", json={"title": "x"}).status_code == 404
    assert client.delete("/tasks/999").status_code == 404


def test_update_is_partial(client):
    t = make(client, description="keep me")
    r = client.patch(f"/tasks/{t['id']}", json={"status": "doing"})
    assert r.json()["status"] == "doing" and r.json()["description"] == "keep me"


def test_complete_and_delete(client):
    t = make(client)
    assert client.post(f"/tasks/{t['id']}/complete").json()["status"] == "done"
    assert client.delete(f"/tasks/{t['id']}").status_code == 204
    assert client.get(f"/tasks/{t['id']}").status_code == 404


def test_filters_and_sorting(client):
    make(client, title="low one", priority="low", tags=["a"])
    make(client, title="high one", priority="high", tags=["b"])
    done = make(client, title="finished", priority="high")
    client.post(f"/tasks/{done['id']}/complete")
    titles = [t["title"] for t in client.get("/tasks").json()]
    assert titles == ["high one", "low one", "finished"]  # priority first, done last
    assert [t["title"] for t in client.get("/tasks?tag=b").json()] == ["high one"]
    assert [t["title"] for t in client.get("/tasks?status=done").json()] == ["finished"]
    assert [t["title"] for t in client.get("/tasks?search=LOW").json()] == ["low one"]


def test_overdue(client):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    t = make(client, title="late", due_date=yesterday)
    assert t["overdue"] is True
    assert [x["title"] for x in client.get("/tasks?overdue=true").json()] == ["late"]
    client.post(f"/tasks/{t['id']}/complete")
    assert client.get(f"/tasks/{t['id']}").json()["overdue"] is False


def test_paging(client):
    for i in range(5):
        make(client, title=f"t{i}")
    assert len(client.get("/tasks?limit=2").json()) == 2
    assert len(client.get("/tasks?limit=2&offset=4").json()) == 1
    assert client.get("/tasks?limit=0").status_code == 422


def test_stats(client):
    make(client, priority="high", tags=["x"])
    d = make(client, tags=["x", "y"])
    client.post(f"/tasks/{d['id']}/complete")
    s = client.get("/stats").json()
    assert s["total"] == 2 and s["completion_rate"] == 0.5
    assert s["by_status"] == {"todo": 1, "done": 1}
    assert s["top_tags"][0] == ["x", 2]


def test_overdue_list_only_has_late_open_tasks(client):
    client.post("/tasks", json={"title": "late", "due_date": "2000-01-01"})
    client.post("/tasks", json={"title": "later", "due_date": "2999-01-01"})
    titles = [t["title"] for t in client.get("/tasks/overdue/list").json()]
    assert titles == ["late"]


def test_reopen(client):
    t = make(client)
    client.post(f"/tasks/{t['id']}/complete")
    r = client.post(f"/tasks/{t['id']}/reopen")
    assert r.status_code == 200 and r.json()["status"] == "todo"
    assert client.post("/tasks/999/reopen").status_code == 404


def test_stats_counts_open_tasks(client):
    make(client)
    d = make(client)
    client.post(f"/tasks/{d['id']}/complete")
    assert client.get("/stats").json()["open"] == 1
