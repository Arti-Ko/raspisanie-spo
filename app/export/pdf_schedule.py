from app.export.pdf_common import content_width_px, render_html_to_pdf, table_tag
from app.export.schedule_layout import DAY_LABELS, blocks_for_week, build_block_rows
from app.repositories.schedule import ScheduleEntry
from app.repositories.teachers import list_teachers
from app.repositories.text_format import abbreviate_name

# Пара, Звонки, затем на каждый день: контент + Каб
COLUMN_WIDTHS_BASE = [4, 12]
DAY_PAIR_WIDTHS = [23, 5]


def export_schedule(
    group_name: str,
    week_label: str,
    date_range_label: str,
    entries: list[ScheduleEntry],
    includes_saturday: bool,
    file_path: str,
) -> None:
    html = build_week_html(
        group_name, week_label, date_range_label, entries, includes_saturday
    )
    render_html_to_pdf(html, file_path, landscape=False)


def build_week_html(
    group_name: str,
    week_label: str,
    date_range_label: str,
    entries: list[ScheduleEntry],
    includes_saturday: bool,
    force_page_break_first: bool = False,
) -> str:
    width = content_width_px(landscape=False)
    entry_by_slot = {(e.day_of_week, e.pair_number): e for e in entries}
    teacher_colors = {t.id: t.color for t in list_teachers()}
    blocks = blocks_for_week(includes_saturday)

    date_line = (
        f"<div class='subtitle'>Даты: {date_range_label}</div>"
        if date_range_label
        else ""
    )

    blocks_html = "".join(
        _build_block_html(
            days,
            entry_by_slot,
            width,
            teacher_colors,
            index > 0 or force_page_break_first,
        )
        for index, days in enumerate(blocks)
    )

    return f"""
    <h1>Расписание группы {group_name} — {week_label}</h1>
    {date_line}
    {blocks_html}
    """


def _build_block_html(
    days: tuple[int, ...],
    entry_by_slot: dict,
    width: int,
    teacher_colors: dict,
    page_break_before: bool,
) -> str:
    column_widths = COLUMN_WIDTHS_BASE + DAY_PAIR_WIDTHS * len(days)
    header_cells = "".join(f"<th>{DAY_LABELS[day]}</th><th>Каб</th>" for day in days)

    rows = build_block_rows(days)
    body_rows = []

    for row_index, spec in enumerate(rows):
        css_class = "even" if row_index % 2 else ""
        cells = []

        if spec.is_zero_period:
            cells.append("<td><b>0</b></td>")
        elif spec.starts_pair:
            cells.append(f"<td rowspan='2'><b>{spec.pair_number}</b></td>")

        cells.append(f"<td>{spec.time_label}</td>")

        for day in days:
            entry = entry_by_slot.get((day, spec.pair_number))
            if spec.is_zero_period:
                content_cell, room_cell = _cells(entry, teacher_colors)
                cells.append(content_cell)
                cells.append(room_cell)
            elif spec.starts_pair:
                content_cell, room_cell = _cells(entry, teacher_colors, rowspan=2)
                cells.append(content_cell)
                cells.append(room_cell)
            # second урок row: content/room already covered by rowspan above

        body_rows.append(f"<tr class='{css_class}'>{''.join(cells)}</tr>")

    page_break = " style='page-break-before: always;'" if page_break_before else ""
    return f"""
    <div{page_break}></div>
    {table_tag(width, column_widths)}
        <tr><th>&nbsp;</th><th>&nbsp;</th>{header_cells}</tr>
        {"".join(body_rows)}
    </table>
    """


def _cells(
    entry: ScheduleEntry | None, teacher_colors: dict, rowspan: int = 1
) -> tuple[str, str]:
    span = f" rowspan='{rowspan}'" if rowspan > 1 else ""
    if entry is None:
        return f"<td{span}>&nbsp;</td>", f"<td{span}>&nbsp;</td>"
    color = teacher_colors.get(entry.effective_teacher_id)
    style = f" style='background-color:{color};'" if color else ""
    content = _cell_text(entry)
    room = entry.room or ""
    return f"<td{span}{style}>{content}</td>", f"<td{span}{style}>{room}</td>"


def _cell_text(entry: ScheduleEntry) -> str:
    name = abbreviate_name(entry.effective_teacher_name)
    text = f"<b>{entry.subject_name}</b><br><i>{name}</i>"
    if entry.substitute_teacher_id:
        text += " <i>(замена)</i>"
    return text
