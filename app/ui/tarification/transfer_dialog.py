from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
)

from app.repositories.tarification import Assignment


class TransferDialog(QDialog):
    def __init__(self, parent=None, assignment: Assignment | None = None):
        super().__init__(parent)
        self.setWindowTitle("Перенос часов между полугодиями")
        self.setMinimumWidth(360)

        info = QLabel(
            f"{assignment.subject_name} — {assignment.group_name}\n"
            f"Естественное полугодие: {assignment.semester}, часов по плану: {assignment.natural_hours}"
        )

        self.transfer_spin = QSpinBox()
        self.transfer_spin.setRange(0, assignment.natural_hours)
        self.transfer_spin.setValue(assignment.transferred_hours)

        form = QFormLayout()
        form.addRow(
            f"Перенести часов в {assignment.other_semester}-е полугодие",
            self.transfer_spin,
        )

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(info)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def value(self) -> int:
        return self.transfer_spin.value()
