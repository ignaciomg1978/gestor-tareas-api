import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from aplicacion.base_de_datos import Base, get_db
from aplicacion.principal import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_tareas.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def _create_task(client, **kwargs):
    payload = {"title": "Test task", **kwargs}
    resp = client.post("/tasks/", json=payload)
    assert resp.status_code == 201
    return resp.json()


def test_update_done_task_returns_400(client):
    task = _create_task(client, status="done")

    resp = client.patch(f"/tasks/{task['id']}", json={"title": "New title"})

    assert resp.status_code == 400
    assert resp.json()["detail"] == "Cannot update a completed task"


def test_update_pending_task_succeeds(client):
    task = _create_task(client)

    resp = client.patch(f"/tasks/{task['id']}", json={"title": "Updated"})

    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated"


def test_update_in_progress_task_succeeds(client):
    task = _create_task(client, status="in_progress")

    resp = client.patch(
        f"/tasks/{task['id']}", json={"status": "done"}
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "done"


def test_update_done_task_status_change_blocked(client):
    task = _create_task(client, status="done")

    resp = client.patch(f"/tasks/{task['id']}", json={"status": "pending"})

    assert resp.status_code == 400
    assert resp.json()["detail"] == "Cannot update a completed task"


# ── Tests para filtro por estado en list_tasks ──────────────────────


def test_list_tasks_filter_by_status(client):
    _create_task(client, title="Pending 1")
    _create_task(client, title="Pending 2")
    _create_task(client, title="Done", status="done")

    resp = client.get("/tasks/", params={"status": "pending"})

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert all(t["status"] == "pending" for t in data)


def test_list_tasks_filter_by_status_no_matches(client):
    _create_task(client, title="Pending")

    resp = client.get("/tasks/", params={"status": "done"})

    assert resp.status_code == 200
    assert resp.json() == []


def test_list_tasks_filter_invalid_status(client):
    resp = client.get("/tasks/", params={"status": "invalid"})

    assert resp.status_code == 422


# ── Tests para limit en list_tasks ──────────────────────────────────


def test_list_tasks_with_limit(client):
    for i in range(5):
        _create_task(client, title=f"Task {i}")

    resp = client.get("/tasks/", params={"limit": 3})

    assert resp.status_code == 200
    assert len(resp.json()) == 3


def test_list_tasks_limit_greater_than_total(client):
    _create_task(client, title="Only one")

    resp = client.get("/tasks/", params={"limit": 10})

    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_list_tasks_limit_zero_returns_422(client):
    resp = client.get("/tasks/", params={"limit": 0})

    assert resp.status_code == 422


def test_list_tasks_negative_limit_returns_422(client):
    resp = client.get("/tasks/", params={"limit": -1})

    assert resp.status_code == 422


# ── Tests combinados: filtro + limit ────────────────────────────────


def test_list_tasks_filter_and_limit_combined(client):
    for i in range(4):
        _create_task(client, title=f"Pending {i}")
    _create_task(client, title="Done", status="done")

    resp = client.get("/tasks/", params={"status": "pending", "limit": 2})

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert all(t["status"] == "pending" for t in data)


def test_list_tasks_without_params_returns_all(client):
    _create_task(client, title="A")
    _create_task(client, title="B")
    _create_task(client, title="C")

    resp = client.get("/tasks/")

    assert resp.status_code == 200
    assert len(resp.json()) == 3
