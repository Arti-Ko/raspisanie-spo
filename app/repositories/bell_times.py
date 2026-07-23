from dataclasses import dataclass

from app.db.database import get_connection

DAY_NAMES = {
    1: "Понедельник",
    2: "Вторник",
    3: "Среда",
    4: "Четверг",
    5: "Пятница",
    6: "Суббота",
}
PAIR_NUMBERS = (1, 2, 3, 4, 5)
LESSON_NUMBERS = (1, 2)


@dataclass(frozen=True)
class ZeroPeriod:
    day_of_week: int
    enabled: bool
    start_time: str | None
    end_time: str | None

    @property
    def label(self) -> str:
        if not self.enabled or not self.start_time or not self.end_time:
            return ""
        return f"{self.start_time}–{self.end_time}"


@dataclass(frozen=True)
class LessonTime:
    day_of_week: int
    pair_number: int
    lesson_number: int
    start_time: str
    end_time: str

    @property
    def label(self) -> str:
        return f"{self.start_time}–{self.end_time}"


def get_zero_period(day_of_week: int) -> ZeroPeriod:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT has_zero_period, zero_period_start, zero_period_end FROM bell_schedule_days WHERE day_of_week = ?",
            (day_of_week,),
        ).fetchone()
        return ZeroPeriod(
            day_of_week,
            bool(row["has_zero_period"]),
            row["zero_period_start"],
            row["zero_period_end"],
        )
    finally:
        conn.close()


def set_zero_period(
    day_of_week: int, enabled: bool, start_time: str | None, end_time: str | None
) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE bell_schedule_days SET has_zero_period = ?, zero_period_start = ?, zero_period_end = ? "
            "WHERE day_of_week = ?",
            (int(enabled), start_time, end_time, day_of_week),
        )
        conn.commit()
    finally:
        conn.close()


def list_lessons(day_of_week: int) -> list[LessonTime]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT day_of_week, pair_number, lesson_number, start_time, end_time FROM bell_schedule_lessons "
            "WHERE day_of_week = ? ORDER BY pair_number, lesson_number",
            (day_of_week,),
        ).fetchall()
        return [
            LessonTime(
                row["day_of_week"],
                row["pair_number"],
                row["lesson_number"],
                row["start_time"],
                row["end_time"],
            )
            for row in rows
        ]
    finally:
        conn.close()


def set_lesson_time(
    day_of_week: int,
    pair_number: int,
    lesson_number: int,
    start_time: str,
    end_time: str,
) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE bell_schedule_lessons SET start_time = ?, end_time = ? "
            "WHERE day_of_week = ? AND pair_number = ? AND lesson_number = ?",
            (start_time, end_time, day_of_week, pair_number, lesson_number),
        )
        conn.commit()
    finally:
        conn.close()


def pair_label(day_of_week: int, pair_number: int) -> str:
    lessons = {
        lesson.lesson_number: lesson
        for lesson in list_lessons(day_of_week)
        if lesson.pair_number == pair_number
    }
    first, second = lessons.get(1), lessons.get(2)
    if first and second:
        return f"{first.start_time}–{second.end_time}"
    if first:
        return first.label
    return ""
