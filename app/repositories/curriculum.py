from dataclasses import dataclass

from app.db.database import get_connection

LESSON_TYPES = ("theory", "practice", "lab")
LESSON_TYPE_LABELS = {
    "theory": "Теория",
    "practice": "Учебная практика (блоками по 6 ч)",
    "lab": "Лабораторно-практическое (с делением на подгруппы)",
}

_COLUMNS = """
    ci.id, ci.program_id, ci.course, ci.semester, ci.subject_id, s.name AS subject_name,
    ci.hours_theory, ci.hours_practice, ci.hours_exam, ci.lesson_type, ci.is_double_pair
"""


@dataclass(frozen=True)
class CurriculumItem:
    id: int
    program_id: int
    course: int
    semester: int
    subject_id: int
    subject_name: str
    hours_theory: int
    hours_practice: int
    hours_exam: int
    lesson_type: str
    is_double_pair: bool

    @property
    def total_hours(self) -> int:
        return self.hours_theory + self.hours_practice + self.hours_exam

    @property
    def lesson_type_label(self) -> str:
        return LESSON_TYPE_LABELS.get(self.lesson_type, self.lesson_type)


def _row_to_item(row) -> CurriculumItem:
    return CurriculumItem(
        row["id"],
        row["program_id"],
        row["course"],
        row["semester"],
        row["subject_id"],
        row["subject_name"],
        row["hours_theory"],
        row["hours_practice"],
        row["hours_exam"],
        row["lesson_type"],
        bool(row["is_double_pair"]),
    )


def list_curriculum(program_id: int, course: int) -> list[CurriculumItem]:
    conn = get_connection()
    try:
        rows = conn.execute(
            f"""
            SELECT {_COLUMNS}
            FROM curriculum_items ci
            JOIN subjects s ON s.id = ci.subject_id
            WHERE ci.program_id = ? AND ci.course = ?
            ORDER BY ci.semester, s.name
            """,
            (program_id, course),
        ).fetchall()
        return [_row_to_item(row) for row in rows]
    finally:
        conn.close()


def get_curriculum_item(item_id: int) -> CurriculumItem:
    conn = get_connection()
    try:
        row = conn.execute(
            f"""
            SELECT {_COLUMNS}
            FROM curriculum_items ci
            JOIN subjects s ON s.id = ci.subject_id
            WHERE ci.id = ?
            """,
            (item_id,),
        ).fetchone()
        return _row_to_item(row)
    finally:
        conn.close()


def add_curriculum_item(
    program_id: int,
    course: int,
    semester: int,
    subject_id: int,
    hours_theory: int,
    hours_practice: int,
    hours_exam: int,
    lesson_type: str = "theory",
    is_double_pair: bool = False,
) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO curriculum_items
                (program_id, course, semester, subject_id, hours_theory, hours_practice, hours_exam,
                 lesson_type, is_double_pair)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                program_id,
                course,
                semester,
                subject_id,
                hours_theory,
                hours_practice,
                hours_exam,
                lesson_type,
                int(is_double_pair),
            ),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_curriculum_item(
    item_id: int,
    semester: int,
    subject_id: int,
    hours_theory: int,
    hours_practice: int,
    hours_exam: int,
    lesson_type: str = "theory",
    is_double_pair: bool = False,
) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE curriculum_items
            SET semester = ?, subject_id = ?, hours_theory = ?, hours_practice = ?, hours_exam = ?,
                lesson_type = ?, is_double_pair = ?
            WHERE id = ?
            """,
            (
                semester,
                subject_id,
                hours_theory,
                hours_practice,
                hours_exam,
                lesson_type,
                int(is_double_pair),
                item_id,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def delete_curriculum_item(item_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM curriculum_items WHERE id = ?", (item_id,))
        conn.commit()
    finally:
        conn.close()
