import pytest
from fastapi.testclient import TestClient

from app import db as dbmod
from app.main import app


@pytest.fixture
def client(tmp_path):
    path = str(tmp_path / "test.db")

    def override():
        conn = dbmod.connect(path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    app.dependency_overrides[dbmod.get_db] = override
    yield TestClient(app)
    app.dependency_overrides.clear()
