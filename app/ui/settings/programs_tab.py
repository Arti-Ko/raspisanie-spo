import sqlite3

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

from app.repositories.programs import (
    add_program,
    delete_program,
    list_programs,
    update_program,
)
from app.ui.settings.program_dialog import ProgramDialog

COLUMNS = ["Код", "Название", "Срок обучения"]


class ProgramsTab(QWidget):
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
        programs = list_programs()
        self.table.setRowCount(len(programs))
        for row, program in enumerate(programs):
            code_item = QTableWidgetItem(program.code)
            code_item.setData(1000, program.id)
            self.table.setItem(row, 0, code_item)
            self.table.setItem(row, 1, QTableWidgetItem(program.name))
            self.table.setItem(row, 2, QTableWidgetItem(program.duration_label))
        self.table.resizeColumnsToContents()

    def _selected_program_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).data(1000)

    def _on_add(self) -> None:
        dialog = ProgramDialog(self)
        if dialog.exec():
            code, name, duration_months = dialog.values()
            try:
                add_program(code, name, duration_months)
            except sqlite3.IntegrityError:
                QMessageBox.warning(
                    self, "Ошибка", f"Программа с кодом «{code}» уже существует."
                )
                return
            self.refresh()

    def _on_edit(self) -> None:
        program_id = self._selected_program_id()
        if program_id is None:
            QMessageBox.information(self, "Изменение", "Выберите программу в таблице.")
            return
        program = next(p for p in list_programs() if p.id == program_id)
        dialog = ProgramDialog(self, program)
        if dialog.exec():
            code, name, duration_months = dialog.values()
            try:
                update_program(program_id, code, name, duration_months)
            except sqlite3.IntegrityError:
                QMessageBox.warning(
                    self, "Ошибка", f"Программа с кодом «{code}» уже существует."
                )
                return
            self.refresh()

    def _on_delete(self) -> None:
        program_id = self._selected_program_id()
        if program_id is None:
            QMessageBox.information(self, "Удаление", "Выберите программу в таблице.")
            return
        answer = QMessageBox.question(self, "Удаление", "Удалить выбранную программу?")
        if answer != QMessageBox.Yes:
            return
        try:
            delete_program(program_id)
        except sqlite3.IntegrityError:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Нельзя удалить программу — на неё ссылаются существующие группы.",
            )
            return
        self.refresh()
