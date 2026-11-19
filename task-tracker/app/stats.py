"""Simple statistics over tasks."""

def completion_rate(done: int, total: int) -> float:
  if total == 0:
	  return 0.0
  return round(done / total * 100, 1)

"""gj""
def overdue(tasks: list[dict], today: str) -> list[dict]:
  return [t for t in tasks if not t.get("done") and t.get("due", "9999") < today]
