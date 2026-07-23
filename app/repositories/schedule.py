from dataclasses import dataclass

from app.db.database import get_connection

_ENTRY_SELECT = """
    SELECT
        se.id, se.group_id, se.calendar_week_id, se.assignment_id,
        se.day_of_week, se.pair_number, se.room,
        a.teacher_id, t.full_name AS teacher_name, sub.name AS subject_name,
        se.substitute_teacher_id, st.full_name AS substitute_teacher_name
    FROM schedule_entries se
    JOIN teacher_assignments a ON a.id = se.assignment_id
    JOIN teachers t ON t.id = a.teacher_id
    JOIN curriculum_items ci ON ci.id = a.curriculum_item_id
    JOIN subjects sub ON sub.id = ci.subject_id
    LEFT JOIN teachers st ON st.id = se.substitute_teacher_id
"""


@dataclass(frozen=True)
class ScheduleEntry:
    id: int
    group_id: int
    calendar_week_id: int
    assignment_id: int
    day_of_week: int
    pair_number: int
    room: str
    teacher_id: int
    teacher_name: str
    subject_name: str
    substitute_teacher_id: int | None
    substitute_teacher_name: str | None

    @property
    def effective_teacher_id(self) -> int:
        return self.substitute_teacher_id or self.teacher_id

    @property
    def effective_teacher_name(self) -> str:
        return self.substitute_teacher_name or self.teacher_name


def _row_to_entry(row) -> ScheduleEntry:
    return ScheduleEntry(
        row["id"],
        row["group_id"],
        row["calendar_week_id"],
        row["assignment_id"],
        row["day_of_week"],
        row["pair_number"],
        row["room"] or "",
        row["teacher_id"],
        row["teacher_name"],
        row["subject_name"],
        row["substitute_teacher_id"],
        row["substitute_teacher_name"],
    )


def list_entries_for_group_week(
    group_id: int, calendar_week_id: int
) -> list[ScheduleEntry]:
    conn = get_connection()
    try:
        rows = conn.execute(
            _ENTRY_SELECT + " WHERE se.group_id = ? AND se.calendar_week_id = ?",
            (group_id, calendar_week_id),
        ).fetchall()
        return [_row_to_entry(row) for row in rows]
    finally:
        conn.close()


def set_entry(
    group_id: int,
    calendar_week_id: int,
    day_of_week: int,
    pair_number: int,
    assignment_id: int | None,
    room: str,
    substitute_teacher_id: int | None,
) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "DELETE FROM schedule_entries WHERE group_id = ? AND calendar_week_id = ? AND day_of_week = ? AND pair_number = ?",
            (group_id, calendar_week_id, day_of_week, pair_number),
        )
        if assignment_id is not None:
            conn.execute(
                """
                INSERT INTO schedule_entries
                    (group_id, calendar_week_id, assignment_id, day_of_week, pair_number, room, substitute_teacher_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    group_id,
                    calendar_week_id,
                    assignment_id,
                    day_of_week,
                    pair_number,
                    room,
                    substitute_teacher_id,
                ),
            )
        conn.commit()
    finally:
        conn.close()


def teacher_conflict_at(
    teacher_id: int,
    calendar_week_id: int,
    day_of_week: int,
    pair_number: int,
    exclude_group_id: int | None = None,
) -> ScheduleEntry | None:
    conn = get_connection()
    try:
        query = _ENTRY_SELECT + """
            WHERE se.calendar_week_id = ? AND se.day_of_week = ? AND se.pair_number = ?
              AND COALESCE(se.substitute_teacher_id, a.teacher_id) = ?
        """
        params = [calendar_week_id, day_of_week, pair_number, teacher_id]
        if exclude_group_id is not None:
            query += " AND se.group_id != ?"
            params.append(exclude_group_id)
        row = conn.execute(query, params).fetchone()
        return _row_to_entry(row) if row else None
    finally:
        conn.close()


def room_conflict_at(
    room: str,
    calendar_week_id: int,
    day_of_week: int,
    pair_number: int,
    exclude_group_id: int | None = None,
) -> ScheduleEntry | None:
    if not room:
        return None
    conn = get_connection()
    try:
        query = _ENTRY_SELECT + """
            WHERE se.calendar_week_id = ? AND se.day_of_week = ? AND se.pair_number = ? AND se.room = ?
        """
        params = [calendar_week_id, day_of_week, pair_number, room]
        if exclude_group_id is not None:
            query += " AND se.group_id != ?"
            params.append(exclude_group_id)
        row = conn.execute(query, params).fetchone()
        return _row_to_entry(row) if row else None
    finally:
        conn.close()


def week_hours_for_group(group_id: int, calendar_week_id: int) -> int:
    entries = list_entries_for_group_week(group_id, calendar_week_id)
    return len([e for e in entries if e.pair_number > 0]) * 2


def clear_group_week(group_id: int, calendar_week_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "DELETE FROM schedule_entries WHERE group_id = ? AND calendar_week_id = ? AND pair_number > 0",
            (group_id, calendar_week_id),
        )
        conn.commit()
    finally:
        conn.close()


def clear_group_weeks(group_id: int, calendar_week_ids: list[int]) -> None:
    conn = get_connection()
    try:
        conn.executemany(
            "DELETE FROM schedule_entries WHERE group_id = ? AND calendar_week_id = ? AND pair_number > 0",
            [(group_id, week_id) for week_id in calendar_week_ids],
        )
        conn.commit()
    finally:
        conn.close()
