from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
)

from app.repositories.groups import Group
from app.repositories.programs import list_programs


class GroupDialog(QDialog):
    def __init__(self, parent=None, group: Group | None = None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать группу" if group else "Новая группа")
        self.setMinimumWidth(360)

        self.name_edit = QLineEdit(group.name if group else "")

        self.program_combo = QComboBox()
        self._programs = list_programs()
        for program in self._programs:
            self.program_combo.addItem(f"{program.code} — {program.name}", program.id)
        if group is not None:
            index = self.program_combo.findData(group.program_id)
            if index >= 0:
                self.program_combo.setCurrentIndex(index)

        self.course_spin = QSpinBox()
        self.course_spin.setRange(1, 6)
        self.course_spin.setValue(group.course if group else 1)

        form = QFormLayout()
        form.addRow("Название группы*", self.name_edit)
        form.addRow("Специальность (программа)*", self.program_combo)
        form.addRow("Курс*", self.course_spin)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Проверка", "Укажите название группы.")
            return
        if self.program_combo.count() == 0:
            QMessageBox.warning(
                self,
                "Проверка",
                "Сначала добавьте хотя бы одну программу на вкладке «Программы».",
            )
            return
        self.accept()

    def values(self) -> tuple[str, int, int]:
        return (
            self.name_edit.text().strip(),
            self.program_combo.currentData(),
            self.course_spin.value(),
        )
