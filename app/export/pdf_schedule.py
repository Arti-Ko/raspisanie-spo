from app.export.pdf_common import content_width_px, render_html_to_pdf, table_tag
from app.repositories.schedule import ScheduleEntry

DAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб"]
PAIRS = [1, 2, 3, 4, 5]
COLUMN_WIDTHS = [10] + [15] * len(DAYS)


def export_schedule(
    group_name: str,
    week_label: str,
    entries: list[ScheduleEntry],
    hours: int,
    hours_limit: int | None,
    file_path: str,
    bell_times: dict[int, str] | None = None,
) -> None:
    html = _build_html(
        group_name, week_label, entries, hours, hours_limit, bell_times or {}
    )
    render_html_to_pdf(html, file_path, landscape=True)


def _build_html(
    group_name: str,
    week_label: str,
    entries: list[ScheduleEntry],
    hours: int,
    hours_limit: int | None,
    bell_times: dict[int, str],
) -> str:
    width = content_width_px(landscape=True)
    entry_by_slot = {(e.day_of_week, e.pair_number): e for e in entries}

    header_cells = "".join(f"<th>{day}</th>" for day in DAYS)
    body_rows = []
    for row_index, pair in enumerate(PAIRS):
        css_class = "even" if row_index % 2 else ""
        pair_label = f"Пара {pair}"
        if pair in bell_times:
            pair_label += f"<br>{bell_times[pair]}"
        cells = [f"<td><b>{pair_label}</b></td>"]
        for day_of_week in range(1, len(DAYS) + 1):
            entry = entry_by_slot.get((day_of_week, pair))
            cells.append(
                f"<td>{_cell_text(entry)}</td>" if entry else "<td>&nbsp;</td>"
            )
        body_rows.append(f"<tr class='{css_class}'>{''.join(cells)}</tr>")

    limit_text = f" / лимит {hours_limit} ч." if hours_limit is not None else ""
    over_class = (
        " over-limit" if hours_limit is not None and hours > hours_limit else ""
    )

    return f"""
    <h1>Расписание группы {group_name}</h1>
    <div class="subtitle">{week_label}</div>
    <div class="summary{over_class}">Часов на неделе: {hours}{limit_text}</div>
    {table_tag(width, COLUMN_WIDTHS)}
        <tr><th>&nbsp;</th>{header_cells}</tr>
        {"".join(body_rows)}
    </table>
    """


def _cell_text(entry: ScheduleEntry) -> str:
    text = f"<b>{entry.subject_name}</b><br>{entry.effective_teacher_name}"
    if entry.room:
        text += f"<br>каб. {entry.room}"
    if entry.substitute_teacher_id:
        text += " <i>(замена)</i>"
    return text
