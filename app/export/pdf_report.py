from app.export.pdf_common import content_width_px, render_html_to_pdf, table_tag
from app.repositories.reports import SubstitutionLine, TeacherReport, WeekLine

WEEKLY_WIDTHS = [12, 10, 16, 34, 10, 18]
SUB_WIDTHS = [12, 10, 16, 34, 10, 18]


def export_teacher_report(report: TeacherReport, file_path: str) -> None:
    html = _build_html(report)
    render_html_to_pdf(html, file_path, landscape=False)


def _build_html(report: TeacherReport) -> str:
    width = content_width_px(landscape=False)
    weekly_rows = _rows(report.weekly_lines, _weekly_row) or _empty_row(6)
    covered_by_rows = _rows(report.covered_by_others, _sub_row) or _empty_row(6)
    covered_for_rows = _rows(report.covered_for_others, _sub_row) or _empty_row(6)

    return f"""
    <h1>СПРАВКА О ПРОЧИТАННЫХ ЧАСАХ</h1>
    <div class="subtitle">Преподаватель: <b>{report.teacher_name}</b></div>

    <div class="summary">
        По тарификации: I полугодие — {report.plan_hours[1]} ч., II полугодие — {report.plan_hours[2]} ч.,
        всего <b>{report.plan_total} ч.</b><br>
        Прочитано фактически: I полугодие — {report.actual_hours[1]} ч., II полугодие — {report.actual_hours[2]} ч.,
        всего <b>{report.actual_total} ч.</b><br>
        Разница (план − факт): <b>{report.difference} ч.</b>
    </div>

    <h2>Понедельная разбивка прочитанных часов</h2>
    {table_tag(width, WEEKLY_WIDTHS)}
        <tr><th>Полугодие</th><th>Неделя</th><th>Группа</th><th>Предмет</th><th>Часов</th><th>Замена</th></tr>
        {weekly_rows}
    </table>

    <h2>Кто заменял этого преподавателя</h2>
    {table_tag(width, SUB_WIDTHS)}
        <tr><th>Полугодие</th><th>Неделя</th><th>Группа</th><th>Предмет</th><th>Часов</th><th>Кто</th></tr>
        {covered_by_rows}
    </table>

    <h2>Кого заменял этот преподаватель</h2>
    {table_tag(width, SUB_WIDTHS)}
        <tr><th>Полугодие</th><th>Неделя</th><th>Группа</th><th>Предмет</th><th>Часов</th><th>Кто</th></tr>
        {covered_for_rows}
    </table>

    <div class="signature">
        Подпись преподавателя ____________________&nbsp;&nbsp;&nbsp;&nbsp;
        Зам. директора по УР ____________________
    </div>
    """


def _rows(lines, row_fn) -> str:
    return "".join(row_fn(line, index) for index, line in enumerate(lines))


def _weekly_row(line: WeekLine, index: int) -> str:
    css_class = "even" if index % 2 else ""
    return (
        f"<tr class='{css_class}'><td>{line.semester}-е</td><td>{line.week_number}</td><td>{line.group_name}</td>"
        f"<td>{line.subject_name}</td><td>{line.hours}</td><td>{'да' if line.is_substitute else ''}</td></tr>"
    )


def _sub_row(line: SubstitutionLine, index: int) -> str:
    css_class = "even" if index % 2 else ""
    return (
        f"<tr class='{css_class}'><td>{line.semester}-е</td><td>{line.week_number}</td><td>{line.group_name}</td>"
        f"<td>{line.subject_name}</td><td>{line.hours}</td><td>{line.other_teacher_name}</td></tr>"
    )


def _empty_row(columns: int) -> str:
    return f"<tr><td colspan='{columns}'>— нет данных —</td></tr>"
