from app.export.pdf_common import render_html_to_pdf
from app.export.pdf_schedule import build_week_html
from app.repositories.calendar_weeks import CalendarWeek
from app.repositories.groups import Group
from app.repositories.schedule import ScheduleEntry


def export_semester_schedule(
    groups: list[Group],
    weeks: list[CalendarWeek],
    semester_label: str,
    entries_by_group_week: dict[tuple[int, int], list[ScheduleEntry]],
    file_path: str,
) -> None:
    sections = []
    is_first = True
    for group in groups:
        for week in weeks:
            entries = entries_by_group_week.get((group.id, week.id), [])
            week_label = f"{semester_label}, Неделя {week.week_number}"
            sections.append(
                build_week_html(
                    group.name,
                    week_label,
                    week.date_range_label,
                    entries,
                    week.includes_saturday,
                    force_page_break_first=not is_first,
                )
            )
            is_first = False
    render_html_to_pdf("".join(sections), file_path, landscape=False)
