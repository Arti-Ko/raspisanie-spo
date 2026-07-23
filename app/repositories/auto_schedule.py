from dataclasses import dataclass, field

from app.repositories.calendar_weeks import CalendarWeek, list_weeks
from app.repositories.schedule import (
    clear_group_week,
    clear_group_weeks,
    list_entries_for_group_week,
    room_conflict_at,
    set_entry,
    teacher_conflict_at,
)
from app.repositories.tarification import Assignment, list_assignments_for_group
from app.repositories.teachers import list_teachers

ALL_DAYS = list(range(1, 7))
PAIRS = list(range(1, 5))
HOURS_PER_PAIR = 2
PRACTICE_BLOCK_PAIRS = 3
DOUBLE_PAIR_HOURS = HOURS_PER_PAIR * 2


@dataclass
class AutoScheduleResult:
    weeks_processed: int = 0
    pairs_placed: int = 0
    unplaced_hours: dict[str, int] = field(default_factory=dict)


def _days_for_week(week: CalendarWeek) -> list[int]:
    return ALL_DAYS if week.includes_saturday else ALL_DAYS[:-1]


def generate_group_semester_schedule(
    group_id: int, academic_year_id: int, semester: int, clear_existing: bool = False
) -> AutoScheduleResult:
    weeks = list_weeks(academic_year_id, semester)
    if clear_existing:
        clear_group_weeks(group_id, [week.id for week in weeks])
    return _generate(group_id, weeks, semester, weeks)


def regenerate_week(
    group_id: int, academic_year_id: int, semester: int, week_id: int
) -> AutoScheduleResult:
    all_weeks = list_weeks(academic_year_id, semester)
    target_week = next((week for week in all_weeks if week.id == week_id), None)
    if target_week is None:
        return AutoScheduleResult()
    clear_group_week(group_id, week_id)
    return _generate(group_id, all_weeks, semester, [target_week])


def _generate(
    group_id: int,
    all_weeks: list[CalendarWeek],
    semester: int,
    weeks_to_fill: list[CalendarWeek],
) -> AutoScheduleResult:
    result = AutoScheduleResult()
    if not all_weeks:
        return result

    assignments = _semester_assignments(group_id, semester)
    assignments_by_id = {a.id: a for a in assignments}
    teacher_rooms = {t.id: t.room for t in list_teachers()}
    remaining = _remaining_hours(assignments, all_weeks, group_id, semester)
    theory_order = [
        a.id for a in assignments if a.lesson_type == "theory" and not a.is_double_pair
    ]
    pointer = 0

    for week in weeks_to_fill:
        result.weeks_processed += 1
        days = _days_for_week(week)
        existing = list_entries_for_group_week(group_id, week.id)
        occupied = {(e.day_of_week, e.pair_number) for e in existing}
        placed_today = {
            day: {e.assignment_id for e in existing if e.day_of_week == day}
            for day in days
        }
        placed_this_week = len(existing)
        limit_pairs = week.hours // HOURS_PER_PAIR

        for assignment in assignments:
            if assignment.lesson_type != "practice" or assignment.is_double_pair:
                continue
            block_hours = HOURS_PER_PAIR * PRACTICE_BLOCK_PAIRS
            while (
                remaining.get(assignment.id, 0) >= block_hours
                and placed_this_week + PRACTICE_BLOCK_PAIRS <= limit_pairs
            ):
                placed = _place_block(
                    group_id, week, assignment, teacher_rooms, occupied, days
                )
                if not placed:
                    break
                occupied.update(placed)
                for day, _pair in placed:
                    placed_today.setdefault(day, set()).add(assignment.id)
                placed_this_week += len(placed)
                remaining[assignment.id] -= block_hours
                result.pairs_placed += len(placed)

        for assignment in assignments:
            if not assignment.is_double_pair:
                continue
            while (
                remaining.get(assignment.id, 0) >= DOUBLE_PAIR_HOURS
                and placed_this_week + 2 <= limit_pairs
            ):
                placed = _place_first_last(
                    group_id, week, assignment, teacher_rooms, occupied, days
                )
                if not placed:
                    break
                occupied.update(placed)
                for day, _pair in placed:
                    placed_today.setdefault(day, set()).add(assignment.id)
                placed_this_week += len(placed)
                remaining[assignment.id] -= DOUBLE_PAIR_HOURS
                result.pairs_placed += len(placed)

        for assignment in assignments:
            if assignment.lesson_type != "lab" or remaining.get(assignment.id, 0) <= 0:
                continue
            wanted_pairs = min(
                remaining[assignment.id] // HOURS_PER_PAIR,
                limit_pairs - placed_this_week,
                len(PAIRS),
            )
            if wanted_pairs <= 0:
                continue
            placed = _place_same_day(
                group_id, week, assignment, teacher_rooms, occupied, wanted_pairs, days
            )
            if not placed:
                continue
            occupied.update(placed)
            for day, _pair in placed:
                placed_today.setdefault(day, set()).add(assignment.id)
            placed_this_week += len(placed)
            remaining[assignment.id] -= len(placed) * HOURS_PER_PAIR
            result.pairs_placed += len(placed)

        for day in days:
            if placed_this_week >= limit_pairs:
                break
            for pair in PAIRS:
                if placed_this_week >= limit_pairs:
                    break
                if (day, pair) in occupied:
                    continue
                assignment_id, pointer = _pick_theory(
                    theory_order,
                    remaining,
                    pointer,
                    assignments_by_id,
                    teacher_rooms,
                    group_id,
                    week.id,
                    day,
                    pair,
                    placed_today.setdefault(day, set()),
                )
                if assignment_id is None:
                    continue
                room = teacher_rooms.get(
                    assignments_by_id[assignment_id].teacher_id, ""
                )
                set_entry(group_id, week.id, day, pair, assignment_id, room, None)
                remaining[assignment_id] -= HOURS_PER_PAIR
                placed_today[day].add(assignment_id)
                occupied.add((day, pair))
                placed_this_week += 1
                result.pairs_placed += 1

    result.unplaced_hours = {
        assignments_by_id[aid].subject_name: hours
        for aid, hours in remaining.items()
        if hours > 0
    }
    return result


def _semester_assignments(group_id: int, semester: int) -> list[Assignment]:
    return [
        a
        for a in list_assignments_for_group(group_id)
        if a.semester == semester
        or (a.other_semester == semester and a.transferred_hours > 0)
    ]


def _remaining_hours(
    assignments: list[Assignment],
    weeks: list[CalendarWeek],
    group_id: int,
    semester: int,
) -> dict[int, int]:
    base_hours = {}
    for a in assignments:
        base_hours[a.id] = (
            a.hours_in_natural_semester
            if a.semester == semester
            else a.transferred_hours
        )

    already_placed: dict[int, int] = {}
    for week in weeks:
        for entry in list_entries_for_group_week(group_id, week.id):
            already_placed[entry.assignment_id] = (
                already_placed.get(entry.assignment_id, 0) + HOURS_PER_PAIR
            )

    return {
        assignment_id: max(0, hours - already_placed.get(assignment_id, 0))
        for assignment_id, hours in base_hours.items()
    }


def _has_conflict(
    assignment: Assignment,
    teacher_rooms: dict,
    group_id: int,
    week_id: int,
    day: int,
    pair: int,
) -> bool:
    if teacher_conflict_at(
        assignment.teacher_id, week_id, day, pair, exclude_group_id=group_id
    ):
        return True
    room = teacher_rooms.get(assignment.teacher_id, "")
    if room and room_conflict_at(room, week_id, day, pair, exclude_group_id=group_id):
        return True
    return False


def _place_block(
    group_id, week, assignment, teacher_rooms, occupied, days
) -> list[tuple[int, int]]:
    room = teacher_rooms.get(assignment.teacher_id, "")
    last_start = PAIRS[-1] - PRACTICE_BLOCK_PAIRS + 1
    for day in days:
        for start in range(1, last_start + 1):
            candidate_pairs = list(range(start, start + PRACTICE_BLOCK_PAIRS))
            if any((day, p) in occupied for p in candidate_pairs):
                continue
            if any(
                _has_conflict(assignment, teacher_rooms, group_id, week.id, day, p)
                for p in candidate_pairs
            ):
                continue
            for p in candidate_pairs:
                set_entry(group_id, week.id, day, p, assignment.id, room, None)
            return [(day, p) for p in candidate_pairs]
    return []


def _place_first_last(
    group_id, week, assignment, teacher_rooms, occupied, days
) -> list[tuple[int, int]]:
    room = teacher_rooms.get(assignment.teacher_id, "")
    first_pair, last_pair = PAIRS[0], PAIRS[-1]
    for day in days:
        if (day, first_pair) in occupied or (day, last_pair) in occupied:
            continue
        if _has_conflict(
            assignment, teacher_rooms, group_id, week.id, day, first_pair
        ) or _has_conflict(
            assignment, teacher_rooms, group_id, week.id, day, last_pair
        ):
            continue
        set_entry(group_id, week.id, day, first_pair, assignment.id, room, None)
        set_entry(group_id, week.id, day, last_pair, assignment.id, room, None)
        return [(day, first_pair), (day, last_pair)]
    return []


def _place_same_day(
    group_id, week, assignment, teacher_rooms, occupied, wanted_pairs, days
) -> list[tuple[int, int]]:
    room = teacher_rooms.get(assignment.teacher_id, "")
    for day in days:
        usable = []
        for pair in PAIRS:
            if (day, pair) in occupied or _has_conflict(
                assignment, teacher_rooms, group_id, week.id, day, pair
            ):
                continue
            usable.append(pair)
            if len(usable) == wanted_pairs:
                break
        if len(usable) == wanted_pairs:
            for pair in usable:
                set_entry(group_id, week.id, day, pair, assignment.id, room, None)
            return [(day, pair) for pair in usable]
    return []


def _pick_theory(
    order,
    remaining,
    pointer,
    assignments_by_id,
    teacher_rooms,
    group_id,
    week_id,
    day,
    pair,
    used_today,
):
    if not order:
        return None, pointer
    n = len(order)
    for offset in range(n):
        assignment_id = order[(pointer + offset) % n]
        if remaining.get(assignment_id, 0) <= 0 or assignment_id in used_today:
            continue
        if _has_conflict(
            assignments_by_id[assignment_id],
            teacher_rooms,
            group_id,
            week_id,
            day,
            pair,
        ):
            continue
        return assignment_id, pointer + offset + 1
    for offset in range(n):
        assignment_id = order[(pointer + offset) % n]
        if remaining.get(assignment_id, 0) <= 0:
            continue
        if _has_conflict(
            assignments_by_id[assignment_id],
            teacher_rooms,
            group_id,
            week_id,
            day,
            pair,
        ):
            continue
        return assignment_id, pointer + offset + 1
    return None, pointer
