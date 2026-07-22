from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.repositories.teachers import (
    add_teacher,
    delete_teacher,
    list_teachers,
    update_teacher,
)
from app.ui.settings.teacher_dialog import TeacherDialog

COLUMNS = ["ФИО", "Кабинет", "Предметы"]


class TeachersTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)

        add_button = QPushButton("Добавить")
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

        layout = QVBoxLayout(self)
        layout.addLayout(buttons_row)
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self) -> None:
        teachers = list_teachers()
        self.table.setRowCount(len(teachers))
        for row, teacher in enumerate(teachers):
            subjects_text = ", ".join(s.name for s in teacher.subjects)
            self.table.setItem(
                row, 0, self._readonly_item(teacher.full_name, teacher.id)
            )
            self.table.setItem(row, 1, self._readonly_item(teacher.room))
            self.table.setItem(row, 2, self._readonly_item(subjects_text))
        self.table.resizeColumnsToContents()

    @staticmethod
    def _readonly_item(text: str, teacher_id: int | None = None) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        if teacher_id is not None:
            item.setData(1000, teacher_id)
        return item

    def _selected_teacher_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).data(1000)

    def _on_add(self) -> None:
        dialog = TeacherDialog(self)
        if dialog.exec():
            full_name, room, subject_ids = dialog.values()
            add_teacher(full_name, room, subject_ids)
            self.refresh()

    def _on_edit(self) -> None:
        teacher_id = self._selected_teacher_id()
        if teacher_id is None:
            QMessageBox.information(
                self, "Изменение", "Выберите преподавателя в таблице."
            )
            return
        teacher = next(t for t in list_teachers() if t.id == teacher_id)
        dialog = TeacherDialog(self, teacher)
        if dialog.exec():
            full_name, room, subject_ids = dialog.values()
            update_teacher(teacher_id, full_name, room, subject_ids)
            self.refresh()

    def _on_delete(self) -> None:
        teacher_id = self._selected_teacher_id()
        if teacher_id is None:
            QMessageBox.information(
                self, "Удаление", "Выберите преподавателя в таблице."
            )
            return
        answer = QMessageBox.question(
            self, "Удаление", "Удалить выбранного преподавателя?"
        )
        if answer == QMessageBox.Yes:
            delete_teacher(teacher_id)
            self.refresh()
