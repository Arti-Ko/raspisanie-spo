from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
)

from app.repositories.programs import Program


class ProgramDialog(QDialog):
    def __init__(self, parent=None, program: Program | None = None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать программу" if program else "Новая программа")
        self.setMinimumWidth(360)

        self.code_edit = QLineEdit(program.code if program else "")
        self.name_edit = QLineEdit(program.name if program else "")

        years, months = divmod(program.duration_months, 12) if program else (0, 0)
        self.years_spin = QSpinBox()
        self.years_spin.setRange(0, 10)
        self.years_spin.setValue(years)
        self.months_spin = QSpinBox()
        self.months_spin.setRange(0, 11)
        self.months_spin.setValue(months)

        duration_row = QHBoxLayout()
        duration_row.addWidget(self.years_spin)
        duration_row.addWidget(QLabel("лет"))
        duration_row.addWidget(self.months_spin)
        duration_row.addWidget(QLabel("мес."))

        form = QFormLayout()
        form.addRow("Код*", self.code_edit)
        form.addRow("Название*", self.name_edit)
        form.addRow("Срок обучения*", duration_row)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        if not self.code_edit.text().strip() or not self.name_edit.text().strip():
            QMessageBox.warning(self, "Проверка", "Укажите код и название программы.")
            return
        if self.years_spin.value() == 0 and self.months_spin.value() == 0:
            QMessageBox.warning(
                self, "Проверка", "Срок обучения должен быть больше нуля."
            )
            return
        self.accept()

    def values(self) -> tuple[str, str, int]:
        duration_months = self.years_spin.value() * 12 + self.months_spin.value()
        return (
            self.code_edit.text().strip(),
            self.name_edit.text().strip(),
            duration_months,
        )
