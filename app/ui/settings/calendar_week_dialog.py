from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
)

from app.repositories.calendar_weeks import CalendarWeek


class CalendarWeekDialog(QDialog):
    def __init__(
        self,
        parent=None,
        week: CalendarWeek | None = None,
        default_week_number: int = 1,
    ):
        super().__init__(parent)
        self.setWindowTitle("Редактировать неделю" if week else "Новая неделя")
        self.setMinimumWidth(320)

        self.week_number_spin = QSpinBox()
        self.week_number_spin.setRange(1, 53)
        self.week_number_spin.setValue(
            week.week_number if week else default_week_number
        )

        self.hours_spin = QSpinBox()
        self.hours_spin.setRange(0, 60)
        self.hours_spin.setValue(week.hours if week else 36)

        self.note_edit = QLineEdit(week.note if week else "")
        self.note_edit.setPlaceholderText("например: праздничная неделя")

        form = QFormLayout()
        form.addRow("Номер недели*", self.week_number_spin)
        form.addRow("Часов*", self.hours_spin)
        form.addRow("Примечание", self.note_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def values(self) -> tuple[int, int, str]:
        return (
            self.week_number_spin.value(),
            self.hours_spin.value(),
            self.note_edit.text().strip(),
        )
