from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QMessageBox,
    QVBoxLayout,
)

from app.repositories.tarification import list_unassigned_curriculum_for_group
from app.repositories.teachers import list_teachers

SEMESTER_LABELS = {1: "I полугодие", 2: "II полугодие"}


class AssignDialog(QDialog):
    def __init__(self, parent=None, group_id: int | None = None):
        super().__init__(parent)
        self.setWindowTitle("Назначить преподавателя")
        self.setMinimumWidth(360)

        self.subject_combo = QComboBox()
        for item_id, subject_name, semester in list_unassigned_curriculum_for_group(
            group_id
        ):
            self.subject_combo.addItem(
                f"{SEMESTER_LABELS[semester]} — {subject_name}", item_id
            )

        self.teacher_combo = QComboBox()
        for teacher in list_teachers():
            self.teacher_combo.addItem(teacher.full_name, teacher.id)

        form = QFormLayout()
        form.addRow("Предмет плана*", self.subject_combo)
        form.addRow("Преподаватель*", self.teacher_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        if self.subject_combo.count() == 0:
            QMessageBox.warning(
                self, "Проверка", "Все предметы плана для этой группы уже назначены."
            )
            return
        if self.teacher_combo.count() == 0:
            QMessageBox.warning(
                self,
                "Проверка",
                "Сначала добавьте преподавателей на вкладке «Преподаватели».",
            )
            return
        self.accept()

    def values(self) -> tuple[int, int]:
        return self.subject_combo.currentData(), self.teacher_combo.currentData()
