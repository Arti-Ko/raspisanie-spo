from dataclasses import dataclass

from app.db.database import get_connection


@dataclass(frozen=True)
class Subject:
    id: int
    name: str


def list_subjects() -> list[Subject]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT id, name FROM subjects ORDER BY name").fetchall()
        return [Subject(row["id"], row["name"]) for row in rows]
    finally:
        conn.close()


def get_or_create_subject(name: str) -> Subject:
    name = name.strip()
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, name FROM subjects WHERE name = ?", (name,)
        ).fetchone()
        if row:
            return Subject(row["id"], row["name"])
        cursor = conn.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
        conn.commit()
        return Subject(cursor.lastrowid, name)
    finally:
        conn.close()


def delete_subject(subject_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        conn.commit()
    finally:
        conn.close()
