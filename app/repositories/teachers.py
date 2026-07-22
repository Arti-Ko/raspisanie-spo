from dataclasses import dataclass

from app.db.database import get_connection
from app.repositories.subjects import Subject


@dataclass(frozen=True)
class Teacher:
    id: int
    full_name: str
    room: str
    subjects: tuple[Subject, ...]


def _load_subjects_for_teacher(conn, teacher_id: int) -> tuple[Subject, ...]:
    rows = conn.execute(
        """
        SELECT s.id, s.name
        FROM subjects s
        JOIN teacher_subjects ts ON ts.subject_id = s.id
        WHERE ts.teacher_id = ?
        ORDER BY s.name
        """,
        (teacher_id,),
    ).fetchall()
    return tuple(Subject(row["id"], row["name"]) for row in rows)


def list_teachers() -> list[Teacher]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, full_name, room FROM teachers ORDER BY full_name"
        ).fetchall()
        return [
            Teacher(
                row["id"],
                row["full_name"],
                row["room"] or "",
                _load_subjects_for_teacher(conn, row["id"]),
            )
            for row in rows
        ]
    finally:
        conn.close()


def add_teacher(full_name: str, room: str, subject_ids: list[int]) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO teachers (full_name, room) VALUES (?, ?)", (full_name, room)
        )
        teacher_id = cursor.lastrowid
        _set_teacher_subjects(conn, teacher_id, subject_ids)
        conn.commit()
        return teacher_id
    finally:
        conn.close()


def update_teacher(
    teacher_id: int, full_name: str, room: str, subject_ids: list[int]
) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE teachers SET full_name = ?, room = ? WHERE id = ?",
            (full_name, room, teacher_id),
        )
        _set_teacher_subjects(conn, teacher_id, subject_ids)
        conn.commit()
    finally:
        conn.close()


def delete_teacher(teacher_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
        conn.commit()
    finally:
        conn.close()


def _set_teacher_subjects(conn, teacher_id: int, subject_ids: list[int]) -> None:
    conn.execute("DELETE FROM teacher_subjects WHERE teacher_id = ?", (teacher_id,))
    conn.executemany(
        "INSERT INTO teacher_subjects (teacher_id, subject_id) VALUES (?, ?)",
        [(teacher_id, subject_id) for subject_id in subject_ids],
    )
