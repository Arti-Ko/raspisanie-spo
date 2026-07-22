from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from app.repositories.curriculum import LESSON_TYPE_LABELS, LESSON_TYPES, CurriculumItem
from app.repositories.subjects import get_or_create_subject, list_subjects


class CurriculumItemDialog(QDialog):
    def __init__(self, parent=None, item: CurriculumItem | None = None):
        super().__init__(parent)
        self.setWindowTitle(
            "Редактировать предмет" if item else "Новый предмет в плане"
        )
        self.setMinimumWidth(380)

        self.semester_combo = QComboBox()
        self.semester_combo.addItem("I полугодие", 1)
        self.semester_combo.addItem("II полугодие", 2)
        if item is not None:
            self.semester_combo.setCurrentIndex(item.semester - 1)

        self.subject_combo = QComboBox()
        self._reload_subjects(item.subject_id if item else None)

        new_subject_row = QHBoxLayout()
        self.new_subject_edit = QLineEdit()
        self.new_subject_edit.setPlaceholderText("Новый предмет...")
        add_subject_button = QPushButton("Добавить")
        add_subject_button.clicked.connect(self._add_subject)
        new_subject_row.addWidget(self.new_subject_edit)
        new_subject_row.addWidget(add_subject_button)

        self.lesson_type_combo = QComboBox()
        for lesson_type in LESSON_TYPES:
            self.lesson_type_combo.addItem(LESSON_TYPE_LABELS[lesson_type], lesson_type)
        if item is not None:
            index = self.lesson_type_combo.findData(item.lesson_type)
            if index >= 0:
                self.lesson_type_combo.setCurrentIndex(index)

        self.theory_spin = QSpinBox()
        self.theory_spin.setRange(0, 2000)
        self.theory_spin.setValue(item.hours_theory if item else 0)

        self.practice_spin = QSpinBox()
        self.practice_spin.setRange(0, 2000)
        self.practice_spin.setSingleStep(6)
        self.practice_spin.setValue(item.hours_practice if item else 0)

        self.exam_spin = QSpinBox()
        self.exam_spin.setRange(0, 200)
        self.exam_spin.setValue(item.hours_exam if item else 0)

        form = QFormLayout()
        form.addRow("Полугодие*", self.semester_combo)
        form.addRow("Предмет*", self.subject_combo)
        form.addRow("", new_subject_row)
        form.addRow("Тип занятия*", self.lesson_type_combo)
        form.addRow("Часов теории", self.theory_spin)
        form.addRow("Часов практики", self.practice_spin)
        form.addRow("Часов экзамена", self.exam_spin)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _reload_subjects(self, selected_subject_id: int | None) -> None:
        self.subject_combo.clear()
        for subject in list_subjects():
            self.subject_combo.addItem(subject.name, subject.id)
        if selected_subject_id is not None:
            index = self.subject_combo.findData(selected_subject_id)
            if index >= 0:
                self.subject_combo.setCurrentIndex(index)

    def _add_subject(self) -> None:
        name = self.new_subject_edit.text().strip()
        if not name:
            return
        subject = get_or_create_subject(name)
        self._reload_subjects(subject.id)
        self.new_subject_edit.clear()

    def _on_accept(self) -> None:
        if self.subject_combo.count() == 0:
            QMessageBox.warning(self, "Проверка", "Добавьте хотя бы один предмет.")
            return
        if (
            self.theory_spin.value() == 0
            and self.practice_spin.value() == 0
            and self.exam_spin.value() == 0
        ):
            QMessageBox.warning(
                self, "Проверка", "Укажите часы хотя бы по одному типу нагрузки."
            )
            return
        if (
            self.lesson_type_combo.currentData() == "practice"
            and self.practice_spin.value() % 6 != 0
        ):
            QMessageBox.warning(
                self,
                "Проверка",
                "Часы учебной практики должны быть кратны 6 (блоками по одному дню).",
            )
            return
        self.accept()

    def values(self) -> tuple[int, int, int, int, int, str]:
        return (
            self.semester_combo.currentData(),
            self.subject_combo.currentData(),
            self.theory_spin.value(),
            self.practice_spin.value(),
            self.exam_spin.value(),
            self.lesson_type_combo.currentData(),
        )
