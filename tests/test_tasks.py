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


# --- Tests para el campo description (máx 200 caracteres) ---


def test_create_task_with_description(client):
    """Crear una tarea con descripción válida debe devolver 201."""
    resp = client.post(
        "/tasks/", json={"title": "Tarea", "description": "Desc corta"}
    )
    assert resp.status_code == 201
    assert resp.json()["description"] == "Desc corta"


def test_create_task_without_description(client):
    """Crear una tarea sin descripción debe devolver null en el campo."""
    resp = client.post("/tasks/", json={"title": "Tarea sin desc"})
    assert resp.status_code == 201
    assert resp.json()["description"] is None


def test_create_task_description_max_200(client):
    """Crear una tarea con descripción de exactamente 200 caracteres debe funcionar."""
    desc = "a" * 200
    resp = client.post("/tasks/", json={"title": "Tarea", "description": desc})
    assert resp.status_code == 201
    assert resp.json()["description"] == desc


def test_create_task_description_exceeds_200(client):
    """Crear una tarea con descripción de más de 200 caracteres debe devolver 422."""
    desc = "a" * 201
    resp = client.post("/tasks/", json={"title": "Tarea", "description": desc})
    assert resp.status_code == 422


def test_update_task_description(client):
    """Actualizar la descripción de una tarea pendiente debe funcionar."""
    task = _create_task(client)
    resp = client.patch(
        f"/tasks/{task['id']}", json={"description": "Nueva descripción"}
    )
    assert resp.status_code == 200
    assert resp.json()["description"] == "Nueva descripción"


def test_update_task_description_exceeds_200(client):
    """Actualizar con descripción de más de 200 caracteres debe devolver 422."""
    task = _create_task(client)
    desc = "b" * 201
    resp = client.patch(f"/tasks/{task['id']}", json={"description": desc})
    assert resp.status_code == 422
