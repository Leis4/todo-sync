"""Сервер общего списка дел. Запуск: python -m uvicorn server:app --port 8000"""

import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Общий список дел")
DB = Path(__file__).with_name("tasks.db")


class Task(BaseModel):
    title: str


def check_title(text):
    text = text.strip()
    if not 1 <= len(text) <= 120 or not text.isprintable():
        raise HTTPException(400, "Введите название от 1 до 120 символов")
    return text


with sqlite3.connect(DB) as db:
    db.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        done INTEGER NOT NULL DEFAULT 0
    )""")


@app.get("/tasks")
def get_tasks():
    with sqlite3.connect(DB) as db:
        rows = db.execute("SELECT id, title, done FROM tasks ORDER BY id DESC").fetchall()
    return [{"id": id, "title": title, "done": bool(done)} for id, title, done in rows]


@app.post("/tasks")
def add_task(task: Task):
    with sqlite3.connect(DB) as db:
        db.execute("INSERT INTO tasks (title) VALUES (?)", (check_title(task.title),))
    return {"ok": True}


@app.patch("/tasks/{task_id}/title")
def rename_task(task_id: int, task: Task):
    with sqlite3.connect(DB) as db:
        changed = db.execute("UPDATE tasks SET title = ? WHERE id = ?",
                             (check_title(task.title), task_id)).rowcount
    if not changed:
        raise HTTPException(404, "Задача не найдена")
    return {"ok": True}


@app.patch("/tasks/{task_id}")
def toggle_task(task_id: int):
    with sqlite3.connect(DB) as db:
        changed = db.execute("UPDATE tasks SET done = 1 - done WHERE id = ?",
                             (task_id,)).rowcount
    if not changed:
        raise HTTPException(404, "Задача не найдена")
    return {"ok": True}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    with sqlite3.connect(DB) as db:
        changed = db.execute("DELETE FROM tasks WHERE id = ?", (task_id,)).rowcount
    if not changed:
        raise HTTPException(404, "Задача не найдена")
    return {"ok": True}
