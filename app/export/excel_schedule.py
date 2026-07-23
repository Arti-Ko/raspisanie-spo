from openpyxl import Workbook
from openpyxl.styles import Alignment

from app.export.excel_styles import (
    OVER_LIMIT_FILL,
    SUBTITLE_FONT,
    TITLE_FONT,
    style_data_row,
    style_header_row,
)
from app.export.schedule_layout import BLOCKS, DAY_LABELS, build_block_rows
from app.repositories.schedule import ScheduleEntry

CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
BLOCK_COLUMNS = 5  # Пара, Время, + 3 дня


def export_schedule(
    group_name: str,
    week_label: str,
    entries: list[ScheduleEntry],
    hours: int,
    hours_limit: int | None,
    file_path: str,
) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Расписание"
    entry_by_slot = {(e.day_of_week, e.pair_number): e for e in entries}

    sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=BLOCK_COLUMNS)
    sheet.cell(
        row=1, column=1, value=f"Расписание группы {group_name} — {week_label}"
    ).font = TITLE_FONT

    limit_text = f" / лимит {hours_limit} ч." if hours_limit is not None else ""
    sheet.merge_cells(start_row=2, start_column=1, end_row=2, end_column=BLOCK_COLUMNS)
    hours_cell = sheet.cell(
        row=2, column=1, value=f"Часов на неделе: {hours}{limit_text}"
    )
    hours_cell.font = SUBTITLE_FONT
    if hours_limit is not None and hours > hours_limit:
        hours_cell.fill = OVER_LIMIT_FILL

    row = 4
    for days in BLOCKS:
        row = _write_block(sheet, row, days, entry_by_slot)
        row += 2

    sheet.column_dimensions["A"].width = 10
    sheet.column_dimensions["B"].width = 14
    for col_letter in "CDE":
        sheet.column_dimensions[col_letter].width = 22

    workbook.save(file_path)


def _write_block(
    sheet, start_row: int, days: tuple[int, ...], entry_by_slot: dict
) -> int:
    title = " – ".join(DAY_LABELS[day] for day in (days[0], days[-1]))
    sheet.merge_cells(
        start_row=start_row, start_column=1, end_row=start_row, end_column=BLOCK_COLUMNS
    )
    sheet.cell(row=start_row, column=1, value=title).font = SUBTITLE_FONT

    header_row = start_row + 1
    sheet.cell(row=header_row, column=1, value="Пара")
    sheet.cell(row=header_row, column=2, value="Время")
    for col_offset, day in enumerate(days):
        sheet.cell(row=header_row, column=3 + col_offset, value=DAY_LABELS[day])
    style_header_row(sheet, header_row, 1, BLOCK_COLUMNS)

    rows = build_block_rows(days)
    pair_merge_start: dict[int, int] = {}
    for row_offset, spec in enumerate(rows):
        row = header_row + 1 + row_offset
        sheet.cell(row=row, column=2, value=spec.time_label)

        if spec.is_zero_period:
            sheet.cell(row=row, column=1, value="0")
        elif spec.starts_pair:
            pair_merge_start[spec.pair_number] = row
            sheet.cell(row=row, column=1, value=f"Пара {spec.pair_number}")
        else:
            first_row = pair_merge_start[spec.pair_number]
            sheet.merge_cells(
                start_row=first_row, start_column=1, end_row=row, end_column=1
            )

        for col_offset, day in enumerate(days):
            col = 3 + col_offset
            if spec.is_zero_period:
                style_data_row(sheet, row, col, col)
                continue
            entry = entry_by_slot.get((day, spec.pair_number))
            if spec.starts_pair and entry:
                sheet.merge_cells(
                    start_row=row, start_column=col, end_row=row + 1, end_column=col
                )
                sheet.cell(row=row, column=col, value=_entry_text(entry)).alignment = (
                    CENTER
                )
        style_data_row(sheet, row, 1, BLOCK_COLUMNS)
        sheet.row_dimensions[row].height = 30

    return header_row + len(rows)


def _entry_text(entry: ScheduleEntry) -> str:
    text = f"{entry.subject_name}\n{entry.effective_teacher_name}"
    if entry.room:
        text += f"\nкаб. {entry.room}"
    if entry.substitute_teacher_id:
        text += " (замена)"
    return text
