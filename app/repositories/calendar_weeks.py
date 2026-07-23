from dataclasses import dataclass
from datetime import date, timedelta

from app.db.database import get_connection


@dataclass(frozen=True)
class CalendarWeek:
    id: int
    academic_year_id: int
    semester: int
    week_number: int
    hours: int
    note: str
    includes_saturday: bool
    start_date: str | None

    @property
    def date_range_label(self) -> str:
        if not self.start_date:
            return ""
        start = date.fromisoformat(self.start_date)
        end = start + timedelta(days=5 if self.includes_saturday else 4)
        return f"{start.strftime('%d.%m.%Y')} - {end.strftime('%d.%m.%Y')}"


def _row_to_week(row) -> CalendarWeek:
    return CalendarWeek(
        row["id"],
        row["academic_year_id"],
        row["semester"],
        row["week_number"],
        row["hours"],
        row["note"] or "",
        bool(row["includes_saturday"]),
        row["start_date"],
    )


_COLUMNS = "id, academic_year_id, semester, week_number, hours, note, includes_saturday, start_date"


def list_weeks(academic_year_id: int, semester: int) -> list[CalendarWeek]:
    conn = get_connection()
    try:
        rows = conn.execute(
            f"""
            SELECT {_COLUMNS}
            FROM calendar_weeks
            WHERE academic_year_id = ? AND semester = ?
            ORDER BY week_number
            """,
            (academic_year_id, semester),
        ).fetchall()
        return [_row_to_week(row) for row in rows]
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
    academic_year_id: int,
    semester: int,
    week_number: int,
    hours: int,
    note: str,
    includes_saturday: bool = False,
    start_date: str | None = None,
) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO calendar_weeks
                (academic_year_id, semester, week_number, hours, note, includes_saturday, start_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                academic_year_id,
                semester,
                week_number,
                hours,
                note,
                int(includes_saturday),
                start_date,
            ),
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


def update_week(
    week_id: int,
    week_number: int,
    hours: int,
    note: str,
    includes_saturday: bool,
    start_date: str | None,
) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE calendar_weeks
            SET week_number = ?, hours = ?, note = ?, includes_saturday = ?, start_date = ?
            WHERE id = ?
            """,
            (week_number, hours, note, int(includes_saturday), start_date, week_id),
        )
        conn.commit()
    finally:
        conn.close()


def set_includes_saturday(week_id: int, includes_saturday: bool) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE calendar_weeks SET includes_saturday = ? WHERE id = ?",
            (int(includes_saturday), week_id),
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
