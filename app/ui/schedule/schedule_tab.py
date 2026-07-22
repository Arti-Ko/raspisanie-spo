from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.export.excel_schedule import export_schedule as export_schedule_excel
from app.export.pdf_schedule import export_schedule as export_schedule_pdf
from app.repositories.academic_years import list_academic_years
from app.repositories.auto_schedule import (
    generate_group_semester_schedule,
    regenerate_week,
)
from app.repositories.bell_times import list_bell_times
from app.repositories.calendar_weeks import list_weeks
from app.repositories.groups import list_groups
from app.repositories.schedule import (
    list_entries_for_group_week,
    room_conflict_at,
    set_entry,
    teacher_conflict_at,
    week_hours_for_group,
)
from app.repositories.tarification import list_assignments_for_group
from app.ui.schedule.lesson_cell_dialog import LessonCellDialog

DAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб"]


class ScheduleTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.year_combo = QComboBox()
        self.year_combo.currentIndexChanged.connect(self._reload_weeks)
        self.semester_combo = QComboBox()
        self.semester_combo.addItem("I полугодие", 1)
        self.semester_combo.addItem("II полугодие", 2)
        self.semester_combo.currentIndexChanged.connect(self._reload_weeks)
        self.week_combo = QComboBox()
        self.week_combo.currentIndexChanged.connect(self.refresh)
        self.group_combo = QComboBox()
        self.group_combo.currentIndexChanged.connect(self.refresh)

        excel_button = QPushButton("Экспорт в Excel")
        excel_button.clicked.connect(self._on_export_excel)
        pdf_button = QPushButton("Экспорт в PDF")
        pdf_button.clicked.connect(self._on_export_pdf)

        selector_row = QHBoxLayout()
        selector_row.addWidget(QLabel("Год:"))
        selector_row.addWidget(self.year_combo)
        selector_row.addWidget(QLabel("Полугодие:"))
        selector_row.addWidget(self.semester_combo)
        selector_row.addWidget(QLabel("Неделя:"))
        selector_row.addWidget(self.week_combo)
        selector_row.addWidget(QLabel("Группа:"))
        selector_row.addWidget(self.group_combo)
        selector_row.addStretch()
        selector_row.addWidget(excel_button)
        selector_row.addWidget(pdf_button)

        fill_button = QPushButton("Заполнить пустые пары (полугодие)")
        fill_button.clicked.connect(self._on_fill_empty)
        regenerate_semester_button = QPushButton("Пересобрать полугодие заново")
        regenerate_semester_button.clicked.connect(self._on_regenerate_semester)
        regenerate_week_button = QPushButton("Пересобрать только эту неделю")
        regenerate_week_button.clicked.connect(self._on_regenerate_week)

        actions_row = QHBoxLayout()
        actions_row.addWidget(fill_button)
        actions_row.addWidget(regenerate_semester_button)
        actions_row.addWidget(regenerate_week_button)
        actions_row.addStretch()

        self.table = QTableWidget(5, len(DAYS))
        self.table.setHorizontalHeaderLabels(DAYS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setMinimumSectionSize(64)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)

        self.hours_label = QLabel("")

        layout = QVBoxLayout(self)
        layout.addLayout(selector_row)
        layout.addLayout(actions_row)
        layout.addWidget(
            QLabel("Двойной клик по ячейке — назначить или изменить пару.")
        )
        layout.addWidget(self.table)
        layout.addWidget(self.hours_label)

        self._update_pair_labels()
        self.refresh_reference_data()

    def _update_pair_labels(self) -> None:
        labels = []
        for bell_time in list_bell_times():
            labels.append(f"Пара {bell_time.pair_number}\n{bell_time.label}")
        if not labels:
            labels = [f"Пара {n}" for n in range(1, 6)]
        self.table.setVerticalHeaderLabels(labels)

    def _bell_times_map(self) -> dict[int, str]:
        return {
            bell_time.pair_number: bell_time.label for bell_time in list_bell_times()
        }

    def refresh_reference_data(self) -> None:
        self._update_pair_labels()

        current_year = self.year_combo.currentData()
        self.year_combo.blockSignals(True)
        self.year_combo.clear()
        for year in list_academic_years():
            self.year_combo.addItem(year.name, year.id)
        self.year_combo.blockSignals(False)
        index = self.year_combo.findData(current_year)
        self.year_combo.setCurrentIndex(index if index >= 0 else 0)

        current_group = self.group_combo.currentData()
        self.group_combo.blockSignals(True)
        self.group_combo.clear()
        for group in list_groups():
            self.group_combo.addItem(group.name, group.id)
        self.group_combo.blockSignals(False)
        index = self.group_combo.findData(current_group)
        self.group_combo.setCurrentIndex(index if index >= 0 else 0)

        self._reload_weeks()

    def _reload_weeks(self) -> None:
        year_id = self.year_combo.currentData()
        semester = self.semester_combo.currentData()
        current_week = self.week_combo.currentData()
        self.week_combo.blockSignals(True)
        self.week_combo.clear()
        if year_id is not None and semester is not None:
            for week in list_weeks(year_id, semester):
                self.week_combo.addItem(
                    f"Неделя {week.week_number} ({week.hours} ч.)", week.id
                )
        self.week_combo.blockSignals(False)
        index = self.week_combo.findData(current_week)
        self.week_combo.setCurrentIndex(index if index >= 0 else 0)
        self.refresh()

    def _current_week_hours_limit(self) -> int | None:
        year_id = self.year_combo.currentData()
        semester = self.semester_combo.currentData()
        week_id = self.week_combo.currentData()
        if year_id is None or week_id is None:
            return None
        for week in list_weeks(year_id, semester):
            if week.id == week_id:
                return week.hours
        return None

    def refresh(self) -> None:
        self.table.clearContents()
        group_id = self.group_combo.currentData()
        week_id = self.week_combo.currentData()
        if group_id is None or week_id is None:
            self.hours_label.setText("")
            return

        entries = list_entries_for_group_week(group_id, week_id)
        for entry in entries:
            text = f"{entry.subject_name}\n{entry.effective_teacher_name}"
            if entry.room:
                text += f"\nкаб. {entry.room}"
            if entry.substitute_teacher_id:
                text += " (замена)"
            item = QTableWidgetItem(text)
            self.table.setItem(entry.pair_number - 1, entry.day_of_week - 1, item)
        self.table.resizeRowsToContents()

        hours = week_hours_for_group(group_id, week_id)
        limit = self._current_week_hours_limit()
        if limit is not None:
            over = " — ПРЕВЫШЕНИЕ" if hours > limit else ""
            self.hours_label.setText(
                f"Часов на неделе: {hours} / лимит {limit} ч.{over}"
            )
            self.hours_label.setStyleSheet(
                "color: #B3261E; font-weight: 600;" if hours > limit else ""
            )
        else:
            self.hours_label.setText(f"Часов на неделе: {hours}")
            self.hours_label.setStyleSheet("")

    def _on_cell_double_clicked(self, row: int, column: int) -> None:
        group_id = self.group_combo.currentData()
        week_id = self.week_combo.currentData()
        if group_id is None or week_id is None:
            QMessageBox.information(
                self, "Расписание", "Сначала выберите год, полугодие, неделю и группу."
            )
            return

        day_of_week = column + 1
        pair_number = row + 1
        entries = list_entries_for_group_week(group_id, week_id)
        current_entry = next(
            (
                e
                for e in entries
                if e.day_of_week == day_of_week and e.pair_number == pair_number
            ),
            None,
        )

        dialog = LessonCellDialog(self, group_id, current_entry)
        if not dialog.exec():
            return
        assignment_id, room, substitute_teacher_id = dialog.values()

        if assignment_id is not None:
            assignment = next(
                a for a in list_assignments_for_group(group_id) if a.id == assignment_id
            )
            effective_teacher_id = substitute_teacher_id or assignment.teacher_id

            teacher_clash = teacher_conflict_at(
                effective_teacher_id, week_id, day_of_week, pair_number, group_id
            )
            if teacher_clash and not self._confirm_conflict(
                f"Преподаватель {teacher_clash.effective_teacher_name} уже занят в это время в группе "
                f"«{self._group_name(teacher_clash.group_id)}». Всё равно поставить?"
            ):
                return
            room_clash = room_conflict_at(
                room, week_id, day_of_week, pair_number, group_id
            )
            if room_clash and not self._confirm_conflict(
                f"Кабинет {room} уже занят в это время другой группой. Всё равно поставить?"
            ):
                return

        set_entry(
            group_id,
            week_id,
            day_of_week,
            pair_number,
            assignment_id,
            room,
            substitute_teacher_id,
        )
        self.refresh()

    def _selected_context(self) -> tuple[int, int, int] | None:
        year_id = self.year_combo.currentData()
        semester = self.semester_combo.currentData()
        group_id = self.group_combo.currentData()
        if year_id is None or semester is None or group_id is None:
            QMessageBox.information(
                self, "Расписание", "Сначала выберите год, полугодие и группу."
            )
            return None
        return year_id, semester, group_id

    def _on_fill_empty(self) -> None:
        context = self._selected_context()
        if context is None:
            return
        year_id, semester, group_id = context
        group_name = self.group_combo.currentText()
        semester_name = self.semester_combo.currentText()
        answer = QMessageBox.question(
            self,
            "Заполнение расписания",
            f"Заполнить пустые пары группы «{group_name}» на {semester_name.lower()} "
            f"по назначениям с вкладки «Тарификация»?\n\nУже проставленные пары не будут затронуты.",
        )
        if answer != QMessageBox.Yes:
            return
        result = generate_group_semester_schedule(
            group_id, year_id, semester, clear_existing=False
        )
        self._show_generation_result(result)

    def _on_regenerate_semester(self) -> None:
        context = self._selected_context()
        if context is None:
            return
        year_id, semester, group_id = context
        group_name = self.group_combo.currentText()
        semester_name = self.semester_combo.currentText()
        answer = QMessageBox.question(
            self,
            "Пересборка полугодия",
            f"Это удалит ВСЕ пары группы «{group_name}» на {semester_name.lower()} (включая расставленные "
            f"вручную) и расставит их заново по текущим правилам. Продолжить?",
        )
        if answer != QMessageBox.Yes:
            return
        result = generate_group_semester_schedule(
            group_id, year_id, semester, clear_existing=True
        )
        self._show_generation_result(result)

    def _on_regenerate_week(self) -> None:
        context = self._selected_context()
        if context is None:
            return
        year_id, semester, group_id = context
        week_id = self.week_combo.currentData()
        if week_id is None:
            QMessageBox.information(self, "Расписание", "Сначала выберите неделю.")
            return
        group_name = self.group_combo.currentText()
        week_name = self.week_combo.currentText()
        answer = QMessageBox.question(
            self,
            "Пересборка недели",
            f"Это удалит и заново расставит пары группы «{group_name}» на «{week_name}». Продолжить?",
        )
        if answer != QMessageBox.Yes:
            return
        result = regenerate_week(group_id, year_id, semester, week_id)
        self._show_generation_result(result)

    def _show_generation_result(self, result) -> None:
        self.refresh()
        message = f"Обработано недель: {result.weeks_processed}\nПоставлено пар: {result.pairs_placed}"
        if result.unplaced_hours:
            details = "\n".join(
                f"— {name}: {hours} ч." for name, hours in result.unplaced_hours.items()
            )
            message += (
                f"\n\nНе поместилось (не хватило часов недели или мешают конфликты "
                f"преподавателя/кабинета):\n{details}"
            )
        QMessageBox.information(self, "Готово", message)

    def _confirm_conflict(self, message: str) -> bool:
        answer = QMessageBox.question(self, "Конфликт расписания", message)
        return answer == QMessageBox.Yes

    @staticmethod
    def _group_name(group_id: int) -> str:
        return next((g.name for g in list_groups() if g.id == group_id), str(group_id))

    def _export_context(self):
        group_id = self.group_combo.currentData()
        week_id = self.week_combo.currentData()
        if group_id is None or week_id is None:
            QMessageBox.information(
                self, "Экспорт", "Сначала выберите год, полугодие, неделю и группу."
            )
            return None
        group_name = self.group_combo.currentText()
        week_label = (
            f"{self.semester_combo.currentText()}, {self.week_combo.currentText()}"
        )
        entries = list_entries_for_group_week(group_id, week_id)
        hours = week_hours_for_group(group_id, week_id)
        limit = self._current_week_hours_limit()
        return group_name, week_label, entries, hours, limit

    def _on_export_excel(self) -> None:
        context = self._export_context()
        if context is None:
            return
        group_name, week_label, entries, hours, limit = context
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт в Excel", f"Расписание_{group_name}.xlsx", "Excel (*.xlsx)"
        )
        if not file_path:
            return
        try:
            export_schedule_excel(
                group_name,
                week_label,
                entries,
                hours,
                limit,
                file_path,
                self._bell_times_map(),
            )
        except OSError as error:
            QMessageBox.warning(self, "Ошибка экспорта", str(error))
            return
        QMessageBox.information(
            self, "Экспорт завершён", f"Файл сохранён:\n{file_path}"
        )

    def _on_export_pdf(self) -> None:
        context = self._export_context()
        if context is None:
            return
        group_name, week_label, entries, hours, limit = context
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт в PDF", f"Расписание_{group_name}.pdf", "PDF (*.pdf)"
        )
        if not file_path:
            return
        try:
            export_schedule_pdf(
                group_name,
                week_label,
                entries,
                hours,
                limit,
                file_path,
                self._bell_times_map(),
            )
        except OSError as error:
            QMessageBox.warning(self, "Ошибка экспорта", str(error))
            return
        QMessageBox.information(
            self, "Экспорт завершён", f"Файл сохранён:\n{file_path}"
        )
