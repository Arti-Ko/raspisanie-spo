from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
)

from app.repositories.schedule import ScheduleEntry
from app.repositories.tarification import list_assignments_for_group
from app.repositories.teachers import list_teachers

EMPTY = "— пусто (очистить) —"
NO_SUBSTITUTE = "— нет замены —"


class LessonCellDialog(QDialog):
    def __init__(
        self,
        parent=None,
        group_id: int | None = None,
        entry: ScheduleEntry | None = None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Пара в расписании")
        self.setMinimumWidth(360)

        self.assignments = list_assignments_for_group(group_id)
        self.teachers_by_id = {t.id: t for t in list_teachers()}

        self.assignment_combo = QComboBox()
        self.assignment_combo.addItem(EMPTY, None)
        for a in self.assignments:
            self.assignment_combo.addItem(f"{a.subject_name} — {a.teacher_name}", a.id)
        self.assignment_combo.currentIndexChanged.connect(self._on_assignment_changed)

        self.room_edit = QLineEdit(entry.room if entry else "")

        self.substitute_combo = QComboBox()
        self.substitute_combo.addItem(NO_SUBSTITUTE, None)
        for teacher in self.teachers_by_id.values():
            self.substitute_combo.addItem(teacher.full_name, teacher.id)

        if entry is not None:
            index = self.assignment_combo.findData(entry.assignment_id)
            if index >= 0:
                self.assignment_combo.setCurrentIndex(index)
            if entry.substitute_teacher_id is not None:
                sub_index = self.substitute_combo.findData(entry.substitute_teacher_id)
                if sub_index >= 0:
                    self.substitute_combo.setCurrentIndex(sub_index)

        form = QFormLayout()
        form.addRow("Предмет / преподаватель", self.assignment_combo)
        form.addRow("Кабинет", self.room_edit)
        form.addRow("Замена (если ведёт другой)", self.substitute_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _on_assignment_changed(self, _index: int) -> None:
        assignment_id = self.assignment_combo.currentData()
        if assignment_id is None or self.room_edit.text().strip():
            return
        assignment = next(a for a in self.assignments if a.id == assignment_id)
        teacher = self.teachers_by_id.get(assignment.teacher_id)
        if teacher and teacher.room:
            self.room_edit.setText(teacher.room)

    def values(self) -> tuple[int | None, str, int | None]:
        return (
            self.assignment_combo.currentData(),
            self.room_edit.text().strip(),
            self.substitute_combo.currentData(),
        )
