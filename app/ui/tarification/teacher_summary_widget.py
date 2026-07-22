from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.repositories.academic_years import list_academic_years
from app.repositories.calendar_weeks import semester_total
from app.repositories.tarification import all_teacher_totals

COLUMNS = [
    "Преподаватель",
    "I полугодие",
    "Лимит I",
    "II полугодие",
    "Лимит II",
    "Всего за год",
]
OVER_LIMIT_COLOR = QColor(255, 205, 205)


class TeacherSummaryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.year_combo = QComboBox()
        self.year_combo.currentIndexChanged.connect(self.refresh)

        selector_row = QHBoxLayout()
        selector_row.addWidget(QLabel("Учебный год (для сверки с лимитом):"))
        selector_row.addWidget(self.year_combo)
        selector_row.addStretch()

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)

        layout = QVBoxLayout(self)
        layout.addLayout(selector_row)
        layout.addWidget(self.table)

        self.reload_years()

    def reload_years(self) -> None:
        current_id = self.year_combo.currentData()
        self.year_combo.blockSignals(True)
        self.year_combo.clear()
        for year in list_academic_years():
            self.year_combo.addItem(year.name, year.id)
        self.year_combo.blockSignals(False)
        index = self.year_combo.findData(current_id)
        self.year_combo.setCurrentIndex(index if index >= 0 else 0)
        self.refresh()

    def refresh(self) -> None:
        year_id = self.year_combo.currentData()
        limit1 = semester_total(year_id, 1) if year_id is not None else 0
        limit2 = semester_total(year_id, 2) if year_id is not None else 0

        totals = all_teacher_totals()
        self.table.setRowCount(len(totals))
        for row, (teacher_id, (name, semesters)) in enumerate(
            sorted(totals.items(), key=lambda kv: kv[1][0])
        ):
            hours1, hours2 = semesters[1], semesters[2]
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self._set_hours_cell(row, 1, hours1, limit1)
            self.table.setItem(
                row, 2, QTableWidgetItem(str(limit1) if year_id is not None else "—")
            )
            self._set_hours_cell(row, 3, hours2, limit2)
            self.table.setItem(
                row, 4, QTableWidgetItem(str(limit2) if year_id is not None else "—")
            )
            self.table.setItem(row, 5, QTableWidgetItem(str(hours1 + hours2)))
        self.table.resizeColumnsToContents()

    def _set_hours_cell(self, row: int, column: int, hours: int, limit: int) -> None:
        item = QTableWidgetItem(str(hours))
        if limit and hours > limit:
            item.setBackground(OVER_LIMIT_COLOR)
        self.table.setItem(row, column, item)
