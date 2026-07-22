from dataclasses import dataclass

from app.db.database import get_connection


@dataclass(frozen=True)
class Program:
    id: int
    code: str
    name: str
    duration_months: int

    @property
    def duration_label(self) -> str:
        years, months = divmod(self.duration_months, 12)
        parts = []
        if years:
            parts.append(f"{years} г.")
        if months:
            parts.append(f"{months} мес.")
        return " ".join(parts) if parts else "0 мес."


def list_programs() -> list[Program]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, code, name, duration_months FROM programs ORDER BY code"
        ).fetchall()
        return [
            Program(row["id"], row["code"], row["name"], row["duration_months"])
            for row in rows
        ]
    finally:
        conn.close()


def add_program(code: str, name: str, duration_months: int) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO programs (code, name, duration_months) VALUES (?, ?, ?)",
            (code, name, duration_months),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_program(program_id: int, code: str, name: str, duration_months: int) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE programs SET code = ?, name = ?, duration_months = ? WHERE id = ?",
            (code, name, duration_months, program_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_program(program_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM programs WHERE id = ?", (program_id,))
        conn.commit()
    finally:
        conn.close()
