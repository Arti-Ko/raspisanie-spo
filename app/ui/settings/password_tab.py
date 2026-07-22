from PySide6.QtWidgets import (
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.repositories.auth import set_password, verify_password


class PasswordTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_edit = QLineEdit()
        self.current_edit.setEchoMode(QLineEdit.Password)
        self.new_edit = QLineEdit()
        self.new_edit.setEchoMode(QLineEdit.Password)
        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.Password)

        form = QFormLayout()
        form.addRow("Текущий пароль", self.current_edit)
        form.addRow("Новый пароль", self.new_edit)
        form.addRow("Повторите новый пароль", self.confirm_edit)

        change_button = QPushButton("Сменить пароль")
        change_button.clicked.connect(self._on_change_password)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(change_button)
        layout.addStretch()

    def _on_change_password(self) -> None:
        if not verify_password(self.current_edit.text()):
            QMessageBox.warning(self, "Ошибка", "Текущий пароль указан неверно.")
            return
        new_password = self.new_edit.text()
        if not new_password:
            QMessageBox.warning(self, "Ошибка", "Новый пароль не может быть пустым.")
            return
        if new_password != self.confirm_edit.text():
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают.")
            return
        set_password(new_password)
        self.current_edit.clear()
        self.new_edit.clear()
        self.confirm_edit.clear()
        QMessageBox.information(self, "Готово", "Пароль изменён.")
