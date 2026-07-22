from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.repositories.subjects import get_or_create_subject, list_subjects
from app.repositories.teachers import Teacher


class TeacherDialog(QDialog):
    def __init__(self, parent=None, teacher: Teacher | None = None):
        super().__init__(parent)
        self._teacher = teacher
        self.setWindowTitle(
            "Редактировать преподавателя" if teacher else "Новый преподаватель"
        )
        self.setMinimumWidth(360)

        self.name_edit = QLineEdit(teacher.full_name if teacher else "")
        self.room_edit = QLineEdit(teacher.room if teacher else "")

        self.subjects_list = QListWidget()
        self._reload_subjects(
            checked_ids={s.id for s in teacher.subjects} if teacher else set()
        )

        new_subject_row = QHBoxLayout()
        self.new_subject_edit = QLineEdit()
        self.new_subject_edit.setPlaceholderText("Новый предмет...")
        add_subject_button = QPushButton("Добавить предмет")
        add_subject_button.clicked.connect(self._add_subject)
        new_subject_row.addWidget(self.new_subject_edit)
        new_subject_row.addWidget(add_subject_button)

        form = QFormLayout()
        form.addRow("ФИО*", self.name_edit)
        form.addRow("Кабинет", self.room_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(QLabel("Предметы:"))
        layout.addWidget(self.subjects_list)
        layout.addLayout(new_subject_row)
        layout.addWidget(buttons)

    def _reload_subjects(self, checked_ids: set[int]) -> None:
        self.subjects_list.clear()
        for subject in list_subjects():
            item = QListWidgetItem(subject.name)
            item.setData(Qt.UserRole, subject.id)
            item.setCheckState(
                Qt.Checked if subject.id in checked_ids else Qt.Unchecked
            )
            self.subjects_list.addItem(item)

    def _add_subject(self) -> None:
        name = self.new_subject_edit.text().strip()
        if not name:
            return
        subject = get_or_create_subject(name)
        checked_ids = self._checked_subject_ids()
        checked_ids.add(subject.id)
        self._reload_subjects(checked_ids)
        self.new_subject_edit.clear()

    def _checked_subject_ids(self) -> set[int]:
        ids = set()
        for i in range(self.subjects_list.count()):
            item = self.subjects_list.item(i)
            if item.checkState() == Qt.Checked:
                ids.add(item.data(Qt.UserRole))
        return ids

    def _on_accept(self) -> None:
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Проверка", "Укажите ФИО преподавателя.")
            return
        self.accept()

    def values(self) -> tuple[str, str, list[int]]:
        return (
            self.name_edit.text().strip(),
            self.room_edit.text().strip(),
            list(self._checked_subject_ids()),
        )
