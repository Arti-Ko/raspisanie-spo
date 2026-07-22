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

from app.repositories.groups import add_group, delete_group, list_groups, update_group
from app.repositories.programs import list_programs
from app.ui.settings.group_dialog import GroupDialog

COLUMNS = ["Группа", "Специальность", "Курс"]


class GroupsTab(QWidget):
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
        groups = list_groups()
        self.table.setRowCount(len(groups))
        for row, group in enumerate(groups):
            name_item = QTableWidgetItem(group.name)
            name_item.setData(1000, group.id)
            self.table.setItem(row, 0, name_item)
            self.table.setItem(
                row, 1, QTableWidgetItem(f"{group.program_code} — {group.program_name}")
            )
            self.table.setItem(row, 2, QTableWidgetItem(str(group.course)))
        self.table.resizeColumnsToContents()

    def _selected_group_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).data(1000)

    def _require_programs(self) -> bool:
        if not list_programs():
            QMessageBox.information(
                self,
                "Нет программ",
                "Сначала добавьте хотя бы одну программу на вкладке «Программы».",
            )
            return False
        return True

    def _on_add(self) -> None:
        if not self._require_programs():
            return
        dialog = GroupDialog(self)
        if dialog.exec():
            name, program_id, course = dialog.values()
            try:
                add_group(name, program_id, course)
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Ошибка", f"Группа «{name}» уже существует.")
                return
            self.refresh()

    def _on_edit(self) -> None:
        group_id = self._selected_group_id()
        if group_id is None:
            QMessageBox.information(self, "Изменение", "Выберите группу в таблице.")
            return
        group = next(g for g in list_groups() if g.id == group_id)
        dialog = GroupDialog(self, group)
        if dialog.exec():
            name, program_id, course = dialog.values()
            try:
                update_group(group_id, name, program_id, course)
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Ошибка", f"Группа «{name}» уже существует.")
                return
            self.refresh()

    def _on_delete(self) -> None:
        group_id = self._selected_group_id()
        if group_id is None:
            QMessageBox.information(self, "Удаление", "Выберите группу в таблице.")
            return
        answer = QMessageBox.question(self, "Удаление", "Удалить выбранную группу?")
        if answer == QMessageBox.Yes:
            delete_group(group_id)
            self.refresh()
