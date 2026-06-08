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


# --- Tests para PATCH /tasks/{id}/complete ---


def test_complete_pending_task(client):
    task = _create_task(client)

    resp = client.patch(f"/tasks/{task['id']}/complete")

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "done"
    assert data["id"] == task["id"]


def test_complete_in_progress_task(client):
    task = _create_task(client, status="in_progress")

    resp = client.patch(f"/tasks/{task['id']}/complete")

    assert resp.status_code == 200
    assert resp.json()["status"] == "done"


def test_complete_already_done_task_returns_400(client):
    task = _create_task(client, status="done")

    resp = client.patch(f"/tasks/{task['id']}/complete")

    assert resp.status_code == 400
    assert resp.json()["detail"] == "La tarea ya está completada"


def test_complete_nonexistent_task_returns_404(client):
    resp = client.patch("/tasks/9999/complete")

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Tarea no encontrada"
