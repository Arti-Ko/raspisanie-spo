from dataclasses import dataclass

from app.db.database import get_connection


@dataclass(frozen=True)
class AcademicYear:
    id: int
    name: str


def list_academic_years() -> list[AcademicYear]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, name FROM academic_years ORDER BY name"
        ).fetchall()
        return [AcademicYear(row["id"], row["name"]) for row in rows]
    finally:
        conn.close()


def add_academic_year(name: str) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute("INSERT INTO academic_years (name) VALUES (?)", (name,))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def delete_academic_year(academic_year_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM academic_years WHERE id = ?", (academic_year_id,))
        conn.commit()
    finally:
        conn.close()
