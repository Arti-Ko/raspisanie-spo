from dataclasses import dataclass

from app.db.database import get_connection


@dataclass(frozen=True)
class Assignment:
    id: int
    teacher_id: int
    teacher_name: str
    group_id: int
    group_name: str
    curriculum_item_id: int
    subject_name: str
    semester: int
    natural_hours: int
    transferred_hours: int
    lesson_type: str

    @property
    def hours_in_natural_semester(self) -> int:
        return self.natural_hours - self.transferred_hours

    @property
    def other_semester(self) -> int:
        return 2 if self.semester == 1 else 1


_ASSIGNMENT_SELECT = """
    SELECT
        a.id, a.teacher_id, t.full_name AS teacher_name,
        a.group_id, g.name AS group_name,
        a.curriculum_item_id, s.name AS subject_name, ci.semester,
        (ci.hours_theory + ci.hours_practice + ci.hours_exam) AS natural_hours,
        a.transferred_hours, ci.lesson_type
    FROM teacher_assignments a
    JOIN teachers t ON t.id = a.teacher_id
    JOIN groups g ON g.id = a.group_id
    JOIN curriculum_items ci ON ci.id = a.curriculum_item_id
    JOIN subjects s ON s.id = ci.subject_id
"""


def _row_to_assignment(row) -> Assignment:
    return Assignment(
        row["id"],
        row["teacher_id"],
        row["teacher_name"],
        row["group_id"],
        row["group_name"],
        row["curriculum_item_id"],
        row["subject_name"],
        row["semester"],
        row["natural_hours"],
        row["transferred_hours"],
        row["lesson_type"],
    )


def list_assignments_for_group(group_id: int) -> list[Assignment]:
    conn = get_connection()
    try:
        rows = conn.execute(
            _ASSIGNMENT_SELECT + " WHERE a.group_id = ? ORDER BY ci.semester, s.name",
            (group_id,),
        ).fetchall()
        return [_row_to_assignment(row) for row in rows]
    finally:
        conn.close()


def list_assignments_for_teacher(teacher_id: int) -> list[Assignment]:
    conn = get_connection()
    try:
        rows = conn.execute(
            _ASSIGNMENT_SELECT + " WHERE a.teacher_id = ? ORDER BY ci.semester, g.name",
            (teacher_id,),
        ).fetchall()
        return [_row_to_assignment(row) for row in rows]
    finally:
        conn.close()


def list_unassigned_curriculum_for_group(group_id: int) -> list[tuple[int, str, int]]:
    conn = get_connection()
    try:
        group_row = conn.execute(
            "SELECT program_id, course FROM groups WHERE id = ?", (group_id,)
        ).fetchone()
        rows = conn.execute(
            """
            SELECT ci.id, s.name AS subject_name, ci.semester
            FROM curriculum_items ci
            JOIN subjects s ON s.id = ci.subject_id
            WHERE ci.program_id = ? AND ci.course = ?
              AND ci.id NOT IN (SELECT curriculum_item_id FROM teacher_assignments WHERE group_id = ?)
            ORDER BY ci.semester, s.name
            """,
            (group_row["program_id"], group_row["course"], group_id),
        ).fetchall()
        return [(row["id"], row["subject_name"], row["semester"]) for row in rows]
    finally:
        conn.close()


def add_assignment(teacher_id: int, group_id: int, curriculum_item_id: int) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO teacher_assignments (teacher_id, group_id, curriculum_item_id) VALUES (?, ?, ?)",
            (teacher_id, group_id, curriculum_item_id),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_transfer(assignment_id: int, transferred_hours: int) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE teacher_assignments SET transferred_hours = ? WHERE id = ?",
            (transferred_hours, assignment_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_assignment(assignment_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM teacher_assignments WHERE id = ?", (assignment_id,))
        conn.commit()
    finally:
        conn.close()


def teacher_semester_totals(teacher_id: int) -> dict[int, int]:
    totals = {1: 0, 2: 0}
    for assignment in list_assignments_for_teacher(teacher_id):
        totals[assignment.semester] += assignment.hours_in_natural_semester
        totals[assignment.other_semester] += assignment.transferred_hours
    return totals


def all_teacher_totals() -> dict[int, tuple[str, dict[int, int]]]:
    conn = get_connection()
    try:
        teacher_rows = conn.execute(
            "SELECT DISTINCT t.id, t.full_name FROM teachers t JOIN teacher_assignments a ON a.teacher_id = t.id ORDER BY t.full_name"
        ).fetchall()
    finally:
        conn.close()
    return {
        row["id"]: (row["full_name"], teacher_semester_totals(row["id"]))
        for row in teacher_rows
    }
