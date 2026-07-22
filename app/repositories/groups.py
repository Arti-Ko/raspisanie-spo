from dataclasses import dataclass

from app.db.database import get_connection


@dataclass(frozen=True)
class Group:
    id: int
    name: str
    program_id: int
    program_code: str
    program_name: str
    course: int


def list_groups() -> list[Group]:
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT g.id, g.name, g.course, p.id AS program_id, p.code AS program_code, p.name AS program_name
            FROM groups g
            JOIN programs p ON p.id = g.program_id
            ORDER BY g.name
            """).fetchall()
        return [
            Group(
                row["id"],
                row["name"],
                row["program_id"],
                row["program_code"],
                row["program_name"],
                row["course"],
            )
            for row in rows
        ]
    finally:
        conn.close()


def add_group(name: str, program_id: int, course: int) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO groups (name, program_id, course) VALUES (?, ?, ?)",
            (name, program_id, course),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_group(group_id: int, name: str, program_id: int, course: int) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE groups SET name = ?, program_id = ?, course = ? WHERE id = ?",
            (name, program_id, course, group_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_group(group_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM groups WHERE id = ?", (group_id,))
        conn.commit()
    finally:
        conn.close()
