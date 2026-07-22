import sqlite3

from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.repositories.groups import list_groups
from app.repositories.tarification import (
    add_assignment,
    delete_assignment,
    list_assignments_for_group,
    update_transfer,
)
from app.ui.tarification.assign_dialog import AssignDialog
from app.ui.tarification.transfer_dialog import TransferDialog

COLUMNS = [
    "Полугодие",
    "Предмет",
    "Преподаватель",
    "Часов по плану",
    "Перенесено",
    "Часов фактически",
]


class GroupAssignmentsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.group_combo = QComboBox()
        self.group_combo.currentIndexChanged.connect(self.refresh)

        selector_row = QHBoxLayout()
        selector_row.addWidget(QLabel("Группа:"))
        selector_row.addWidget(self.group_combo)
        selector_row.addStretch()

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)

        assign_button = QPushButton("Назначить преподавателя")
        transfer_button = QPushButton("Перенос часов")
        delete_button = QPushButton("Удалить назначение")
        assign_button.clicked.connect(self._on_assign)
        transfer_button.clicked.connect(self._on_transfer)
        delete_button.clicked.connect(self._on_delete)

        buttons_row = QHBoxLayout()
        buttons_row.addWidget(assign_button)
        buttons_row.addWidget(transfer_button)
        buttons_row.addWidget(delete_button)
        buttons_row.addStretch()

        self.totals_label = QLabel("")

        layout = QVBoxLayout(self)
        layout.addLayout(selector_row)
        layout.addLayout(buttons_row)
        layout.addWidget(self.table)
        layout.addWidget(self.totals_label)

        self.reload_groups()

    def reload_groups(self) -> None:
        current_id = self.group_combo.currentData()
        self.group_combo.blockSignals(True)
        self.group_combo.clear()
        for group in list_groups():
            self.group_combo.addItem(group.name, group.id)
        self.group_combo.blockSignals(False)
        index = self.group_combo.findData(current_id)
        self.group_combo.setCurrentIndex(index if index >= 0 else 0)
        self.refresh()

    def refresh(self) -> None:
        group_id = self.group_combo.currentData()
        if group_id is None:
            self.table.setRowCount(0)
            self.totals_label.setText("")
            return
        assignments = list_assignments_for_group(group_id)
        self.table.setRowCount(len(assignments))
        totals = {1: 0, 2: 0}
        for row, a in enumerate(assignments):
            semester_item = QTableWidgetItem(f"{a.semester}-е")
            semester_item.setData(1000, a.id)
            self.table.setItem(row, 0, semester_item)
            self.table.setItem(row, 1, QTableWidgetItem(a.subject_name))
            self.table.setItem(row, 2, QTableWidgetItem(a.teacher_name))
            self.table.setItem(row, 3, QTableWidgetItem(str(a.natural_hours)))
            self.table.setItem(
                row,
                4,
                QTableWidgetItem(
                    str(a.transferred_hours) if a.transferred_hours else "—"
                ),
            )
            self.table.setItem(
                row, 5, QTableWidgetItem(str(a.hours_in_natural_semester))
            )
            totals[a.semester] += a.hours_in_natural_semester
            totals[a.other_semester] += a.transferred_hours
        self.table.resizeColumnsToContents()
        self.totals_label.setText(
            f"Часы группы: I полугодие — {totals[1]} ч., II полугодие — {totals[2]} ч."
        )

    def _selected_assignment_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).data(1000)

    def _on_assign(self) -> None:
        group_id = self.group_combo.currentData()
        if group_id is None:
            QMessageBox.information(
                self, "Нет групп", "Сначала добавьте группу на вкладке «Группы»."
            )
            return
        dialog = AssignDialog(self, group_id)
        if dialog.exec():
            curriculum_item_id, teacher_id = dialog.values()
            try:
                add_assignment(teacher_id, group_id, curriculum_item_id)
            except sqlite3.IntegrityError:
                QMessageBox.warning(
                    self, "Ошибка", "Этот предмет уже назначен для группы."
                )
                return
            self.refresh()

    def _on_transfer(self) -> None:
        assignment_id = self._selected_assignment_id()
        if assignment_id is None:
            QMessageBox.information(
                self, "Перенос часов", "Выберите назначение в таблице."
            )
            return
        group_id = self.group_combo.currentData()
        assignment = next(
            a for a in list_assignments_for_group(group_id) if a.id == assignment_id
        )
        dialog = TransferDialog(self, assignment)
        if dialog.exec():
            update_transfer(assignment_id, dialog.value())
            self.refresh()

    def _on_delete(self) -> None:
        assignment_id = self._selected_assignment_id()
        if assignment_id is None:
            QMessageBox.information(self, "Удаление", "Выберите назначение в таблице.")
            return
        answer = QMessageBox.question(
            self, "Удаление", "Удалить назначение преподавателя?"
        )
        if answer == QMessageBox.Yes:
            delete_assignment(assignment_id)
            self.refresh()
