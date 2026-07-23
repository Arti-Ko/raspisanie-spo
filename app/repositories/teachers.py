from dataclasses import dataclass

from app.db.database import get_connection
from app.repositories.subjects import Subject
from app.repositories.text_format import capitalize_full_name

COLOR_PALETTE = [
    "#F8CBAD",
    "#C6E0B4",
    "#BDD7EE",
    "#FFE699",
    "#D9C2E9",
    "#F4B183",
    "#A9D18E",
    "#9DC3E6",
    "#FFD966",
    "#B4A7D6",
    "#F2A0A0",
    "#A0D4D0",
]


@dataclass(frozen=True)
class Teacher:
    id: int
    full_name: str
    room: str
    color: str
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
            "SELECT id, full_name, room, color FROM teachers ORDER BY full_name"
        ).fetchall()
        return [
            Teacher(
                row["id"],
                row["full_name"],
                row["room"] or "",
                row["color"] or _next_color(conn),
                _load_subjects_for_teacher(conn, row["id"]),
            )
            for row in rows
        ]
    finally:
        conn.close()


def _next_color(conn) -> str:
    count = conn.execute("SELECT COUNT(*) AS n FROM teachers").fetchone()["n"]
    return COLOR_PALETTE[count % len(COLOR_PALETTE)]


def add_teacher(full_name: str, room: str, subject_ids: list[int]) -> int:
    full_name = capitalize_full_name(full_name)
    conn = get_connection()
    try:
        color = _next_color(conn)
        cursor = conn.execute(
            "INSERT INTO teachers (full_name, room, color) VALUES (?, ?, ?)",
            (full_name, room, color),
        )
        teacher_id = cursor.lastrowid
        _set_teacher_subjects(conn, teacher_id, subject_ids)
        conn.commit()
        return teacher_id
    finally:
        conn.close()


def update_teacher(
    teacher_id: int, full_name: str, room: str, subject_ids: list[int], color: str
) -> None:
    full_name = capitalize_full_name(full_name)
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE teachers SET full_name = ?, room = ?, color = ? WHERE id = ?",
            (full_name, room, color, teacher_id),
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
