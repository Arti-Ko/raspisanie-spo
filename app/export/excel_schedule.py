from openpyxl import Workbook

from app.export.excel_styles import (
    OVER_LIMIT_FILL,
    SUBTITLE_FONT,
    TITLE_FONT,
    style_data_row,
    style_header_row,
)
from app.repositories.schedule import ScheduleEntry

DAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб"]
PAIRS = [1, 2, 3, 4, 5]


def export_schedule(
    group_name: str,
    week_label: str,
    entries: list[ScheduleEntry],
    hours: int,
    hours_limit: int | None,
    file_path: str,
    bell_times: dict[int, str] | None = None,
) -> None:
    bell_times = bell_times or {}
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Расписание"

    last_col = 1 + len(DAYS)
    sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=last_col)
    sheet.cell(
        row=1, column=1, value=f"Расписание группы {group_name} — {week_label}"
    ).font = TITLE_FONT

    limit_text = f" / лимит {hours_limit} ч." if hours_limit is not None else ""
    sheet.merge_cells(start_row=2, start_column=1, end_row=2, end_column=last_col)
    hours_cell = sheet.cell(
        row=2, column=1, value=f"Часов на неделе: {hours}{limit_text}"
    )
    hours_cell.font = SUBTITLE_FONT
    if hours_limit is not None and hours > hours_limit:
        hours_cell.fill = OVER_LIMIT_FILL

    header_row = 4
    sheet.cell(row=header_row, column=1, value="Пара")
    for col, day in enumerate(DAYS, start=2):
        sheet.cell(row=header_row, column=col, value=day)
    style_header_row(sheet, header_row, 1, last_col)

    entry_by_slot = {(e.day_of_week, e.pair_number): e for e in entries}
    for row_offset, pair in enumerate(PAIRS):
        row = header_row + 1 + row_offset
        pair_label = f"Пара {pair}"
        if pair in bell_times:
            pair_label += f"\n{bell_times[pair]}"
        sheet.cell(row=row, column=1, value=pair_label)
        for col_offset, _day in enumerate(DAYS):
            day_of_week = col_offset + 1
            entry = entry_by_slot.get((day_of_week, pair))
            col = col_offset + 2
            if entry:
                text = f"{entry.subject_name}\n{entry.effective_teacher_name}"
                if entry.room:
                    text += f"\nкаб. {entry.room}"
                if entry.substitute_teacher_id:
                    text += " (замена)"
                sheet.cell(row=row, column=col, value=text)
        style_data_row(sheet, row, 1, last_col)
        sheet.row_dimensions[row].height = 48

    sheet.column_dimensions["A"].width = 10
    for col_letter in "BCDEFG":
        sheet.column_dimensions[col_letter].width = 20

    workbook.save(file_path)
