from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
)

from app.repositories.calendar_weeks import CalendarWeek

DATE_FORMAT = "dd.MM.yyyy"


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

        self.saturday_check = QCheckBox("Суббота учебная (6-дневная неделя)")
        self.saturday_check.setChecked(week.includes_saturday if week else False)

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDisplayFormat(DATE_FORMAT)
        self.start_date_edit.setCalendarPopup(True)
        if week and week.start_date:
            self.start_date_edit.setDate(
                QDate.fromString(week.start_date, "yyyy-MM-dd")
            )
        else:
            self.start_date_edit.setDate(QDate.currentDate())

        form = QFormLayout()
        form.addRow("Номер недели*", self.week_number_spin)
        form.addRow("Часов*", self.hours_spin)
        form.addRow("Дата начала (понедельник)", self.start_date_edit)
        form.addRow("", self.saturday_check)
        form.addRow("Примечание", self.note_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def values(self) -> tuple[int, int, str, bool, str]:
        return (
            self.week_number_spin.value(),
            self.hours_spin.value(),
            self.note_edit.text().strip(),
            self.saturday_check.isChecked(),
            self.start_date_edit.date().toString("yyyy-MM-dd"),
        )
