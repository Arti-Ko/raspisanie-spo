import sqlite3

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.repositories.academic_years import (
    add_academic_year,
    delete_academic_year,
    list_academic_years,
)
from app.ui.settings.semester_weeks_widget import SemesterWeeksWidget


class CalendarTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.year_combo = QComboBox()
        self.year_combo.currentIndexChanged.connect(self._on_year_changed)
        new_year_button = QPushButton("Новый учебный год")
        new_year_button.clicked.connect(self._on_new_year)
        delete_year_button = QPushButton("Удалить учебный год")
        delete_year_button.clicked.connect(self._on_delete_year)

        year_row = QHBoxLayout()
        year_row.addWidget(QLabel("Учебный год:"))
        year_row.addWidget(self.year_combo)
        year_row.addWidget(new_year_button)
        year_row.addWidget(delete_year_button)
        year_row.addStretch()

        self.semester1_widget = SemesterWeeksWidget(semester=1)
        self.semester2_widget = SemesterWeeksWidget(semester=2)

        semesters_tabs = QTabWidget()
        semesters_tabs.addTab(self.semester1_widget, "I полугодие")
        semesters_tabs.addTab(self.semester2_widget, "II полугодие")

        layout = QVBoxLayout(self)
        layout.addLayout(year_row)
        layout.addWidget(semesters_tabs)

        self.refresh()

    def refresh(self) -> None:
        current_id = self.year_combo.currentData()
        self.year_combo.blockSignals(True)
        self.year_combo.clear()
        for year in list_academic_years():
            self.year_combo.addItem(year.name, year.id)
        self.year_combo.blockSignals(False)

        index = self.year_combo.findData(current_id)
        self.year_combo.setCurrentIndex(index if index >= 0 else 0)
        self._on_year_changed(self.year_combo.currentIndex())

    def _on_year_changed(self, _index: int) -> None:
        year_id = self.year_combo.currentData()
        self.semester1_widget.set_academic_year(year_id)
        self.semester2_widget.set_academic_year(year_id)

    def _on_new_year(self) -> None:
        name, ok = QInputDialog.getText(
            self, "Новый учебный год", "Название (например 2026-2027):"
        )
        name = name.strip()
        if not ok or not name:
            return
        try:
            add_academic_year(name)
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", f"Учебный год «{name}» уже существует.")
            return
        self.refresh()
        index = self.year_combo.findText(name)
        if index >= 0:
            self.year_combo.setCurrentIndex(index)

    def _on_delete_year(self) -> None:
        year_id = self.year_combo.currentData()
        if year_id is None:
            return
        answer = QMessageBox.question(
            self, "Удаление", "Удалить учебный год и весь его календарь недель?"
        )
        if answer == QMessageBox.Yes:
            delete_academic_year(year_id)
            self.refresh()
