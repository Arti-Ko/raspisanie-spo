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

from app.repositories.bell_times import list_bell_times, update_bell_time
from app.ui.settings.bell_time_dialog import BellTimeDialog

COLUMNS = ["Пара", "Начало", "Конец"]


class BellTimesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)

        edit_button = QPushButton("Изменить время")
        edit_button.clicked.connect(self._on_edit)

        buttons_row = QHBoxLayout()
        buttons_row.addWidget(edit_button)
        buttons_row.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(buttons_row)
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self) -> None:
        bell_times = list_bell_times()
        self.table.setRowCount(len(bell_times))
        for row, bell_time in enumerate(bell_times):
            number_item = QTableWidgetItem(f"Пара {bell_time.pair_number}")
            number_item.setData(1000, bell_time.pair_number)
            self.table.setItem(row, 0, number_item)
            self.table.setItem(row, 1, QTableWidgetItem(bell_time.start_time))
            self.table.setItem(row, 2, QTableWidgetItem(bell_time.end_time))
        self.table.resizeColumnsToContents()

    def _on_edit(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Изменение", "Выберите пару в таблице.")
            return
        bell_time = next(
            b
            for b in list_bell_times()
            if b.pair_number == self.table.item(row, 0).data(1000)
        )
        dialog = BellTimeDialog(self, bell_time)
        if dialog.exec():
            start_time, end_time = dialog.values()
            update_bell_time(bell_time.pair_number, start_time, end_time)
            self.refresh()
