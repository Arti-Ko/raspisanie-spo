from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.repositories.calendar_weeks import (
    add_week,
    add_weeks_bulk,
    delete_week,
    list_weeks,
    next_week_number,
    semester_total,
    update_week,
)
from app.ui.settings.calendar_week_dialog import CalendarWeekDialog

COLUMNS = ["Неделя", "Часов", "Даты", "Суббота", "Примечание"]


class SemesterWeeksWidget(QWidget):
    def __init__(self, semester: int, parent=None):
        super().__init__(parent)
        self.semester = semester
        self.academic_year_id: int | None = None

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)

        add_button = QPushButton("Добавить неделю")
        edit_button = QPushButton("Изменить")
        delete_button = QPushButton("Удалить")
        add_button.clicked.connect(self._on_add)
        edit_button.clicked.connect(self._on_edit)
        delete_button.clicked.connect(self._on_delete)

        buttons_row = QHBoxLayout()
        buttons_row.addWidget(add_button)
        buttons_row.addWidget(edit_button)
        buttons_row.addWidget(delete_button)
        buttons_row.addStretch()

        self.bulk_count_spin = QSpinBox()
        self.bulk_count_spin.setRange(1, 53)
        self.bulk_count_spin.setValue(17)
        self.bulk_hours_spin = QSpinBox()
        self.bulk_hours_spin.setRange(0, 60)
        self.bulk_hours_spin.setValue(36)
        bulk_button = QPushButton("Добавить пачкой")
        bulk_button.clicked.connect(self._on_bulk_add)

        bulk_row = QHBoxLayout()
        bulk_row.addWidget(QLabel("Быстрое добавление:"))
        bulk_row.addWidget(self.bulk_count_spin)
        bulk_row.addWidget(QLabel("недель по"))
        bulk_row.addWidget(self.bulk_hours_spin)
        bulk_row.addWidget(QLabel("ч."))
        bulk_row.addWidget(bulk_button)
        bulk_row.addStretch()

        self.total_label = QLabel("Итого за полугодие: 0 ч.")

        layout = QVBoxLayout(self)
        layout.addLayout(buttons_row)
        layout.addLayout(bulk_row)
        layout.addWidget(self.table)
        layout.addWidget(self.total_label)

    def set_academic_year(self, academic_year_id: int | None) -> None:
        self.academic_year_id = academic_year_id
        self.refresh()

    def refresh(self) -> None:
        if self.academic_year_id is None:
            self.table.setRowCount(0)
            self.total_label.setText("Итого за полугодие: 0 ч.")
            return
        weeks = list_weeks(self.academic_year_id, self.semester)
        self.table.setRowCount(len(weeks))
        for row, week in enumerate(weeks):
            number_item = QTableWidgetItem(str(week.week_number))
            number_item.setData(1000, week.id)
            self.table.setItem(row, 0, number_item)
            self.table.setItem(row, 1, QTableWidgetItem(str(week.hours)))
            self.table.setItem(row, 2, QTableWidgetItem(week.date_range_label))
            self.table.setItem(
                row, 3, QTableWidgetItem("да" if week.includes_saturday else "")
            )
            self.table.setItem(row, 4, QTableWidgetItem(week.note))
        self.table.resizeColumnsToContents()
        total = semester_total(self.academic_year_id, self.semester)
        self.total_label.setText(f"Итого за полугодие: {total} ч.")

    def _selected_week_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).data(1000)

    def _require_year(self) -> bool:
        if self.academic_year_id is None:
            QMessageBox.information(
                self, "Учебный год", "Сначала выберите или создайте учебный год."
            )
            return False
        return True

    def _on_add(self) -> None:
        if not self._require_year():
            return
        default_number = next_week_number(self.academic_year_id, self.semester)
        dialog = CalendarWeekDialog(self, default_week_number=default_number)
        if dialog.exec():
            week_number, hours, note, includes_saturday, start_date = dialog.values()
            add_week(
                self.academic_year_id,
                self.semester,
                week_number,
                hours,
                note,
                includes_saturday,
                start_date,
            )
            self.refresh()

    def _on_bulk_add(self) -> None:
        if not self._require_year():
            return
        add_weeks_bulk(
            self.academic_year_id,
            self.semester,
            self.bulk_count_spin.value(),
            self.bulk_hours_spin.value(),
            "",
        )
        self.refresh()

    def _on_edit(self) -> None:
        week_id = self._selected_week_id()
        if week_id is None:
            QMessageBox.information(self, "Изменение", "Выберите неделю в таблице.")
            return
        week = next(
            w
            for w in list_weeks(self.academic_year_id, self.semester)
            if w.id == week_id
        )
        dialog = CalendarWeekDialog(self, week)
        if dialog.exec():
            week_number, hours, note, includes_saturday, start_date = dialog.values()
            update_week(
                week_id, week_number, hours, note, includes_saturday, start_date
            )
            self.refresh()

    def _on_delete(self) -> None:
        week_id = self._selected_week_id()
        if week_id is None:
            QMessageBox.information(self, "Удаление", "Выберите неделю в таблице.")
            return
        answer = QMessageBox.question(self, "Удаление", "Удалить выбранную неделю?")
        if answer == QMessageBox.Yes:
            delete_week(week_id)
            self.refresh()
