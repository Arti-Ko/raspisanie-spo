from app.export.pdf_common import content_width_px, render_html_to_pdf, table_tag
from app.export.schedule_layout import BLOCKS, DAY_LABELS, build_block_rows
from app.repositories.schedule import ScheduleEntry

COLUMN_WIDTHS = [12, 14, 24.67, 24.67, 24.66]


def export_schedule(
    group_name: str,
    week_label: str,
    entries: list[ScheduleEntry],
    hours: int,
    hours_limit: int | None,
    file_path: str,
) -> None:
    html = _build_html(group_name, week_label, entries, hours, hours_limit)
    render_html_to_pdf(html, file_path, landscape=False)


def _build_html(
    group_name: str,
    week_label: str,
    entries: list[ScheduleEntry],
    hours: int,
    hours_limit: int | None,
) -> str:
    width = content_width_px(landscape=False)
    entry_by_slot = {(e.day_of_week, e.pair_number): e for e in entries}

    limit_text = f" / лимит {hours_limit} ч." if hours_limit is not None else ""
    over_class = (
        " over-limit" if hours_limit is not None and hours > hours_limit else ""
    )

    blocks_html = "".join(
        _build_block_html(days, entry_by_slot, width) for days in BLOCKS
    )

    return f"""
    <h1>Расписание группы {group_name}</h1>
    <div class="subtitle">{week_label}</div>
    <div class="summary{over_class}">Часов на неделе: {hours}{limit_text}</div>
    {blocks_html}
    """


def _build_block_html(days: tuple[int, ...], entry_by_slot: dict, width: int) -> str:
    title = " – ".join(DAY_LABELS[day] for day in (days[0], days[-1]))
    header_cells = "".join(f"<th>{DAY_LABELS[day]}</th>" for day in days)

    rows = build_block_rows(days)
    body_rows = []
    pair_row_count: dict[int, int] = {}
    for spec in rows:
        if not spec.is_zero_period:
            pair_row_count[spec.pair_number] = (
                pair_row_count.get(spec.pair_number, 0) + 1
            )

    for row_index, spec in enumerate(rows):
        css_class = "even" if row_index % 2 else ""
        cells = []

        if spec.is_zero_period:
            cells.append("<td><b>0</b></td>")
        elif spec.starts_pair:
            cells.append(f"<td rowspan='2'><b>Пара {spec.pair_number}</b></td>")

        cells.append(f"<td>{spec.time_label}</td>")

        for day in days:
            if spec.is_zero_period:
                cells.append("<td>&nbsp;</td>")
                continue
            entry = entry_by_slot.get((day, spec.pair_number))
            if spec.starts_pair:
                content = _cell_text(entry) if entry else "&nbsp;"
                cells.append(f"<td rowspan='2'>{content}</td>")
            # second урок row: cell already covered by rowspan above, emit nothing

        body_rows.append(f"<tr class='{css_class}'>{''.join(cells)}</tr>")

    return f"""
    <h2>{title}</h2>
    {table_tag(width, COLUMN_WIDTHS)}
        <tr><th>Пара</th><th>Время</th>{header_cells}</tr>
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
