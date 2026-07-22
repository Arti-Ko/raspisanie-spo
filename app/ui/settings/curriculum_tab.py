import sqlite3

from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
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

from app.repositories.curriculum import (
    add_curriculum_item,
    delete_curriculum_item,
    list_curriculum,
    update_curriculum_item,
)
from app.repositories.programs import list_programs
from app.ui.settings.curriculum_item_dialog import CurriculumItemDialog

COLUMNS = ["Полугодие", "Предмет", "Тип", "Теория", "Практика", "Экзамен", "Итого"]
SEMESTER_LABELS = {1: "I полугодие", 2: "II полугодие"}


class CurriculumTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.program_combo = QComboBox()
        self.program_combo.currentIndexChanged.connect(self.refresh)
        self.course_spin = QSpinBox()
        self.course_spin.setRange(1, 6)
        self.course_spin.valueChanged.connect(self.refresh)

        selector_row = QHBoxLayout()
        selector_row.addWidget(QLabel("Специальность (программа):"))
        selector_row.addWidget(self.program_combo)
        selector_row.addWidget(QLabel("Курс:"))
        selector_row.addWidget(self.course_spin)
        selector_row.addStretch()

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)

        add_button = QPushButton("Добавить предмет")
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

        self.totals_label = QLabel("")

        layout = QVBoxLayout(self)
        layout.addLayout(selector_row)
        layout.addLayout(buttons_row)
        layout.addWidget(self.table)
        layout.addWidget(self.totals_label)

        self.reload_programs()

    def refresh_reference_data(self) -> None:
        self.reload_programs()

    def reload_programs(self) -> None:
        current_id = self.program_combo.currentData()
        self.program_combo.blockSignals(True)
        self.program_combo.clear()
        for program in list_programs():
            self.program_combo.addItem(f"{program.code} — {program.name}", program.id)
        self.program_combo.blockSignals(False)
        index = self.program_combo.findData(current_id)
        self.program_combo.setCurrentIndex(index if index >= 0 else 0)
        self.refresh()

    def refresh(self) -> None:
        program_id = self.program_combo.currentData()
        if program_id is None:
            self.table.setRowCount(0)
            self.totals_label.setText("")
            return
        items = list_curriculum(program_id, self.course_spin.value())
        self.table.setRowCount(len(items))
        totals = {1: 0, 2: 0}
        for row, item in enumerate(items):
            semester_item = QTableWidgetItem(SEMESTER_LABELS[item.semester])
            semester_item.setData(1000, item.id)
            self.table.setItem(row, 0, semester_item)
            self.table.setItem(row, 1, QTableWidgetItem(item.subject_name))
            self.table.setItem(row, 2, QTableWidgetItem(item.lesson_type_label))
            self.table.setItem(row, 3, QTableWidgetItem(str(item.hours_theory)))
            self.table.setItem(row, 4, QTableWidgetItem(str(item.hours_practice)))
            self.table.setItem(row, 5, QTableWidgetItem(str(item.hours_exam)))
            self.table.setItem(row, 6, QTableWidgetItem(str(item.total_hours)))
            totals[item.semester] += item.total_hours
        self.table.resizeColumnsToContents()
        self.totals_label.setText(
            f"Итого: I полугодие — {totals[1]} ч., II полугодие — {totals[2]} ч."
        )

    def _selected_item_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).data(1000)

    def _require_program(self) -> int | None:
        program_id = self.program_combo.currentData()
        if program_id is None:
            QMessageBox.information(
                self,
                "Нет программ",
                "Сначала добавьте программу на вкладке «Программы».",
            )
            return None
        return program_id

    def _on_add(self) -> None:
        program_id = self._require_program()
        if program_id is None:
            return
        dialog = CurriculumItemDialog(self)
        if dialog.exec():
            semester, subject_id, theory, practice, exam, lesson_type = dialog.values()
            try:
                add_curriculum_item(
                    program_id,
                    self.course_spin.value(),
                    semester,
                    subject_id,
                    theory,
                    practice,
                    exam,
                    lesson_type,
                )
            except sqlite3.IntegrityError:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Этот предмет уже есть в плане на выбранное полугодие.",
                )
                return
            self.refresh()

    def _on_edit(self) -> None:
        item_id = self._selected_item_id()
        if item_id is None:
            QMessageBox.information(self, "Изменение", "Выберите предмет в таблице.")
            return
        program_id = self.program_combo.currentData()
        item = next(
            i
            for i in list_curriculum(program_id, self.course_spin.value())
            if i.id == item_id
        )
        dialog = CurriculumItemDialog(self, item)
        if dialog.exec():
            semester, subject_id, theory, practice, exam, lesson_type = dialog.values()
            try:
                update_curriculum_item(
                    item_id, semester, subject_id, theory, practice, exam, lesson_type
                )
            except sqlite3.IntegrityError:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Этот предмет уже есть в плане на выбранное полугодие.",
                )
                return
            self.refresh()

    def _on_delete(self) -> None:
        item_id = self._selected_item_id()
        if item_id is None:
            QMessageBox.information(self, "Удаление", "Выберите предмет в таблице.")
            return
        answer = QMessageBox.question(
            self, "Удаление", "Удалить предмет из учебного плана?"
        )
        if answer == QMessageBox.Yes:
            delete_curriculum_item(item_id)
            self.refresh()
