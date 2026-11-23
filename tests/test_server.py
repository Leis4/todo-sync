import os
import sqlite3
import tempfile
from pathlib import Path

import pytest

# Отдельная база для тестов, чтобы не трогать tasks.db.
os.environ["TODO_DB"] = str(Path(tempfile.mkdtemp()) / "test_tasks.db")

from fastapi.testclient import TestClient  # noqa: E402
import server  # noqa: E402

client = TestClient(server.app)


@pytest.fixture(autouse=True)
def clean_db():
    with sqlite3.connect(server.DB) as db:
        db.execute("DELETE FROM tasks")
    yield


def test_add_and_list():
    response = client.post("/tasks", json={"title": "Подготовить курсовую"})
    assert response.status_code == 200

    data = client.get("/tasks").json()
    assert len(data) == 1
    assert data[0]["title"] == "Подготовить курсовую"
    assert data[0]["done"] is False


def test_rename_and_toggle():
    client.post("/tasks", json={"title": "Старое название"})
    task_id = client.get("/tasks").json()[0]["id"]

    response = client.patch(f"/tasks/{task_id}/title", json={"title": "Новое название"})
    assert response.status_code == 200
    assert client.get("/tasks").json()[0]["title"] == "Новое название"

    response = client.patch(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert client.get("/tasks").json()[0]["done"] is True


def test_delete():
    client.post("/tasks", json={"title": "Удалить меня"})
    task_id = client.get("/tasks").json()[0]["id"]

    assert client.delete(f"/tasks/{task_id}").status_code == 200
    assert client.get("/tasks").json() == []


def test_empty_title_rejected():
    assert client.post("/tasks", json={"title": "   "}).status_code == 400
    assert client.post("/tasks", json={"title": "x" * 121}).status_code == 400


def test_missing_task_returns_404():
    assert client.patch("/tasks/999999").status_code == 404
    assert client.delete("/tasks/999999").status_code == 404


def test_two_clients_share_list():
    first = TestClient(server.app)
    second = TestClient(server.app)

    first.post("/tasks", json={"title": "Общая задача"})
    assert second.get("/tasks").json()[0]["title"] == "Общая задача"

    task_id = second.get("/tasks").json()[0]["id"]
    second.patch(f"/tasks/{task_id}")
    assert first.get("/tasks").json()[0]["done"] is True
