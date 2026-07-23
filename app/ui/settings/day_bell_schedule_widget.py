from PySide6.QtCore import QTime
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from app.repositories.bell_times import (
    LESSON_NUMBERS,
    PAIR_NUMBERS,
    get_zero_period,
    list_lessons,
    set_lesson_time,
    set_zero_period,
)

TIME_FORMAT = "HH:mm"
LESSON_COLUMNS = [
    "Пара",
    "Урок 1 начало",
    "Урок 1 конец",
    "Урок 2 начало",
    "Урок 2 конец",
]


def _time_edit(value: str | None) -> QTimeEdit:
    edit = QTimeEdit(QTime.fromString(value, TIME_FORMAT) if value else QTime(8, 0))
    edit.setDisplayFormat(TIME_FORMAT)
    return edit


class DayBellScheduleWidget(QWidget):
    def __init__(self, day_of_week: int, parent=None):
        super().__init__(parent)
        self.day_of_week = day_of_week

        self.zero_period_checkbox = QCheckBox("Нулевая пара")
        self.zero_period_start = _time_edit(None)
        self.zero_period_end = _time_edit(None)
        self.zero_period_checkbox.toggled.connect(self._on_zero_period_toggled)

        zero_row = QHBoxLayout()
        zero_row.addWidget(self.zero_period_checkbox)
        zero_row.addWidget(QLabel("с"))
        zero_row.addWidget(self.zero_period_start)
        zero_row.addWidget(QLabel("до"))
        zero_row.addWidget(self.zero_period_end)
        zero_row.addStretch()

        self.table = QTableWidget(len(PAIR_NUMBERS), len(LESSON_COLUMNS))
        self.table.setHorizontalHeaderLabels(LESSON_COLUMNS)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        for row, pair_number in enumerate(PAIR_NUMBERS):
            self.table.setItem(row, 0, QTableWidgetItem(f"Пара {pair_number}"))
            for lesson_number in LESSON_NUMBERS:
                self.table.setCellWidget(
                    row, 1 + (lesson_number - 1) * 2, _time_edit(None)
                )
                self.table.setCellWidget(
                    row, 2 + (lesson_number - 1) * 2, _time_edit(None)
                )

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self._on_save)

        layout = QVBoxLayout(self)
        layout.addLayout(zero_row)
        layout.addWidget(self.table)
        layout.addWidget(save_button)

        self.load()

    def _on_zero_period_toggled(self, checked: bool) -> None:
        self.zero_period_start.setEnabled(checked)
        self.zero_period_end.setEnabled(checked)

    def load(self) -> None:
        zero_period = get_zero_period(self.day_of_week)
        self.zero_period_checkbox.setChecked(zero_period.enabled)
        self._on_zero_period_toggled(zero_period.enabled)
        if zero_period.start_time:
            self.zero_period_start.setTime(
                QTime.fromString(zero_period.start_time, TIME_FORMAT)
            )
        if zero_period.end_time:
            self.zero_period_end.setTime(
                QTime.fromString(zero_period.end_time, TIME_FORMAT)
            )

        lessons = {
            (lesson.pair_number, lesson.lesson_number): lesson
            for lesson in list_lessons(self.day_of_week)
        }
        for row, pair_number in enumerate(PAIR_NUMBERS):
            for lesson_number in LESSON_NUMBERS:
                lesson = lessons.get((pair_number, lesson_number))
                if lesson is None:
                    continue
                start_col = 1 + (lesson_number - 1) * 2
                end_col = 2 + (lesson_number - 1) * 2
                self.table.cellWidget(row, start_col).setTime(
                    QTime.fromString(lesson.start_time, TIME_FORMAT)
                )
                self.table.cellWidget(row, end_col).setTime(
                    QTime.fromString(lesson.end_time, TIME_FORMAT)
                )

    def _on_save(self) -> None:
        set_zero_period(
            self.day_of_week,
            self.zero_period_checkbox.isChecked(),
            (
                self.zero_period_start.time().toString(TIME_FORMAT)
                if self.zero_period_checkbox.isChecked()
                else None
            ),
            (
                self.zero_period_end.time().toString(TIME_FORMAT)
                if self.zero_period_checkbox.isChecked()
                else None
            ),
        )
        for row, pair_number in enumerate(PAIR_NUMBERS):
            for lesson_number in LESSON_NUMBERS:
                start_col = 1 + (lesson_number - 1) * 2
                end_col = 2 + (lesson_number - 1) * 2
                start_time = (
                    self.table.cellWidget(row, start_col).time().toString(TIME_FORMAT)
                )
                end_time = (
                    self.table.cellWidget(row, end_col).time().toString(TIME_FORMAT)
                )
                set_lesson_time(
                    self.day_of_week, pair_number, lesson_number, start_time, end_time
                )
        QMessageBox.information(self, "Готово", "Расписание звонков сохранено.")
