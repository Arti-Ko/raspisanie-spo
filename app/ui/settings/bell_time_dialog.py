from PySide6.QtCore import QTime
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QTimeEdit,
    QVBoxLayout,
)

from app.repositories.bell_times import BellTime

TIME_FORMAT = "HH:mm"


class BellTimeDialog(QDialog):
    def __init__(self, parent=None, bell_time: BellTime | None = None):
        super().__init__(parent)
        self.setWindowTitle(f"Пара {bell_time.pair_number}")
        self.setMinimumWidth(280)

        self.start_edit = QTimeEdit(QTime.fromString(bell_time.start_time, TIME_FORMAT))
        self.start_edit.setDisplayFormat(TIME_FORMAT)
        self.end_edit = QTimeEdit(QTime.fromString(bell_time.end_time, TIME_FORMAT))
        self.end_edit.setDisplayFormat(TIME_FORMAT)

        form = QFormLayout()
        form.addRow("Начало", self.start_edit)
        form.addRow("Конец", self.end_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def values(self) -> tuple[str, str]:
        return self.start_edit.time().toString(
            TIME_FORMAT
        ), self.end_edit.time().toString(TIME_FORMAT)
