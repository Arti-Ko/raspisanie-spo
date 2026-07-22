from dataclasses import dataclass

from app.db.database import get_connection


@dataclass(frozen=True)
class CalendarWeek:
    id: int
    academic_year_id: int
    semester: int
    week_number: int
    hours: int
    note: str


def list_weeks(academic_year_id: int, semester: int) -> list[CalendarWeek]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, academic_year_id, semester, week_number, hours, note
            FROM calendar_weeks
            WHERE academic_year_id = ? AND semester = ?
            ORDER BY week_number
            """,
            (academic_year_id, semester),
        ).fetchall()
        return [
            CalendarWeek(
                row["id"],
                row["academic_year_id"],
                row["semester"],
                row["week_number"],
                row["hours"],
                row["note"] or "",
            )
            for row in rows
        ]
    finally:
        conn.close()


def semester_total(academic_year_id: int, semester: int) -> int:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT COALESCE(SUM(hours), 0) AS total FROM calendar_weeks WHERE academic_year_id = ? AND semester = ?",
            (academic_year_id, semester),
        ).fetchone()
        return row["total"]
    finally:
        conn.close()


def next_week_number(academic_year_id: int, semester: int) -> int:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT COALESCE(MAX(week_number), 0) AS max_week FROM calendar_weeks WHERE academic_year_id = ? AND semester = ?",
            (academic_year_id, semester),
        ).fetchone()
        return row["max_week"] + 1
    finally:
        conn.close()


def add_week(
    academic_year_id: int, semester: int, week_number: int, hours: int, note: str
) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO calendar_weeks (academic_year_id, semester, week_number, hours, note)
            VALUES (?, ?, ?, ?, ?)
            """,
            (academic_year_id, semester, week_number, hours, note),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def add_weeks_bulk(
    academic_year_id: int, semester: int, count: int, hours: int, note: str
) -> None:
    conn = get_connection()
    try:
        start_row = conn.execute(
            "SELECT COALESCE(MAX(week_number), 0) AS max_week FROM calendar_weeks WHERE academic_year_id = ? AND semester = ?",
            (academic_year_id, semester),
        ).fetchone()
        start = start_row["max_week"] + 1
        conn.executemany(
            "INSERT INTO calendar_weeks (academic_year_id, semester, week_number, hours, note) VALUES (?, ?, ?, ?, ?)",
            [
                (academic_year_id, semester, start + i, hours, note)
                for i in range(count)
            ],
        )
        conn.commit()
    finally:
        conn.close()


def update_week(week_id: int, week_number: int, hours: int, note: str) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE calendar_weeks SET week_number = ?, hours = ?, note = ? WHERE id = ?",
            (week_number, hours, note, week_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_week(week_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM calendar_weeks WHERE id = ?", (week_id,))
        conn.commit()
    finally:
        conn.close()
