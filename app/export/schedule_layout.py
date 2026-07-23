from dataclasses import dataclass

from app.repositories.bell_times import get_zero_period, list_lessons

DAY_LABELS = {1: "Пн", 2: "Вт", 3: "Ср", 4: "Чт", 5: "Пт", 6: "Сб"}
BLOCK_SIZE = 3


@dataclass(frozen=True)
class RowSpec:
    pair_number: int
    lesson_number: int | None
    time_label: str

    @property
    def is_zero_period(self) -> bool:
        return self.pair_number == 0

    @property
    def starts_pair(self) -> bool:
        return self.lesson_number == 1


def blocks_for_week(includes_saturday: bool) -> list[tuple[int, ...]]:
    days = list(range(1, 7)) if includes_saturday else list(range(1, 6))
    return [tuple(days[i : i + BLOCK_SIZE]) for i in range(0, len(days), BLOCK_SIZE)]


def build_block_rows(days: tuple[int, ...]) -> list[RowSpec]:
    reference_day = days[0]
    rows: list[RowSpec] = []

    zero_period = next(
        (zp for zp in (get_zero_period(day) for day in days) if zp.enabled), None
    )
    if zero_period:
        rows.append(RowSpec(0, None, zero_period.label))

    lessons_by_pair: dict[int, dict[int, str]] = {}
    for lesson in list_lessons(reference_day):
        lessons_by_pair.setdefault(lesson.pair_number, {})[
            lesson.lesson_number
        ] = lesson.label

    for pair_number in range(1, 5):
        pair_lessons = lessons_by_pair.get(pair_number, {})
        rows.append(RowSpec(pair_number, 1, pair_lessons.get(1, "")))
        rows.append(RowSpec(pair_number, 2, pair_lessons.get(2, "")))
    return rows
