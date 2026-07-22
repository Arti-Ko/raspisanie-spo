from dataclasses import dataclass, field

from app.db.database import get_connection
from app.repositories.tarification import teacher_semester_totals

HOURS_PER_PAIR = 2


@dataclass(frozen=True)
class WeekLine:
    semester: int
    week_number: int
    group_name: str
    subject_name: str
    hours: int
    is_substitute: bool


@dataclass(frozen=True)
class SubstitutionLine:
    semester: int
    week_number: int
    group_name: str
    subject_name: str
    other_teacher_name: str
    hours: int


@dataclass(frozen=True)
class TeacherReport:
    teacher_id: int
    teacher_name: str
    plan_hours: dict[int, int]
    actual_hours: dict[int, int]
    weekly_lines: list[WeekLine] = field(default_factory=list)
    covered_by_others: list[SubstitutionLine] = field(default_factory=list)
    covered_for_others: list[SubstitutionLine] = field(default_factory=list)

    @property
    def plan_total(self) -> int:
        return self.plan_hours[1] + self.plan_hours[2]

    @property
    def actual_total(self) -> int:
        return self.actual_hours[1] + self.actual_hours[2]

    @property
    def difference(self) -> int:
        return self.plan_total - self.actual_total


_WEEKLY_QUERY = """
    SELECT
        cw.semester, cw.week_number, g.name AS group_name, sub.name AS subject_name,
        se.substitute_teacher_id, a.teacher_id AS original_teacher_id,
        t.full_name AS original_teacher_name, st.full_name AS substitute_teacher_name
    FROM schedule_entries se
    JOIN calendar_weeks cw ON cw.id = se.calendar_week_id
    JOIN groups g ON g.id = se.group_id
    JOIN teacher_assignments a ON a.id = se.assignment_id
    JOIN teachers t ON t.id = a.teacher_id
    JOIN curriculum_items ci ON ci.id = a.curriculum_item_id
    JOIN subjects sub ON sub.id = ci.subject_id
    LEFT JOIN teachers st ON st.id = se.substitute_teacher_id
    WHERE COALESCE(se.substitute_teacher_id, a.teacher_id) = ?
       OR a.teacher_id = ?
    ORDER BY cw.semester, cw.week_number
"""


def build_teacher_report(teacher_id: int, teacher_name: str) -> TeacherReport:
    plan_hours = teacher_semester_totals(teacher_id)
    actual_hours = {1: 0, 2: 0}
    weekly_lines: list[WeekLine] = []
    covered_by_others: list[SubstitutionLine] = []
    covered_for_others: list[SubstitutionLine] = []

    conn = get_connection()
    try:
        rows = conn.execute(_WEEKLY_QUERY, (teacher_id, teacher_id)).fetchall()
    finally:
        conn.close()

    for row in rows:
        effective_teacher_id = (
            row["substitute_teacher_id"] or row["original_teacher_id"]
        )
        is_substitute_row = row["substitute_teacher_id"] is not None

        if effective_teacher_id == teacher_id:
            weekly_lines.append(
                WeekLine(
                    row["semester"],
                    row["week_number"],
                    row["group_name"],
                    row["subject_name"],
                    HOURS_PER_PAIR,
                    is_substitute_row,
                )
            )
            actual_hours[row["semester"]] += HOURS_PER_PAIR

        if is_substitute_row and row["original_teacher_id"] == teacher_id:
            covered_by_others.append(
                SubstitutionLine(
                    row["semester"],
                    row["week_number"],
                    row["group_name"],
                    row["subject_name"],
                    row["substitute_teacher_name"],
                    HOURS_PER_PAIR,
                )
            )
        elif is_substitute_row and row["substitute_teacher_id"] == teacher_id:
            covered_for_others.append(
                SubstitutionLine(
                    row["semester"],
                    row["week_number"],
                    row["group_name"],
                    row["subject_name"],
                    row["original_teacher_name"],
                    HOURS_PER_PAIR,
                )
            )

    return TeacherReport(
        teacher_id,
        teacher_name,
        plan_hours,
        actual_hours,
        weekly_lines,
        covered_by_others,
        covered_for_others,
    )
